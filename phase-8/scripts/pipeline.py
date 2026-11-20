#!/usr/bin/env python3
"""Phase 8: the agent-operable entry point to Phases 3-7.

This is a thin driver over a declared manifest, not a new pipeline. Every step it
knows about is a script that already exists and was already run; the manifest
records what each one reads, writes, calls over the network and is constrained by.

What it is for. Phases 3-7 are 48 steps across six directories, four invocation
styles and nine external services, and the order is a dependency graph rather than
a list. An agent asked to re-run or extend a phase needs three things this driver
supplies: the order, the preconditions, and a refusal when a precondition is not
met.

The one rule the project plan is explicit about (Phase 8 prompt, 2026-11-19): if a
step fails or returns nothing, that is reported. Nothing here substitutes a
placeholder, an estimate or a cached value for a step that did not run, and `run`
fails a step whose declared outputs did not appear even when the script itself
exited 0.

Subcommands
  list      the manifest, filterable by phase, class or ruling
  check     preconditions per step: inputs present, outputs present, credentials set
  rulings   which steps the four binding rulings constrain, and where code disagrees
  run       execute one step, with failure surfaced rather than absorbed

Inputs
  phase-8/data/phase8-pipeline-steps.csv

Run from the repo root:
    python phase-8/scripts/pipeline.py check
"""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path

MANIFEST = Path("phase-8/data/phase8-pipeline-steps.csv")

# The four rulings the manifest tags steps with. Text is abbreviated; the full
# wording is in docs/project-plan.md under "Awaiting PI review".
RULINGS = {
    "R1": "Full-text verification reads Europe PMC JATS (or raw PMC JATS from efetch), "
          "never connector-extracted PMC text, which deletes italicised gene symbols.",
    "R2": "Single-reader verification is accepted, with its measured instability recorded "
          "as a limit: 12.3% on the three-way verdict, 3.9% on supported-versus-not.",
    "R3": "Any pathway, near-miss, enrichment or convergence analysis reads "
          "phase3-expression-targets.csv.gz, not the capped candidate list, and records which it used.",
    "R4": "A failed or empty API call is reported, never replaced by a placeholder or an estimate.",
}

CLASS_HELP = {
    "reproducible": "every input is committed; no network, no model reader",
    "network": "needs an external service, and possibly a credential",
    "model_reader": "needs host.llm in the Claude Science python kernel",
    "blocked": "an input is not in the repo and cannot be regenerated from it",
}


def load(repo: Path) -> list[dict]:
    path = repo / MANIFEST
    if not path.exists():
        sys.exit(f"manifest not found: {path}\nRun from the repo root, or pass --repo.")
    with path.open() as fh:
        steps = list(csv.DictReader(fh))
    if not steps:
        sys.exit(f"manifest is empty: {path}")
    return steps


def split(field: str) -> list[str]:
    return [x.strip() for x in (field or "").split(";") if x.strip()]


def is_glob(path: str) -> bool:
    """A declared input that names a pattern rather than a file, e.g. <ranked-dir>."""
    return "<" in path


def present(repo: Path, rel: str) -> bool | None:
    """True, False, or None where presence is not decidable from the repo."""
    if is_glob(rel):
        return None
    return (repo / rel).exists()


def producers(steps: list[dict]) -> dict[str, str]:
    """Which step writes each declared output. A missing input that no step writes
    is a genuine gap; one that a step writes is just an unrun predecessor."""
    out: dict[str, str] = {}
    for s in steps:
        for path in split(s["outputs"]):
            out.setdefault(path, s["step_id"])
    return out


def status_of(repo: Path, step: dict, prod: dict[str, str] | None = None) -> dict:
    ins, outs = split(step["inputs"]), split(step["outputs"])
    missing_in = [p for p in ins if present(repo, p) is False]
    undecidable = [p for p in ins if present(repo, p) is None]
    missing_out = [p for p in outs if present(repo, p) is False]
    creds = [c.strip() for c in (step["credentials"] or "").replace(",", " ").split() if c.strip()]
    unset = [c for c in creds if not os.environ.get(c)]
    prod = prod or {}
    regenerable = {p: prod[p] for p in missing_in if p in prod}
    unproduced = [p for p in missing_in if p not in prod]
    ready = not missing_in and not undecidable and step["reproducibility"] != "blocked"
    return {
        "ready": ready,
        "regenerable_inputs": regenerable,
        "unproduced_inputs": unproduced,
        "missing_inputs": missing_in,
        "undecidable_inputs": undecidable,
        "missing_outputs": missing_out,
        "unset_credentials": unset,
    }


def cmd_list(repo: Path, args) -> int:
    steps = load(repo)
    for s in steps:
        if args.phase and args.phase not in s["phase"]:
            continue
        if args.klass and s["reproducibility"] != args.klass:
            continue
        if args.ruling and args.ruling not in s["rulings"]:
            continue
        tag = f"[{s['rulings']}]" if s["rulings"] else ""
        print(f"{s['step_id']:7} {s['reproducibility']:13} {s['name']} {tag}")
        print(f"        {s['script']}")
    return 0


def cmd_check(repo: Path, args) -> int:
    all_steps = load(repo)
    prod = producers(all_steps)
    steps = [s for s in all_steps if not args.step or s["step_id"] == args.step]
    if args.step and not steps:
        sys.exit(f"no such step: {args.step}")
    counts = {"ready": 0, "blocked": 0, "incomplete": 0}
    for s in steps:
        st = status_of(repo, s, prod)
        if s["reproducibility"] == "blocked":
            counts["blocked"] += 1
            print(f"BLOCKED  {s['step_id']:7} {s['name']}")
            print(f"         cannot run: {s['blocked_by']}")
        elif st["missing_inputs"]:
            counts["incomplete"] += 1
            print(f"MISSING  {s['step_id']:7} {s['name']}")
            for p, owner in st["regenerable_inputs"].items():
                print(f"         not present, written by {owner}: {p}")
            for p in st["unproduced_inputs"]:
                print(f"         not present and no step in this manifest writes it: {p}")
        else:
            counts["ready"] += 1
            note = ""
            if st["unset_credentials"]:
                note = f"  (credential not set in this environment: {', '.join(st['unset_credentials'])})"
            print(f"READY    {s['step_id']:7} {s['name']}{note}")
        for p in st["missing_outputs"]:
            print(f"         output not yet produced: {p}")
    print()
    print(f"{counts['ready']} ready, {counts['incomplete']} with a missing input, "
          f"{counts['blocked']} blocked on an input the repo does not carry")
    return 0


def cmd_rulings(repo: Path, args) -> int:
    steps = load(repo)
    for key, text in RULINGS.items():
        tagged = [s for s in steps if key in s["rulings"]]
        print(f"{key}  {text}")
        if not tagged:
            print("     no step tagged")
        for s in tagged:
            print(f"     {s['compliance']:14} {s['step_id']:7} {s['name']}")
            if s["compliance"] != "compliant":
                print(f"                    {s['compliance_evidence']}")
        print()
    bad = [s for s in steps if s["compliance"] == "non_compliant"]
    print(f"{len(bad)} step(s) disagree with a ruling they are tagged with.")
    return 1 if bad else 0


def cmd_run(repo: Path, args) -> int:
    all_steps = load(repo)
    steps = {s["step_id"]: s for s in all_steps}
    s = steps.get(args.step)
    if s is None:
        sys.exit(f"no such step: {args.step}\nKnown: {', '.join(sorted(steps))}")
    st = status_of(repo, s, producers(all_steps))

    if s["reproducibility"] == "blocked":
        sys.exit(f"{s['step_id']} cannot run here: {s['blocked_by']}\n"
                 "This is a real gap, not a configuration problem. Do not substitute "
                 "another input for the missing one.")
    if s["invocation"] == "kernel":
        sys.exit(f"{s['step_id']} needs the Claude Science python kernel, which supplies "
                 f"host.llm and the MCP connectors. It cannot be driven from here.\n"
                 f"Run instead:  {s['command']}")
    if s["invocation"] == "R":
        print(f"note: {s['step_id']} is an R step; invoking Rscript")
    if st["missing_inputs"]:
        lines = [f"{p}  (written by {owner}; run that first)"
                 for p, owner in st["regenerable_inputs"].items()]
        lines += [f"{p}  (no step in this manifest writes it)" for p in st["unproduced_inputs"]]
        sys.exit(f"{s['step_id']} is missing {len(st['missing_inputs'])} declared input(s):\n  "
                 + "\n  ".join(lines))
    if st["unset_credentials"]:
        print(f"warning: credential(s) not set in this environment: "
              f"{', '.join(st['unset_credentials'])}. The step will be allowed to fail "
              f"rather than run degraded.")

    if s["invocation"] == "R":
        argv = ["Rscript", s["script"]] + s["command"].split()
    else:
        argv = [sys.executable, s["script"]] + s["command"].split()
    print(f"$ {' '.join(argv)}")
    if args.dry_run:
        print("(dry run; nothing executed)")
        return 0

    before = {p: (repo / p).stat().st_mtime for p in split(s["outputs"]) if (repo / p).exists()}
    proc = subprocess.run(argv, cwd=repo)
    if proc.returncode != 0:
        print(f"\nFAILED  {s['step_id']} exited {proc.returncode}. "
              f"Its outputs are unchanged or partial; nothing was substituted.", file=sys.stderr)
        return proc.returncode

    # Exit 0 is not proof the step produced anything. Check the declared outputs.
    unwritten, unchanged = [], []
    for p in split(s["outputs"]):
        f = repo / p
        if not f.exists():
            unwritten.append(p)
        elif f.stat().st_size == 0:
            unwritten.append(f"{p} (empty)")
        elif p in before and f.stat().st_mtime == before[p]:
            unchanged.append(p)
    if unwritten:
        print(f"\nFAILED  {s['step_id']} exited 0 but did not produce:\n  "
              + "\n  ".join(unwritten), file=sys.stderr)
        return 1
    if unchanged:
        print(f"\nnote: {s['step_id']} exited 0 and left these outputs untouched: "
              f"{', '.join(unchanged)}")
    print(f"\nOK      {s['step_id']} produced {len(split(s['outputs']))} declared output(s)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".", help="repo root (default: .)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="list manifest steps")
    p.add_argument("--phase")
    p.add_argument("--class", dest="klass", choices=sorted(CLASS_HELP))
    p.add_argument("--ruling", choices=sorted(RULINGS))
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser("check", help="report preconditions per step")
    p.add_argument("--step")
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("rulings", help="which steps each binding ruling constrains")
    p.set_defaults(fn=cmd_rulings)

    p = sub.add_parser("run", help="execute one step")
    p.add_argument("step")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_run)

    args = ap.parse_args()
    return args.fn(Path(args.repo).resolve(), args)


if __name__ == "__main__":
    raise SystemExit(main())
