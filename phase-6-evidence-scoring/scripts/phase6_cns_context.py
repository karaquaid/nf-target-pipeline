#!/usr/bin/env python3
"""Phase 6, stage 1: assemble an evidence packet for each attributed CNS claim.

The Phase 5 literature pass kept only the matched sentence, which is not enough
to adjudicate: "brain penetration is limited by ABCB1-mediated efflux" reads the
same whether the paper measured it or is restating someone else who did. The
discriminator is where the sentence sits. In the imatinib/tariquidar paper
(PMID 19591692) two of the three matched sentences are in Background - prior work
being summarised - and the one that matters is in Results.

So this stage re-fetches each paper and seats every claim sentence in its source
paragraph, recording the section heading, the publication type and the
surrounding text. Nothing is judged here; stage 2 (phase6_cns_adjudicate.py)
reads these packets.

The fetched context is cached to data/phase6-cns-claim-context.json so stage 2
is reproducible without network access. Re-run this stage only to refresh it.

Sources: NCBI E-utilities - PubMed efetch for the record and abstract, PMC
efetch for the full-text body where a PMCID exists. Both are public APIs; no key
is required at this volume (50 papers).
"""
from __future__ import annotations

import difflib
import json
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "phase-6-evidence-scoring" / "data"
SHEET = DATA / "phase6-cns-adjudication-sheet.csv"
OUT = DATA / "phase6-cns-claim-context.json"

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
# Fraction of the claim sentence that must appear as one contiguous run inside a
# paragraph before we accept that paragraph as its home. The Phase 5 sentences
# carry artifacts from tag-stripping ("thedistribution", "[]" for citations), so
# exact containment fails on about a third of them; longest-common-substring at
# 0.30 seats them without seating the wrong paragraph.
MIN_MATCH_FRAC = 0.30


def _text(el) -> str:
    return " ".join(t.strip() for t in el.itertext() if t and t.strip())


def _norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(t).lower())


def efetch(session: requests.Session, db: str, ids: list[str], tries: int = 4) -> str:
    params = {"db": db, "id": ",".join(ids), "retmode": "xml"}
    for attempt in range(tries):
        try:
            r = session.get(EUTILS + "efetch.fcgi", params=params, timeout=90)
            r.raise_for_status()
            return r.text
        except Exception:
            if attempt == tries - 1:
                raise
            time.sleep(2 ** attempt)
    return ""


def pubmed_records(session: requests.Session, pmids: list[str]) -> dict:
    """Title, journal, year, publication types and abstract, per PMID.

    Publication type is a first-class signal for the adjudication: a sentence in
    a Review is restating primary work by construction.
    """
    out: dict[str, dict] = {}
    for i in range(0, len(pmids), 100):
        chunk = pmids[i : i + 100]
        root = ET.fromstring(efetch(session, "pubmed", chunk))
        for art in root.iter("PubmedArticle"):
            pmid_el = art.find(".//PMID")
            if pmid_el is None:
                continue
            pmid = pmid_el.text
            abst_parts = []
            for ab in art.iter("AbstractText"):
                label = ab.attrib.get("Label")
                body = _text(ab)
                abst_parts.append(f"{label}: {body}" if label else body)
            out[pmid] = {
                "pub_types": sorted({_text(pt) for pt in art.iter("PublicationType")}),
                "abstract": " ".join(abst_parts),
            }
        time.sleep(0.4)
    return out


def pmc_blocks(session: requests.Session, pmcid: str) -> list[dict]:
    """Section-tagged paragraphs and tables from a PMC full text."""
    root = ET.fromstring(efetch(session, "pmc", [pmcid]))
    body = root.find(".//body")
    if body is None:
        return []
    blocks: list[dict] = []
    for sec in body.iter("sec"):
        title_el = sec.find("title")
        section = _text(title_el) if title_el is not None else ""
        for p in sec.findall("p"):
            blocks.append({"section": section, "kind": "paragraph", "text": _text(p)})
    for p in body.findall("p"):
        blocks.append({"section": "", "kind": "paragraph", "text": _text(p)})
    for tw in body.iter("table-wrap"):
        blocks.append({"section": "TABLE", "kind": "table", "text": _text(tw)})
    return blocks


def locate(sentence: str, blocks: list[dict]) -> tuple[float, int | None]:
    """Seat a claim sentence in the block it came from.

    Longest contiguous normalised run rather than a similarity ratio: a sentence
    whose middle is corrupted still matches on its head or tail, while an
    unrelated paragraph of similar length does not.
    """
    ns = _norm(sentence)
    if len(ns) < 20:
        return 0.0, None
    best = (0.0, None)
    for i, b in enumerate(blocks):
        nt = _norm(b["text"])
        if not nt:
            continue
        m = difflib.SequenceMatcher(None, ns, nt, autojunk=False).find_longest_match(
            0, len(ns), 0, len(nt)
        )
        frac = m.size / len(ns)
        if frac > best[0]:
            best = (frac, i)
    return best if best[0] >= MIN_MATCH_FRAC else (best[0], None)


def main() -> None:
    sheet = pd.read_csv(SHEET)
    session = requests.Session()
    session.headers.update({"User-Agent": "python-requests"})

    pmids = sorted({str(p) for p in sheet["pmid"].dropna().unique()})
    recs = pubmed_records(session, pmids)

    pmcids = sorted({str(p) for p in sheet["pmcid"].dropna().unique()})
    bodies: dict[str, list[dict]] = {}
    for pmcid in pmcids:
        try:
            bodies[pmcid] = pmc_blocks(session, pmcid)
        except Exception as exc:  # a paper that will not parse is recorded, not dropped
            bodies[pmcid] = []
            print(f"  ! {pmcid}: {type(exc).__name__}")
        time.sleep(0.4)

    packets = {}
    for _, c in sheet.iterrows():
        pmid = str(c["pmid"])
        rec = recs.get(pmid, {})
        pmcid = None if pd.isna(c["pmcid"]) else str(c["pmcid"])
        blocks = bodies.get(pmcid or "", [])
        frac, idx = locate(c["sentence"], blocks) if blocks else (0.0, None)

        if idx is not None:
            source, section = "pmc_body", blocks[idx]["section"] or "(untitled section)"
            context, kind = blocks[idx]["text"], blocks[idx]["kind"]
        elif rec.get("abstract"):
            source, section = "pubmed_abstract", "Abstract"
            context, kind = rec["abstract"], "abstract"
        else:
            source, section, context, kind = "none", "", "", ""

        packets[c["claim_id"]] = {
            "claim_id": c["claim_id"],
            "moiety": c["moiety"],
            "pmid": pmid,
            "pmcid": pmcid,
            "access": c["access"],
            "title": c["title"],
            "journal": c["journal_abbrev"],
            "year": None if pd.isna(c["pub_year"]) else str(int(c["pub_year"])),
            "pub_types": rec.get("pub_types", []),
            "sentence": c["sentence"],
            "context_source": source,
            "context_section": section,
            "context_kind": kind,
            "context_text": context,
            "match_frac": round(float(frac), 3),
        }

    OUT.write_text(json.dumps(packets, indent=1) + "\n")

    seated = sum(1 for p in packets.values() if p["context_source"] == "pmc_body")
    abst = sum(1 for p in packets.values() if p["context_source"] == "pubmed_abstract")
    print(
        json.dumps(
            {
                "claims": len(packets),
                "papers": len(pmids),
                "pmc_bodies_fetched": sum(1 for b in bodies.values() if b),
                "seated_in_pmc_paragraph": seated,
                "fell_back_to_abstract": abst,
                "no_context": len(packets) - seated - abst,
                "sections": pd.Series(
                    [p["context_section"] for p in packets.values()]
                ).value_counts().head(12).to_dict(),
                "review_articles": sum(
                    1 for p in packets.values() if "Review" in p["pub_types"]
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
