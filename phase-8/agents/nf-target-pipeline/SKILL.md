---
name: nf-target-pipeline
description: "Operate Phases 3 to 7 of nf-target-pipeline: expression-derived candidate ranking, evidence coverage review, the drug and tractability layer, cross-disease mechanistic validation, evidence scoring, and literature validation. Drives the committed scripts through a declared step manifest that records each step's inputs, outputs, external services and binding rulings, refuses a step whose preconditions are not met, and never substitutes a placeholder for a step that did not run. Use for any re-run, extension or audit of the NF target pipeline downstream of Phase 2."
---

# Operating the NF target pipeline, Phases 3 to 7

This skill does not replace the phase scripts. Every step it knows about is a committed script
that was already run and reviewed. What this adds is the order, the preconditions, and a refusal
when a precondition is not met.

Work from the repo root. The driver is `phase-8/scripts/pipeline.py` and its manifest is
`phase-8/data/phase8-pipeline-steps.csv`.

```
python phase-8/scripts/pipeline.py list        # 48 steps, filterable by phase, class or ruling
python phase-8/scripts/pipeline.py check       # preconditions per step
python phase-8/scripts/pipeline.py rulings     # what each binding ruling constrains
python phase-8/scripts/pipeline.py run <id>    # execute one step
```

Read the manifest before you plan a run. It is the authority on what a step reads, writes and
calls, and it is maintained by hand: a change to a script that moves a path is a change to the
manifest too.

## The one rule that is not negotiable

If a step fails, or an API returns nothing, you report it. You do not fill the gap with a
placeholder, a cached value from a different run, an estimate, or a neighbouring source that
happens to be reachable. This is the Phase 8 prompt's own instruction, carried in the manifest as
ruling R4.

The driver enforces the part it can: a step that exits 0 without producing its declared outputs
is reported as a failure, because an exit code is not evidence that anything was written. The
rest is yours. When a step cannot run, say which precondition is missing and stop.

## What the step classes mean

| class | meaning | how to run it |
|---|---|---|
| `reproducible` | every input is committed, no network, no model reader | `pipeline.py run <id>` |
| `network` | needs an external service, sometimes a credential | `pipeline.py run <id>`, with the credential declared on the cell |
| `model_reader` | needs `host.llm`, and sometimes an MCP connector | the Claude Science python kernel, not the driver. `run` refuses and prints the import line |
| `blocked` | an input is not in the repo and cannot be regenerated from it | it does not run here. Say so |

Four steps are `model_reader` and the driver will not pretend otherwise: the two Phase 6
adjudication passes, the Phase 7 literature fallback, and the Phase 7 stability measurement.
They are invoked as `import <module> as m; m.main(host)` from the kernel.

## What cannot be re-run from this repository

Five Phase 3 steps are blocked. Phase 2 wrote one ranked list per dataset under
`build/phase2/<acc>/<acc>_de.csv`, and those files are not committed: only the ingestion manifest
row is. So the chain from contrast labelling through rank matrices, Robust Rank Aggregation and
the candidate rule cannot be rebuilt here, and neither can the KEGG enrichment that needs the
per-stratum background. Their outputs are committed, so everything downstream runs.

One further step cannot be regenerated: the Phase 5 write-up reads `build/phase5/phase5-inputs.json`,
which no committed script writes.

Do not work around either gap by substituting a different input. Report it.

## The four binding rulings

`pipeline.py rulings` prints these against the steps they constrain, with a compliance verdict
per step. Two steps currently disagree with a ruling, which is recorded rather than silently fixed.

**R1. Full-text verification reads Europe PMC JATS, never connector-extracted PMC text.** The
PubMed connector's extraction drops italic markup, and journals italicise gene symbols, so a
symbol can vanish from a retrieved body. Self-disagreement runs 23.1% where the claim's label is
missing from the body against 8.6% where it is present, so this degrades judgement rather than
merely hiding text. The shared client is `lib/europepmc_client.py`; it tries Europe PMC first and
NCBI efetch second, and the fallback does most of the work (efetch served 36 of 59 sampled
papers). `missing_inline_strings()` re-reads the rendered text and returns any inline markup that
failed to survive, so a caller asserts it is empty. Keep the connector for search and metadata.

The Phase 5 and Phase 6 retrieval steps are compliant by a different route: they parse raw PMC
JATS from `efetch` directly, so no markup is lost.

**R2. Single-reader verification is accepted, with its instability recorded as a limit.** 12.3%
self-disagreement on the three-way verdict, 3.9% on supported versus not. Do not add a second
reader. Do not report a three-way verdict as if it were stable; the binary call is what the
evidence tiers rest on.

**R3. Any pathway, near-miss, enrichment or convergence analysis reads
`phase3-expression-targets.csv.gz`, not the capped candidate list, and records which it used.**
The top-200 cap excludes 1,120 of 2,227 replicated tier A and B genes. It exists for a
presentation chart, and the failure it caused was shaping an analysis silently: the withdrawn
MPNST PARP1 convergence rested on a base-excision-repair signature the cap had truncated from ten
genes to five.

Both steps that read the capped list were changed on 2026-11-20 and neither was re-run, so their
committed tables stand as produced while any future run complies. `phase3_kegg_enrich.py` takes
`--foreground replicated` by default and `phase7_compare_lists.py` loads the full table for the
near-miss pass only, leaving the exact-match comparison on the capped list that Phase 4 consumes.
Both record which list they used.

One residual is not closed and you should not describe ruling 3 as discharged: the near-miss pass
selects its pathways, and its per-pathway gene lists, from `phase3-kegg-enrichment.csv`, which was
computed on the capped foreground and cannot be regenerated because the Phase 2 ranked lists it
needs are not committed.

If you write a new pathway or convergence analysis, read the full table and say so in the output.

**R4. A failed or empty API call is reported.** See above.

## Where a human decides

Do not resolve any of these yourself. Put the question to the user with what you measured.

- Whether to re-run a step whose output is a committed, reviewed deliverable. A re-run that moves
  verdicts breaks the correspondence between a table and the write-up that describes it.
- Any change to the fixed manifestation vocabulary. It is project-wide, and it has been changed
  once (Pheochromocytoma, 2026-11-17).
- Whether a dataset or a paper is in scope, and whether germline NF attribution is established.
- Whether a trial counts as an NF trial. `nf_specific_basis` is three-state: `statement`,
  `provenance_nf_in_eligibility` (verified against the registry, where the NF mention usually lives)
  and `provenance_no_nf_mention`. Of 209 NF-specific trials, 188 are by statement, 17 by eligibility
  criteria and 4 name NF nowhere. Two of those four are not NF trials; two are MPNST trials that
  never state whether their patients have NF1 and are kept and flagged, not dropped.
- Whether a near-miss or convergence is a finding. A malignant-versus-benign contrast raises every
  replication and repair pathway, so coherent up-regulation of one is the expected case. Ask for a
  proliferation control before reporting any such convergence.
- Merging a pull request.

## Reporting

Findings before methods. State what you did not do. Never report a number you have not read back
off a saved table, and never report a count from a partial or capped input as if it were a
measurement of the whole.

Two scope words are part of rulings and are not interchangeable with their neighbours. A stratum
with no dataset in the launch set has "no expression contrast **found**", never "exists". A drug
reached through a manifestation-term trial query is in a `manifestation` trial, and only
`nf_specific` means an NF trial.

## Validating a change

`phase-8/data/phase8-validation-set.csv` holds the targets with NF clinical precedent, built from
the drugs actually trialled in NF. Build it from `matches_phase4_interaction_drug`, not
`matches_phase4_drug`: the latter joins against the ChEMBL drug universe alone and reports 40
interventions where the interaction table supports 68, dropping the mTOR inhibitors among others.
Both columns are carried, so check which one you are reading. `phase-8/scripts/phase8_validate.py` checks whether the
pipeline surfaces each one in the stratum its trial evidence implies. Run it after any change
that could move the candidate lists.

It tests recall of the already-known, and parts of the pipeline were built from the same
evidence, so it is a sanity check rather than an independent validation. A pipeline that cannot
recover the approved NF drug's target is demonstrably broken; passing does not prove the converse.
