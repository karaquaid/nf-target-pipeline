#!/usr/bin/env python3
"""Offline self-test: runs the whole build on stub sources, with no network and no API key.

    python litmonitor/selftest.py

Proves the install works and the pipeline is wired correctly: search, extraction, aggregation
across papers, full-text verdicts, tier assignment, scope exclusion, coverage, the retrieval
queue, the write-up and the figure. It does NOT test the live sources or the model prompts;
use --dry-run on a real config for the first and a --limit run for the second.
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402
import config as cfgmod  # noqa: E402
import llm  # noqa: E402
import monitor as mon  # noqa: E402
import report  # noqa: E402

CONFIG = """
[study]
name = "selftest"
description = "Offline fixture study."
[labels]
diseases = ["DIS1", "DIS2"]
manifestations = ["Manifestation A", "Manifestation B", "Other"]
[extraction]
entity = "gene presented as a target"
[scope]
exclude_labels = ["EXCLUDED1"]
exclude_labels_reason = "germline disease gene"
excluded_tiers = ["full text - not supported"]
[paths]
workdir = "WORKDIR"
frozen = []
[[queries]]
disease = "DIS1"
manifestation = "Manifestation A"
query = "fixture query one"
[[queries]]
disease = "DIS2"
manifestation = "Manifestation B"
query = "fixture query two"
"""

# Four papers. P1 and P2 both support GENE1 in DIS1/Manifestation A, so the row must aggregate
# to two papers. P3 supports an excluded label. P4 has no retrievable body, so its row must stay
# at "abstract only" and must appear in the retrieval queue.
PAPERS = {
    "1": {"title": "GENE1 drives disease", "abstract": "GENE1 is a target in DIS1.",
          "doi": "10.1000/a", "pmcid": "PMC1", "body": True,
          "claims": [("GENE1", "DIS1", "Manifestation A", "kinase signalling")],
          "verdict": "supported"},
    "2": {"title": "GENE1 again, plus GENE2", "abstract": "GENE1 and GENE2 in DIS1.",
          "doi": "10.1000/b", "pmcid": "PMC2", "body": True,
          "claims": [("GENE1", "DIS1", "Manifestation A", "confirms kinase signalling"),
                     ("GENE2", "DIS1", "Other", "transcriptional")],
          "verdict": "partially_supported"},
    "3": {"title": "EXCLUDED1 germline", "abstract": "EXCLUDED1 causes DIS2.",
          "doi": "10.1000/c", "pmcid": "PMC3", "body": True,
          "claims": [("EXCLUDED1", "DIS2", "Manifestation B", "loss of function")],
          "verdict": "supported"},
    "4": {"title": "GENE3 unread", "abstract": "GENE3 may matter in DIS2.",
          "doi": "10.1101/d", "pmcid": None, "body": False,
          "claims": [("GENE3", "DIS2", "Manifestation B", "speculative")],
          "verdict": None},
}


def install_stubs():
    mon.esearch = lambda term, mindate, retmax=200: list(PAPERS)
    mon.esummary = lambda pmids: {
        p: {"pmid": p, "title": PAPERS[p]["title"], "journal": "Fixture J", "year": "2026",
            "doi": PAPERS[p]["doi"], "first_author": "Author"} for p in pmids}
    mon.efetch_abstract = lambda pmids: {p: PAPERS[p]["abstract"] for p in pmids}
    mon.epmc_record = lambda pmid: {"pmcid": PAPERS[pmid]["pmcid"], "doi": PAPERS[pmid]["doi"],
                                    "journal": "Fixture J"}
    # The body carries its own pmid, so the stub judge cannot be handed the wrong paper. The
    # first version of this fixture matched papers by claim text and silently judged paper 2
    # with paper 1's verdict, which looked like an aggregation bug in build.py and was not.
    def stub_fulltext(pmcid, min_sections=3):
        if not pmcid:
            return {"text": None, "route": None}
        pmid = next(p for p in PAPERS if PAPERS[p]["pmcid"] == pmcid)
        return {"text": "<sec>fixture body PMIDTOKEN:%s</sec>" % pmid, "route": "europepmc"}

    mon.fetch_fulltext = stub_fulltext
    llm.resolve_model = lambda preference=None, env_var="x": "fixture-model"

    def fake(prompt, system=None, model=None, max_tokens=2000, salvage_key=None, **kw):
        usage = {"input_tokens": 10, "output_tokens": 5}
        if prompt.startswith("Abstract below"):
            pmid = next(p for p in PAPERS if PAPERS[p]["title"] in prompt)
            targets = [{"gene": g, "disease": d, "manifestations": [m], "role": "therapeutic target",
                        "mechanism": mech, "evidence": "cell line"}
                       for g, d, m, mech in PAPERS[pmid]["claims"]]
            return {"data": {"targets": targets}, "usage": usage}
        if prompt.startswith("Article full text"):
            token = prompt.split("PMIDTOKEN:")[1].split("<")[0] if "PMIDTOKEN:" in prompt else None
            pmid = token if token in PAPERS else None
            if pmid is None:
                return {"data": {"judgements": []}, "usage": usage}
            js = [{"gene_target": g, "manifestation": m, "verdict": PAPERS[pmid]["verdict"],
                   "mechanism_from_fulltext": "body: " + mech,
                   "manifestation_in_fulltext": m, "study_system": "mouse model"}
                  for g, d, m, mech in PAPERS[pmid]["claims"]]
            return {"data": {"judgements": js}, "usage": usage}
        return {"data": {"annotations": []}, "usage": usage}

    llm.complete_json = fake
    build.llm = llm
    build.mon = mon
    report_module = report


def main():
    tmp = Path(tempfile.mkdtemp(prefix="litmonitor-selftest-"))
    cfg_path = tmp / "selftest.toml"
    cfg_path.write_text(CONFIG.replace("WORKDIR", str(tmp / "work")))
    install_stubs()
    args = type("A", (), {"config": cfg_path, "since": None, "stamp": "test", "limit": None,
                          "annotate": False, "dry_run": False, "overwrite": True})()
    rc = build.run(args)
    assert rc == 0, "build returned %s" % rc

    cfg = cfgmod.load(cfg_path)
    data = cfg.workdir / "data"
    t = pd.read_csv(data / "targets.csv")
    c = pd.read_csv(data / "candidates.csv")
    r = pd.read_csv(data / "references.csv", dtype={"pmid": str})
    cov = pd.read_csv(data / "coverage.csv", index_col=0)
    q = pd.read_csv(data / "retrieval-queue.csv")
    checks = []

    def check(name, got, want):
        checks.append((name, got, want, got == want))

    g1 = t[(t.gene_target == "GENE1") & (t.manifestation == "Manifestation A")].iloc[0]
    check("GENE1 aggregates two papers", int(g1.n_supporting_papers), 2)
    check("GENE1 supported by one full text", int(g1.n_fulltext_supported), 1)
    check("GENE1 partial from the other", int(g1.n_fulltext_partial), 1)
    check("GENE1 tier is the best verdict", g1.evidence_tier, "full text - supported")
    check("GENE1 mechanism comes from the body", str(g1.mechanism).startswith("body:"), True)
    check("GENE1 mechanism_source", g1.mechanism_source, "full text")
    g3 = t[t.gene_target == "GENE3"].iloc[0]
    check("unread paper stays abstract only", g3.evidence_tier, "abstract only")
    check("preprint-only row flagged", bool(g3.preprint_only), True)
    check("excluded label present in audit table", int((t.gene_target == "EXCLUDED1").sum()), 1)
    check("excluded label absent from candidates", int((c.gene_target == "EXCLUDED1").sum()), 0)
    check("candidate rows", len(c), len(t) - 1)
    check("coverage total equals candidate rows", int(cov.total.sum()), len(c))
    check("references cover every paper", len(r), 4)
    check("retrieval queue holds the unread paper", list(q.pmid.astype(str)), ["4"])
    check("queue counts its unanchored row", int(q.unanchored_rows.iloc[0]), 1)
    check("run log written", (data / "run.json").exists(), True)

    text = report.build(cfg, report.stats(cfg))
    (cfg.workdir / "docs").mkdir(parents=True, exist_ok=True)
    (cfg.workdir / "docs" / "selftest-target-map.md").write_text(text)
    check("write-up has no em dash", "\u2014" in text, False)
    check("write-up states the row count", "%d rows over" % len(c) in text, True)

    import figure
    fig_counts, present = figure.counts(cfg, c)
    check("figure plots every candidate row", int(fig_counts.to_numpy().sum()), len(c))
    fig = figure.make_figure(cfg, fig_counts, present, len(c))
    out = cfg.workdir / "docs" / "figures" / "selftest-coverage.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100, bbox_inches="tight")
    check("figure written", out.exists() and out.stat().st_size > 5000, True)

    width = max(len(n) for n, *_ in checks)
    for name, got, want, ok in checks:
        print("%-5s %-*s got %r" % ("pass" if ok else "FAIL", width, name, got)
              + ("" if ok else " want %r" % (want,)))
    failed = [n for n, _, _, ok in checks if not ok]
    print("\n%d checks, %d failed" % (len(checks), len(failed)))
    if not failed:
        shutil.rmtree(tmp, ignore_errors=True)
    else:
        print("artifacts left in %s" % tmp)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
