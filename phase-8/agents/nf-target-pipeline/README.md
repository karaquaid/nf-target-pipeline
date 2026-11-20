# NF Target Pipeline Operator

The agent that runs Phases 3 to 7 of this repository: candidate ranking, coverage review, the
drug and tractability layer, mechanistic validation, evidence scoring and literature validation.

**This file is only about recreating the agent inside Claude Science.** You do not need it, or
the agent, to run the pipeline. The driver is a plain script, and `phase-8/docs/phase8-workflow.md`
is the walkthrough:

```
python phase-8/scripts/pipeline.py check
```

| File | What it is |
|---|---|
| `SKILL.md` | The protocol: run order, step classes, binding rulings, decision points. Published as the skill `nf-target-pipeline`. |
| `profile.json` | The agent profile: identity, job, boundaries. |

## Inside Claude Science

Recreate both in another workspace from a clone of this repository, using the `repl` tool:

```python
import json, pathlib
d = pathlib.Path("phase-8/agents/nf-target-pipeline")
host.skills.publish(name="nf-target-pipeline", content=(d / "SKILL.md").read_text())
host.agents.create(**json.loads((d / "profile.json").read_text()))
```

The profile is unrestricted: it gets the live skill catalogue and every connector the workspace
has, because the pipeline reaches ChEMBL, Open Targets, DGIdb, the Guide to Pharmacology, openFDA,
ClinicalTrials.gov, Monarch, KEGG, NCBI E-utilities and PubMed. Four steps need `host.llm` and so
only run inside a Claude Science kernel; the rest are ordinary scripts.

## What it will not do

It does not decide scope, change the manifestation vocabulary, re-run a reviewed deliverable
without being asked, or merge its own pull requests. It reports a failed or empty API call rather
than filling the gap, which is the one instruction the Phase 8 prompt states outright.
