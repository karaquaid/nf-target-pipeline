# Phase 7 follow-up — how unstable is single-reader full-text verification?

*Measurement, not correction. No Phase 1b table was modified. Run 2026-11-17 with
`phase-7/scripts/phase7_verification_stability.py`; tables in
`phase-7/data/phase7-verification-stability.csv` and
`phase-7/data/phase7-verification-stability-summary.json`.*

## The short answer

- **The reader disagrees with itself on 12.3% of claims** (19/155; Wilson 95% CI 8.0–18.4%,
  paper-clustered bootstrap 5.0–20.8%) when the identical body and the identical prompt are
  read twice.
- **It disagrees with Phase 1b's recorded verdict on 20.7% of claims** (17/82; Wilson
  13.4–30.7%, clustered 11.7–31.7%); a second fresh run gives 23.2%. That figure is not a
  pure reader-noise estimate — see the caveat below.
- **Almost all of this is the supported ↔ partially_supported boundary, not support ↔ no
  support.** Collapsed to the distinction the candidate derivation actually uses (any support
  vs `full text - not supported`), self-disagreement falls to 3.9% (6/155, clustered
  0–8.6%) and disagreement with Phase 1b to 8.5% (7/82, clustered 1.3–18.1%).
- **A large slice of the apparent instability is retrieval damage, not judgement.** 53 of the
  59 sampled papers carry the dropped-italics signature; in 23 of 155 claims the gene label
  does not appear anywhere in the retrieved body. The markup guard voided 3 of 9 fresh
  `not_supported` verdicts in run 1 and 5 of 13 in run 2 — a third to two fifths of all
  negative verdicts were rendered against a body with the label deleted. Self-disagreement is
  10.6% where the label is present and 21.7% where it is absent.

## Population and sample

The claim unit is `(gene_target, disease, manifestation, pmid)` where Phase 1b read that paper
in full. Reconstructed from `phase1b-literature-targets.csv` (`paper_access`,
`n_papers_fulltext_read`, `verdicts_from_whole_body`) and `phase1b-references.csv`:
**469 claim pairs across 155 papers.**

Phase 1b records verdict *counts* per row, not a verdict per claim. A claim's recorded verdict
is recoverable only where a row's full-text verdicts are unanimous, their count equals
`n_papers_fulltext_read`, and all came from the whole-body pass: **235 of 469 pairs**. The
other 234 cannot be attributed to a claim at all, which is itself a finding — Phase 1b's table
cannot be audited at claim level for half its full-text evidence.

Sampling is a one-stage cluster sample with seed **20261117**: papers shuffled, walked in
order, and every full-text claim of a sampled paper verified in one prompt — Phase 1b's own
prompt unit. 74 papers were attempted; **59 yielded a body** (15 did not: 9 returned empty or
stub text, 3 had no PMC id, 3 returned no article). That gives **155 verified claims, 33% of
the 469-claim population**, over **59 of 155 papers (38%)**, and **82 claims** in the
reproduction subsample. Intervals are reported both as Wilson intervals and as a bootstrap
resampling whole papers, because claims from one paper share a body and a prompt.

The 45 claims on the 15 unretrieved papers are in the CSV with `body_retrieved=False` and no
verdicts. They are not counted in any rate.

## Method

Retrieval: PubMed MCP connector `get_full_text_article`, as Phase 7 used. Verification: the
litmonitor `verdict_prompt` and `VERDICT_SYSTEM` verbatim — whole body, references stripped,
no excerpting — model `claude-sonnet-5`, thinking disabled, two independent batched passes over
identical prompts. Phase 1b nominally requested `temperature=0`; temperature is not settable on
this model, and the Phase 7 RNF213 episode shows determinism was not achieved in practice
either, so run-to-run variation is what the pipeline actually has.

## A. Self-consistency — same reader, same input, twice

| quantity | value |
|---|---|
| claims | 155 |
| three-way disagreement | 19 (12.3%), Wilson 8.0–18.4%, clustered 5.0–20.8% |
| after voiding guard-caught verdicts | 17/150 (11.3%) |
| binary, support vs not supported | 6 (3.9%), clustered 0–8.6% |

Direction of the 19 disagreements: supported↔partially_supported 13, partially_supported↔
not_supported 5, supported↔not_supported 1. The reader is stable about whether a paper supports
a target at all and unstable about whether that support is direct or indirect.

## B. Reproduction of Phase 1b's recorded verdict

| quantity | value |
|---|---|
| claims with a determinable Phase 1b whole-body verdict | 82 |
| run 1 disagrees | 17 (20.7%), Wilson 13.4–30.7%, clustered 11.7–31.7% |
| run 2 disagrees | 19 (23.2%), Wilson 15.4–33.4% |
| neither run reproduces | 14 (17.1%) |
| binary, support vs not supported | 7 (8.5%), clustered 1.3–18.1% |

Where it moves: 6 `supported` → `partially_supported`, 5 `partially_supported` →
`not_supported`, 4 `partially_supported` → `supported`, 1 `not_supported` → `supported`,
1 `not_supported` → `partially_supported`. The fresh reader is, on balance, stricter than the
Phase 1b record.

**This number is not a pure measure of reader noise.** It conflates reader instability with
(i) the retrieval change — Phase 1b read Europe PMC/NCBI JATS with markup intact, this run read
the connector's extracted text with italicised symbols deleted — and (ii) any protocol drift
between then and now. It is an upper bound on how reproducible the recorded verdicts are under
today's pipeline, not an estimate of how often the Phase 1b reader was wrong.

## How much is retrieval artefact

The connector's PMC extraction deletes italic markup, and journals italicise gene symbols. In
PMID 41898501 the body opens "…-related schwannomatosis (-SWN) is caused by pathogenic
mutations in thegene…" — the symbol is gone, not merely unformatted.

- 53 of 59 sampled papers show the signature (Phase 7 saw 17 of 22).
- The claim's own label is absent from the retrieved body in 23 of 155 claims (39 on a strict
  exact-token test; 23 after also accepting the digit-stripped base, e.g. YAP1→YAP).
- The markup guard voided 3 of 9 `not_supported` verdicts in run 1 and 5 of 13 in run 2.
- Self-disagreement is 10.6% (14/132) where the label is present and 21.7% (5/23) where it is
  absent.

So the negative verdicts — the ones that would demote a row — are the ones most contaminated by
retrieval damage. **The guard protects one direction only.** In the RNF213 adjudication below,
the reader returned a *positive* verdict against a body from which the label had been deleted,
reasoning from surrounding context; no symbol-presence guard catches that.

## The two contradictions, re-adjudicated

**PMID 36148553 — YAP1/WWTR1 (YAP/TAZ) | NF2-SWN | Meningioma. Verdict: supported. Phase 1b's
record stands; Phase 7's `not_supported` does not reproduce.** Three fresh whole-body reads of
the connector body and three of the clean Europe PMC JATS all return `supported`, for the
meningioma claim and for the companion vestibular schwannoma claim. The label is abundant in
both bodies (YAP 80, TAZ 103 occurrences in the connector body), so retrieval is not the
explanation — the body states that NF2 loss reduces LATS1/2-mediated YAP/TAZ phosphorylation and
that TAZ knockdown reduces NF2-null meningioma cell proliferation. This one is reader noise.

**PMID 39367156 — RNF213 | NF1 | Other. Verdict: supported. Phase 1b's record stands; Phase 7's
`not_supported` is a retrieval artefact and is inadmissible.** The connector's extracted body
contains the string `RNF213` **zero** times; the Europe PMC JATS body Phase 1b read contains it
**34** times. Any verdict rendered against that body is void under the guard. Three fresh reads
of the clean body return `supported` (the paper reports the RNF213 p.R4810K modifier variant in
an NF1 patient with moyamoya syndrome). Against the degraded body the reader returned
`partially_supported` three times — inferring from context about a symbol it could not see,
which is exactly the failure mode the guard cannot detect.

Both papers were read in full text; access for every claim in this study is recorded per row in
the CSV.

## What this implies for Phase 1b's evidence tiers

1. **The tier wall between "read in full" and "abstract only" holds.** Nothing here touches it,
   and it remains the most load-bearing distinction in the map.
2. **The three-way verdict is not a stable quantity at claim level.** One claim in eight flips
   between `supported` and `partially_supported` on a re-read with the input held fixed, and one
   in five differs from what Phase 1b wrote down. A single-reader verdict should not be reported
   as if it were a measurement with no error bar.
3. **The derived candidate list is much more robust than the verdict column.** The decision the
   list actually makes — drop a row whose only full-text verdict is `not supported` — flips on
   3.9% of claims on re-read and 8.5% against the Phase 1b record. Row-level tiers are also
   buffered by aggregation: a row takes the best verdict across its papers, so a single
   supported↔partial flip usually changes nothing. (Row-level tier propagation was not computed
   here; this is an argument about the aggregation rule, not a measured row-level rate.)
4. **`not supported` is the verdict to distrust, and it should not be acted on from connector
   text alone.** A third to two fifths of fresh negatives in this sample were rendered against a
   body with the label deleted. Any demotion, exclusion, or contradiction claim should be
   re-checked against the Europe PMC JATS body before it is believed — which is what resolved
   RNF213 here.
5. **Half of Phase 1b's full-text evidence cannot be audited at claim level** (234 of 469 pairs).
   Recording a verdict per claim, not per row, costs nothing at build time and is the single
   cheapest fix to this table's auditability.

## Limits

- 155 of 469 claims (33%), 59 of 155 papers (38%). Intervals are reported honestly and are wide;
  the clustered interval for the self-consistency rate is 5.0–20.8%.
- The measurement population is restricted to claims whose body is retrievable through the
  PubMed connector today. Phase 1b also read 20 papers from user-supplied PDFs and 27 through
  NCBI author-manuscript efetch; those routes are not available here, so papers reachable only
  that way are under-represented. Two runs per claim bound self-consistency pairwise only — with
  three or more runs the disagreement rate would be higher by construction.
- Measurement B's subsample is restricted to rows whose full-text verdicts were unanimous, which
  excludes the mixed-verdict rows where Phase 1b already disagreed with itself across papers.
  Those are plausibly the harder claims, so 20.7% may understate disagreement over the whole
  table.
- Verdicts here come from one reader with no adjudication, exactly like Phase 1b and Phase 7.
  This study measures reproducibility, not correctness. Absence of a symbol from a retrieved
  body is evidence about retrieval, never evidence against the claim.
