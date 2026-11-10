# nf-target-pipeline

A pipeline that takes raw gene expression data from neurofibromatosis tumours and returns a prioritised, evidence-scored list of candidate drug targets.

The published expression datasets are small, scattered across tumour types, and frequently lack matched healthy controls, while the drug and tractability evidence needed to judge a candidate sits in a dozen separate databases. The pipeline stitches those together: it runs differential expression on public datasets, aggregates ranked lists across datasets by disease and manifestation, queries drug-interaction and tractability databases for each candidate, and cross-checks mechanistic support via the Monarch knowledge graph and DisMech. Phase 6 will combine those signals into a scored ranking. It is built to be operated by a Claude agent end to end, so a run can be repeated, audited, and pointed at a new dataset without rewriting it.

A parallel literature-derived target list is built independently of the expression data and compared against the expression-derived list at the end. Targets one approach finds and the other misses are as interesting as the overlap.

## Scope

Three diseases: **NF1**, **NF2-related schwannomatosis (NF2-SWN)**, and **schwannomatosis (SWN)**. Evidence that cannot be attributed to one of them (sporadic tumours carrying the same somatic lesion, for instance) is excluded rather than carried as unlabelled.

Every dataset and every target is labelled with its disease and with one or more manifestations from a fixed vocabulary (plexiform neurofibroma, MPNST, vestibular schwannoma, pain, optic pathway glioma, and so on). Those labels travel through every stage so the final list can be filtered by clinical problem instead of read as one undifferentiated ranking. The vocabulary is defined in [`docs/project-plan.md`](docs/project-plan.md).

## Status

**Phases 1 through 5 are complete.** Phase 6 (evidence-strength scoring) is next.

| Phase | What it produced | Key deliverable |
|---|---|---|
| **1a** – dataset scope | 160 NF expression datasets labelled across GEO and ArrayExpress, 3,662 in-scope samples | [`phase-1a/docs/phase1a-dataset-scope.md`](phase-1a/docs/phase1a-dataset-scope.md) |
| **1b** – literature targets | 182 gene targets drawn from 234 papers (155 read in full text), labelled by disease and manifestation | [`phase-1b/docs/phase1b-literature-targets.md`](phase-1b/docs/phase1b-literature-targets.md) |
| **2** – data ingestion and DE | 15 of 21 launch-set datasets produced ranked DE lists; ingestion manifest records provenance per dataset | [`phase-2/docs/phase2-pipeline-spec.md`](phase-2/docs/phase2-pipeline-spec.md) |
| **3** – rank aggregation | Robust rank aggregation across 23 contrasts produced 1,927 expression-derived candidate targets across 8 strata | [`phase-3/docs/phase3-expression-targets.md`](phase-3/docs/phase3-expression-targets.md) |
| **3b** – prioritisation | 9 disease × manifestation combinations selected for Phase 4; no candidate-bearing stratum deferred | [`phase-3b/docs/phase3b-prioritisation.md`](phase-3b/docs/phase3b-prioritisation.md) |
| **4** – drug layer | 1,930 candidate genes queried across DGIdb, Open Targets, ChEMBL, ClinicalTrials, openFDA, Guide to Pharmacology; 848 have a drug interaction, 189 an approved drug, 932 undrugged but tractable | [`phase-4/docs/phase4-drug-tractability.md`](phase-4/docs/phase4-drug-tractability.md) |
| **5** – mechanistic validation | Monarch KG and DisMech queried for 1,902 candidate genes; 630 carry a causal gene-disease edge | [`phase-5-mechanistic-validation/docs/phase5-mechanistic-validation.md`](phase-5-mechanistic-validation/docs/phase5-mechanistic-validation.md) |

A literature-watch agent runs monthly to flag new NF papers against the Phase 1b target list. Its configuration and skill live under [`literature-watch/agents/nf-literature-monitor/`](literature-watch/agents/nf-literature-monitor/).

The phase-by-phase plan in [`docs/project-plan.md`](docs/project-plan.md) is the source of truth for scope and ordering and is updated in place as decisions change.

## Layout

```
docs/                             project plan and other cross-phase documents
phase-1a/                         public expression-dataset scope (GEO/ArrayExpress sweep)
phase-1b/                         literature-derived candidate targets
phase-2/                          data ingestion, preprocessing and differential expression
phase-3/                          robust rank aggregation and expression-derived candidates
phase-3b/                         evidence coverage review and manifestation prioritisation
phase-4/                          drug interaction, selectivity and tractability layer
phase-5-mechanistic-validation/   cross-disease mechanistic validation (Monarch KG + DisMech)
literature-watch/                 monthly literature monitor agent
  data/        small reference files only: candidate lists, coverage tables, manifests
  docs/        that phase's write-up and figures
  scripts/     the code that produced them
```

One folder per phase, added as each phase lands. Anything cross-phase — the project plan above all — stays at the root. Raw expression data stays out of the repository, for size and data-use terms.

## Provenance

Literature claims record whether they were confirmed against full text or only an abstract. Database queries are written against current API documentation rather than recalled syntax. Where a value is missing it is flagged as missing, not estimated. Every phase deliverable is regenerated by committed code from committed inputs; the data files in each `data/` subdirectory are the canonical outputs, not intermediate artefacts.

## Program and license

This project is part of Anthropic's AI for Science Rare Disease Research Program, in which the Children's Tumor Foundation participates.

MIT licensed.
