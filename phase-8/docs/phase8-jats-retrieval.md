# The Europe PMC JATS retrieval path

Implements the ruling of 2026-11-17: **full-text verification reads Europe PMC JATS, not
connector-extracted PMC text; the PubMed connector keeps search and metadata.** This was the one
piece of implied work the plan recorded as not done, and a prerequisite for Phase 8.

## What was actually missing

Less than the plan implied, and in a different place.

- `litmonitor/monitor.py` has fetched Europe PMC `fullTextXML` since Phase 1b and feeds **raw
  JATS XML** to the reader, so markup was never lost there.
- `phase-7/scripts/phase7_verification_stability.py` already carried a `fetch_epmc()` and a
  `--retrieval {connector,epmc}` switch — which is how the damage was measured in the first place.

The damage was confined to `phase7_fallback_literature.py`, which used the connector's extracted
text. What did not exist anywhere was a **shared client** with a stated guarantee, which is what
this adds.

## What is new: a provable symbol-preservation guarantee

`lib/europepmc_client.py` renders JATS to plain text and then **checks its own output**.
`missing_inline_strings()` re-reads the rendered text and returns every inline-markup string —
`italic`, `bold`, `sup`, `sub`, `sc`, `monospace`, `underline` — that failed to survive. A caller
asserts it is empty.

This is the property the symbol-presence guard could not provide. That guard voided a
`not_supported` verdict when the label was missing from the body, which catches false negatives
only; it could never catch the positive-verdict-on-a-deleted-symbol case that PMID 39367156 /
RNF213 demonstrated. Checking the renderer instead makes the deletion impossible rather than
detectable after the fact.

The guard earned its keep during development: an early draft dropped `<table-wrap>`, which
silently lost an italicised gene symbol (BMPR1B) that appeared only in a table. Tables are now
retained; only citation noise (`xref`) and back matter are removed.

`python lib/europepmc_client.py --selftest` fetches the RNF213 paper and asserts both that the
symbol is present and that nothing inline was dropped.

## Measured against the connector, on Phase 7's own sample

155 claims over 59 papers — the same sample Phase 7 used. The question asked per claim is only
*does the claim's own gene symbol appear in the retrieved body?*; no verdict was re-run, because
re-reading would conflate the retrieval change with the reader noise Phase 7 measured separately.

| | connector | Europe PMC JATS |
|---|---|---|
| papers retrieved | 59 | **59** |
| claims whose label is absent (strict) | 39 | **33** |
| claims whose label is absent (lax) | 23 | **17** |
| inline strings dropped by the renderer | — | **0** |

**6 claims recovered, 0 lost.** CDKN2A, DCN, FGFR, NFKB, POSTN and TGFB1, across three papers.

## Two findings that change how this should be described

**1. "Europe PMC JATS" is a two-route path, and the second route does most of the work.**
Europe PMC served 23 of 59 papers; **NCBI efetch served 36**. All six recovered claims came via
efetch. Open-access status does not predict which route works — a paper closed at the publisher
often has a free author manuscript that only efetch serves. Any later description of this as "the
Europe PMC path" should say *Europe PMC first, NCBI efetch second*; dropping the fallback would
lose more than the connector ever cost.

**2. The residual 33 are not a retrieval problem.** Every one of them was also absent from the
connector body, so nothing regressed, and they are dominated by label-vocabulary mismatch rather
than missing text: `MAP2K1/2 (MEK1/2)` alone accounts for 10, in papers that write "MEK1/2" while
the token list carries MAP2K1 and MAP2K2. Lax matching — accepting the digit-stripped base — takes
the residual from 33 to 17. Closing the rest needs a synonym layer of the kind
`phase6_drug_synonyms.py` already applies to drugs, not a better retrieval route.

## What this does not do

- **No existing verdict was re-run.** Phase 1b and Phase 7 tiers stand as produced. Re-running
  them is a separate decision with a real cost, and the stability measurement says the binary
  supported-or-not call is stable at 3.9% regardless.
- **`phase7_fallback_literature.py` is not yet switched over.** It still uses the connector. The
  client is in place for it and for Phase 8; the switch is a follow-up.
- **`litmonitor/monitor.py` is not refactored** to import the shared client, though it carries
  equivalent two-route logic. It backs a scheduled agent, and changing its imports to remove a
  duplication is not worth breaking a working monitor without a reason to touch it.

## Files

| file | what |
|---|---|
| `lib/europepmc_client.py` | the client: resolve, fetch, render, self-check. CLI with `--selftest` |
| `phase-8/scripts/jats_revalidation.py` | the measurement above, regenerable |
| `phase-8/data/phase8-jats-revalidation.csv` | 155 rows, per claim, both routes |
| `phase-8/data/phase8-jats-revalidation-summary.json` | the counts |
