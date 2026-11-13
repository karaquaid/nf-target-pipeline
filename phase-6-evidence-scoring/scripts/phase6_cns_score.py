#!/usr/bin/env python3
"""Phase 6, stage 4: weight each claim instead of dropping it.

The first aggregation rule was a filter: a claim counted fully or not at all, and
a claim we could not confirm as the paper's own finding was discarded. That is
too blunt in both directions. Confirming originality depends on retrievable full
text, and only 62 of the 124 claims are seated in a section - for the rest the
`primary` label is an inference from the abstract, corroborated for 47 of 55 by
first-person study language and unverified for 8. Discarding on an unverifiable
label throws away real evidence; accepting it at full weight overstates it.

So every claim keeps a voice, scaled by how much the evidence behind it can be
trusted. Weight is the product of independent factors, each a judgement recorded
here rather than buried in code:

  originality   how sure we are the paper made this finding rather than citing it
  corroboration whether section placement and study language back that label up
  arm           whether the measurement reflects normal physiology
  species       human exposure outranks animal, which outranks in-vitro
  basis         a measured exposure outranks a clinical observation, which
                outranks an assertion, which outranks a prediction
  access        full text outranks abstract-only, as Phase 1b scores it
  confidence    the adjudicator's own confidence
  span          whether the quoted support survived the stage 3 audit

A drug then carries a signed score rather than a verdict: demonstrated claims add
their weight to support, contradicted claims to exclusion. Reported per drug:

  evidence_mass    support + exclusion, i.e. how much weighted evidence exists
  direction_score  (support - exclusion) / mass, in [-1, +1]
  band             the three-state label the Phase 6 rubric still requires,
                   derived from mass and direction by explicit thresholds

Unknown claims contribute nothing in either direction and do not dilute the
score: absence is not negative evidence. A drug with little mass lands in
`unknown` as unassessed, and keeps its score so it can be ranked within that
state rather than tied with drugs that have no literature at all.

Reads the stage 2 proposals, the stage 1 context and the stage 3 span audit.
Writes data/phase6-cns-evidence-scores.csv and adds score columns to the rollup.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "phase-6-evidence-scoring" / "data"

# --- weights -----------------------------------------------------------------
# Defaults, not discoveries. Every value is a judgement about how much a claim of
# that kind should count, and this block is the place to change the scoring.
ORIGINALITY = {"primary": 1.00, "unclear": 0.60, "restated": 0.35}
ARM = {
    "normal": 1.00,
    "not_applicable": 0.90,
    "unclear": 0.60,
    "transporter_knockout_or_inhibitor": 0.45,
    "bbb_modifying_cointervention": 0.35,
}
SPECIES = {"human": 1.00, "mouse": 0.75, "rat": 0.75, "other_animal": 0.60, "in_vitro": 0.35, "na": 0.50}
BASIS = {
    "measured_pk_human": 1.00,
    "measured_pk_animal": 0.90,
    "clinical_cns_response": 0.80,
    "preclinical_cns_efficacy": 0.60,
    "mechanistic_assertion": 0.30,
    "review_restatement": 0.30,
    "design_or_prediction": 0.20,
}
ACCESS = {"full_text": 1.00, "abstract_only": 0.85}
CONFIDENCE = {"high": 1.00, "medium": 0.85, "low": 0.60}
SPAN = {"all_fragments_verbatim": 1.00, "no_span_quoted": 0.60, "fragment_not_found": 0.40}

# Banding thresholds. MIN_MASS is roughly one mid-quality claim: below it a drug
# is unassessed rather than scored. MIN_DIRECTION keeps a drug whose evidence
# points both ways out of a one-sided verdict.
MIN_MASS = 0.75
MIN_DIRECTION = 0.35

FIRST_PERSON = re.compile(r"\b(we |our |this study|here we|in the present study)", re.I)


def corroboration(label: str, section: str, pub_types: str, context: str) -> tuple[float, str]:
    """How well independent signals back the originality label.

    Section placement and publication type are properties of the record, not of
    the adjudicator's reasoning, so they are the closest thing to an external
    check this corpus affords.
    """
    sec = str(section).lower()
    review = "review" in str(pub_types).lower()
    if label != "primary":
        return 1.00, "not_applicable_label_not_primary"
    if "result" in sec or sec == "table":
        return 1.00, "seated_in_results_or_table"
    if "discussion" in sec or "conclusion" in sec:
        return 0.90, "seated_in_discussion"
    if "background" in sec or "introduction" in sec or review:
        return 0.50, "primary_label_contradicted_by_placement"
    if sec == "abstract":
        return (0.95, "abstract_with_first_person_study_language") if FIRST_PERSON.search(
            str(context)
        ) else (0.80, "abstract_without_first_person_language")
    return 0.90, "seated_in_descriptive_section"


def main() -> None:
    prop = pd.read_csv(DATA / "phase6-cns-adjudication-proposed.csv")
    packets = json.loads((DATA / "phase6-cns-claim-context.json").read_text())
    audit = pd.read_csv(DATA / "phase6-cns-span-audit.csv").set_index("claim_id")["span_status"].to_dict()

    rows = []
    for _, r in prop.iterrows():
        cid = r["claim_id"]
        p = packets[cid]
        corr, corr_reason = corroboration(
            r.get("proposed_primary_or_restated"),
            p.get("context_section"),
            "; ".join(p.get("pub_types") or []),
            p.get("context_text", ""),
        )
        f = {
            "originality": ORIGINALITY.get(r.get("proposed_primary_or_restated"), 0.5),
            "corroboration": corr,
            "arm": ARM.get(r.get("proposed_experimental_arm"), 0.6),
            "species": SPECIES.get(r.get("proposed_species"), 0.5),
            "basis": BASIS.get(r.get("proposed_evidence_basis"), 0.3),
            "access": ACCESS.get(r.get("access"), 0.85),
            "confidence": CONFIDENCE.get(r.get("proposed_confidence"), 0.85),
            "span": SPAN.get(audit.get(cid, "no_span_quoted"), 0.6),
        }
        weight = 1.0
        for v in f.values():
            weight *= v
        verdict = r.get("proposed_verdict")
        rows.append(
            {
                "claim_id": cid,
                "moiety": r["moiety"],
                "proposed_verdict": verdict,
                "access": r.get("access"),
                "context_section": p.get("context_section"),
                **{f"w_{k}": round(v, 3) for k, v in f.items()},
                "corroboration_reason": corr_reason,
                "evidence_weight": round(weight, 4),
                "signed_contribution": round(
                    weight * (1 if verdict == "demonstrated" else -1 if verdict == "contradicted" else 0), 4
                ),
            }
        )
    scores = pd.DataFrame(rows)
    scores.to_csv(DATA / "phase6-cns-evidence-scores.csv", index=False)

    rollup = pd.read_csv(DATA / "phase6-cns-adjudication-rollup.csv")
    agg = []
    for _, r in rollup.iterrows():
        sub = scores[scores["moiety"] == r["moiety"]]
        support = float(sub.loc[sub["proposed_verdict"] == "demonstrated", "evidence_weight"].sum())
        exclusion = float(sub.loc[sub["proposed_verdict"] == "contradicted", "evidence_weight"].sum())
        mass = support + exclusion
        direction = (support - exclusion) / mass if mass else 0.0
        if mass < MIN_MASS:
            band, why = "unknown", f"evidence mass {mass:.2f} below {MIN_MASS}; unassessed"
        elif abs(direction) < MIN_DIRECTION:
            band, why = "unknown", f"evidence points both ways (direction {direction:+.2f}); unresolved"
        else:
            band = "demonstrated" if direction > 0 else "contradicted"
            why = f"mass {mass:.2f}, direction {direction:+.2f}"
        top = sub.reindex(sub["evidence_weight"].sort_values(ascending=False).index).head(3)
        agg.append(
            {
                "support_weight": round(support, 3),
                "exclusion_weight": round(exclusion, 3),
                "evidence_mass": round(mass, 3),
                "direction_score": round(direction, 3),
                "scored_band": band,
                "scored_rationale": why,
                "top_weighted_claim_ids": ", ".join(
                    f"{c} ({w:.2f})" for c, w in zip(top["claim_id"], top["evidence_weight"]) if w > 0
                ),
            }
        )
    for k in agg[0]:
        rollup[k] = [a[k] for a in agg]
    rollup["band_differs_from_rule"] = [
        (str(b) or "blank") != (str(v) if isinstance(v, str) and v else "blank")
        for b, v in zip(rollup["scored_band"], rollup["proposed_drug_verdict"])
    ]
    rollup.to_csv(DATA / "phase6-cns-adjudication-rollup.csv", index=False)

    print(
        json.dumps(
            {
                "claims_scored": len(scores),
                "weight_quartiles": scores["evidence_weight"].quantile([0.25, 0.5, 0.75]).round(3).to_dict(),
                "weight_range": [float(scores["evidence_weight"].min()), float(scores["evidence_weight"].max())],
                "bands": rollup["scored_band"].value_counts().to_dict(),
                "differs_from_rule": rollup.loc[rollup["band_differs_from_rule"], "moiety"].tolist(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
