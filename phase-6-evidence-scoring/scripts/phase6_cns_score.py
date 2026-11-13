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

# Banding thresholds. A drug is judged on its BEST evidence, not its most
# (decided 2026-11-13, Kara): the band reads the single heaviest claim on each
# side rather than the sum, so twenty weak mentions cannot outweigh one good
# measurement and one good measurement is not diluted by weak company.
# MIN_PEAK is the quality a single claim must reach to say anything at all: at
# 0.50 an abstract-derived animal PK measurement clears it (~0.55) while a
# hedged assertion or a prediction does not. MIN_DIRECTION keeps a drug whose
# best evidence points both ways out of a one-sided verdict.
# evidence_mass is still reported - it describes how much corroboration exists -
# but it no longer decides the band.
MIN_PEAK = 0.50
MIN_DIRECTION = 0.35
MIN_MASS = 0.75  # retained only for the comparison column mass_band

# Compartment classes. A drug excluded from CSF and normal brain can still reach
# an intracranial tumour, where the barrier is disrupted; in this corpus that is
# the rule rather than the exception - normal brain carries 24 contradicted
# claims against 1 demonstrated, tumour tissue 9 demonstrated against 1. Scoring
# the two together makes a coherent finding look like a self-contradiction, so
# each class is banded separately (decided 2026-11-13, Kara).
BARRIER_INTACT = {"csf", "normal_brain", "brain_unspecified"}
TUMOUR = {"tumour_tissue"}
# A clinical or preclinical CNS response is evidence about drug reaching tumour,
# even though no compartment was sampled.
TUMOUR_BASES = {"clinical_cns_response", "preclinical_cns_efficacy"}


def compartment_class(compartment: str, basis: str) -> str:
    if compartment in TUMOUR or basis in TUMOUR_BASES:
        return "tumour"
    if compartment in BARRIER_INTACT:
        return "barrier_intact"
    return "none"


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
                "compartment": r.get("proposed_compartment"),
                "compartment_class": compartment_class(
                    r.get("proposed_compartment"), r.get("proposed_evidence_basis")
                ),
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
        mass_direction = (support - exclusion) / mass if mass else 0.0
        # Best evidence on each side, and the band that follows from it.
        # `or 0` is wrong here: an empty side gives NaN, and NaN is truthy, so it
        # propagates through max() and every comparison returns False - which put
        # every drug in `contradicted` on the first run of this change.
        def _best(verdict: str, frame=None) -> float:
            f = sub if frame is None else frame
            v = f.loc[f["proposed_verdict"] == verdict, "evidence_weight"].max()
            return 0.0 if pd.isna(v) else float(v)

        def _band(frame) -> tuple:
            bs, be = _best("demonstrated", frame), _best("contradicted", frame)
            pk = max(bs, be)
            dr = (bs - be) / pk if pk else 0.0
            if pk == 0:
                return "unknown", "no_claim_carries_a_verdict", bs, be, dr
            if pk < MIN_PEAK:
                return "unknown", "below_peak_threshold", bs, be, dr
            if abs(dr) < MIN_DIRECTION:
                return "unknown", "conflicting_best_evidence", bs, be, dr
            return ("demonstrated" if dr > 0 else "contradicted"), "resolved", bs, be, dr

        barrier = sub[sub["compartment_class"] == "barrier_intact"]
        tumour = sub[sub["compartment_class"] == "tumour"]
        b_band, b_reason, b_sup, b_exc, b_dir = _band(barrier)
        t_band, t_reason, t_sup, t_exc, t_dir = _band(tumour)
        best_support, best_exclusion = _best("demonstrated"), _best("contradicted")
        peak = max(best_support, best_exclusion)
        direction = (best_support - best_exclusion) / peak if peak else 0.0
        # Three ways to land in `unknown`, and Phase 6 must be able to tell them
        # apart: a drug nobody measured, a drug measured only weakly, and a drug
        # whose best evidence disagrees with itself. Collapsing them would repeat
        # the mistake the three-state rule exists to prevent.
        if peak == 0:
            band, reason = "unknown", "no_claim_carries_a_verdict"
            why = "no attributed claim carries a demonstrated or contradicted verdict"
        elif peak < MIN_PEAK:
            band, reason = "unknown", "below_peak_threshold"
            why = f"best claim weighs {peak:.2f}, below {MIN_PEAK}; unassessed"
        elif abs(direction) < MIN_DIRECTION:
            band, reason = "unknown", "conflicting_best_evidence"
            why = (
                f"best evidence points both ways (support {best_support:.2f} vs "
                f"exclusion {best_exclusion:.2f}); unresolved"
            )
        else:
            band = "demonstrated" if direction > 0 else "contradicted"
            reason = "resolved"
            why = f"best claim {peak:.2f}, direction {direction:+.2f}"

        # A difference BETWEEN compartments is a finding, not a conflict: record
        # it as a split and let Phase 6 pick the compartment its manifestation
        # needs, rather than cancelling one against the other.
        resolved = [x for x in (b_band, t_band) if x != "unknown"]
        if len(set(resolved)) == 2:
            band, reason = "compartment_split", "compartment_split"
            why = (
                f"barrier-intact compartments read {b_band} "
                f"(best {max(b_sup, b_exc):.2f}), tumour tissue reads {t_band} "
                f"(best {max(t_sup, t_exc):.2f})"
            )
        elif reason == "conflicting_best_evidence" and len(set(resolved)) == 1:
            band, reason = resolved[0], "resolved_within_compartment"
            why = f"single compartment class resolves to {resolved[0]}; whole-drug best claims had looked contested"
        mass_band = (
            "unknown"
            if mass < MIN_MASS or abs(mass_direction) < MIN_DIRECTION
            else ("demonstrated" if mass_direction > 0 else "contradicted")
        )
        top = sub.reindex(sub["evidence_weight"].sort_values(ascending=False).index).head(3)
        agg.append(
            {
                "support_weight": round(support, 3),
                "exclusion_weight": round(exclusion, 3),
                "evidence_mass": round(mass, 3),
                "best_support_weight": round(best_support, 3),
                "best_exclusion_weight": round(best_exclusion, 3),
                "peak_weight": round(peak, 3),
                "direction_score": round(direction, 3),
                "mass_direction_score": round(mass_direction, 3),
                "mass_band": mass_band,
                "scored_band": band,
                "band_reason": reason,
                "band_barrier_intact": b_band,
                "band_barrier_reason": b_reason,
                "barrier_best_support": round(b_sup, 3),
                "barrier_best_exclusion": round(b_exc, 3),
                "band_tumour": t_band,
                "band_tumour_reason": t_reason,
                "tumour_best_support": round(t_sup, 3),
                "tumour_best_exclusion": round(t_exc, 3),
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
