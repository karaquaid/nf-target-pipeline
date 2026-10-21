# Phase 2 pipeline spec

**Status:** the six methodological calls were ratified by Kara on 2026-10-19. This document is what the
ingestion scripts are checked against: a script that departs from it is wrong until this file is changed
first. The reasoning behind each call is in the Phase 2 section of `docs/project-plan.md`.

## Inputs

| input | file | note |
|---|---|---|
| launch set | `phase-2/data/phase2-launchset-readiness.csv` | 21 datasets, regenerate with `phase-2/scripts/phase2_launchset_readiness.py` |
| sample membership and arms (GEO) | `phase-2/data/phase2-sample-overrides.csv` | `use_in_phase2`, `de_role`, `de_arm`; overrides the Phase 1a labels |
| sample membership and arms (ArrayExpress) | `phase-2/data/phase2-non-geo-samples.csv` | same role for datasets with no Phase 1a sample labels |
| rulings and stated contrasts | `phase-2/data/phase2-review-diagnosis.json` | `decisions` block, keyed by accession |
| frozen Phase 1a labels | `phase-1a/data/phase1a-samples.csv` | used only where no override row exists |

A sample enters a contrast only if an override (or non-GEO) row says so. Absence of a row means the
Phase 1a label stands; absence of `de_arm` means the dataset has no contrast yet and is not runnable.

`phase-2/scripts/phase2_verify_arms.py` is the gate on the arm assignment: it compares every arm label and
arm size against the contrast recorded for that dataset and exits non-zero on a disagreement. Run it after any
edit to `de_arm`, before the pipeline reads the file.

`phase-2/scripts/phase2_raw_file_check.py` is the equivalent gate on the inputs: it confirms that every
dataset's archive files resolve and that what they hold matches the recorded `data_availability`. As of
2026-10-20 all 21 resolve, 20.2 GB in total.

## Per-dataset pipeline

One pass per dataset, no cross-dataset pooling at any step.

1. **Fetch** raw files into `build/phase2/<accession>/`, outside the repo. Record the source URL, file
   names, byte sizes and retrieval date in the manifest. A dataset whose raw files do not resolve is
   recorded as a failure, never silently substituted with a processed matrix.
2. **Normalize**, per assay class:
   - expression array: background-correct and normalize with the platform's standard route, then log2
   - bulk RNA-seq raw counts: keep counts; normalization is internal to DESeq2
   - single-cell: pseudobulk to **one profile per patient** using that dataset's stated patient rule,
     then treat as counts
3. **Map identifiers** to HGNC symbols through a pinned Ensembl release. Record the release in the
   manifest. Keep the original probe or gene id on every row. Count, do not silently drop: unmapped
   features, multi-mapping probes, and the collapse rule used when several probes hit one symbol.
4. **Batch-correct (optional, off by default).** ComBat within a dataset only, on a covariate that is
   actually populated in the sample table (platform, batch, FFPE vs fresh). Skip with a logged reason
   when the covariate is confounded with `de_arm`. Never correct across datasets.
5. **Test**, per the ratified engines:
   - expression array: `limma`, `trend=TRUE`
   - raw counts: `DESeq2`
   - pseudobulked single-cell: `limma-trend` on log-CPM
   - targeted panel (GSE239561, NanoString nCounter PanCancer IO360, 770 genes): housekeeping-gene
     normalization first, then `limma` on the log2 normalized counts. Not the plain array route. Kept in the
     ranking by Kara's ruling of 2026-10-20, with `gene_space = panel:770` in the manifest: Phase 3 restricts
     this dataset's contribution to the panel genes and treats every off-panel gene as not measured here,
     never as ranked low
   Contrast is `de_arm` vs the dataset's declared reference arm. Arms with fewer than 2 samples are
   excluded from the test and named in the manifest.
6. **Write outputs** (below), then stop. Ranking across datasets is Phase 3.

## Output contract

Per dataset, written to disk so Phase 3 re-runs without re-downloading:

- `<accession>_samples.csv` - one row per ingested sample: `sample_id`, `de_arm`, `de_role`,
  `patient_id`, `platform`, `batch`, `preservation`, plus any covariate extracted from
  `characteristics`.
- `<accession>_matrix.tsv.gz` - the normalized matrix actually tested, genes by samples, with the
  identifier columns from step 3.
- `<accession>_de.csv` - **the full ranked gene list**, not a thresholded table: `gene_symbol`,
  `source_id`, `statistic` (signed), `log2fc`, `p_value`, `fdr`, `rank`, `direction`. Rank aggregation
  in Phase 3 reads this file and nothing else.
- one row appended to `phase-2/data/phase2-ingestion-manifest.csv`: accession, assay class, engine and
  version, reference arm, `effect_type` (`disease_vs_normal` or `between_state`), `gene_space`
  (`transcriptome` or `panel:<n>`), n per arm, Ensembl release, mapping losses, ComBat applied or the
  reason it was not, patient rule, raw-file provenance, and run date.

`effect_type` is load-bearing: 7 of the 21 datasets carry a human control arm and the rest compare two
tumour states, and Phase 3 may not mix the two readings in one ranking without saying so.

## Datasets that produce no ranking

In the manifest and the matrix, absent from the Phase 3 meta-analysis, by ruling rather than by failure:

- **GSE232528** (14 NF2-patient meningiomas) and **GSE344687** (11 NF2-associated vestibular schwannoma
  libraries): single-armed once sporadic comparators are excluded, per the standing policy that sporadic
  material is never a reference arm.
- **GSE218493**: two samples, one per arm, so no test is possible. Kept at Kara's instruction.

## Verification requirement

Before writing a preprocessing function, fetch the current documentation for the package it calls
(GEOquery or GEOparse, limma, DESeq2, sva/ComBat) and cite the version and doc source in the script
header. Package APIs shift across versions, and a remembered signature is not evidence.

## Implementation

Two scripts, file-based interface, run from the repo root.

- `phase-2/scripts/phase2_ingest.py` resolves the design, downloads into `build/phase2/<accession>/`,
  writes `<accession>_samples.csv`, calls the R worker, and appends the manifest row. It decides
  nothing biological: membership, arms, reference arm and patient rule all come from the committed
  tables, and it exits with an explanation rather than guessing when one is missing.
- `phase-2/scripts/phase2_de.R` owns normalization and testing. It needs limma, DESeq2, edgeR, sva,
  data.table, Matrix and R.utils; pass `--rscript` to point the orchestrator at that environment.

```
python phase-2/scripts/phase2_ingest.py --accession GSE163071 --rscript <env>/bin/Rscript
python phase-2/scripts/phase2_ingest.py --all --skip-existing --rscript <env>/bin/Rscript
python phase-2/scripts/phase2_ingest.py --accession GSE41747 --combat batch   # within-dataset only
```

### Route status, 2026-10-21

| engine | datasets | state |
|---|---|---|
| `deseq2` | 5 bulk RNA-seq | **validated** on GSE163071: 29,542 genes, 1 contrast |
| `author_matrix_limma_trend` | GSE207400 | **validated**: 44,985 rows over 3 contrasts |
| `nanostring_housekeeping_limma` | GSE239561 | **validated**: 750 endogenous genes over 5 contrasts |
| `pseudobulk_limma_trend` | 4 single-cell | **validated** on GSE232516: 4 10x libraries, 36,591 rows |
| `pseudobulk_author_matrix` | GSE292071 | implemented, unrun: the deposit is one `.mtx.gz` with no features or barcodes file, so the gene and plate axes cannot be recovered from the series-level file yet |
| `limma_trend` | 6 expression arrays | implemented, unrun: the CEL route needs oligo or affy plus the platform annotation package, and `bioconductor-oligo` does not resolve from bioconda on this machine. The engine stops with that message rather than falling back to a processed file |
| `two_colour_limma` | E-TABM-69, E-MEXP-258 | reader only: both are legacy Tab2MAGE exports whose per-array column names must be read off the file before `limma::read.maimages` is pointed at them |

### Three things the first runs settled

1. **Matrix columns are matched on four keys.** Deposited matrices name their columns by GSM, by
   sample title, or by an internal id that appears only in `Sample_description` (GSE163071's columns
   are `Lb3303` and the like; GSE207400's are `M1014` for "Tumor Sample M1014"). The orchestrator
   fetches the series SOFT header and carries title, `soft_title` and `description`; the worker
   matches on all of them, exactly first, then by unique substring in either direction, and reports
   what it could not match rather than dropping samples.
2. **The gene identifier column is chosen by name.** GSE163071's counts lead with Chromosome, Start,
   Stop, Strand and then Gene Symbol; taking column 1 silently produced chromosome numbers as gene
   names in the first run.
3. **Pseudobulk is one profile per patient per arm.** GSE232516's patient P13 contributes both a
   pseudarthrosis and an iliac-crest sample, so collapsing to the patient would merge a case with a
   control. Profiles stay separate and the patient enters the model as a blocking factor, but only
   where at least 2 residual degrees of freedom survive it; at n=4 the block is dropped with a logged
   reason instead of saturating the design.
