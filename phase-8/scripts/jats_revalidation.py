#!/usr/bin/env python3
"""Re-measure Phase 7's verification sample through the Europe PMC JATS path.

Phase 7 measured the PubMed connector's PMC extraction deleting italicised gene
symbols from article bodies, and showed the damage degrades judgement: claims
whose own label was missing from the retrieved body disagreed with themselves
23.1% of the time against 8.6% where the label was present. Kara ruled that
verification reads Europe PMC JATS instead.

This script tests whether that ruling actually fixes the problem, on the same
155 claims over 59 papers, by asking one question per claim: does the claim's
own gene symbol appear in the retrieved body?

It does NOT re-run any verdict. Re-reading the claims would conflate the
retrieval change with reader noise, which Phase 7 measured separately at 12.3%
on the three-way verdict and 3.9% on supported-or-not.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "lib"))
from europepmc_client import get_fulltext  # noqa: E402


def tokens(raw: str) -> list:
    return [t.strip() for t in str(raw).split(";") if t.strip()]


def present(toks: list, text: str, lax: bool = False) -> bool:
    """Phase 7's rule, copied verbatim so the comparison is like for like.

    Case-INSENSITIVE word-boundary match; `lax` also accepts the digit-stripped
    base (YAP1 -> YAP). An earlier draft of this script used a case-sensitive
    match and a body that excluded the abstract, and reported the JATS route as
    WORSE than the connector (46 label-absent against 39). That was an artifact
    of changing the measurement, not a regression in the route.
    """
    low = text.lower()
    for t in toks:
        variants = {t}
        if lax:
            s = re.sub(r"\d+$", "", t)
            if len(s) >= 3:
                variants.add(s)
        for v in variants:
            if re.search(r"\b%s\b" % re.escape(v.lower()), low):
                return True
    return False


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sample", default="phase-7/data/phase7-verification-stability.csv")
    ap.add_argument("--out", default="phase-8/data/phase8-jats-revalidation.csv")
    ap.add_argument("--summary", default="phase-8/data/phase8-jats-revalidation-summary.json")
    args = ap.parse_args()

    S = pd.read_csv(args.sample)
    S = S[S.body_retrieved.astype(str).str.lower() == "true"].copy()

    bodies, rows = {}, []
    for pmid, pmcid in S[["pmid", "pmc"]].drop_duplicates().itertuples(index=False):
        doc = get_fulltext(pmid=str(pmid), pmcid=(pmcid if isinstance(pmcid, str) else None))
        bodies[pmid] = doc
        print("  %s %-12s route=%-10s chars=%-7d dropped=%d"
              % (pmid, doc.get("pmcid"), doc.get("route"), len(doc["text"] or ""),
                 len(doc["symbol_check"])), flush=True)

    for r in S.itertuples():
        doc = bodies.get(r.pmid, {})
        # Connector bodies included front matter, so compare on abstract + body.
        text = ((doc.get("abstract") or "") + "\n" + (doc.get("text") or "")).strip()
        toks = tokens(r.symbol_tokens)
        rows.append({
            "pmid": r.pmid, "pmcid": doc.get("pmcid"), "gene_target": r.gene_target,
            "symbol_tokens": r.symbol_tokens,
            "connector_symbol_in_body": str(r.symbol_in_body).lower() == "true",
            "connector_symbol_in_body_lax": str(r.symbol_in_body_lax).lower() == "true",
            "jats_route": doc.get("route"), "jats_retrieved": bool(text),
            "jats_chars": len(text),
            "jats_symbol_in_body": present(toks, text) if text else None,
            "jats_symbol_in_body_lax": present(toks, text, lax=True) if text else None,
            "jats_inline_dropped": len(doc.get("symbol_check") or []),
            "jats_error": doc.get("error"),
        })

    out = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    out.to_csv(args.out, index=False)

    got = out[out.jats_retrieved]
    summary = {
        "claims": int(len(out)),
        "papers": int(out.pmid.nunique()),
        "jats_retrieved_claims": int(len(got)),
        "jats_retrieved_papers": int(got.pmid.nunique()),
        "jats_unretrievable_papers": sorted(set(out[~out.jats_retrieved].pmid.astype(str))),
        "routes": out.drop_duplicates("pmid").jats_route.value_counts(dropna=False).to_dict(),
        "connector_label_absent_strict": int((~out.connector_symbol_in_body).sum()),
        "connector_label_absent_lax": int((~out.connector_symbol_in_body_lax).sum()),
        "jats_label_absent_strict": int((got.jats_symbol_in_body == False).sum()),  # noqa: E712
        "jats_label_absent_lax": int((got.jats_symbol_in_body_lax == False).sum()),  # noqa: E712
        "recovered_claims": int(((~got.connector_symbol_in_body)
                                 & (got.jats_symbol_in_body == True)).sum()),  # noqa: E712
        "lost_claims": int(((got.connector_symbol_in_body)
                            & (got.jats_symbol_in_body == False)).sum()),  # noqa: E712
        "total_inline_strings_dropped_by_renderer": int(out.jats_inline_dropped.sum()),
    }
    with open(args.summary, "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
