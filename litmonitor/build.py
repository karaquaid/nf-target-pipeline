#!/usr/bin/env python3
"""Build a verification-graded target map from scratch. The first-run counterpart to monitor.py.

    python litmonitor/build.py --config litmonitor/configs/nf.toml

This is the work the NF project calls Phase 1b: sweep a fixed query bank, extract target
claims from every abstract, aggregate claims across papers into one row per target, disease
and manifestation, retrieve full text wherever a free route reaches it, judge every claim
against the complete article body, grade each row by how deeply it was checked, and derive a
candidate list under the config's scope rules.

Differences from monitor.py, which exists for the incremental case:
- no date floor by default, so the sweep is the whole literature the queries reach
- claims are AGGREGATED across papers, so a row carries every paper that supports it and a
  count of how many were verified, rather than one row per paper
- it emits the derived products a first build needs: a coverage matrix, a reference table, a
  retrieval queue of papers nobody could read, and optional per-label annotations

Writes only under the config's workdir. Running it twice overwrites that study's tables, which
is why it refuses a workdir that already holds tables unless --overwrite is given.
"""

import argparse
import datetime as dt
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfgmod  # noqa: E402
import llm  # noqa: E402
import monitor as mon  # noqa: E402

TIER_BY_VERDICT = {"supported": "full text - supported",
                   "partially_supported": "full text - partial",
                   "not_supported": "full text - not supported"}

ANNOTATION_SYSTEM = ("You annotate molecular targets for a disease target-discovery pipeline. "
                     "You output JSON only. You distinguish a target that can be drugged from a "
                     "readout that merely reports disease state.")


def annotation_prompt(labels_with_context):
    body = "\n".join("- %s | manifestations: %s | mechanisms: %s" % (lab, m, x)
                     for lab, m, x in labels_with_context)
    return """For each target below, set three flags. Judge from the mechanism text given plus what is known of the target's pharmacology.

- likely_biomarker: true if this reads as a readout of disease state rather than something to drug. Tumour-suppressor losses belong here: the lesion is an absence, with nothing to inhibit.
- mutation_restricted: true if the target is only relevant in a defined genotype. Name it in mutation_context.
- tme_target: true if the target acts in the tumour microenvironment (immune, vascular, stromal) rather than in the tumour cell.

A flag is a property of the target, not of one manifestation. Where a target is both, pick the call its evidence here is dominated by and say so in the note.

Return JSON: {{"annotations":[{{"label":"","likely_biomarker":false,"mutation_restricted":false,"mutation_context":"","tme_target":false,"note":""}}]}}

TARGETS:
{body}""".format(body=body)


def sweep(cfg, since, log):
    """Run every query, recording per-query yield so the method section can report it."""
    hits, per_query = set(), []
    for q in cfg.queries:
        ids = set(mon.esearch(q["query"], since))
        per_query.append({"disease": q["disease"], "manifestation": q.get("manifestation", ""),
                          "query": q["query"], "hits": len(ids)})
        hits |= ids
        time.sleep(0.34)
    log["per_query"] = per_query
    return sorted(hits)


def extract_claims(cfg, pmids, meta, abstracts, model, usages):
    """One extraction pass per abstract. Returns claim records, one per gene and manifestation."""
    claims = []
    for pmid in pmids:
        abstract = abstracts.get(pmid, "")
        if not abstract:
            continue
        out = llm.complete_json(mon.extract_prompt(cfg, meta.get(pmid, {}).get("title", ""), abstract),
                                system=mon.EXTRACT_SYSTEM, model=model, max_tokens=2000,
                                salvage_key="gene")
        usages.append(out["usage"])
        data = out["data"] or {}
        for t in (data.get("targets") or data.get("salvaged") or []):
            gene = (t.get("gene") or "").strip()
            disease = (t.get("disease") or "").strip()
            if not gene or disease not in cfg.diseases:
                continue
            for m in (t.get("manifestations") or ["Other"]):
                claims.append({"pmid": pmid, "gene_target": gene, "disease": disease,
                               "manifestation": m if m in cfg.manifestations else "Other",
                               "mechanism": (t.get("mechanism") or "").strip(),
                               "study_system": (t.get("evidence") or "").strip()})
    return claims


def verify(cfg, claims, meta, model, usages):
    """Retrieve each paper's body once and judge all of that paper's claims against it."""
    by_paper = defaultdict(list)
    for c in claims:
        by_paper[c["pmid"]].append((c["gene_target"], c["disease"], c["manifestation"]))
    verdicts, access, routes = {}, {}, {}
    for i, (pmid, paper_claims) in enumerate(sorted(by_paper.items()), 1):
        rec = mon.epmc_record(pmid)
        meta.setdefault(pmid, {})
        meta[pmid]["pmcid"] = rec.get("pmcid")
        meta[pmid]["doi"] = meta[pmid].get("doi") or rec.get("doi")
        meta[pmid]["journal"] = meta[pmid].get("journal") or rec.get("journal")
        got = mon.fetch_fulltext(rec["pmcid"]) if rec.get("pmcid") else {"text": None, "route": None}
        access[pmid] = "full_text" if got["text"] else "abstract_only"
        routes[pmid] = got["route"]
        if not got["text"]:
            continue
        unique = sorted(set(paper_claims))
        out = llm.complete_json(mon.verdict_prompt(cfg, unique, got["text"]), system=mon.VERDICT_SYSTEM,
                               model=model, max_tokens=3000, salvage_key="gene_target")
        usages.append(out["usage"])
        for j in ((out["data"] or {}).get("judgements") or (out["data"] or {}).get("salvaged") or []):
            gene, manif = j.get("gene_target"), j.get("manifestation")
            match = [c for c in unique if c[0] == gene and c[2] == manif] or \
                    [c for c in unique if c[0] == gene]
            if match:
                verdicts[(match[0][0], match[0][1], match[0][2], pmid)] = j
        if i % 10 == 0:
            print("  verified %d/%d papers" % (i, len(by_paper)))
    return verdicts, access, routes


def aggregate(cfg, claims, verdicts, access, meta, stamp):
    """One row per target, disease and manifestation, carrying every paper that supports it."""
    rows = {}
    for c in claims:
        key = (c["gene_target"], c["disease"], c["manifestation"])
        r = rows.setdefault(key, {"pmids": set(), "mech_abstract": [], "mech_fulltext": [],
                                  "systems": set(), "verdicts": []})
        r["pmids"].add(c["pmid"])
        if c["mechanism"]:
            r["mech_abstract"].append(c["mechanism"])
        if c["study_system"]:
            r["systems"].add(c["study_system"])
    for (gene, disease, manif, pmid), j in verdicts.items():
        r = rows.get((gene, disease, manif))
        if r is None:
            continue
        r["verdicts"].append(j.get("verdict"))
        if j.get("mechanism_from_fulltext"):
            r["mech_fulltext"].append(j["mechanism_from_fulltext"])
        if j.get("study_system"):
            r["systems"].add(j["study_system"])

    out = []
    for (gene, disease, manif), r in rows.items():
        pmids = sorted(r["pmids"])
        n_sup = r["verdicts"].count("supported")
        n_part = r["verdicts"].count("partially_supported")
        n_not = r["verdicts"].count("not_supported")
        if n_sup:
            tier = "full text - supported"
        elif n_part:
            tier = "full text - partial"
        elif n_not:
            tier = "full text - not supported"
        else:
            tier = "abstract only"
        preprints = [p for p in pmids if mon.is_preprint(meta.get(p, {}).get("doi"),
                                                         meta.get(p, {}).get("journal"))]
        mech = (max(r["mech_fulltext"], key=len) if r["mech_fulltext"]
                else max(r["mech_abstract"], key=len) if r["mech_abstract"] else "")
        out.append({
            "gene_target": gene, "disease": disease, "manifestation": manif,
            "n_supporting_papers": len(pmids),
            "n_fulltext_supported": n_sup, "n_fulltext_partial": n_part,
            "n_fulltext_not_supported": n_not,
            "n_papers_fulltext_read": sum(1 for p in pmids if access.get(p) == "full_text"),
            "n_papers_abstract_only": sum(1 for p in pmids if access.get(p) != "full_text"),
            "n_preprint_papers": len(preprints), "preprint_only": bool(preprints) and len(preprints) == len(pmids),
            "evidence_tier": tier, "mechanism": mech,
            "mechanism_source": ("full text" if r["mech_fulltext"] else
                                 "abstract" if r["mech_abstract"] else "none"),
            "study_system": ";".join(sorted(s for s in r["systems"] if s)),
            "supporting_pmids": ";".join(pmids),
            "paper_access": ";".join("%s:%s" % (p, access.get(p, "abstract_only")) for p in pmids),
            "excluded_label": gene in cfg.exclude_labels,
            "excluded_reason": cfg.exclude_labels_reason if gene in cfg.exclude_labels else "",
            "first_seen": stamp, "in_baseline": True})
    df = pd.DataFrame(out)
    return df.sort_values(["n_fulltext_supported", "n_supporting_papers", "gene_target"],
                          ascending=[False, False, True]).reset_index(drop=True)


def derive_candidates(cfg, targets):
    """Scope filters from the config. Excluded rows stay in the audit table with their flag."""
    excluded = targets.gene_target.isin(cfg.exclude_labels)
    keep = ~excluded & ~targets.evidence_tier.isin(cfg.excluded_tiers)
    return targets[keep].drop(columns=["excluded_label", "excluded_reason"]).reset_index(drop=True)


def coverage(cfg, candidates):
    cov = (candidates.pivot_table(index="manifestation", columns="disease", values="gene_target",
                                  aggfunc="count", fill_value=0)
           .reindex(cfg.manifestations).fillna(0).astype(int))
    for d in cfg.diseases:
        if d not in cov.columns:
            cov[d] = 0
    cov = cov[cfg.diseases]
    cov["total"] = cov.sum(axis=1)
    return cov


def references(targets, meta, access, routes, stamp):
    pmids = sorted({p for s in targets.supporting_pmids for p in str(s).split(";") if p})
    rows = []
    for p in pmids:
        m = meta.get(p, {})
        supports = targets[targets.supporting_pmids.str.contains(p, regex=False)]
        rows.append({"pmid": p, "first_author": m.get("first_author"), "year": m.get("year"),
                     "journal": m.get("journal"), "title": m.get("title"), "doi": m.get("doi"),
                     "pmc": m.get("pmcid"), "access_used": access.get(p, "abstract_only"),
                     "retrieval_route": routes.get(p) or "", "is_preprint": mon.is_preprint(m.get("doi"), m.get("journal")),
                     "rows_supported": len(supports),
                     "labels_supported": ";".join(sorted(set(supports.gene_target))),
                     "first_seen": stamp, "in_baseline": True})
    return pd.DataFrame(rows)


def retrieval_queue(targets, refs):
    """Papers nobody could read, ranked by how many unverified rows a copy would anchor."""
    unread = refs[refs.access_used != "full_text"]
    rows = []
    for r in unread.itertuples():
        sub = targets[targets.supporting_pmids.str.contains(r.pmid, regex=False)]
        anchorable = sub[sub.evidence_tier == "abstract only"]
        if anchorable.empty:
            continue
        rows.append({"pmid": r.pmid, "first_author": r.first_author, "year": r.year,
                     "journal": r.journal, "title": r.title, "doi": r.doi,
                     "unanchored_rows": len(anchorable),
                     "sole_support_rows": int((anchorable.n_supporting_papers == 1).sum()),
                     "manifestations": ";".join(sorted(set(anchorable.manifestation)))})
    q = pd.DataFrame(rows)
    if q.empty:
        return q
    q = q.sort_values(["unanchored_rows", "sole_support_rows"], ascending=False).reset_index(drop=True)
    q.insert(0, "rank", range(1, len(q) + 1))
    return q


def annotate(cfg, candidates, model, usages, batch=25):
    """Per-label flags. Curated judgement, not extracted evidence, and labelled as such."""
    labels = []
    for lab, grp in candidates.groupby("gene_target"):
        labels.append((lab, "; ".join(sorted(set(grp.manifestation))[:4]),
                       " | ".join(m for m in grp.mechanism.dropna().unique()[:3] if m)[:400]))
    out = []
    for i in range(0, len(labels), batch):
        res = llm.complete_json(annotation_prompt(labels[i:i + batch]), system=ANNOTATION_SYSTEM,
                                model=model, max_tokens=4000, salvage_key="label")
        usages.append(res["usage"])
        for a in ((res["data"] or {}).get("annotations") or (res["data"] or {}).get("salvaged") or []):
            out.append({"gene_target": a.get("label"),
                        "likely_biomarker": bool(a.get("likely_biomarker")),
                        "mutation_restricted": bool(a.get("mutation_restricted")),
                        "mutation_context": a.get("mutation_context", ""),
                        "tme_target": bool(a.get("tme_target")),
                        "annotation_note": a.get("note", ""), "annotation_source": "model"})
    ann = pd.DataFrame(out).drop_duplicates("gene_target")
    missing = sorted(set(candidates.gene_target) - set(ann.gene_target))
    for lab in missing:
        ann.loc[len(ann)] = {"gene_target": lab, "likely_biomarker": False,
                             "mutation_restricted": False, "mutation_context": "",
                             "tme_target": False, "annotation_note": "not annotated",
                             "annotation_source": "unannotated"}
    return ann


def run(args):
    cfg = cfgmod.load(args.config)
    data = cfg.workdir / "data"
    existing = sorted(data.glob("*.csv")) if data.exists() else []
    if existing and not args.overwrite:
        raise SystemExit("%s already holds %d tables; pass --overwrite to rebuild, or use "
                         "monitor.py for an incremental update" % (data, len(existing)))
    data.mkdir(parents=True, exist_ok=True)
    stamp = args.stamp or dt.date.today().strftime("%Y-%m")
    log = {"study": cfg.study, "stamp": stamp, "config": str(cfg.path), "mode": "build",
           "since": args.since or "unbounded", "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}

    pmids = sweep(cfg, args.since or "1800/01/01", log)
    log["screened"] = len(pmids)
    print("study %s | %d queries | %d unique records" % (cfg.study, len(cfg.queries), len(pmids)))
    if args.limit:
        pmids = pmids[: args.limit]
    if args.dry_run:
        log["dry_run"] = True
        json.dump(log, open(data / "run.json", "w"), indent=1)
        print("dry run: search only, no model calls. Per-query yield in %s" % (data / "run.json"))
        return 0

    meta, abstracts = {}, {}
    for i in range(0, len(pmids), 100):
        chunk = pmids[i:i + 100]
        meta.update(mon.esummary(chunk))
        abstracts.update(mon.efetch_abstract(chunk))
        time.sleep(0.34)
    log["with_abstract"] = sum(1 for p in pmids if abstracts.get(p))

    model = llm.resolve_model()
    usages = []
    claims = extract_claims(cfg, pmids, meta, abstracts, model, usages)
    log["claims"] = len(claims)
    log["papers_with_claims"] = len({c["pmid"] for c in claims})
    print("claims: %d from %d papers" % (len(claims), log["papers_with_claims"]))
    if not claims:
        json.dump(log, open(data / "run.json", "w"), indent=1)
        print("no claims extracted; nothing to build")
        return 0

    verdicts, access, routes = verify(cfg, claims, meta, model, usages)
    log["papers_fulltext_read"] = sum(1 for v in access.values() if v == "full_text")
    log["verdict_pairs"] = len(verdicts)

    targets = aggregate(cfg, claims, verdicts, access, meta, stamp)
    candidates = derive_candidates(cfg, targets)
    refs = references(targets, meta, access, routes, stamp)
    cov = coverage(cfg, candidates)
    queue = retrieval_queue(targets, refs)

    targets.to_csv(data / "targets.csv", index=False)
    candidates.to_csv(data / "candidates.csv", index=False)
    refs.to_csv(data / "references.csv", index=False)
    cov.to_csv(data / "coverage.csv")
    if not queue.empty:
        queue.to_csv(data / "retrieval-queue.csv", index=False)
    if args.annotate:
        annotate(cfg, candidates, model, usages).to_csv(data / "annotations.csv", index=False)

    log.update({"rows": len(targets), "candidate_rows": len(candidates),
                "labels": int(candidates.gene_target.nunique()), "papers": len(refs),
                "tiers": targets.evidence_tier.value_counts().to_dict(),
                "queue_rows": int(len(queue)), "annotated": bool(args.annotate),
                "model": model, "tokens": llm.cost_note(usages)})
    json.dump(log, open(data / "run.json", "w"), indent=1)
    print("rows %d | candidates %d over %d labels | papers %d (%d read in full)"
          % (len(targets), len(candidates), candidates.gene_target.nunique(), len(refs),
             log["papers_fulltext_read"]))
    print("wrote %s" % data)
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True, type=Path)
    p.add_argument("--since", help="optional entry-date floor, YYYY-MM-DD. Omit for the whole literature")
    p.add_argument("--stamp", help="build label, defaults to this month")
    p.add_argument("--limit", type=int, help="cap papers processed, for a smoke test")
    p.add_argument("--annotate", action="store_true", help="also assign per-label curated flags")
    p.add_argument("--dry-run", action="store_true", help="search only, no model calls")
    p.add_argument("--overwrite", action="store_true", help="rebuild over existing tables")
    args = p.parse_args()
    if args.since:
        args.since = args.since.replace("-", "/")
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
