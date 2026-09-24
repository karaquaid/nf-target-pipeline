# nf-target-pipeline

A pipeline that takes raw gene expression data from neurofibromatosis tumours and returns a prioritised, evidence-scored list of candidate drug targets.

The work is aimed at the rare-disease problem that makes target discovery hard in NF: the published expression datasets are small, scattered across tumour types, and frequently lack matched healthy controls, while the drug and tractability evidence needed to judge a candidate sits in a dozen separate databases. The pipeline stitches those together — differential expression and pathway enrichment on public datasets, then drug-interaction, selectivity, clinical-stage, safety and delivery-route evidence layered on top — and scores each candidate rather than presenting every hit as equally strong. It is built to be operated by a Claude agent end to end, so that a run can be repeated, audited, and pointed at a new dataset without rewriting it.

A parallel literature-derived target list is built independently of the expression data, and the two are compared at the end. Targets one approach finds and the other misses are as interesting as the overlap.

## Scope

Three diseases: **NF1**, **NF2-related schwannomatosis (NF2-SWN)**, and **schwannomatosis (SWN)**. Evidence that cannot be attributed to one of them — sporadic tumours carrying the same somatic lesion, for instance — is excluded rather than carried as unlabelled.

Every dataset and every target is labelled with its disease and with one or more manifestations from a fixed vocabulary (plexiform neurofibroma, MPNST, vestibular schwannoma, pain, optic pathway glioma, and so on). Those labels travel through every stage, so the final list can be filtered by clinical problem instead of read as one undifferentiated ranking. The vocabulary is defined in [`docs/project-plan.md`](docs/project-plan.md).

## Status

Early. The literature-derived target list (Phase 1b) is the first completed stage — see [`docs/phase1b-literature-targets.md`](docs/phase1b-literature-targets.md). Dataset selection, ingestion, and the expression-derived arm are in progress. The phase-by-phase plan in [`docs/project-plan.md`](docs/project-plan.md) is the source of truth for scope and ordering, and is updated in place as decisions change.

## Layout

```
docs/     project plan, per-phase write-ups, scoring methodology
scripts/  ingestion, analysis, and database-integration code
data/     small reference files only — candidate lists, coverage tables
```

Raw expression data stays out of the repository, for size and for data-use terms.

## Provenance

Literature claims record whether they were confirmed against full text or only an abstract, and database queries are written against current API documentation rather than recalled syntax. Where a value is missing it is flagged as missing, not estimated.

## License and funding

MIT licensed. Supported by Anthropic's AI for Science program.
