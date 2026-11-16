#!/usr/bin/env python3
"""Phase 6, stage 5c: adjudicate the OPG tumor-compartment claims.

Same rubric, same tool schema, same synonym list as the CNS pass - only the
corpus differs. Run from the python kernel: import phase6_opg_adjudicate as m;
m.main(host).

Writes data/phase6-opg-adjudicated.csv with proposed_* columns, and
-model-run.json. Nothing here decides anything: the human verdict columns stay
in phase6-cns-human-verdicts.csv.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "phase-6-evidence-scoring" / "data"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import phase6_cns_adjudicate as cns


def main(host=None) -> None:
    if host is None or not hasattr(host, "llm"):
        raise SystemExit("Run in the python kernel: import phase6_opg_adjudicate as m; m.main(host)")
    claims = pd.read_csv(DATA / "phase6-opg-literature-claims.csv")
    att = claims[claims["drug_named_in_sentence"] == True].copy()  # noqa: E712
    packets = json.loads((DATA / "phase6-opg-claim-context.json").read_text())
    syn = json.loads((DATA / "phase6-drug-synonyms.json").read_text())["drugs"]

    ids = [c for c in att["claim_id"] if c in packets]
    reqs = [{"prompt": cns.build_prompt(packets[c], syn.get(packets[c]["moiety"], {}).get("synonyms")),
             "tools": [cns.TOOL], "tool_choice": {"type": "tool", "name": "adjudicate_claim"},
             "max_tokens": 1200, "thinking": {"type": "disabled"}, "model": host.reasoning_model()}
            for c in ids]
    results = host.llm(reqs, max_concurrency=8)

    rows, errors = [], []
    for cid, r in zip(ids, results):
        if "error" in r or not r.get("tool_use"):
            errors.append({"claim_id": cid, "error": r.get("error", "no tool_use")})
            rows.append({"claim_id": cid}); continue
        row = {"claim_id": cid}
        row.update({f"proposed_{k}": v for k, v in r["tool_use"]["input"].items()})
        rows.append(row)

    prop = pd.DataFrame(rows)
    merged = att.merge(prop, on="claim_id", how="left")
    for col in ("context_source", "context_section", "match_frac"):
        merged[col] = merged["claim_id"].map(lambda c: packets[c].get(col))
    merged["source_pass"] = "phase6_opg"
    merged.to_csv(DATA / "phase6-opg-adjudicated.csv", index=False)

    run = {"stage": "phase6_opg_adjudicate.py", "model": results[0].get("model") if results else None,
           "claims_submitted": len(ids), "errors": errors,
           "verdict_counts": merged["proposed_verdict"].value_counts(dropna=False).to_dict(),
           "compartment_counts": merged["proposed_compartment"].value_counts(dropna=False).to_dict(),
           "basis_counts": merged["proposed_evidence_basis"].value_counts(dropna=False).to_dict()}
    (DATA / "phase6-opg-model-run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(json.dumps(run, indent=2)[:1600])


if __name__ == "__main__":
    main()
