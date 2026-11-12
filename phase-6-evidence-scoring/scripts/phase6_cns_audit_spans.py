#!/usr/bin/env python3
"""Phase 6, stage 3: check that every quoted span is real.

The adjudicator returns a verbatim span from the supplied text as support for its
verdict. That claim is checkable, and checking it is the cheapest guard the stage
has against a confidently-worded verdict resting on text that was never there.
This stage recomputes it rather than trusting the model's own assertion.

Spans legitimately join two fragments of one paragraph with an ellipsis, so the
test is per fragment: strip the ellipsis, normalise away punctuation, spacing and
case (the Phase 5 sentences carry tag-stripping artifacts), then require every
fragment of at least 12 characters to appear in the context the model was given.

Writes data/phase6-cns-span-audit.csv, one row per claim. A missing fragment is
not automatically a wrong verdict; it means the stated support is not where the
model said it was, so that verdict has to be re-read by hand.
"""
from __future__ import annotations

import difflib
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "phase-6-evidence-scoring" / "data"
MIN_FRAGMENT_CHARS = 12


def norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(t).lower())


def fragments(span: str) -> list:
    parts = re.split(r"\s*(?:\.\.\.|\u2026|\[\.\.\.\])\s*", str(span))
    return [p.strip() for p in parts if len(norm(p)) >= MIN_FRAGMENT_CHARS]


def main() -> None:
    prop = pd.read_csv(DATA / "phase6-cns-adjudication-proposed.csv")
    packets = json.loads((DATA / "phase6-cns-claim-context.json").read_text())

    rows = []
    for _, r in prop.iterrows():
        cid = r["claim_id"]
        p = packets[cid]
        hay = norm(p["context_text"]) + norm(p["sentence"])
        frags = fragments(r.get("proposed_quoted_support", ""))
        if not frags:
            status, found, total, worst = "no_span_quoted", 0, 0, None
        else:
            ok = [f for f in frags if norm(f) in hay]
            found, total = len(ok), len(frags)
            status = "all_fragments_verbatim" if found == total else "fragment_not_found"
            worst = None
            if found != total:
                nm = norm([f for f in frags if norm(f) not in hay][0])
                m = difflib.SequenceMatcher(None, nm, hay, autojunk=False).find_longest_match(
                    0, len(nm), 0, len(hay)
                )
                worst = round(m.size / len(nm), 3)
        rows.append(
            {
                "claim_id": cid,
                "moiety": r["moiety"],
                "proposed_verdict": r.get("proposed_verdict"),
                "proposed_confidence": r.get("proposed_confidence"),
                "basis_location": r.get("proposed_basis_location"),
                "span_status": status,
                "fragments_found": found,
                "fragments_total": total,
                "longest_run_frac_of_missing": worst,
            }
        )

    audit = pd.DataFrame(rows)
    audit.to_csv(DATA / "phase6-cns-span-audit.csv", index=False)
    failed = audit[audit["span_status"] == "fragment_not_found"]
    print(
        json.dumps(
            {
                "claims_audited": len(audit),
                "status_counts": audit["span_status"].value_counts().to_dict(),
                "failed_claim_ids": failed["claim_id"].tolist(),
                "failed_carrying_a_verdict": failed.loc[
                    failed["proposed_verdict"] != "unknown", "claim_id"
                ].tolist(),
                "no_span_claim_ids": audit.loc[
                    audit["span_status"] == "no_span_quoted", "claim_id"
                ].tolist(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
