# NF Literature Monitor

An agent that refreshes the NF literature target map once a month: re-runs the fixed query
bank restricted to new records, verifies the claims against full text, merges into the running
tables under `literature-watch/data/` without disturbing verified rows, regenerates the
write-up and figure, and opens a pull request of the deltas.

It never writes to `phase-1b/`, which is the frozen snapshot the manuscript cites.

Everything it needs is in this directory, so a collaborator can stand it up in their own
workspace without access to ours.

| File | What it is |
|---|---|
| `SKILL.md` | The protocol. Rules, workflow, and what a good monthly report says. |
| `kernel.py` | Helper functions loaded with the skill: retrieval ladder, preprint detection, the two prompt builders. |
| `profile.json` | The agent profile: name, description and system prompt, exported from the live definition. |

The protocol reads `phase-1b/data/phase1b-queries.csv`, the 32 PubMed queries verbatim with
the disease and manifestation each targets. Those queries define what the corpus means, so
changing one makes that manifestation's counts incomparable with earlier runs. If you change
one, say so in the pull request.

## Installing it

In Claude Science, run this in the `repl` tool from a session with access to this repository:

```python
import json
spec = json.load(open("literature-watch/agents/nf-literature-monitor/profile.json"))

host.skills.edit("nf-literature-monthly", "SKILL.md",
                 open("literature-watch/agents/nf-literature-monitor/SKILL.md").read())
host.skills.edit("nf-literature-monthly", "kernel.py",
                 open("literature-watch/agents/nf-literature-monitor/kernel.py").read())
host.skills.publish("nf-literature-monthly")

host.agents.create(spec["name"], display_name=spec["display_name"],
                   description=spec["description"], system_prompt=spec["system_prompt"])
```

Leaving `skill_names` unset gives the profile the full skill catalog and every connector, which
is deliberate: a later run that needs a source we have not used yet should not stall on a
missing attachment. Pass an explicit list instead if you want a tighter loadout, and attach the
PubMed and gene-symbol connectors by hand, since a curated profile starts with none.

Then pick "NF Literature Monitor" from the session config on a new conversation and say
`run the monthly update`.

## What it will not do

It does not run the expression pipeline, change the manifestation vocabulary or the scope
rules, merge its own pull requests, or hand-edit derived tables. Scope questions come back to
you as questions.

## Using it for a different disease

The retrieval ladder, the verdict rubric and the flag-plus-derived-table pattern transfer
unchanged. The query bank and the manifestation vocabulary have to be rebuilt for the new
disease, ideally from an existing clinical standard. The three target annotation flags are the
least transferable, since they depend on the pharmacology of the specific gene set. The
protocol earns its cost where the literature is small enough to read exhaustively and uneven
enough across subphenotypes that counting papers misranks them.
