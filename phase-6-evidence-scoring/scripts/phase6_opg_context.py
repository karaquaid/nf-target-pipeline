#!/usr/bin/env python3
"""Phase 6, stage 5b: context packets for the OPG claims.

Reuses phase6_cns_context's fetching and sentence-seating rather than
reimplementing them, so OPG claims arrive at the adjudicator in exactly the
shape CNS claims do: section heading, publication type, containing paragraph.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import pandas as pd, requests

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "phase-6-evidence-scoring" / "data"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import phase6_cns_context as ctx


def main() -> None:
    claims = pd.read_csv(DATA / "phase6-opg-literature-claims.csv")
    att = claims[claims["drug_named_in_sentence"] == True].copy()  # noqa: E712
    session = requests.Session(); session.headers.update({"User-Agent": "python-requests"})

    pmids = sorted({str(p) for p in att["pmid"].dropna().unique()})
    recs = ctx.pubmed_records(session, pmids)
    pmcids = sorted({str(p) for p in att["pmcid"].dropna().unique()})
    bodies = {}
    for pmcid in pmcids:
        try:
            bodies[pmcid] = ctx.pmc_blocks(session, pmcid)
        except Exception as exc:
            bodies[pmcid] = []
            print(f"  ! {pmcid}: {type(exc).__name__}")
        time.sleep(0.34)

    packets, seated, abst = {}, 0, 0
    for _, c in att.iterrows():
        pmid = str(c["pmid"]); rec = recs.get(pmid, {})
        pmcid = None if pd.isna(c["pmcid"]) else str(c["pmcid"])
        blocks = bodies.get(pmcid or "", [])
        frac, idx = ctx.locate(c["sentence"], blocks) if blocks else (0.0, None)
        if idx is not None:
            source, section = "pmc_body", blocks[idx]["section"] or "(untitled section)"
            text, kind = blocks[idx]["text"], blocks[idx]["kind"]; seated += 1
        elif rec.get("abstract"):
            source, section, text, kind = "pubmed_abstract", "Abstract", rec["abstract"], "abstract"; abst += 1
        else:
            source, section, text, kind = "none", "", c["sentence"], ""
        packets[c["claim_id"]] = {
            "claim_id": c["claim_id"], "moiety": c["moiety"], "pmid": pmid, "pmcid": pmcid,
            "access": c["access"], "title": c["title"], "journal": c["journal"],
            "year": None if pd.isna(c["pub_year"]) else str(c["pub_year"]),
            "pub_types": rec.get("pub_types", []), "sentence": c["sentence"],
            "context_source": source, "context_section": section, "context_kind": kind,
            "context_text": text, "match_frac": round(float(frac), 3),
        }
    (DATA / "phase6-opg-claim-context.json").write_text(json.dumps(packets, indent=1) + "\n")
    print(json.dumps({"claims": len(packets), "papers": len(pmids), "seated_in_paragraph": seated,
                      "fell_back_to_abstract": abst,
                      "no_context": len(packets) - seated - abst}, indent=2))


if __name__ == "__main__":
    main()
