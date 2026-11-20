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

**One more step cannot be regenerated, and it was not previously recorded.** The Phase 5 write-up
reads `build/phase5/phase5-inputs.json`, which no committed script writes.

**Two steps disagree with a binding ruling.** Ruling 3 of 2026-11-17 requires any pathway,
near-miss, enrichment or convergence analysis to read `phase3-expression-targets.csv.gz` rather
than the capped candidate list. `phase3_kegg_enrich.py` computes over-representation on the capped
foreground, and the pathway near-miss pass in `phase7_compare_lists.py` builds its expression side
from the capped list. The second is the mechanism behind the withdrawn MPNST PARP1 convergence:
the ruling was recorded, the code was not changed. Neither is fixed here, because the same ruling
says no rerun of Phases 3 to 6 and a change would move committed tables. `pipeline.py rulings`
prints both as `non_compliant`, so the disagreement is visible rather than latent.

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

## The step classes

| Class | Steps | Meaning |
|---|---|---|
| `reproducible` | 23 | every input committed, no network, no model reader |
| `network` | 16 | needs an external service, sometimes a credential |
| `model_reader` | 4 | needs `host.llm`, and sometimes an MCP connector |
| `blocked` | 5 | an input is not in the repo and cannot be regenerated from it |

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
- It does not fix the two ruling-3 disagreements, which would move committed tables.
- It does not re-run any committed deliverable. Every table in the repository stands as produced,
  except the two Phase 3b tables regenerated byte-identically while testing the driver.
- It covers Phases 3 to 7 only. Phases 1a, 1b and 2 are out of the wrap's scope, and Phase 2's
  hand-off is the boundary that blocks five Phase 3 steps.
