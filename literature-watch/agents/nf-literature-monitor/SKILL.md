---
name: nf-literature-monthly
description: "Monthly refresh of the neurofibromatosis literature target map: re-run the fixed PubMed query bank, keep only new records, extract and verify target claims against full text, merge into the running tables without disturbing verified rows, and regenerate the write-up and figure. Writes only under literature-watch/, leaving the published phase-1b/ snapshot frozen. Use for any incremental update to the NF target evidence tables, and as a worked protocol for building a verification-graded target map in another rare disease."
---

# Monthly NF literature update

This is the Phase 1b protocol of `nf-target-pipeline`, packaged for repeat runs. A first run
for a different disease is a different job: see "Reusing this outside NF" at the end.

Helpers load automatically with this skill (`kernel.py`): `nf_manifestations()`,
`epmc_record()`, `fetch_fulltext()`, `strip_references()`, `is_preprint()`,
`extraction_prompt()`, `verdict_prompt()`.

## Where things live, and what you may write

`phase-1b/` is **frozen**. It is the snapshot the manuscript cites, and it must stay
byte-identical so a reader can reproduce the published numbers. You read it and you never
write to it. The same goes for `phase-1a/` and `phase-2/`.

Everything you produce goes under `literature-watch/`:

| Path | What it holds |
|---|---|
| `literature-watch/data/` | The running tables: the frozen snapshot plus every update merged in. Same schema as `phase-1b/data/`. |
| `literature-watch/docs/` | The regenerated write-up and figure, describing the running tables. |
| `literature-watch/updates/<YYYY-MM>/` | One directory per run: the new rows, the new papers, and the run report. |
| `literature-watch/CHANGELOG.md` | One entry per run, newest first. |

On the very first run, `literature-watch/data/` does not exist. Create it by copying
`phase-1b/data/` verbatim, then add two provenance columns to the row and reference tables
before merging anything:

- `first_seen`: `"phase-1b snapshot"` for every baseline row, and `"YYYY-MM"` for rows added
  by a later run.
- `in_phase1b_snapshot`: true for baseline rows, false for added ones.

Those two columns are what let a reader separate the published list from everything that
arrived after it, which is the whole reason this folder is separate.

## The rules that make the output trustworthy

Violating any of these silently corrupts the evidence grading, which is the point of the
resource.

1. **The manifestation vocabulary is fixed and applied verbatim.** Twenty terms, from
   `nf_manifestations()`. Never invent one. A phenotype outside the list goes to `Other`,
   and you report how many landed there.
2. **Never downgrade or overwrite a verified row.** A row already tiered `full text -
   supported` keeps its tier unless a newly read paper contradicts it. New evidence adds
   papers and can promote a row; it does not silently re-judge settled ones. Without this a
   repeating run churns the tiers and the map stops being comparable with itself.
3. **Open access and readability are different things.** A paper can be closed at the
   publisher while a free author manuscript sits in PMC. `fetch_fulltext()` tries both
   routes; never call a paper unreachable on the strength of an open-access flag.
4. **Absence is not the same as unverified.** A claim nobody has read is tiered
   `abstract only`, not scored as weak evidence.
5. **Scope filters are flags plus derived tables, never deletions.** Germline driver genes
   and contradicted rows stay in the audit table with their flags; the candidate list is
   derived from it.
6. **Numbers in prose come from the saved tables.** Regenerate with the committed scripts;
   never hand-edit a count.

## Workflow

### 1. Establish the cutoff and the current state

Read `literature-watch/CHANGELOG.md` for the last run date, or fall back to the latest
`year` in the reference table on a first run. Search from one month before that date, not
from the last publication date: PubMed indexing lags.

Record before-counts from the saved tables (rows, labels, papers, tier split). Every number
you report at the end is a difference against these.

### 2. Re-run the query bank

`phase-1b/data/phase1b-queries.csv` holds the 32 queries verbatim, each tagged with the
disease and manifestation it targets. Run them unchanged, through the PubMed connector
(`search_articles`, relevance-sorted), adding a date floor. Changing a query changes what the
corpus means. If one must change, add the new query to
`literature-watch/data/queries-added.csv` rather than editing the frozen bank, say so in the
pull request, and treat the affected manifestation's counts as not comparable with earlier
runs.

Drop PMIDs already in the running reference table. What remains is the month's intake.

### 3. Extract claims from abstracts

Fetch metadata and abstracts (`get_article_metadata`). For each, call `host.llm` with
`extraction_prompt(title, abstract)` and the system line below, as a parallel fan-out with
`model=host.reasoning_model()`.

> You extract drug-target claims from biomedical abstracts for a neurofibromatosis
> target-discovery pipeline. You output JSON only. You never infer facts that are not stated
> or directly implied by the text provided. If the abstract does not name a specific
> molecular target, you return an empty list.

Expect some calls to fail or truncate. Retry with a larger token budget, then salvage
individual objects from partial JSON, then fall back to one call per claim. A paper that
legitimately names no target contributes nothing and is not a failure.

### 4. Normalise gene symbols

Validate every symbol against MyGene with `scopes="symbol"` (official symbols only).
**Do not use alias matching**: it maps common shorthand onto unrelated genes. Curate the
residue by hand, reading the row's own mechanism text to disambiguate. Keep genuine families,
complexes and pathways as the label, set `label_type`, and list members in
`constituent_genes`.

### 5. Verify against full text

For each new paper, `epmc_record(pmid)` then `fetch_fulltext(pmcid)`. For papers with a body,
judge every claim from that paper in one call with `verdict_prompt(claims, body)` and
`model=host.reasoning_model()`, with this system line:

> You verify drug-target claims against the complete body of a research article. You output
> JSON only. You never credit a claim the article does not itself demonstrate or explicitly
> assert.

One call per paper, not per claim: the model needs the whole body in front of it. Apply
`manifestation_in_fulltext` corrections **per paper**, not per row, so a paper that studies a
different manifestation moves only its own support.

Papers no route reaches go to the running `phase1b-upload-priority.csv` with `pdf_status =
"still needed"`, ranked by how many abstract-only rows each would anchor, with
`europepmc_url` and `pmc_url` before the publisher DOI. Never hand that list to a human with
only DOI links: it sends them to paywalls for papers that are free.

### 6. Merge into the running tables

Merge at the level of the (gene_target, disease, manifestation, pmid) assignment, not the
row. A new paper supporting an existing row adds a PMID and can raise the tier; it never
lowers one. Stamp `first_seen = "YYYY-MM"` and `in_phase1b_snapshot = false` on genuinely new
rows, and leave both columns untouched on baseline rows you merely added a paper to. Set
`is_preprint` and `preprint_server` with `is_preprint(doi, journal)`, and propagate
`n_preprint_papers` and `preprint_only` to rows.

New target labels need the three curated annotations (`likely_biomarker`,
`mutation_restricted`, `tme_target`) in the running annotation table, which is keyed by label
and joined by the candidate script. The join asserts every label has exactly one annotation,
so the pipeline fails loudly if you forget.

Write the month's deltas to `literature-watch/updates/<YYYY-MM>/`: the new rows, the new
papers, and any row whose tier changed, with the before and after value.

### 7. Regenerate and report

From the repository root, pointing the committed scripts at the running folder:

    python phase-1b/scripts/make_phase1b_candidates.py --data literature-watch/data
    python phase-1b/scripts/build_phase1b_report.py --data literature-watch/data \
        --out literature-watch/docs/nf-literature-current.md
    python phase-1b/scripts/make_phase1b_figure.py \
        --targets literature-watch/data/phase1b-candidate-targets.csv \
        --out literature-watch/docs/figures/coverage-verification.png

The scripts are read from `phase-1b/scripts/` and not modified. If one needs a change, that
is a pull request against the scripts in their own right, and you say so rather than copying
a patched version into the watch folder.

Then read the numbers back **off the saved tables**, not off kernel variables, prepend an
entry to `literature-watch/CHANGELOG.md`, and open a pull request against current `main`
(check the previous pull request has merged before extending its branch). The body states:
papers screened and added, new rows and new labels, tier movements in both directions, any row
whose tier changed and why, manifestations whose coverage changed, the length of the unread
queue, and an explicit line confirming nothing under `phase-1b/` was touched.

## What a good monthly report says

Deltas, not totals, and the ones that change a decision first: a manifestation that crossed
from no full-text-supported target to having one; a new target label in a thin manifestation;
a row that lost its support. A month with no new papers is a valid result and is reported as
one, with a CHANGELOG entry recording that the run happened and found nothing.

## Reusing this outside NF

Three components transfer unchanged: the retrieval ladder (`fetch_fulltext`), the per-paper
verdict rubric (`verdict_prompt`), and the flag-plus-derived-table pattern for scope filters.
The query bank and the manifestation vocabulary must be rebuilt for the new disease, ideally
from an existing clinical standard rather than drafted fresh. The target annotation flags are
the least transferable, since the biomarker-versus-target judgement depends on the
pharmacology of the specific gene set.

The protocol pays off where the literature is small enough to read exhaustively,
heterogeneous enough that claims arrive at different evidence levels, and uneven enough
across subphenotypes that counting papers gives the wrong ranking.
