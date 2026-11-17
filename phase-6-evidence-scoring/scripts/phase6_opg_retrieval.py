#!/usr/bin/env python3
"""Phase 6, stage 5: retrieve tumor-compartment evidence for the OPG stratum.

The Phase 5 CNS pass asked whether a drug crosses the blood-brain barrier. For
optic pathway glioma - the only stratum where CNS delivery applies at all - the
operative question is different: does the drug act on an intracranial glioma,
where the barrier is disrupted and clinical response is itself evidence of
delivery. That literature was never retrieved, which is why 16 of the 18
OPG-stratum drugs carry no tumor-compartment claim of any kind.

This pass runs a query bank built for that question - optic pathway glioma,
paediatric low-grade glioma, pilocytic astrocytoma, intracranial response - over
the same 18 moieties, and applies the Phase 5 discipline unchanged: every
sentence keeps a drug_named_in_sentence flag requiring the drug name or a ChEMBL
synonym IN THE SENTENCE, and access is recorded per claim as full text or
abstract only.

Claim ids are OPG-001 onward so they never collide with the CNS-nnn ids.

Writes data/phase6-opg-literature-claims.csv and -provenance.json.
"""
from __future__ import annotations

import json
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "phase-6-evidence-scoring" / "data"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
RETMAX = 25

QUERIES = [
    '("{d}") AND ("optic pathway glioma" OR "optic glioma" OR "optic nerve glioma")',
    '("{d}") AND ("low-grade glioma" OR "pilocytic astrocytoma" OR "low grade glioma") AND (child* OR p*ediatric)',
    '("{d}") AND ("neurofibromatosis type 1" OR NF1) AND (glioma OR "brain tumor" OR "brain tumour")',
    '("{d}") AND (intracranial OR "central nervous system") AND (response OR "response rate" OR efficacy OR "progression-free")',
]
# A sentence is kept only if it could bear on whether the drug acts in, or reaches,
# an intracranial tumor. Exposure words are kept alongside response words because
# a CSF or tumour-tissue measurement in this literature is equally relevant.
RELEVANT = re.compile(
    r"\b(respon\w+|partial response|complete response|objective response|progression[- ]free|PFS|"
    r"tumou?r (volume|shrink\w+|regression|reduction)|radiographic|intracranial|"
    r"penetrat\w+|CSF|cerebrospinal|brain[- ]to[- ]plasma|exposure|concentration)\b",
    re.I,
)


def _text(el) -> str:
    return " ".join(t.strip() for t in el.itertext() if t and t.strip())


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 40]


def esearch(session, term):
    r = session.get(EUTILS + "esearch.fcgi", params={"db": "pubmed", "term": term,
                    "retmax": RETMAX, "retmode": "json"}, timeout=60)
    r.raise_for_status()
    return r.json().get("esearchresult", {}).get("idlist", [])


def efetch_pubmed(session, pmids):
    r = session.get(EUTILS + "efetch.fcgi", params={"db": "pubmed", "id": ",".join(pmids),
                    "retmode": "xml"}, timeout=120)
    r.raise_for_status()
    return ET.fromstring(r.text)


def pmc_body(session, pmcid):
    r = session.get(EUTILS + "efetch.fcgi", params={"db": "pmc", "id": pmcid, "retmode": "xml"}, timeout=120)
    if r.status_code != 200:
        return []
    try:
        root = ET.fromstring(r.text)
    except ET.ParseError:
        return []
    body = root.find(".//body")
    if body is None:
        return []
    out = []
    for sec in body.iter("sec"):
        ti = sec.find("title")
        name = _text(ti) if ti is not None else ""
        for p in sec.findall("p"):
            out.append((name, _text(p)))
    return out


def main() -> None:
    syn = json.loads((DATA / "phase6-drug-synonyms.json").read_text())["drugs"]
    rollup = pd.read_csv(DATA / "phase6-cns-adjudication-rollup.csv")
    matches = pd.read_csv(ROOT / "phase-5-mechanistic-validation" / "data" / "phase5-drug-matches.csv.gz",
                          low_memory=False)
    matches["bbb"] = matches["bbb_required"].astype(str).str.lower().eq("true")
    opg_drugs = set(matches.loc[matches["bbb"], "drug_name"].dropna().str.upper())
    moieties = [r["moiety"] for _, r in rollup.iterrows()
                if any(v.strip().upper() in opg_drugs for v in str(r["label_variants"]).split("|"))]

    session = requests.Session()
    session.headers.update({"User-Agent": "python-requests"})

    seen_pmids, rows, per_drug = {}, [], []
    for moiety in moieties:
        names = [moiety] + [s for s in syn.get(moiety, {}).get("synonyms", [])]
        pmids = []
        for q in QUERIES:
            try:
                pmids += esearch(session, q.format(d=moiety))
            except Exception as exc:
                print(f"  ! esearch {moiety}: {type(exc).__name__}")
            time.sleep(0.34)
        pmids = list(dict.fromkeys(pmids))
        if not pmids:
            per_drug.append({"moiety": moiety, "papers_screened": 0, "claims_total": 0, "claims_attributed": 0})
            continue

        root = efetch_pubmed(session, pmids)
        time.sleep(0.34)
        n_claims = n_attr = 0
        for art in root.iter("PubmedArticle"):
            pmid = art.find(".//PMID").text
            ids = {i.get("IdType"): i.text for i in art.iter("ArticleId")}
            title_el = art.find(".//ArticleTitle")
            title = _text(title_el) if title_el is not None else ""
            journal_el = art.find(".//ISOAbbreviation")
            year_el = art.find(".//PubDate/Year")
            pub_types = sorted({_text(pt) for pt in art.iter("PublicationType")})
            abstract = " ".join(
                (f"{ab.attrib.get('Label')}: " if ab.attrib.get("Label") else "") + _text(ab)
                for ab in art.iter("AbstractText")
            )
            blocks = [("Abstract", abstract, "abstract_only")] if abstract else []
            pmcid = ids.get("pmc")
            if pmcid:
                for sec, para in pmc_body(session, pmcid):
                    blocks.append((sec or "(untitled section)", para, "full_text"))
                time.sleep(0.34)
            for section, text, access in blocks:
                for s in sentences(text):
                    if not RELEVANT.search(s):
                        continue
                    named = any(re.search(rf"\b{re.escape(n)}\b", s, re.I) for n in names)
                    n_claims += 1
                    n_attr += int(named)
                    rows.append({
                        "moiety": moiety, "pmid": pmid, "pmcid": pmcid, "doi": ids.get("doi"),
                        "journal": journal_el.text if journal_el is not None else "",
                        "pub_year": year_el.text if year_el is not None else "",
                        "pub_types": "; ".join(pub_types), "title": title,
                        "access": access, "context_section": section,
                        "sentence": s, "drug_named_in_sentence": named,
                    })
            seen_pmids[pmid] = title
        per_drug.append({"moiety": moiety, "papers_screened": len(pmids),
                         "claims_total": n_claims, "claims_attributed": n_attr})
        print(f"  {moiety}: {len(pmids)} papers, {n_claims} sentences, {n_attr} attributed")

    claims = pd.DataFrame(rows)
    if not claims.empty:
        claims = claims.sort_values(["moiety", "access", "pmid"], kind="mergesort").reset_index(drop=True)
        claims.insert(0, "claim_id", [f"OPG-{i:03d}" for i in range(1, len(claims) + 1)])
    claims.to_csv(DATA / "phase6-opg-literature-claims.csv", index=False)
    pd.DataFrame(per_drug).to_csv(DATA / "phase6-opg-by-drug.csv", index=False)

    att = claims[claims["drug_named_in_sentence"]] if not claims.empty else claims
    prov = {
        "stage": "phase6_opg_retrieval.py",
        "question": "does the drug act on, or reach, an intracranial glioma (tumor compartment)",
        "moieties": len(moieties), "queries_per_moiety": len(QUERIES), "retmax": RETMAX,
        "papers": len(seen_pmids), "sentences": int(len(claims)),
        "attributed": int(len(att)),
        "attributed_full_text": int((att["access"] == "full_text").sum()) if len(att) else 0,
        "attributed_abstract_only": int((att["access"] == "abstract_only").sum()) if len(att) else 0,
        "note": ("Attribution requires the drug name or a ChEMBL synonym in the sentence itself, as in Phase 5. "
                 "Unattributed sentences are retained but are not evidence about that drug."),
    }
    (DATA / "phase6-opg-provenance.json").write_text(json.dumps(prov, indent=2) + "\n")
    print(json.dumps(prov, indent=2))


if __name__ == "__main__":
    main()
