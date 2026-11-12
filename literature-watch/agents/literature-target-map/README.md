# Target Map Builder

The agent that performs a first build of a literature target map: the work this project calls
Phase 1b, generalised to any disease.

| File | What it is |
|---|---|
| `SKILL.md` | The protocol. Published as the skill `literature-target-map`. |
| `profile.json` | The agent profile: identity, job, boundaries. |

## Inside Claude Science

Recreate both in another workspace by pasting this into the `repl` tool from a clone of this
repository:

    import json, pathlib
    d = pathlib.Path("literature-watch/agents/literature-target-map")
    host.skills.edit("literature-target-map", "SKILL.md", (d / "SKILL.md").read_text())
    host.skills.publish("literature-target-map")
    p = json.loads((d / "profile.json").read_text())
    host.agents.create(p["name"], display_name=p["display_name"], description=p["description"],
                       system_prompt=p["system_prompt"])

Both calls raise an approval card; the agent appears in the session config picker once approved.
Agent profiles are per workspace and do not travel through the skill registry, which is why the
profile is committed here rather than shared from the catalog.

## Outside Claude Science

You do not need the agent. The same protocol runs as scripts, with no Claude Science and no
access to this repository:

    cp litmonitor/configs/template.toml mystudy.toml
    export ANTHROPIC_API_KEY=sk-...
    python litmonitor/selftest.py
    python litmonitor/build.py --config mystudy.toml --dry-run
    python litmonitor/build.py --config mystudy.toml --annotate
    python litmonitor/review.py --config mystudy.toml --stamp 2026-11
    python litmonitor/report.py --config mystudy.toml

See `litmonitor/README.md`. The agent exists for the parts that benefit from a conversation:
designing the vocabulary, arguing about scope, and reading extracted rows against their
abstracts before a full run.

## Relationship to the monitor

`literature-target-map` builds a map. `nf-literature-monthly`, in the sibling directory, keeps
one current. Same rules, same tables, different job: the builder aggregates claims across papers
into rows, the monitor appends to rows that already exist and never downgrades a verified one.
