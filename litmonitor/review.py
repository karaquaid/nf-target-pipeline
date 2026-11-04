#!/usr/bin/env python3
"""Review gate for a monitor run. Config-driven, and usable with no baseline at all.

    python litmonitor/review.py --config litmonitor/configs/nf.toml --stamp 2026-11

Three layers, cheapest first. --offline runs the first two.

1. Frozen-path guard: directories the config declares frozen must be untouched, checked
   against git rather than trusted.
2. Deterministic invariants: baseline rows unchanged, no verified row downgraded, labels
   inside the config's vocabulary, counts internally consistent, the candidate list equal to
   what the derivation rule produces.
3. Second reader: re-judges a random sample of the run's verdicts against the same bodies and
   measures disagreement, then checks every number in the generated prose against a digest
   computed from the tables.

Checks that need something the study does not have (no baseline, no annotations, no prose)
are skipped with a note rather than failed. A cold-start study still gets layers 1 and 3 and
most of layer 2.
"""

import argparse
import importlib.util
import json
import random
import subprocess
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfgmod  # noqa: E402
import llm  # noqa: E402
import monitor as mon  # noqa: E402

DISAGREEMENT_FAIL = 0.34
SAMPLE_MAX = 8


class Report:
    def __init__(self):
        self.rows = []

    def add(self, level, check, detail):
        self.rows.append({"level": level, "check": check, "detail": detail})
        print("%-5s %-34s %s" % (level, check, detail))

    ok = lambda self, c, d="": self.add("pass", c, d)
    warn = lambda self, c, d="": self.add("warn", c, d)
    fail = lambda self, c, d="": self.add("FAIL", c, d)
    skip = lambda self, c, d="": self.add("skip", c, d)

    @property
    def failed(self):
        return any(r["level"] == "FAIL" for r in self.rows)

    @property
    def warned(self):
        return any(r["level"] == "warn" for r in self.rows)

    def markdown(self, cfg, stamp):
        mark = {"pass": "ok", "warn": "warn", "FAIL": "**FAIL**", "skip": "n/a"}
        head = ["# Review report: %s, %s" % (cfg.study, stamp), "",
                "| | Check | Detail |", "|---|---|---|"]
        body = ["| %s | %s | %s |" % (mark[r["level"]], r["check"], r["detail"]) for r in self.rows]
        verdict = "**FAILED**" if self.failed else ("passed with warnings" if self.warned else "passed")
        return "\n".join(head + body + ["", "Result: %s." % verdict, ""])


def git_clean(paths, rep):
    if not paths:
        rep.skip("frozen paths untouched", "config declares none")
        return
    try:
        diff = subprocess.run(["git", "diff", "--name-only", "HEAD", "--"] + list(paths),
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception as exc:
        rep.warn("frozen paths untouched", "git unavailable: %r" % exc)
        return
    if diff:
        rep.fail("frozen paths untouched", "modified: " + diff.replace("\n", ", "))
    else:
        rep.ok("frozen paths untouched", ", ".join(paths))


def baseline_tables(cfg):
    if not cfg.baseline:
        return {}
    return {p.name: p for p in Path(cfg.baseline).glob("*.csv")}


def check_baseline_preserved(cfg, rep):
    base = baseline_tables(cfg)
    if not base:
        rep.skip("baseline rows preserved", "cold start, no baseline to compare against")
        return
    data = cfg.workdir / "data"
    checked = 0
    for name, src in sorted(base.items()):
        live_path = data / name
        if not live_path.exists():
            continue
        frozen, live = pd.read_csv(src), pd.read_csv(live_path)
        if "in_baseline" not in live.columns or not set(mon.ROW_KEY) <= set(frozen.columns):
            continue
        kept = live[live.in_baseline.astype(bool)]
        shared = [c for c in frozen.columns if c in kept.columns]
        a = frozen[shared].sort_values(mon.ROW_KEY).reset_index(drop=True)
        b = kept[shared].sort_values(mon.ROW_KEY).reset_index(drop=True)
        checked += 1
        if a.equals(b):
            rep.ok("baseline rows preserved", "%s: %d rows identical" % (name, len(a)))
        else:
            detail = ("shape %s vs %s" % (a.shape, b.shape) if a.shape != b.shape
                      else "%d rows differ" % int((a != b).any(axis=1).sum()))
            rep.fail("baseline rows preserved", "%s: %s" % (name, detail))
    if not checked:
        rep.skip("baseline rows preserved", "no comparable table found")


def check_no_downgrade(cfg, rep):
    base = baseline_tables(cfg)
    tpath, _ = mon.table_paths(cfg)
    if tpath.name not in base:
        rep.skip("no verified row downgraded", "cold start, nothing carried over")
        return
    frozen = pd.read_csv(base[tpath.name])
    live = pd.read_csv(tpath)
    before = frozen.set_index(mon.ROW_KEY).evidence_tier.to_dict()
    rank = cfg.tier_rank
    bad = ["%s | %s | %s: %s -> %s" % (r.gene_target, r.disease, r.manifestation,
                                       before[(r.gene_target, r.disease, r.manifestation)], r.evidence_tier)
           for r in live.itertuples()
           if (r.gene_target, r.disease, r.manifestation) in before
           and rank.get(r.evidence_tier, 0) < rank.get(before[(r.gene_target, r.disease, r.manifestation)], 0)]
    if bad:
        rep.fail("no verified row downgraded", "; ".join(bad[:4]))
    else:
        rep.ok("no verified row downgraded", "%d carried rows" % len(before))


def check_vocabulary(cfg, rep):
    tpath, _ = mon.table_paths(cfg)
    live = pd.read_csv(tpath)
    issues = []
    for col, allowed in (("manifestation", set(cfg.manifestations)), ("disease", set(cfg.diseases)),
                         ("evidence_tier", set(cfg.tier_rank))):
        if col in live.columns:
            bad = sorted(set(live[col].dropna()) - allowed)
            if bad:
                issues.append("%s: %s" % (col, bad[:4]))
    if issues:
        rep.fail("config vocabulary", "; ".join(issues))
    else:
        rep.ok("config vocabulary", "%d rows, all labels in range" % len(live))


def check_internal_consistency(cfg, rep):
    tpath, rpath = mon.table_paths(cfg)
    live, refs = pd.read_csv(tpath), pd.read_csv(rpath, dtype={"pmid": str})
    known = set(refs.pmid.astype(str))
    bad_count, orphan = [], set()
    for r in live.itertuples():
        pmids = [p for p in str(r.supporting_pmids).split(";") if p]
        if len(pmids) != int(r.n_supporting_papers):
            bad_count.append("%s|%s" % (r.gene_target, r.manifestation))
        orphan |= set(pmids) - known
    rep.fail("paper counts match pmid lists", "%d rows disagree: %s" % (len(bad_count), bad_count[:3])) \
        if bad_count else rep.ok("paper counts match pmid lists", "%d rows" % len(live))
    rep.fail("every supporting pmid is in references", "missing: %s" % sorted(orphan)[:5]) \
        if orphan else rep.ok("every supporting pmid is in references", "%d papers" % len(refs))

    ann = cfg.workdir / "data" / "phase1b-target-annotations.csv"
    if not ann.exists():
        rep.skip("one annotation per label", "study has no annotation table")
        return
    a = pd.read_csv(ann)
    missing = sorted(set(live.gene_target) - set(a.gene_target))
    dupes = a.gene_target[a.gene_target.duplicated()].tolist()
    if missing or dupes:
        rep.fail("one annotation per label", "missing %d (%s) duplicated %d"
                 % (len(missing), missing[:3], len(dupes)))
    else:
        rep.ok("one annotation per label", "%d labels" % a.gene_target.nunique())


def derive_rule(cfg):
    """The study's own derivation if the config names one, else the generic config rule.

    Importing the study's script matters: a second copy of a scope rule drifts from the
    first, and then this check passes while being wrong.
    """
    if cfg.derive_module and Path(cfg.derive_module).exists():
        spec = importlib.util.spec_from_file_location("study_derive", cfg.derive_module)
        module = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(Path(cfg.derive_module).resolve().parent))
        spec.loader.exec_module(module)
        return module.derive, Path(cfg.derive_module).name
    def generic(targets):
        excluded = targets.gene_target.isin(cfg.exclude_labels)
        if "excluded_label" in targets.columns:
            excluded = excluded | targets.excluded_label.astype(bool)
        return targets[~excluded & ~targets.evidence_tier.isin(cfg.excluded_tiers)]
    return generic, "config scope rule"


def check_candidates(cfg, rep):
    tpath, _ = mon.table_paths(cfg)
    cand_path = next((p for p in (cfg.workdir / "data" / "candidates.csv",
                                  cfg.workdir / "data" / "phase1b-candidate-targets.csv")
                      if p.exists()), None)
    if not cand_path:
        rep.skip("candidate list re-derivable", "study has no candidate table")
        return
    try:
        rule, source = derive_rule(cfg)
        expect = rule(pd.read_csv(tpath))
    except Exception as exc:
        rep.warn("candidate list re-derivable", "could not apply the rule: %r" % exc)
        return
    cand = pd.read_csv(cand_path)
    a = set(map(tuple, expect[mon.ROW_KEY].values))
    b = set(map(tuple, cand[mon.ROW_KEY].values))
    if a == b:
        rep.ok("candidate list re-derivable", "%d rows match %s" % (len(cand), source))
    else:
        rep.fail("candidate list re-derivable",
                 "only in candidates: %s; missing: %s" % (sorted(b - a)[:3], sorted(a - b)[:3]))


def check_prose(cfg, rep, forbid_em_dash=True):
    docs = sorted((cfg.workdir / "docs").glob("*.md")) if (cfg.workdir / "docs").exists() else []
    if not docs:
        rep.skip("house style", "no generated prose")
        return
    for doc in docs:
        if forbid_em_dash and "\u2014" in doc.read_text(encoding="utf-8"):
            rep.fail("house style", "%s contains an em dash" % doc.name)
        else:
            rep.ok("house style", "%s clean" % doc.name)


def digest(cfg):
    tpath, rpath = mon.table_paths(cfg)
    live, refs = pd.read_csv(tpath), pd.read_csv(rpath, dtype={"pmid": str})
    d = {"rows": len(live), "labels": int(live.gene_target.nunique()), "papers": len(refs),
         "tiers": live.evidence_tier.value_counts().to_dict(),
         "by_disease": live.disease.value_counts().to_dict(),
         "rows_by_manifestation": live.manifestation.value_counts().to_dict()}
    if "access_used" in refs.columns:
        d["full_text_papers"] = int(refs.access_used.astype(str).str.startswith("full_text").sum())
    if "in_baseline" in live.columns:
        d["rows_added_since_baseline"] = int((~live.in_baseline.astype(bool)).sum())
    return d


def check_numbers_in_prose(cfg, stamp, rep, model):
    texts = []
    for p in list((cfg.workdir / "docs").glob("*.md")) + list((cfg.workdir / "updates" / stamp).glob("*.md")):
        if p.name == "review-report.md":
            continue
        texts.append("### %s\n%s" % (p.name, p.read_text(encoding="utf-8")[:12000]))
    if not texts:
        rep.skip("numbers in prose", "no generated prose to check")
        return
    prompt = ("Below is a data digest computed from the tables, then prose generated from the same "
              "tables. List every quantitative claim in the prose that the digest does not support, "
              "or that it contradicts. Ignore dates, identifiers, PMIDs and DOIs. If a claim cannot "
              "be checked against the digest, say so rather than guessing.\n\n"
              'Return JSON: {"unsupported":[{"claim":"","why":""}]}\n\nDIGEST:\n%s\n\nPROSE:\n%s'
              % (json.dumps(digest(cfg), indent=1), "\n\n".join(texts)))
    out = llm.complete_json(prompt, system=("You are a reviewer checking numbers in scientific prose "
                                            "against the data they describe. You output JSON only."),
                            model=model, max_tokens=2000, salvage_key="claim")
    items = (out["data"] or {}).get("unsupported") or (out["data"] or {}).get("salvaged") or []
    if items:
        rep.fail("numbers in prose", "; ".join("%s (%s)" % (i.get("claim", "")[:60], i.get("why", "")[:50])
                                               for i in items[:4]))
    else:
        rep.ok("numbers in prose", "no unsupported quantitative claims")


def check_verdict_stability(cfg, stamp, rep, model, seed=0):
    """Re-judge a sample independently. This measures whether a verdict is reproducible,
    not whether it is right, which is the honest limit of a single-reader design."""
    rows_path = cfg.workdir / "updates" / stamp / "new-rows.csv"
    if not rows_path.exists():
        rep.skip("verdict stability", "no new rows this run")
        return
    rows = pd.read_csv(rows_path, dtype={"pmid": str})
    judged = rows[rows.evidence_tier.astype(str).str.startswith("full text")]
    if judged.empty:
        rep.skip("verdict stability", "no full-text verdicts this run")
        return
    back = {"full text - supported": "supported", "full text - partial": "partially_supported",
            "full text - not supported": "not_supported"}
    sample = random.Random(seed).sample(sorted(judged.pmid.unique()),
                                        min(SAMPLE_MAX, judged.pmid.nunique()))
    agree = total = 0
    disagreements = []
    for pmid in sample:
        rec = mon.epmc_record(pmid)
        body = mon.fetch_fulltext(rec["pmcid"])["text"] if rec.get("pmcid") else None
        if not body:
            continue
        sub = judged[judged.pmid == pmid]
        claims = [tuple(getattr(r, k) for k in mon.ROW_KEY) for r in sub.itertuples()]
        out = llm.complete_json(mon.verdict_prompt(cfg, claims, body), system=mon.VERDICT_SYSTEM,
                                model=model, max_tokens=3000, salvage_key="gene_target")
        second = {(j.get("gene_target"), j.get("manifestation")): j.get("verdict")
                  for j in ((out["data"] or {}).get("judgements") or [])}
        for r in sub.itertuples():
            now = second.get((r.gene_target, r.manifestation))
            if now is None:
                continue
            total += 1
            if now == back.get(r.evidence_tier):
                agree += 1
            else:
                disagreements.append("%s|%s: %s vs %s" % (r.gene_target, r.manifestation,
                                                          back.get(r.evidence_tier), now))
    if not total:
        rep.warn("verdict stability", "sample could not be re-judged (no bodies retrieved)")
        return
    rate = 1 - agree / total
    detail = "%d of %d re-judged pairs disagree (%.0f%%)%s" % (
        total - agree, total, 100 * rate, "; " + "; ".join(disagreements[:3]) if disagreements else "")
    if rate > DISAGREEMENT_FAIL:
        rep.fail("verdict stability", detail)
    elif disagreements:
        rep.warn("verdict stability", detail)
    else:
        rep.ok("verdict stability", detail)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True, type=Path)
    p.add_argument("--stamp", required=True)
    p.add_argument("--out", type=Path)
    p.add_argument("--offline", action="store_true", help="deterministic checks only")
    args = p.parse_args()
    cfg = cfgmod.load(args.config)
    rep = Report()

    git_clean(cfg.frozen, rep)
    check_baseline_preserved(cfg, rep)
    check_no_downgrade(cfg, rep)
    check_vocabulary(cfg, rep)
    check_internal_consistency(cfg, rep)
    check_candidates(cfg, rep)
    check_prose(cfg, rep)
    if args.offline:
        rep.warn("second reader", "skipped (--offline): verdict stability and prose numbers unchecked")
    else:
        model = llm.resolve_model()
        check_numbers_in_prose(cfg, args.stamp, rep, model)
        check_verdict_stability(cfg, args.stamp, rep, model)

    out = args.out or (cfg.workdir / "updates" / args.stamp / "review-report.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rep.markdown(cfg, args.stamp), encoding="utf-8")
    print("\nreview report: %s" % out)
    return 1 if rep.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
