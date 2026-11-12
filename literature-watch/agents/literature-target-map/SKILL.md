---
name: literature-target-map
description: "Build a verification-graded map of candidate drug targets for a disease from the literature: design a query bank and manifestation vocabulary, sweep PubMed, extract target claims from abstracts, verify each claim against complete article bodies, aggregate across papers into one row per target and manifestation, grade every row by how deeply it was checked, and derive a candidate list under explicit scope rules. Use for a first build in a new disease, and as the protocol behind the litmonitor build scripts. Companion to nf-literature-monthly, which refreshes a map that already exists."
---

# Building a literature target map

The first build of a target map, which the NF project calls Phase 1b. One run produces a
candidate list, the audit table behind it, a reference table, a coverage matrix, a retrieval
queue and a write-up.

Two ways to run it, same protocol:

- **Scripted**, needing no Claude Science: `litmonitor/build.py`, then `review.py`,
  `report.py`, `figure.py`, all driven by one TOML config. This is what someone outside this
  workspace uses.
- **Conversationally**, as this agent, when the config needs designing, the vocabulary needs
  arguing over, or the scope calls need a person in the loop.

Prefer the scripts for the mechanical work even when running conversationally. Rerunning a
script is cheap and reproducible; redoing a sweep by hand is neither.

## The six rules

These are the ways a target map quietly stops being trustworthy. They outrank everything below.

1. **A claim nobody checked never sits at the same tier as one read in full.** The tier column
   is the product. `abstract only` means nobody looked, which is not the same as weak evidence.
2. **Verify against the whole article, never an excerpt.** A result the article cites from
   another paper is not that article's support. When this project compared excerpt-based
   verdicts with whole-body verdicts, they disagreed often enough to be worth the cost.
3. **Never report a number you have not read back off a saved table.** Numbers quoted from the
   variables that produced them drift from the file by one bug.
4. **Scope filters are flags plus a derived table, never deletions.** Every exclusion has to be
   reversible and countable later.
5. **Vocabulary and query bank are fixed before the run, then left alone.** Change one and the
   corpus means something different, so counts stop being comparable. Add, do not edit.
6. **Scope questions go to a person.** Whether a new label is a disease driver, whether a
   borderline paper is in scope, whether a vocabulary term should exist: ask, do not decide.

## Designing the config

Most of the quality of a map is decided here, before any paper is read.

**Manifestation vocabulary.** Take it from a standard the field already uses: diagnostic
criteria, a registry phenotype list, a consensus guideline. A vocabulary invented for one
analysis cannot be compared with anyone else's and will not survive contact with a collaborator.
Always include a catch-all `Other`, and watch its share. If a large fraction of rows land there,
the vocabulary does not fit the literature and should be revisited rather than forced.

**Query bank.** One query per disease and manifestation you want counted separately, plus a
broad one per disease. Keep them in the config, verbatim, from the first run onward.
Unversioned queries are the most common reason a sweep cannot be reproduced, including in this
project, where the original bank survived only in a chat transcript and had to be recovered.

**Scope exclusions.** `exclude_labels` is for entities so well studied that listing them as
candidates adds nothing, typically the germline disease genes. They stay in the audit table with
a flag. Keep recurrent somatic drivers unless told otherwise: they usually carry the progression
signal a later stratification step depends on.

## Running a build

    python litmonitor/selftest.py                                  # no network, no API key
    python litmonitor/build.py --config study.toml --dry-run       # per-query yield only
    python litmonitor/build.py --config study.toml --limit 20      # smoke test
    python litmonitor/build.py --config study.toml --annotate      # the real run
    python litmonitor/review.py --config study.toml --stamp YYYY-MM
    python litmonitor/report.py --config study.toml
    python litmonitor/figure.py --config study.toml

Always dry-run first and report the per-query yield before spending anything. A query returning
thousands of records is usually too broad; one returning nothing is usually malformed. Run the
self-test after any change to the scripts.

## What the pipeline does, and what to check

**Extraction** reads each abstract and returns targets with a disease, manifestations, a role
and a mechanism sentence. It is told not to extract the disease gene where it merely defines the
cohort, cell-type markers, assay reagents, or genes named only as background citation. Read a
handful of extracted rows against their abstracts before trusting a run.

**Retrieval** tries Europe PMC full text, then NCBI efetch against PubMed Central. Open access
status does not predict which works: a paper closed at the publisher often has a free author
manuscript that only the second route serves. In this project the two routes together reached 89
of 236 papers where one route alone reached 56.

**Verification** judges every claim from a paper against that paper's complete body and returns
supported, partially supported or not supported, with the mechanism as the body states it.
Partial usually means the article supports the target for a different manifestation, which is
information rather than failure.

**Aggregation** collapses claims into one row per target, disease and manifestation, carrying
every supporting paper, the count of each verdict, and the best verdict as the row's tier.

**Gene symbols.** Resolve to official HGNC symbols and do not accept alias matching unchecked:
in this project an alias-tolerant lookup mapped SPP1 to CXXC1, ATR to MMAB, MIF to AMH and AR to
AKR1B1, because each is a legitimate alias of an unrelated gene. Keep family and complex labels
as the label, with constituent genes in their own column.

## Reporting a build

Lead with what the map cannot support. The useful finding of a first build is usually where the
literature is thin, not which target ranks first: manifestations with few rows, rows resting on
one paper, rows nobody has verified. State the share of rows in `Other`, since that measures
whether the vocabulary fits. Name the papers nobody could retrieve and what they would anchor;
`retrieval-queue.csv` ranks them.

Say plainly that verdicts come from a single reader, and that the review gate measures whether
they are reproducible rather than whether they are right.

## Reusing this in another disease

The protocol transfers unchanged. What does not transfer: the manifestation vocabulary, which
must come from the new field's own standard, and the scope exclusions, which depend on which
genes that field already considers settled. The annotation flags are least transferable, since
the biomarker-versus-target judgement rests on the pharmacology of the specific gene set.

The approach pays off where the literature is small enough to read exhaustively, heterogeneous
enough that claims arrive at different evidence levels, and uneven enough across subphenotypes
that counting papers alone gives the wrong ranking.
