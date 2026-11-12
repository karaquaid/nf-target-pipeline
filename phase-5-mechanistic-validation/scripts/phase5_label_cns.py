#!/usr/bin/env python3
"""Mine openFDA SPL label text for statements about CNS and CSF distribution.

Why. Phase 6 scores CNS delivery three-state - demonstrated, contradicted,
unknown - but nothing in the pipeline could populate `contradicted`, because the
only CNS signal available was ChEMBL's CALCULATED descriptor flag, which is
wrong on the drugs that matter (selumetinib, trametinib, dabrafenib, tovorafenib
and lamotrigine are all marked predicted_non_permeant). Curated BBB datasets do
not help either: B3DB covers 2 of the 15 drugs of interest with a measured logBB.
FDA labels do carry distribution statements for approved drugs, and Phase 4
already queried openFDA but kept only metadata - routes, brand names, record
counts - not the text. This pass re-queries the label endpoint for the text.

What it does NOT do: it does not decide CNS delivery. It extracts quoted
sentences with their label record id so a human reads the claim, and it keeps
positive and limiting statements separate rather than collapsing them into a
verdict. A drug whose label says nothing is `no_statement`, never a negative.

Scope: distinct drugs on candidate rows where bbb_required is true and
max_phase >= --min-phase (default 3), since SPL labels exist for approved and
late-stage products.

Provenance rule inherited from Phase 4: a non-200 that is not a 404 is recorded
as a FAILURE, never collapsed into an empty result.

Usage:
  python phase5_label_cns.py --builddir build/phase5 --datadir <phase>/data
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

import pandas as pd
import requests

LABEL = "https://api.fda.gov/drug/label.json"
# Distribution-bearing sections ONLY. Deliberately excludes warnings_and_cautions,
# adverse_reactions, information_for_patients and spl_medguide: in lamotrigine's
# label every CSF and CNS mention sits in those fields and is about aseptic
# meningitis and CNS depression, i.e. adverse events, not brain penetration.
# Harvesting them would manufacture penetration evidence out of toxicity text.
SECTIONS = ["clinical_pharmacology", "pharmacokinetics", "description"]

CNS_WORDS = r"(?:blood[\s-]?brain barrier|central nervous system|\bCNS\b|\bCSF\b|cerebrospinal fluid|\bbrain\b|intracranial|meninge\w*)"
LIMITED = re.compile(
    r"(?:does not (?:appreciably )?(?:cross|penetrate|distribute)|do not cross|"
    r"poorly|limited|minimal|negligible|low(?:er)? (?:concentrations?|penetration|levels?)|"
    r"not detected|undetectable|restricted)[^.]{0,120}" + CNS_WORDS, re.I)
POSITIVE = re.compile(
    r"(?:cross(?:es|ed|ing)?|penetrat\w+|distribut\w+|detected|measured|achieved|present)"
    r"[^.]{0,120}" + CNS_WORDS, re.I)
QUANT = re.compile(r"(?:CSF|cerebrospinal fluid|brain)[^.]{0,60}(?:ratio|:\s?plasma|concentrations?)"
                   r"[^.]{0,60}\d", re.I)
# A CNS word alone is not a distribution claim. The sentence must also carry a
# distribution cue, or adverse-event prose scores as pharmacokinetics.
DISTRIBUTION_CUE = re.compile(
    r"(?:distribut\w+|penetrat\w+|cross(?:es|ed|ing)?|partition\w*|concentrations?|"
    r"ratio|exposure|volume of distribution|\bVd\b|protein[\s-]?binding|uptake|efflux|"
    r"P-?gp|permeab\w+)", re.I)
FAILURES: list[dict] = []


def get(session: requests.Session, params: dict, tries: int = 4) -> dict | None:
    key = os.environ.get("OPENFDA_API_KEY")
    if key:
        params = {**params, "api_key": key}
    last = None
    for attempt in range(tries):
        try:
            r = session.get(LABEL, params=params, timeout=90)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 404:          # openFDA's "no match"
                return {"results": []}
            last = f"HTTP {r.status_code}"
        except requests.RequestException as exc:
            last = f"{type(exc).__name__}"
        time.sleep(2 ** attempt)
    FAILURES.append({"search": params.get("search", "")[:160], "error": last})
    return None


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.;])\s+", text) if s.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--builddir", default="build/phase5")
    ap.add_argument("--datadir", default="phase-5-mechanistic-validation/data")
    ap.add_argument("--min-phase", type=float, default=3.0)
    ap.add_argument("--batch", type=int, default=1)  # retained for compatibility
    args = ap.parse_args()
    build, data = Path(args.builddir), Path(args.datadir)

    m = pd.read_csv(build / "phase5-drug-matches.csv.gz", low_memory=False)
    has = m[m.drug_name.notna()]
    cns = has[has.bbb_required.astype(str).str.lower() == "true"]
    phase = pd.to_numeric(cns.max_phase_numeric, errors="coerce")
    drugs = sorted({str(d).upper().strip() for d in cns[phase >= args.min_phase].drug_name})
    print(f"{len(drugs)} distinct drugs under a CNS requirement at phase >= {args.min_phase}",
          flush=True)

    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    rows, per_drug, requests_made = [], {}, 0
    seen_label_ids: set[str] = set()

    # One drug per request. A batched OR query with limit=100 came back with
    # records for only 3 of 6 drugs, so the batch form silently loses coverage.
    for i, drug in enumerate(drugs, 1):
        batch = [drug]
        body = get(session, {"search": f'openfda.generic_name:("{drug}")', "limit": 5})
        if i % 50 == 0:
            print(f"  {i}/{len(drugs)} drugs queried", flush=True)
        requests_made += 1
        if body is None:
            continue
        for rec in body.get("results", []) or []:
            of = rec.get("openfda", {}) or {}
            generics = {g.upper().strip() for g in (of.get("generic_name") or [])}
            match = generics & set(batch)
            if not match:
                continue
            label_id = rec.get("id", "")
            for sec in SECTIONS:
                for blob in (rec.get(sec) or []):
                    for sent in sentences(blob):
                        if not re.search(CNS_WORDS, sent, re.I):
                            continue
                        if not DISTRIBUTION_CUE.search(sent):
                            continue
                        lim = bool(LIMITED.search(sent))
                        pos = bool(POSITIVE.search(sent)) and not lim
                        if not (lim or pos):
                            continue
                        for drug in sorted(match):
                            rows.append({
                                "drug_name": drug, "label_id": label_id, "section": sec,
                                "statement_kind": "limited" if lim else "penetration",
                                "has_number": bool(QUANT.search(sent)),
                                "sentence": sent[:600],
                                "effective_time": rec.get("effective_time"),
                            })
            for drug in sorted(match):
                per_drug.setdefault(drug, set()).add(label_id)
            seen_label_ids.add(label_id)
        time.sleep(0.3)

    st = pd.DataFrame(rows).drop_duplicates(subset=["drug_name", "label_id", "sentence"])
    st.to_csv(data / "phase5-label-cns-statements.csv", index=False)

    verdicts = []
    for drug in drugs:
        sub = st[st.drug_name == drug] if len(st) else st
        n_lim = int((sub.statement_kind == "limited").sum()) if len(sub) else 0
        n_pos = int((sub.statement_kind == "penetration").sum()) if len(sub) else 0
        if drug not in per_drug:
            verdict = "no_label_found"
        elif n_lim and n_pos:
            verdict = "mixed_statements"
        elif n_lim:
            verdict = "states_limited_cns_distribution"
        elif n_pos:
            verdict = "states_cns_distribution"
        else:
            verdict = "no_statement"
        verdicts.append({"drug_name": drug, "label_verdict": verdict,
                         "n_limiting_statements": n_lim, "n_penetration_statements": n_pos,
                         "n_statements_with_a_number": int(sub.has_number.sum()) if len(sub) else 0,
                         "n_label_records": len(per_drug.get(drug, ())),
                         "label_ids": "|".join(sorted(per_drug.get(drug, ()))[:5])})
    vd = pd.DataFrame(verdicts).sort_values(["label_verdict", "drug_name"])
    vd.to_csv(data / "phase5-label-cns-verdicts.csv", index=False)

    prov = {
        "endpoint": LABEL,
        "sections_read": SECTIONS,
        "scope": f"distinct drugs with bbb_required and max_phase >= {args.min_phase}",
        "drugs_in_scope": len(drugs),
        "api_requests_made": requests_made,
        "api_key_used": bool(os.environ.get("OPENFDA_API_KEY")),
        "failed_requests": len(FAILURES),
        "failures": FAILURES,
        "label_records_seen": len(seen_label_ids),
        "drugs_with_a_label": len(per_drug),
        "statement_rows": int(len(st)),
        "verdicts": vd.label_verdict.value_counts().to_dict(),
        "caveat": "extraction is regex over label prose; the sentence and label_id are kept so "
                  "a human verifies each claim. A label that says nothing is no_statement, "
                  "never evidence against CNS delivery.",
    }
    json.dump(prov, open(data / "phase5-label-cns-provenance.json", "w"), indent=2)
    print(json.dumps({k: v for k, v in prov.items() if k != "failures"}, indent=2))


if __name__ == "__main__":
    main()
