#!/usr/bin/env python3
"""Phase 6: score every candidate and rank it within its stratum.

One row per candidate (gene x disease x manifestation), 3,752 of them across the
nine strata the Phase 3b prioritisation selected. The rubric combines the
evidence the earlier phases produced - expression, literature, cross-disease
mechanism, tractability, drug development stage - applies the route and safety
adjustments Phase 6 calls for, and adds CNS delivery in the one stratum where it
applies.

Four rules this file exists to enforce, all settled earlier with Kara:

1. Absence is not negative evidence. A component that could not speak for a
   candidate is dropped from the weighted mean and its weight redistributed,
   never scored zero. Which sources could have spoken is recorded per candidate
   in `coverage`, so a zero from a source with no data reads differently from a
   zero from a source that looked.
2. CNS delivery applies only where the manifestation is in the brain. It enters
   the score for bbb_required strata (NF1 optic pathway glioma alone) and is not
   an input of any kind elsewhere.
3. Compartment follows the manifestation. Optic pathway glioma is a tumor, so a
   drug whose bands split takes its tumor band, not its barrier-intact band.
   Selumetinib is the case that matters: contradicted through an intact barrier,
   demonstrated in tumor.
4. Clinical-response evidence of tumor delivery carries positive weight (Kara,
   2026-11-16). The circularity this invites - a drug credited for delivery on
   the strength of the same trials that score its clinical stage - is not hidden:
   `delivery_basis` records whether a positive delivery score came from a
   measured tumor concentration or from clinical response, so the double-count
   is visible to anyone reading the table.

Ranking is within disease x manifestation, never across, because the evidence
sources available differ by stratum.

Inputs   phase-4/data/phase4-target-dossier.csv
         phase-5-mechanistic-validation/data/phase5-target-support.csv
         phase-5-mechanistic-validation/data/phase5-tractability-state.csv
         phase-5-mechanistic-validation/data/phase5-drug-matches.csv.gz
         phase-6-evidence-scoring/data/phase6-cns-adjudication-rollup.csv
         phase-6-evidence-scoring/data/phase6-cns-evidence-scores.csv
Outputs  data/phase6-candidate-scores.csv
         data/phase6-candidate-scores-summary.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
P4 = ROOT / "phase-4" / "data"
P5 = ROOT / "phase-5-mechanistic-validation" / "data"
DATA = ROOT / "phase-6-evidence-scoring" / "data"

# --- component scores --------------------------------------------------------
# Every value here is a judgement about how much a kind of evidence should count,
# not a measurement. This block is the place to change the rubric.
EXPRESSION = {"A_aggregated": 1.00, "B_replicated": 0.70, "C_single_dataset": 0.40}
LITERATURE = {"full text - supported": 1.00, "full text - partial": 0.70, "abstract only": 0.40}
# D_no_edges is NOT scored (Kara, 2026-11-16): Monarch and DisMech returning no
# edge for a gene is assessed-found-nothing, and their coverage is itself uneven
# by disease - no DisMech entry for NF2-SWN, no Monarch causal edge for SWN - so
# a zero there would often score a database gap rather than the biology. Absent
# from this map means dropped from the weighted mean, as the absence rule requires.
MECHANISM = {"A_mechanism": 1.00, "B_phenotype": 0.75, "C_other_only": 0.35}
TRACTABILITY = {"evidence_present": 1.00, "assessed_no_evidence": 0.00}  # not_assessed -> no score
# best_max_phase is the highest phase any drug against this target reached in ANY
# indication, and it keeps full marks regardless of indication (Kara, 2026-11-17):
# the pipeline exists to find drugs NEW to NF patients, so an approval earned
# elsewhere is the signal of interest, not a dilution of it. An approved drug
# establishes human target engagement, PK and safety; which disease it was
# approved for is what repurposing proposes to change. 388 candidates score 1.00,
# of which 182 have no drug ever tested in an NF trial - those are flagged
# `novel_to_nf` rather than discounted, because they are the repurposing
# opportunities this phase is meant to surface.
DRUG_STAGE = {4: 1.00, 3: 0.80, 2: 0.60, 1: 0.40, 0: 0.15}

WEIGHTS = {"expression": 0.30, "literature": 0.20, "mechanism": 0.20,
           "tractability": 0.15, "drug_stage": 0.15}
DELIVERY_WEIGHT = 0.20          # added in bbb_required strata; others rescale to 0.80

# Delivery band -> score. `unknown` is 0.5, the neutral midpoint: unassessed, not
# a penalty. `contradicted` is the only state that costs a candidate anything.
DELIVERY = {"demonstrated": 1.00, "unknown": 0.50, "contradicted": 0.00}

NEUTRAL_PRIOR = 0.50            # what an unassessed component contributes

# Safety is a property of the target's remaining OPTIONS, not of any one drug
# (Kara, 2026-11-17). The flat version penalised a target when any single drug
# against it had been withdrawn or carried a boxed warning, which scaled with how
# well studied the target was rather than how dangerous it was: TP53 took 0.60
# for 2 withdrawn drugs out of 465, and all 71 withdrawn-penalised candidates
# still had other drugs. A target is downweighted only as its usable options are
# exhausted.
SAFETY_EXHAUSTED = 0.60     # no drug against this target is free of a safety problem
SAFETY_MOSTLY_FLAGGED = 0.85  # more than half the drugs carry one
SAFETY_CLEAN = 1.00
ROUTE_INAPPROPRIATE = 0.40      # every drug this candidate has is route-excluded

# Which compartment a manifestation needs. Only bbb_required strata consult this.
MANIFESTATION_COMPARTMENT = {"Optic pathway glioma": "tumor"}


def _truthy(v) -> bool:
    return str(v).strip().lower() == "true"


def drug_delivery_lookup() -> tuple[dict, dict]:
    """Per moiety: the band for each compartment class, and what the tumor band rests on."""
    rollup = pd.read_csv(DATA / "phase6-cns-adjudication-rollup.csv")
    # Read the verdicts file directly: the rollup merge does not carry the
    # compartment a verdict was made about, and defaulting that to "applies
    # everywhere" let a barrier-intact verdict score a tumor stratum.
    hv_path = DATA / "phase6-cns-human-verdicts.csv"
    hv = pd.read_csv(hv_path) if hv_path.exists() else pd.DataFrame(columns=["moiety"])
    hv_map = {r["moiety"]: (r.get("human_verdict"), r.get("compartment")) for _, r in hv.iterrows()}
    scores = pd.read_csv(DATA / "phase6-cns-evidence-scores.csv")
    bases = []
    for f in ("phase6-cns-adjudication-proposed.csv", "phase6-opg-adjudicated.csv"):
        p = DATA / f
        if p.exists():
            bases.append(pd.read_csv(p)[["claim_id", "proposed_evidence_basis"]])
    basis = pd.concat(bases).drop_duplicates("claim_id") if bases else pd.DataFrame()
    scores = scores.merge(basis, on="claim_id", how="left")

    bands, basis_of = {}, {}
    for _, r in rollup.iterrows():
        human, human_comp = hv_map.get(r["moiety"], (None, None))
        bands[r["moiety"]] = {
            "overall": r.get("scored_band"),
            "barrier_intact": r.get("band_barrier_intact"),
            "tumor": r.get("band_tumor"),
            "human_verdict": human if isinstance(human, str) and human else None,
            "human_compartment": human_comp if isinstance(human_comp, str) else None,
        }
        sub = scores[(scores["moiety"] == r["moiety"]) & (scores["compartment_class"] == "tumor")
                     & (scores["proposed_verdict"] == "demonstrated")]
        if len(sub):
            top = sub.loc[sub["evidence_weight"].idxmax()]
            b = str(top.get("proposed_evidence_basis", ""))
            basis_of[r["moiety"]] = "tumor_measured" if b.startswith("measured") else "tumor_clinical"
    return bands, basis_of


def delivery_for(row, matches, variants, bands, basis_of) -> tuple:
    """Best delivery state among this candidate's drugs, with its basis recorded."""
    sub = matches[(matches["gene_symbol"] == row["gene_symbol"])
                  & (matches["disease"] == row["disease"])
                  & (matches["manifestation"] == row["manifestation"])]
    if not len(sub):
        return None, "no_drug", ""
    compartment = MANIFESTATION_COMPARTMENT.get(row["manifestation"], "barrier_intact")
    best, best_moiety, best_state = None, "", ""
    for name in sub["drug_name"].dropna().unique():
        moiety = variants.get(str(name).upper())
        if not moiety or moiety not in bands:
            continue
        b = bands[moiety]
        # Compartment first, always. Taking the overall band here applied a
        # barrier-intact finding inside a tumor stratum - cobimetinib and
        # sorafenib are contradicted through an intact barrier but unknown in
        # tumor, and were scoring 0.0 for optic pathway glioma on that basis.
        # A human verdict overrides only the compartment it was made about.
        state = b.get(compartment)
        if b["human_verdict"] and b.get("human_compartment") in (None, compartment):
            state = b["human_verdict"]
        if state in (None, "compartment_split"):
            state = b.get("overall") if b.get("overall") != "compartment_split" else b.get(compartment)
        score = DELIVERY.get(state)
        if score is None:
            continue
        if best is None or score > best:
            best, best_moiety, best_state = score, moiety, state
    if best is None:
        return None, "no_assessed_drug", ""
    if best_state == "demonstrated":
        basis = basis_of.get(best_moiety, "tumor_clinical" if compartment == "tumor" else "barrier_intact")
    elif best_state == "contradicted":
        basis = f"{compartment}_contradicted"
    else:
        basis = "unassessed"
    return best, basis, best_moiety


def main() -> None:
    dossier = pd.read_csv(P4 / "phase4-target-dossier.csv", low_memory=False)
    support = pd.read_csv(P5 / "phase5-target-support.csv")[
        ["gene_symbol", "disease", "manifestation", "phase5_support_tier"]]
    tract = pd.read_csv(P5 / "phase5-tractability-state.csv")[["gene_symbol", "tractability_evidence"]]
    matches = pd.read_csv(P5 / "phase5-drug-matches.csv.gz", low_memory=False)
    rollup = pd.read_csv(DATA / "phase6-cns-adjudication-rollup.csv")
    bands, basis_of = drug_delivery_lookup()
    variants = {v.strip().upper(): r["moiety"] for _, r in rollup.iterrows()
                for v in str(r["label_variants"]).split("|") if v.strip()}

    df = dossier.merge(support, on=["gene_symbol", "disease", "manifestation"], how="left")
    df = df.merge(tract, on="gene_symbol", how="left")

    rows = []
    for _, r in df.iterrows():
        comp, cov = {}, []

        comp["expression"] = EXPRESSION.get(r.get("expr_best_tier"))
        cov.append("expression" if pd.notna(r.get("expr_best_tier")) else "-expression")
        comp["literature"] = LITERATURE.get(r.get("lit_best_tier"))
        cov.append("literature" if pd.notna(r.get("lit_best_tier")) else "-literature")

        tier = r.get("phase5_support_tier")
        comp["mechanism"] = MECHANISM.get(tier)  # 'unassessed' is absent from the map by design
        cov.append("mechanism" if tier in MECHANISM else "-mechanism")

        comp["tractability"] = TRACTABILITY.get(r.get("tractability_evidence"))
        cov.append("tractability" if r.get("tractability_evidence") in TRACTABILITY else "-tractability")

        n_drugs = float(r.get("n_drugs") or 0)
        phase = r.get("best_max_phase")
        comp["drug_stage"] = DRUG_STAGE.get(int(phase)) if pd.notna(phase) else (0.15 if n_drugs else None)
        cov.append("drug_stage" if comp["drug_stage"] is not None else "-drug_stage")

        bbb = _truthy(r.get("bbb_required"))
        delivery = delivery_basis = delivery_moiety = None
        if bbb:
            delivery, delivery_basis, delivery_moiety = delivery_for(r, matches, variants, bands, basis_of)
            cov.append("cns_delivery" if delivery is not None else "-cns_delivery")

        weights = dict(WEIGHTS)
        if bbb:
            weights = {k: v * (1 - DELIVERY_WEIGHT) for k, v in weights.items()}
            weights["cns_delivery"] = DELIVERY_WEIGHT
            comp["cns_delivery"] = delivery

        # Unassessed weight contributes at the neutral midpoint rather than being
        # redistributed (Kara, 2026-11-16). Redistribution rewarded ignorance: a
        # candidate assessed on two maxed components scored a perfect 1.0 and tied
        # with one assessed on five, and 104 candidates sat at rank 1 - a pseudogene
        # among them. Shrinking keeps absence non-punitive (0.5 is exactly neutral)
        # while stopping it from earning a top score.
        present = {k: v for k, v in comp.items() if v is not None}
        assessed_w = sum(weights[k] for k in present)
        missing_w = sum(weights.values()) - assessed_w
        composite = ((sum(present[k] * weights[k] for k in present) + missing_w * NEUTRAL_PRIOR)
                     / (assessed_w + missing_w))

        withdrawn = float(r.get("n_drugs_withdrawn") or 0)
        boxed = float(r.get("n_drugs_black_box") or 0)
        flagged = withdrawn + boxed
        if not n_drugs or not flagged:
            safety = SAFETY_CLEAN
        else:
            frac_flagged = min(flagged / n_drugs, 1.0)
            if frac_flagged >= 0.999:
                # Exhausted, but a withdrawal is not a boxed warning: the harsher
                # multiplier is reserved for a target whose every drug was pulled.
                safety = SAFETY_EXHAUSTED if withdrawn else SAFETY_MOSTLY_FLAGGED
            elif frac_flagged > 0.5:
                safety = SAFETY_MOSTLY_FLAGGED
            else:
                safety = SAFETY_CLEAN
        route_ok = float(r.get("n_route_appropriate_drugs") or 0)
        topical_only = float(r.get("n_excluded_topical_only") or 0)
        route = ROUTE_INAPPROPRIATE if (n_drugs and not route_ok and topical_only) else 1.00

        rows.append({
            "gene_symbol": r["gene_symbol"], "disease": r["disease"], "manifestation": r["manifestation"],
            **{f"s_{k}": comp.get(k) for k in list(WEIGHTS) + ["cns_delivery"]},
            "n_components_assessed": len(present),
            "coverage": ";".join(cov),
            "composite_evidence": round(composite, 4) if pd.notna(composite) else np.nan,
            "safety_multiplier": safety, "route_multiplier": route,
            "score": round(composite * safety * route, 4) if pd.notna(composite) else np.nan,
            "delivery_basis": delivery_basis, "delivery_from_drug": delivery_moiety,
            "bbb_required": bbb,
            "n_drugs_in_nf_trials": int(r.get("n_drugs_in_nf_trials") or 0),
            "novel_to_nf": bool(comp["drug_stage"] == 1.00 and not (r.get("n_drugs_in_nf_trials") or 0)),
            "insufficient_evidence": len(present) < 2,
        })

    out = pd.DataFrame(rows)
    out["rank_in_stratum"] = out.groupby(["disease", "manifestation"])["score"].rank(
        ascending=False, method="min")
    out = out.sort_values(["disease", "manifestation", "rank_in_stratum"]).reset_index(drop=True)
    out.to_csv(DATA / "phase6-candidate-scores.csv", index=False)

    opg = out[out["bbb_required"]]
    summary = {
        "candidates": len(out),
        "strata": int(out.groupby(["disease", "manifestation"]).ngroups),
        "weights": WEIGHTS, "delivery_weight": DELIVERY_WEIGHT,
        "insufficient_evidence": int(out["insufficient_evidence"].sum()),
        "components_assessed": out["n_components_assessed"].value_counts().sort_index().to_dict(),
        "route_downweighted": int((out["route_multiplier"] < 1).sum()),
        "safety_downweighted": int((out["safety_multiplier"] < 1).sum()),
        "delivery_basis_counts": opg["delivery_basis"].value_counts(dropna=False).to_dict(),
        "score_quartiles": out["score"].quantile([0.25, 0.5, 0.75]).round(3).to_dict(),
        "top_per_stratum": out[out["rank_in_stratum"] == 1][
            ["disease", "manifestation", "gene_symbol", "score"]].to_dict("records"),
        "note": ("Delivery enters only in bbb_required strata. A positive delivery score whose "
                 "delivery_basis is tumor_clinical rests on the same trials that score clinical "
                 "stage - recorded rather than hidden, per Kara 2026-11-16."),
    }
    (DATA / "phase6-candidate-scores-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2)[:2600])


if __name__ == "__main__":
    main()
