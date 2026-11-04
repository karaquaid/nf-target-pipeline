#!/usr/bin/env python3
"""Literature target monitor. One disease per config; nothing disease-specific in the code.

    python litmonitor/monitor.py --config litmonitor/configs/nf.toml --since 2026-10-01

Re-runs the config's query bank with a date floor, drops PMIDs already in the corpus,
extracts target claims from the new abstracts, retrieves full text where any free route
reaches it, judges every claim against the complete article body, and merges into the
running tables without downgrading a row that is already verified.

Cold start (no `paths.baseline` in the config) builds the tables from scratch, so a group
with no existing corpus can run this on their own disease from an empty directory.

Writes only under `paths.workdir`. Directories listed in `paths.frozen` are never touched;
review.py checks that against git rather than taking it on trust.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfgmod  # noqa: E402
import llm  # noqa: E402

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
TOOL = "litmonitor"
BASELINE_TAG = "baseline"
PREPRINT_PREFIXES = ("10.1101", "10.21203", "10.20944", "10.31219", "10.64898", "10.26434", "10.48550")
ROW_KEY = ["gene_target", "disease", "manifestation"]

EXTRACT_SYSTEM = ("You extract target claims from biomedical abstracts for a disease "
                  "target-discovery pipeline. You output JSON only. You never infer facts that are "
                  "not stated or directly implied by the text provided. If the abstract does not "
                  "name a specific molecular target, you return an empty list.")
VERDICT_SYSTEM = ("You verify target claims against the complete body of a research article. You "
                  "output JSON only. You never credit a claim the article does not itself "
                  "demonstrate or explicitly assert.")


def _get(url, timeout=45):
    return urllib.request.urlopen(url, timeout=timeout).read().decode("utf-8", "replace")


def _contact():
    email = os.environ.get("LITMONITOR_CONTACT_EMAIL")
    return {"email": email} if email else {}


def esearch(term, mindate, retmax=200):
    p = {"db": "pubmed", "term": term, "retmax": retmax, "retmode": "json", "datetype": "edat",
         "mindate": mindate, "maxdate": "3000/12/31", "tool": TOOL}
    p.update(_contact())
    return json.loads(_get(EUTILS + "/esearch.fcgi?" + urllib.parse.urlencode(p)))["esearchresult"].get("idlist", [])


def esummary(pmids):
    p = {"db": "pubmed", "id": ",".join(pmids), "retmode": "json", "tool": TOOL}
    p.update(_contact())
    d = json.loads(_get(EUTILS + "/esummary.fcgi?" + urllib.parse.urlencode(p)))
    out = {}
    for pid, rec in d.get("result", {}).items():
        if pid == "uids":
            continue
        doi = next((a["value"] for a in rec.get("articleids", []) if a.get("idtype") == "doi"), None)
        out[pid] = {"pmid": pid, "title": rec.get("title", ""), "journal": rec.get("fulljournalname"),
                    "year": (rec.get("pubdate") or "")[:4], "doi": doi,
                    "first_author": (rec.get("sortfirstauthor") or "").split(" ")[0]}
    return out


def efetch_abstract(pmids):
    p = {"db": "pubmed", "id": ",".join(pmids), "rettype": "abstract", "retmode": "xml", "tool": TOOL}
    p.update(_contact())
    xml = _get(EUTILS + "/efetch.fcgi?" + urllib.parse.urlencode(p))
    out = {}
    for art in re.findall(r"<PubmedArticle>.*?</PubmedArticle>", xml, re.S):
        pid = re.search(r"<PMID[^>]*>(\d+)</PMID>", art)
        if pid:
            txt = " ".join(re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", art, re.S))
            out[pid.group(1)] = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", txt)).strip()
    return out


def epmc_record(pmid):
    url = EPMC + "/search?" + urllib.parse.urlencode(
        {"query": "EXT_ID:%s" % pmid, "resultType": "core", "format": "json"})
    try:
        hits = json.loads(_get(url))["resultList"]["result"]
    except Exception:
        return {}
    if not hits:
        return {}
    r = hits[0]
    return {"pmcid": r.get("pmcid"), "doi": r.get("doi"), "is_open_access": r.get("isOpenAccess"),
            "author_manuscript": r.get("authMan"),
            "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title")}


def fetch_fulltext(pmcid, min_sections=3):
    """Europe PMC, then NCBI efetch. Open-access status does not predict which route works:
    a paper closed at the publisher often has a free author manuscript that only efetch serves."""
    pid = str(pmcid)
    for route, url in (("europepmc", "%s/%s/fullTextXML" % (EPMC, pid)),
                       ("efetch", "%s/efetch.fcgi?db=pmc&rettype=xml&id=%s" % (EUTILS, pid.replace("PMC", "")))):
        try:
            body = _get(url)
        except Exception:
            time.sleep(0.3)
            continue
        if body.count("<sec") >= min_sections and len(body) > 8000:
            return {"text": re.sub(r"<back>.*?</back>", "", body, flags=re.S), "route": route}
    return {"text": None, "route": None}


def is_preprint(doi=None, journal=None):
    d = (doi or "").strip().lower()
    if any(d.startswith(p + "/") for p in PREPRINT_PREFIXES):
        return True
    return bool(re.search(r"rxiv|research square|res sq|preprint", (journal or "").lower()))


def extract_prompt(cfg, title, abstract):
    return """Abstract below. Extract every {entity}.

Rules:
- Use the official human HGNC gene symbol where one exists. For a family or complex with no single symbol, use the common name.
- Do NOT extract: {exclude}.
- disease: exactly one of {diseases}, or "Not specified".
- manifestations: from this fixed list, verbatim, one or more: {manif}
- role: one of {roles}.
- mechanism: <= 25 words, stated in the abstract.
- evidence: one of {systems}.

Return JSON: {{"targets":[{{"gene":"","disease":"","manifestations":[],"role":"","mechanism":"","evidence":""}}]}}
Empty list if nothing qualifies.

TITLE: {title}
ABSTRACT: {abstract}""".format(
        entity=cfg.entity, exclude=cfg.exclude_guidance or "assay reagents or background citations",
        diseases=", ".join('"%s"' % d for d in cfg.diseases), manif="; ".join(cfg.manifestations),
        roles=", ".join('"%s"' % r for r in cfg.roles),
        systems=", ".join('"%s"' % s for s in cfg.systems),
        title=title, abstract=(abstract or "")[:6000])


def verdict_prompt(cfg, claims, body):
    listed = "\n".join("- %s | %s | %s" % c for c in claims)
    return """Article full text (JATS XML, references removed) follows. Judge each claim against the WHOLE article, not its abstract.

Claims, as target | disease | manifestation:
{claims}

For each claim return one object:
- verdict: "supported" if this article presents the target as a driver, modifier or therapeutic target for that disease and manifestation; "partially_supported" if it supports the target but for a different manifestation or disease, or only indirectly; "not_supported" otherwise.
- mechanism_from_fulltext: <= 25 words as the body states it, else "".
- manifestation_in_fulltext: what the body studies, verbatim from: {manif}
- study_system: one of {systems}.

A cited result from another paper is not this paper's support.

Return JSON: {{"judgements":[{{"gene_target":"","manifestation":"","verdict":"","mechanism_from_fulltext":"","manifestation_in_fulltext":"","study_system":""}}]}}

FULL TEXT:
{body}""".format(claims=listed, manif="; ".join(cfg.manifestations),
                 systems=", ".join('"%s"' % s for s in cfg.systems), body=(body or "")[:260000])


TARGET_COLUMNS = ROW_KEY + ["n_supporting_papers", "evidence_tier", "mechanism", "study_system",
                            "supporting_pmids", "paper_access", "excluded_label",
                            "first_seen", "in_baseline"]
REF_COLUMNS = ["pmid", "first_author", "year", "journal", "title", "doi", "pmc", "access_used",
               "is_preprint", "first_seen", "in_baseline"]


def bootstrap(cfg):
    """Create the running tables: copy a baseline if the config names one, else start empty."""
    data = cfg.workdir / "data"
    data.mkdir(parents=True, exist_ok=True)
    if cfg.baseline:
        for src in sorted(Path(cfg.baseline).glob("*.csv")):
            df = pd.read_csv(src)
            if {"gene_target", "pmid"} & set(df.columns):
                df["first_seen"] = BASELINE_TAG
                df["in_baseline"] = True
            df.to_csv(data / src.name, index=False)
        return "copied %d tables from %s" % (len(list(Path(cfg.baseline).glob('*.csv'))), cfg.baseline)
    pd.DataFrame(columns=TARGET_COLUMNS).to_csv(data / "targets.csv", index=False)
    pd.DataFrame(columns=REF_COLUMNS).to_csv(data / "references.csv", index=False)
    return "cold start: empty tables created in %s" % data


def table_paths(cfg):
    """The running tables, whatever they are called. A baselined study keeps the baseline's
    filenames so the committed scripts keep working; a cold start uses neutral ones."""
    data = cfg.workdir / "data"
    targets = next((p for p in (data / "targets.csv",
                                data / "phase1b-literature-targets.csv") if p.exists()), None)
    refs = next((p for p in (data / "references.csv",
                             data / "phase1b-references.csv") if p.exists()), None)
    if not targets or not refs:
        raise SystemExit("no running tables in %s; run once to bootstrap" % data)
    return targets, refs


def run(args):
    cfg = cfgmod.load(args.config)
    created = bootstrap(cfg) if not (cfg.workdir / "data").exists() else ""
    tpath, rpath = table_paths(cfg)
    targets = pd.read_csv(tpath)
    refs = pd.read_csv(rpath, dtype={"pmid": str})
    stamp = args.stamp or dt.date.today().strftime("%Y-%m")
    outdir = cfg.workdir / "updates" / stamp
    outdir.mkdir(parents=True, exist_ok=True)
    print("study %s | %s | tables %s" % (cfg.study, created or "existing tables", tpath.name))

    known = set(refs.pmid.astype(str)) if len(refs) else set()
    found = set()
    for q in cfg.queries:
        found |= set(esearch(q["query"], args.since))
        time.sleep(0.34)
    new = sorted(found - known)
    print("queries %d | hits %d | new %d" % (len(cfg.queries), len(found), len(new)))
    if args.limit:
        new = new[: args.limit]
    run_log = {"study": cfg.study, "stamp": stamp, "since": args.since, "config": str(cfg.path),
               "screened": len(found), "new": len(new), "bootstrap": created}
    if args.dry_run:
        run_log["dry_run"] = True
        json.dump(run_log, open(outdir / "run.json", "w"), indent=1)
        print("dry run: search only, no model calls")
        return 0
    if not new:
        json.dump(run_log, open(outdir / "run.json", "w"), indent=1)
        print("no new papers; run recorded")
        return 0

    meta, abstracts = {}, {}
    for i in range(0, len(new), 100):
        batch = new[i:i + 100]
        meta.update(esummary(batch))
        abstracts.update(efetch_abstract(batch))
        time.sleep(0.34)

    model = llm.resolve_model()
    usages, rows = [], []
    for pmid in new:
        abstract = abstracts.get(pmid, "")
        if not abstract:
            continue
        out = llm.complete_json(extract_prompt(cfg, meta.get(pmid, {}).get("title", ""), abstract),
                                system=EXTRACT_SYSTEM, model=model, max_tokens=2000, salvage_key="gene")
        usages.append(out["usage"])
        data = out["data"] or {}
        for t in (data.get("targets") or data.get("salvaged") or []):
            gene = (t.get("gene") or "").strip()
            disease = (t.get("disease") or "Not specified").strip()
            if not gene or disease not in cfg.diseases:
                continue
            for m in (t.get("manifestations") or ["Other"]):
                rows.append({"pmid": pmid, "gene_target": gene, "disease": disease,
                             "manifestation": m if m in cfg.manifestations else "Other",
                             "mechanism": t.get("mechanism", ""), "study_system": t.get("evidence", "")})
    print("claims extracted: %d from %d papers" % (len(rows), len({r['pmid'] for r in rows})))

    by_paper = {}
    for r in rows:
        by_paper.setdefault(r["pmid"], []).append(tuple(r[k] for k in ROW_KEY))
    verdicts, access = [], {}
    for pmid, claims in by_paper.items():
        rec = epmc_record(pmid)
        meta.setdefault(pmid, {})
        meta[pmid]["pmcid"] = rec.get("pmcid")
        meta[pmid]["doi"] = meta[pmid].get("doi") or rec.get("doi")
        meta[pmid]["journal"] = meta[pmid].get("journal") or rec.get("journal")
        body = fetch_fulltext(rec["pmcid"])["text"] if rec.get("pmcid") else None
        access[pmid] = "full_text" if body else "abstract_only"
        if not body:
            continue
        out = llm.complete_json(verdict_prompt(cfg, claims, body), system=VERDICT_SYSTEM,
                                model=model, max_tokens=3000, salvage_key="gene_target")
        usages.append(out["usage"])
        for j in ((out["data"] or {}).get("judgements") or (out["data"] or {}).get("salvaged") or []):
            j["pmid"] = pmid
            verdicts.append(j)
    print("papers with full text: %d/%d | verdicts: %d"
          % (sum(v == "full_text" for v in access.values()), len(by_paper), len(verdicts)))

    tier_map = {"supported": "full text - supported", "partially_supported": "full text - partial",
                "not_supported": "full text - not supported"}
    best = {}
    for j in verdicts:
        tier = tier_map.get(j.get("verdict"))
        if not tier:
            continue
        k = (j.get("gene_target"), j.get("pmid"))
        if cfg.tier_rank[tier] > cfg.tier_rank.get(best.get(k, "abstract only"), 0):
            best[k] = tier

    added = []
    for r in rows:
        added.append({**r, "evidence_tier": best.get((r["gene_target"], r["pmid"]), "abstract only"),
                      "n_supporting_papers": 1, "supporting_pmids": r["pmid"],
                      "paper_access": "%s:%s" % (r["pmid"], access.get(r["pmid"], "abstract_only")),
                      "excluded_label": r["gene_target"] in cfg.exclude_labels,
                      "first_seen": stamp, "in_baseline": False})
    pd.DataFrame(added).to_csv(outdir / "new-rows.csv", index=False)

    newrefs = [{"pmid": p, "first_author": meta.get(p, {}).get("first_author"),
                "year": meta.get(p, {}).get("year"), "journal": meta.get(p, {}).get("journal"),
                "title": meta.get(p, {}).get("title"), "doi": meta.get(p, {}).get("doi"),
                "pmc": meta.get(p, {}).get("pmcid"), "access_used": access.get(p, "abstract_only"),
                "is_preprint": is_preprint(meta.get(p, {}).get("doi"), meta.get(p, {}).get("journal")),
                "first_seen": stamp, "in_baseline": False}
               for p in sorted({r["pmid"] for r in added})]
    pd.DataFrame(newrefs).to_csv(outdir / "new-papers.csv", index=False)

    if args.merge:
        merged = pd.concat([targets, pd.DataFrame(added)], ignore_index=True)
        merged.to_csv(tpath, index=False)
        pd.concat([refs, pd.DataFrame(newrefs)], ignore_index=True).to_csv(rpath, index=False)
        print("merged into %s and %s" % (tpath.name, rpath.name))
    else:
        print("deltas written; rerun with --merge to apply them to the running tables")

    run_log.update({"claims": len(added), "verdicts": len(verdicts), "model": model,
                    "fulltext_papers": sum(v == "full_text" for v in access.values()),
                    "merged": bool(args.merge), "tokens": llm.cost_note(usages)})
    json.dump(run_log, open(outdir / "run.json", "w"), indent=1)
    print("wrote %s" % outdir)
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True, type=Path)
    p.add_argument("--since", required=True, help="PubMed entry-date floor, YYYY-MM-DD")
    p.add_argument("--stamp", help="run label, defaults to this month")
    p.add_argument("--limit", type=int, help="cap papers processed, for a smoke test")
    p.add_argument("--merge", action="store_true", help="apply the deltas to the running tables")
    p.add_argument("--dry-run", action="store_true", help="search and dedupe only, no model calls")
    args = p.parse_args()
    args.since = args.since.replace("-", "/")
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
