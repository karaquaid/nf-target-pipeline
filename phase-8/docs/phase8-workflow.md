# Phases 3 to 7 as an agent-operable workflow

The Phase 8 scope ruling of 2026-11-19 settled the form: agent-operable in chat, driven by
committed scripts, with a human at each decision point, rather than a standalone Agent SDK
program. This is that build.

Three pieces:

| Piece | What it is |
|---|---|
| `phase-8/data/phase8-pipeline-steps.csv` | the manifest: 48 steps, what each reads, writes, calls and is constrained by |
| `phase-8/scripts/pipeline.py` | the driver: `list`, `check`, `rulings`, `run` |
| `phase-8/agents/nf-target-pipeline/` | the agent skill and profile, for running it in a Claude Science session |

The manifest is maintained by hand. It is a contract, not a scrape: the inputs and outputs were
derived by reading each script and cross-checked against the paths it actually opens, and a change
that moves a path is a change to the manifest too.

## What the wrap found

**Five Phase 3 steps cannot run from this repository.** Phase 2 wrote one ranked list per dataset
under `build/phase2/<acc>/<acc>_de.csv` and those files are not committed, only the ingestion
manifest row. So contrast labelling, the rank matrices, the Robust Rank Aggregation and the
candidate rule cannot be rebuilt here, and neither can the KEGG enrichment, which needs the
per-stratum background `universe.csv` that the rank-matrix step writes. Their outputs are
committed, so all 43 downstream steps run.

**One more step could not be regenerated, and is now fixed.** The Phase 5 write-up read three JSON
files from the build directory that no committed script writes. Every fact it needed was already in
the committed `phase5-provenance.json` the script itself emits, so that is now the fallback: a live
run prefers its own build artefacts, a clean clone reconstructs the same values, and the dossier
counts are asserted against `phase4-target-dossier.csv` rather than trusted, so a drifted
provenance file fails loudly instead of propagating a stale number.

Two run facts genuinely are not derivable and are carried in a `PROCESS_HISTORY` constant, the
convention Phase 4's report builder already uses: the 43 symbols that resolved only through the
Phase 4 alias (the committed associations table drops the `resolved_via` column) and the 2,950
distinct GO process terms (counted across all 3,777 DisMech disorder entries, not the NF mechanism
nodes, so the committed NF-only table cannot answer it). Both were caught by the regeneration
check, which is the reason to run it: an earlier attempt derived the GO count from the NF nodes and
produced 26, silently replacing a figure about the whole release with one about a fragment of it.

The regenerated write-up differs from the committed one in exactly one way, and the regenerated
version is the correct one: it lists 16 data files the committed version was missing, because that
document predates the CNS-literature, drug-search, label-CNS and tractability-state passes. No
number moved.

**Two steps disagreed with a binding ruling, and both are now changed (Kara, 2026-11-20).** Ruling
3 of 2026-11-17 requires any pathway, near-miss, enrichment or convergence analysis to read
`phase3-expression-targets.csv.gz` rather than the capped candidate list. `phase3_kegg_enrich.py`
computed over-representation on the capped foreground, and the pathway near-miss pass in
`phase7_compare_lists.py` built its expression side from the capped list, which is the mechanism
behind the withdrawn MPNST PARP1 convergence. Both now read the full table, restricted to
non-driver tier A and B genes with no rank cap, which is the population the ruling describes the
cap as having halved. Both record which list they used, per the ruling's second clause. **Neither
was re-run**, so every committed table stands as produced.

Running the near-miss pass into a scratch directory to check the code path works shows what the cap
was doing: **shared-pathway near misses fall from 56 to 5, and six of the seven pathways disappear
entirely.** A literature gene only counts as a near miss when it is not itself an expression
candidate in that stratum, and under the cap many of them looked absent when they were merely
hidden. Basal cell carcinoma, hematopoietic cell lineage, leishmaniasis, rheumatoid arthritis,
Th1/Th2 differentiation and the cytokine-receptor pathway were all cap artefacts. The only survivor
is base excision repair against PARP1 in NF1 MPNST, the convergence already examined and withdrawn
as a proliferation readout. The compliant analysis therefore produces no near-miss finding that was
not already dealt with.

**A residual the change cannot close.** The pass still selects its pathways, and its per-pathway
gene lists, from `phase3-kegg-enrichment.csv`, which was computed on the capped foreground and
cannot be regenerated because `build/phase3/universe.csv` depends on the uncommitted Phase 2 ranked
lists. The surviving rows show it: they name five base-excision-repair genes where the Phase 7
examination established the signature is ten, the other five falling below the cap. Ruling 3 is
implemented in the code, not yet discharged in the data.

**One step violated the failure-surfacing rule, and is fixed.** `phase7_fallback_literature.py`
retried a failed full-text batch one paper at a time and silently dropped any that still failed,
so a paper whose body could not be retrieved was indistinguishable from one that has none. Its
retrieval also still used the PubMed connector, which ruling 1 forbids for verification. Both are
now corrected: the stage uses `lib/europepmc_client`, asserts the client's symbol-preservation
check is empty, and writes every unretrieved paper with a reason to `fulltext-failures.json`. The
committed `phase7-fallback-candidates.csv` predates the switch and stands as produced; re-running
it is a separate decision.

The remaining 16 network steps were audited for failure handling and surface failures correctly:
none has an `except: pass` around an API call, and `phase5_monarch.py` does better than printing,
persisting the error per record in its checkpoint.

**A fourth defect, found only by regenerating.** `build_phase4_report.py` carried the same gzip
defect `phase4_dossier.py` had been fixed for: it read `phase4-opentargets-tractability.csv` while
the committed table is gzipped, so it could not regenerate its own output. The Phase 8 manifest
check reported the file as a missing input, which is how it surfaced.

Fixing that and regenerating showed the committed Phase 4 write-up was **stale against its own
data**. The manifestation-rule change of 2026-11-17, which moved ANNUBP out of the topical-eligible
set and vestibular schwannoma into the CNS-required set, landed in the code but its regenerated
report never did. Three figures were wrong: route-appropriate drugs for ANNUBP read 210 against 206,
for vestibular schwannoma 1,041 against 205, and the delivery-inappropriate count 427 against 715
(271 topical-only, 394 predicted non-permeant, 50 biologics). No other document quotes those
numbers. The regenerated write-up is committed with the corrected figures.

## The step classes

| Class | Steps | Meaning |
|---|---|---|
| `reproducible` | 23 | every input committed, no network, no model reader |
| `network` | 16 | needs an external service, sometimes a credential |
| `model_reader` | 4 | needs `host.llm`, and sometimes an MCP connector |
| `blocked` | 5 | an input is not in the repo and cannot be regenerated from it |

`pipeline.py check` now reports 42 ready, 1 waiting on an unrun predecessor's build output, and 5
blocked. `pipeline.py rulings` reports no step disagreeing with a ruling it is tagged with.

The four `model_reader` steps are the two Phase 6 adjudication passes, the Phase 7 literature
fallback and the Phase 7 stability measurement. They are invoked from the kernel as
`import <module> as m; m.main(host)`. `pipeline.py run` refuses them and prints that line rather
than attempting a subprocess that would fail obscurely.

## Failure surfacing

The Phase 8 prompt's instruction is that the agent reports a failure rather than proceeding with a
placeholder. The driver enforces the mechanical half:

- A step whose declared inputs are absent does not run. The message names each missing file and,
  where another step writes it, which step to run first.
- A `blocked` step does not run, and the refusal says the gap is real rather than a configuration
  problem.
- **A step that exits 0 without producing its declared outputs is reported as a failure**, and an
  output that exists but is empty counts as not produced. An exit code is not evidence that
  anything was written.
- An output left untouched by a successful run is reported as a note, not hidden.

Verified both ways: `p3b.01` re-ran and regenerated its two committed tables byte-identically, and
a step contrived to exit 0 while writing nothing was caught and failed.

Credentials are reported as unset rather than worked around. A step that needs `OPENFDA_API_KEY`
or `GTPAPIKEY` is allowed to fail if the key is absent, because a degraded run that looks like a
complete one is the failure mode this phase exists to prevent.

## Where a human decides

The ruling chose chat operation partly to keep a human at each decision point. The skill lists
them: re-running a reviewed deliverable, any change to the fixed manifestation vocabulary, scope
and germline-attribution calls, whether a near-miss or convergence is a finding, and merging a
pull request.

## Using it

```
python phase-8/scripts/pipeline.py check                 # what can run right now
python phase-8/scripts/pipeline.py list --class network  # what needs a service
python phase-8/scripts/pipeline.py rulings               # what the rulings constrain
python phase-8/scripts/pipeline.py run p4.11             # one step, with failure surfaced
python phase-8/scripts/pipeline.py run p4.11 --dry-run   # print the command only
```

Validation of a change is `phase-8/scripts/phase8_validate.py`; the record is
`phase-8/docs/phase8-validation.md`.

## What this does not do

- It does not orchestrate a full end-to-end run. The dependency order is declared and the
  preconditions are checked, but each step is invoked deliberately, which is what the ruling asked
  for.
- It does not discharge ruling 3 in the data. Both scripts now read the full table, but the
  enrichment table they depend on was computed on the capped foreground and cannot be regenerated
  here.
- It does not re-run any committed deliverable. Every table in the repository stands as produced,
  except the two Phase 3b tables regenerated byte-identically while testing the driver, and the
  Phase 5 write-up, whose regeneration adds 16 missing file-list entries and moves no number.
- It does not correct `matches_phase4_drug`. The corrected join is carried alongside it as
  `matches_phase4_interaction_drug` so the two populations cannot be conflated.
- It covers Phases 3 to 7 only. Phases 1a, 1b and 2 are out of the wrap's scope, and Phase 2's
  hand-off is the boundary that blocks five Phase 3 steps.
