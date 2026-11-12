#!/usr/bin/env python3
"""Write up a built target map. Every current-state number is computed from the tables.

    python litmonitor/report.py --config mystudy.toml

Counts that describe the DATA are recomputed here, so the prose cannot drift from the tables.
Counts that describe the PROCESS and no longer exist in any table come from run.json, which
build.py writes. Nothing is hardcoded; if a number is not derivable, the sentence is not written.
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfgmod  # noqa: E402

TIER_ORDER = ["full text - supported", "full text - partial", "full text - not supported",
              "abstract only"]


def stats(cfg):
    data = cfg.workdir / "data"
    t = pd.read_csv(data / "targets.csv")
    c = pd.read_csv(data / "candidates.csv")
    r = pd.read_csv(data / "references.csv", dtype={"pmid": str})
    cov = pd.read_csv(data / "coverage.csv", index_col=0)
    log = json.load(open(data / "run.json")) if (data / "run.json").exists() else {}
    q = pd.read_csv(data / "retrieval-queue.csv") if (data / "retrieval-queue.csv").exists() else None
    ann = pd.read_csv(data / "annotations.csv") if (data / "annotations.csv").exists() else None
    tiers = {k: int(v) for k, v in c.evidence_tier.value_counts().items()}
    s = {
        "study": cfg.study, "description": cfg.description, "rows": len(t), "candidates": len(c),
        "labels": int(c.gene_target.nunique()), "papers": len(r),
        "read_full": int((r.access_used == "full_text").sum()),
        "tiers": tiers, "anchored": len(c) - tiers.get("abstract only", 0),
        "by_disease": {d: int((c.disease == d).sum()) for d in cfg.diseases},
        "excluded_rows": len(t) - len(c),
        "excluded_labels": sorted(set(t[t.excluded_label.astype(bool)].gene_target))
        if "excluded_label" in t.columns else [],
        "single_paper": int((c.n_supporting_papers == 1).sum()),
        "preprint_only": int(c.preprint_only.astype(bool).sum()) if "preprint_only" in c.columns else 0,
        "other_share": round(100 * (c.manifestation == "Other").mean(), 1) if len(c) else 0.0,
        "mechanism_none": int((c.mechanism_source == "none").sum()) if "mechanism_source" in c.columns else None,
        "queries": len(cfg.queries), "log": log, "cov": cov,
        "thin": {m: int(cov.loc[m, "total"]) for m in cov.index if 0 < cov.loc[m, "total"] < 10},
        "empty": [m for m in cov.index if cov.loc[m, "total"] == 0],
        "queue": None if q is None or q.empty else {"papers": len(q),
                                                    "rows": int(q.unanchored_rows.sum()),
                                                    "top": q.head(10).to_dict("records")},
        "annotations": None if ann is None else {
            "labels": len(ann),
            "biomarker": int(ann.likely_biomarker.sum()),
            "mutation_restricted": int(ann.mutation_restricted.sum()),
            "tme": int(ann.tme_target.sum()),
            "unflagged": int((~ann.likely_biomarker & ~ann.mutation_restricted & ~ann.tme_target).sum())},
    }
    return s


def build(cfg, s):
    log = s["log"]
    cov = s["cov"]
    cov_rows = "\n".join("| %s | %s | %d |" % (m, " | ".join(str(int(cov.loc[m, d])) for d in cfg.diseases),
                                               int(cov.loc[m, "total"]))
                         for m in cov.index)
    tier_rows = "\n".join("| %s | %d |" % (t, s["tiers"][t]) for t in TIER_ORDER if s["tiers"].get(t))
    parts = ["# %s: literature target map" % s["study"],
             "",
             s["description"] or "",
             "",
             "## What this is",
             "",
             "A map of molecular targets named in the literature of this disease, with every claim "
             "graded by how deeply it was checked. The distinction the map exists to preserve is "
             "between a claim somebody verified against a complete article and a claim nobody has "
             "checked. Both are kept; they are never pooled.",
             "",
             "## Method",
             "",
             "%d queries were run against PubMed%s. Abstracts of the returned records were read for "
             "target claims, each claim was attributed to a disease and one or more manifestations "
             "from a fixed vocabulary, and claims were aggregated across papers into one row per "
             "target, disease and manifestation." % (
                 s["queries"], "" if log.get("since") in (None, "unbounded")
                 else " with an entry-date floor of %s" % log["since"]),
             "",
             "Full text was then retrieved for every paper supporting a claim, by two free routes in "
             "order: the Europe PMC full-text service, then NCBI efetch against PubMed Central. Open "
             "access status does not predict which route works, which is why both are tried: a paper "
             "closed at the publisher often has a free author manuscript that only the second route "
             "serves. Where a body was retrieved, every claim from that paper was judged against the "
             "complete article rather than its abstract, and a result cited from another paper was "
             "not counted as this paper's support.",
             ""]
    if log.get("screened"):
        parts += ["The sweep screened %d unique records, of which %d named at least one target. "
                  "Full text was reached for %d of %d contributing papers." % (
                      log["screened"], log.get("papers_with_claims", 0),
                      log.get("papers_fulltext_read", s["read_full"]), s["papers"]), ""]
    parts += ["## The list", "",
              "**%d rows over %d target labels, from %d papers.** %d of %d candidate rows rest on at "
              "least one paper read in full; %d rest on an abstract alone." % (
                  s["candidates"], s["labels"], s["papers"], s["anchored"], s["candidates"],
                  s["tiers"].get("abstract only", 0)),
              "",
              "| Evidence tier | Rows |", "|---|---|", tier_rows, "",
              "By disease: " + ", ".join("%s %d" % (d, n) for d, n in s["by_disease"].items()) + ".", ""]
    if s["excluded_rows"]:
        parts += ["%d rows are held out of the candidate list as %s (%s). They stay in the audit "
                  "table with a flag, so the exclusion is reversible rather than a deletion." % (
                      s["excluded_rows"], cfg.exclude_labels_reason,
                      ", ".join(s["excluded_labels"][:8])), ""]
    parts += ["## Coverage", "",
              "| Manifestation | %s | Total |" % " | ".join(cfg.diseases),
              "|---|%s|---|" % ("---|" * len(cfg.diseases)), cov_rows, ""]
    if s["thin"] or s["empty"]:
        thin_txt = ", ".join("%s (%d)" % (m, n) for m, n in sorted(s["thin"].items(), key=lambda x: x[1]))
        parts += ["Coverage is uneven, and the thin cells are the point of the table rather than a "
                  "defect in it. " + (("Under ten rows: %s. " % thin_txt) if s["thin"] else "")
                  + (("No rows at all: %s. " % ", ".join(s["empty"])) if s["empty"] else "")
                  + "A manifestation with few rows has a small literature, not a solved biology.", ""]
    if s["queue"]:
        parts += ["## What nobody could read", "",
                  "%d papers could not be retrieved by either free route. Between them they are the "
                  "sole evidence behind %d rows that currently rest on an abstract. "
                  "`retrieval-queue.csv` ranks them by how many such rows a copy would move, so a "
                  "person with library access can work down it in priority order." % (
                      s["queue"]["papers"], s["queue"]["rows"]), ""]
    parts += ["## Limitations", "",
              "- %d candidate rows rest on a single paper. One paper is a claim, not a finding." % s["single_paper"],
              "- %d rows have never been checked against full text. They are visible in the tier "
              "column rather than mixed in." % s["tiers"].get("abstract only", 0)]
    if s["preprint_only"]:
        parts += ["- %d rows rest only on preprints, which have not been peer reviewed." % s["preprint_only"]]
    if s["mechanism_none"]:
        parts += ["- %d rows carry no mechanism text. `mechanism_source` records whether the "
                  "mechanism came from full text, an abstract, or nowhere, rather than mixing them "
                  "in one unmarked column." % s["mechanism_none"]]
    parts += ["- %.1f per cent of rows fall in the catch-all Other manifestation. A large share "
              "there means the vocabulary does not fit this literature and should be revisited "
              "against a standard the field already uses." % s["other_share"],
              "- Verdicts come from a single reader. `review.py` re-judges a sample to measure "
              "whether they are reproducible, which is not the same as correct.",
              ""]
    if s["annotations"]:
        a = s["annotations"]
        parts += ["## Target annotations", "",
                  "Three flags travel with each label, to stop a ranking treating unlike things "
                  "alike: %d of %d labels read as likely biomarkers rather than drug targets, %d are "
                  "restricted to a genotype, and %d act in the tumour microenvironment rather than "
                  "the tumour cell. %d carry none of the three. These are curated judgement, not "
                  "extracted evidence, and tractability data from a target database supersedes them "
                  "where they disagree." % (a["biomarker"], a["labels"], a["mutation_restricted"],
                                            a["tme"], a["unflagged"]), ""]
    parts += ["## Outputs", "",
              "| File | Contents |", "|---|---|",
              "| `data/targets.csv` | Every row, including those held out of the candidate list |",
              "| `data/candidates.csv` | The prioritisation input: audit table minus the scope exclusions |",
              "| `data/references.csv` | One row per paper: access route, preprint status, what it supports |",
              "| `data/coverage.csv` | The coverage matrix above |"]
    if s["queue"]:
        parts += ["| `data/retrieval-queue.csv` | Unreadable papers, ranked by rows a copy would anchor |"]
    if s["annotations"]:
        parts += ["| `data/annotations.csv` | Per-label flags, one row per label |"]
    parts += ["| `data/run.json` | Build log: per-query yield, token counts, model used |", ""]
    return "\n".join(parts)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True, type=Path)
    p.add_argument("--out", type=Path, help="defaults to <workdir>/docs/<study>-target-map.md")
    p.add_argument("--allow-em-dash", action="store_true",
                   help="by default an em dash in generated prose is an error, matching this project's style")
    args = p.parse_args()
    cfg = cfgmod.load(args.config)
    s = stats(cfg)
    text = build(cfg, s)
    if "\u2014" in text and not args.allow_em_dash:
        raise AssertionError("em dash in generated text")
    out = args.out or (cfg.workdir / "docs" / ("%s-target-map.md" % cfg.study))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print("wrote %s (%d chars) from %d rows" % (out, len(text), s["candidates"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
