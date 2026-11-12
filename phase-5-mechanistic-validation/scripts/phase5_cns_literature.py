#!/usr/bin/env python3
"""Retrieve CNS-penetration literature claims for the drug shortlist.

Why this script exists. The committed corpus (phase5-cns-literature-*.csv/json)
was first produced by ad-hoc calls to the PubMed MCP connector from an
interactive cell. Connector calls are not available to a committed script, so
the corpus had no reproducible code behind it and could not be re-run with a
wider query bank. This script reimplements the same protocol against NCBI
E-utilities, which any script can call, so the corpus is regenerable.

Protocol, unchanged from the original pass:
  * the shortlist's drug labels are normalised to active moieties by stripping
    salt suffixes - selumetinib and selumetinib sulfate are one drug, and
    querying both splits the evidence across two rows
  * two queries per moiety (QUERIES below), relevance-sorted, 12 results each
  * PubMed record and abstract via efetch; PMC body via efetch where a PMCID
    exists, capped at --full-text-budget papers per moiety
  * a sentence is kept when it carries BOTH a CNS term and a distribution cue;
    a CNS term alone matches adverse-event prose
  * each claim records its access level (full_text or abstract_only) so
    abstract-only evidence stays weaker by construction, and a
    drug_named_in_sentence flag, because only 27 percent of matched sentences
    name the drug they were retrieved for - a paper retrieved for one drug
    routinely discusses others

What the script does NOT do: adjudicate. `direction` is a keyword split kept
only as a sorting aid, and it is demonstrably unreliable - a paper reporting a
5-fold brain-to-plasma increase in P-gp knockout mice, i.e. efflux-LIMITED
penetration, lands in `supporting`. The finding needs a human or a reasoning
stage, reading the sentence in context.

Reliability. Every non-200 that is not an empty result set is recorded as a
FAILURE and never collapsed into "no evidence": the original pass lost two
drugs to a batch failure and reported them as zero-evidence until retried.
Responses are cached under --builddir so a re-run costs no requests.

Usage (from the repository root):
  python phase-5-mechanistic-validation/scripts/phase5_cns_literature.py \
      --builddir build/phase5 --datadir phase-5-mechanistic-validation/data
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import requests

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
IDCONV = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
TOOL = "nf-target-pipeline"

QUERIES = [
    '{d} AND (blood-brain barrier OR cerebrospinal fluid OR brain penetration OR CNS penetration)',
    '{d} AND ("brain-to-plasma" OR "brain to plasma" OR Kpuu OR "unbound brain" OR "CSF concentration")',
]
SALTS = r"\s+(MESYLATE|SULFATE|HYDROCHLORIDE|TOSYLATE|MALATE|FUMARATE|ANHYDROUS|DIMETHYL SULFOXIDE)$"

CNS = re.compile(r"(blood[\s-]?brain barrier|cerebrospinal fluid|\bCSF\b|brain[\s-]?to[\s-]?plasma|"
                 r"brain penetrat\w+|CNS penetrat\w+|intracranial|unbound brain|\bKp,?uu\b|"
                 r"brain exposure)", re.I)
CUE = re.compile(r"(penetrat\w+|distribut\w+|cross\w*|concentrations?|ratio|exposure|partition\w*|"
                 r"efflux|P-?gp|permeab\w+|accumulat\w+)", re.I)
LIMITING = re.compile(r"(?:does not|do not|poorly|limited|minimal|negligible|low(?:er)?|restricted|"
                      r"not detect\w*|undetectable|impaired|insufficient|inadequate)[^.]{0,120}"
                      r"(?:blood[\s-]?brain|CNS|brain|cerebrospinal|CSF)", re.I)

# Brand names and development codes, so attribution does not miss a sentence
# that names the drug only by its code (DAY101, AZD6244, GSK1120212 ...).
SYNONYMS = {
    "AVAPRITINIB": ["avapritinib", "BLU-285", "ayvakit"],
    "BINIMETINIB": ["binimetinib", "MEK162", "ARRY-162", "mektovi"],
    "COBIMETINIB": ["cobimetinib", "GDC-0973", "XL518", "cotellic"],
    "DABRAFENIB": ["dabrafenib", "GSK2118436", "tafinlar"],
    "DASATINIB": ["dasatinib", "BMS-354825", "sprycel"],
    "ENCORAFENIB": ["encorafenib", "LGX818", "braftovi"],
    "IMATINIB": ["imatinib", "STI571", "STI-571", "gleevec", "glivec"],
    "MIDOSTAURIN": ["midostaurin", "PKC412", "rydapt"],
    "PAZOPANIB": ["pazopanib", "GW786034", "votrient"],
    "PEXIDARTINIB": ["pexidartinib", "PLX3397", "turalio"],
    "QUIZARTINIB": ["quizartinib", "AC220", "vanflyta"],
    "REGORAFENIB": ["regorafenib", "BAY 73-4506", "stivarga"],
    "RIPRETINIB": ["ripretinib", "DCC-2618", "qinlock"],
    "SELUMETINIB": ["selumetinib", "AZD6244", "AZD 6244", "ARRY-142886", "koselugo"],
    "SORAFENIB": ["sorafenib", "BAY 43-9006", "nexavar"],
    "SUNITINIB": ["sunitinib", "SU11248", "sutent"],
    "TIVOZANIB": ["tivozanib", "AV-951", "KRN-951", "fotivda"],
    "TOVORAFENIB": ["tovorafenib", "DAY101", "DAY 101", "TAK-580", "MLN2480", "ojemda"],
    "TRAMETINIB": ["trametinib", "GSK1120212", "mekinist"],
    "VEMURAFENIB": ["vemurafenib", "PLX4032", "RG7204", "zelboraf"],
}

FAILURES: list[dict] = []


def _params(extra: dict, email: str | None, api_key: str | None) -> dict:
    p = {"tool": TOOL, **extra}
    if email:
        p["email"] = email
    if api_key:
        p["api_key"] = api_key
    return p


def _get(session: requests.Session, url: str, params: dict, what: str, tries: int = 4):
    last = None
    for attempt in range(tries):
        try:
            r = session.get(url, params=params, timeout=90)
            if r.status_code == 200:
                return r
            last = f"HTTP {r.status_code}"
        except requests.RequestException as exc:
            last = type(exc).__name__
        time.sleep(1.5 * (attempt + 1))
    FAILURES.append({"what": what, "error": last})
    return None


def esearch(session, query, retmax, email, key) -> list[str]:
    r = _get(session, f"{EUTILS}/esearch.fcgi",
             _params({"db": "pubmed", "term": query, "retmax": retmax,
                      "sort": "relevance", "retmode": "json"}, email, key),
             f"esearch {query[:60]}")
    if r is None:
        return []
    return (r.json().get("esearchresult", {}) or {}).get("idlist", []) or []


def _text(node) -> str:
    return " ".join(t.strip() for t in node.itertext() if t and t.strip())


def efetch_pubmed(session, pmids, email, key) -> dict[str, dict]:
    if not pmids:
        return {}
    r = _get(session, f"{EUTILS}/efetch.fcgi",
             _params({"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}, email, key),
             f"efetch pubmed {len(pmids)} ids")
    if r is None:
        return {}
    out = {}
    for art in ET.fromstring(r.content).iter("PubmedArticle"):
        pmid_el = art.find(".//PMID")
        if pmid_el is None:
            continue
        pmid = pmid_el.text
        doi = next((i.text for i in art.iter("ArticleId") if i.get("IdType") == "doi"), None)
        abst = " ".join(_text(a) for a in art.iter("AbstractText"))
        jt = art.find(".//Journal/ISOAbbreviation") or art.find(".//Journal/Title")
        yr = art.find(".//JournalIssue/PubDate/Year") or art.find(".//JournalIssue/PubDate/MedlineDate")
        ttl = art.find(".//ArticleTitle")
        out[pmid] = {"pmid": pmid, "doi": doi, "abstract": abst,
                     "journal": jt.text if jt is not None else None,
                     "publication_date": yr.text if yr is not None else None,
                     "title": _text(ttl) if ttl is not None else None}
    return out


def pmcids(session, pmids, email, key) -> dict[str, str | None]:
    if not pmids:
        return {}
    r = _get(session, IDCONV,
             _params({"ids": ",".join(pmids), "format": "json", "versions": "no"}, email, key),
             f"idconv {len(pmids)} ids")
    if r is None:
        return {p: None for p in pmids}
    # the ID converter returns pmid as a JSON integer; without str() every
    # lookup by string PMID misses and no full text is ever fetched
    return {str(rec.get("pmid")): rec.get("pmcid") for rec in (r.json().get("records") or [])}


def efetch_pmc(session, pmcid, email, key) -> str | None:
    r = _get(session, f"{EUTILS}/efetch.fcgi",
             _params({"db": "pmc", "id": pmcid.replace("PMC", ""), "retmode": "xml"}, email, key),
             f"efetch pmc {pmcid}")
    if r is None:
        return None
    try:
        root = ET.fromstring(r.content)
    except ET.ParseError:
        FAILURES.append({"what": f"parse pmc {pmcid}", "error": "ParseError"})
        return None
    body = root.find(".//body")
    return _text(body) if body is not None else None


def sentences(text: str | None) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.;])\s+", text or "") if s.strip()]


def extract(text: str | None, access: str) -> list[dict]:
    return [{"access": access, "sentence": s[:700], "has_number": bool(re.search(r"\d", s)),
             "direction": "limiting" if LIMITING.search(s) else "supporting"}
            for s in sentences(text) if CNS.search(s) and CUE.search(s)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--builddir", default="build/phase5")
    ap.add_argument("--datadir", default="phase-5-mechanistic-validation/data")
    ap.add_argument("--retmax", type=int, default=12)
    ap.add_argument("--full-text-budget", type=int, default=5)
    ap.add_argument("--email", default=os.environ.get("NCBI_CONTACT_EMAIL"),
                    help="contact address for E-utilities; omitted when absent")
    args = ap.parse_args()
    build, data = Path(args.builddir), Path(args.datadir)
    build.mkdir(parents=True, exist_ok=True)
    data.mkdir(parents=True, exist_ok=True)
    key = os.environ.get("NCBI_API_KEY")
    pause = 0.12 if key else 0.36          # NCBI allows 10/s with a key, 3/s without

    shortlist = pd.read_csv(data / "phase5-supported-target-drugs.csv")
    moieties: dict[str, list[str]] = {}
    for label in sorted({str(x).upper().strip() for x in shortlist.drug_name.dropna()}):
        moieties.setdefault(re.sub(SALTS, "", label).strip(), []).append(label)

    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    cache_path = build / "phase5-cns-literature-cache.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    rows, per_drug = [], []
    for n, (moiety, variants) in enumerate(sorted(moieties.items()), 1):
        if moiety in cache:
            packet = cache[moiety]
        else:
            pmids: list[str] = []
            for q in QUERIES:
                pmids += esearch(session, q.format(d=moiety), args.retmax, args.email, key)
                time.sleep(pause)
            pmids = list(dict.fromkeys(pmids))
            meta = {}
            for i in range(0, len(pmids), 4):      # small batches: large ones failed in the first pass
                meta.update(efetch_pubmed(session, pmids[i:i + 4], args.email, key))
                time.sleep(pause)
            ids = pmcids(session, pmids, args.email, key)
            time.sleep(pause)
            budget, arts = args.full_text_budget, []
            for pmid in pmids:
                m = meta.get(pmid)
                if not m:
                    continue
                pmcid = ids.get(pmid)
                full = None
                if pmcid and budget > 0:
                    full = efetch_pmc(session, pmcid, args.email, key)
                    budget -= 1
                    time.sleep(pause)
                arts.append({**m, "pmcid": pmcid, "full_text_retrieved": bool(full),
                             "hits": extract(m.get("abstract"), "abstract_only")
                                     + extract(full, "full_text")})
            packet = {"moiety": moiety, "variants": variants, "pmids": pmids, "articles": arts}
            cache[moiety] = packet
            cache_path.write_text(json.dumps(cache))
        for a in packet["articles"]:
            for h in a["hits"]:
                pat = "|".join(re.escape(s) for s in SYNONYMS.get(moiety, [moiety.lower()]))
                rows.append({"moiety": moiety, "label_variants": "|".join(packet["variants"]),
                             "pmid": a["pmid"], "pmcid": a["pmcid"], "doi": a["doi"],
                             "journal": a["journal"], "publication_date": a["publication_date"],
                             "title": a["title"], "access": h["access"],
                             "direction": h["direction"], "has_number": h["has_number"],
                             "sentence": h["sentence"],
                             "drug_named_in_sentence": bool(re.search(pat, h["sentence"], re.I))})
        print(f"{n}/{len(moieties)} {moiety}: papers={len(packet['articles'])} "
              f"full_text={sum(1 for a in packet['articles'] if a['full_text_retrieved'])} "
              f"claims={sum(len(a['hits']) for a in packet['articles'])}", flush=True)

    claims = (pd.DataFrame(rows)
              .drop_duplicates(subset=["moiety", "pmid", "sentence"])
              .sort_values(["moiety", "access", "direction", "pmid"]))
    claims.to_csv(data / "phase5-cns-literature-claims.csv", index=False)

    att = claims[claims.drug_named_in_sentence]
    by = []
    for moiety, packet in sorted(cache.items()):
        sub, a_ = claims[claims.moiety == moiety], att[att.moiety == moiety]
        by.append({"moiety": moiety, "label_variants": "|".join(packet["variants"]),
                   "papers_screened": len(packet["articles"]),
                   "papers_with_full_text": sum(1 for a in packet["articles"] if a["full_text_retrieved"]),
                   "claims_total": len(sub), "claims_attributed": len(a_),
                   "attributed_full_text": int((a_.access == "full_text").sum()),
                   "attributed_abstract_only": int((a_.access == "abstract_only").sum()),
                   "attributed_with_a_number": int(a_.has_number.sum()),
                   "evidence_access": ("full_text" if (a_.access == "full_text").any()
                                       else "abstract_only" if len(a_) else "none")})
    by_df = pd.DataFrame(by).sort_values(["evidence_access", "moiety"])
    by_df.to_csv(data / "phase5-cns-literature-by-drug.csv", index=False)

    json.dump({
        "source": "PubMed and PubMed Central via NCBI E-utilities",
        "generated_by": "phase-5-mechanistic-validation/scripts/phase5_cns_literature.py",
        "query_bank": [q.format(d="<MOIETY>") for q in QUERIES],
        "scope": f"{len(moieties)} active moieties normalised from the shortlist drug labels "
                 "(salt forms collapsed)",
        "retmax_per_query": args.retmax, "full_text_budget_per_moiety": args.full_text_budget,
        "contact_email_sent": bool(args.email), "api_key_used": bool(key),
        "moieties": len(moieties),
        "papers_screened": int(by_df.papers_screened.sum()),
        "papers_with_full_text": int(by_df.papers_with_full_text.sum()),
        "claims": int(len(claims)),
        "claims_full_text": int((claims.access == "full_text").sum()),
        "claims_abstract_only": int((claims.access == "abstract_only").sum()),
        "claims_with_a_number": int(claims.has_number.sum()),
        "claims_attributed_to_the_drug": int(len(att)),
        "attribution_rule": "the drug name, brand name or development code must appear in the "
                            "sentence itself; unattributed sentences are retained but flagged, "
                            "because a paper retrieved for one drug routinely discusses others",
        "moieties_with_an_attributed_claim": int(att.moiety.nunique()),
        "moieties_with_no_claim": by_df[by_df.claims_total == 0].moiety.tolist(),
        "failed_requests": len(FAILURES), "failures": FAILURES,
        "caveat": "sentences are regex-selected and NOT adjudicated; `direction` is a keyword split "
                  "and is unreliable (a 5-fold brain-to-plasma increase in P-gp knockout mice, i.e. "
                  "efflux-limited penetration, lands in `supporting`). Every claim carries its PMID, "
                  "DOI and access level so the finding can be read in context.",
    }, open(data / "phase5-cns-literature-provenance.json", "w"), indent=2)

    print(f"\npapers {int(by_df.papers_screened.sum())} | full text "
          f"{int(by_df.papers_with_full_text.sum())} | claims {len(claims)} "
          f"(full_text {int((claims.access == 'full_text').sum())}, "
          f"abstract_only {int((claims.access == 'abstract_only').sum())}) | "
          f"attributed {len(att)} | failures {len(FAILURES)}")


if __name__ == "__main__":
    main()
