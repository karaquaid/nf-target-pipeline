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
     normalization first, then `limma` on the log2 normalized counts. Not the plain array route, and
     `gene_space` in the manifest records that the result covers 770 genes rather than the
     transcriptome, so Phase 3 cannot read an absent gene as a low rank
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
