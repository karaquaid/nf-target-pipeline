#!/usr/bin/env python3
"""Phase 8 validation: does the pipeline recover the targets with NF clinical precedent?

The standard is built in `phase8-validation-set.csv` from the drugs actually trialled in
neurofibromatosis: a gene qualifies when a drug with a directional interaction against it
(inhibitor, antagonist, agonist, blocker or modulator) was an intervention in a trial the
Phase 4 table flags `nf_specific`. This asks whether the pipeline surfaces each such gene in the
disease and manifestation stratum its trial evidence implies.

What this is and is not. It tests recall of the already-known, and parts of the pipeline were
built from the same evidence, so it is a sanity check rather than an independent validation. A
pipeline that cannot recover the approved NF drug's target is demonstrably broken; passing does
not prove the converse.

Which list each stage is read from, per the ruling of 2026-11-17:
  phase3-candidate-targets.csv       the capped top-200 ranking list, which feeds Phase 4
  phase3-expression-targets.csv.gz   the full table, read to separate "not measured" from
                                     "measured but below the cap"

Outcome per gene x disease x manifestation, in order of precedence:
  scored                       Phase 6 scored it in that stratum
  annotated_not_scored         Phase 4 carried it, Phase 6 did not score it
  below_cap                    in the full expression table for that stratum, not in the capped list
  not_differentially_expressed not in the full expression table for that stratum. Note what this
                               does and does not say: the full table holds genes Phase 3 called
                               in at least one dataset or scored by aggregation, not every gene
                               measured. The measured universe lives in build/phase3/universe.csv,
                               which is not committed, so "measured but not called" cannot be
                               separated from "not measured" here
  stratum_not_selected         Phase 3b did not carry that disease x manifestation into Phase 4
  disease_level_only           the trial named no manifestation; checked against any stratum of
                               that disease and reported separately

Inputs
  phase-8/data/phase8-validation-set.csv
  phase-3/data/phase3-candidate-targets.csv
  phase-3/data/phase3-expression-targets.csv.gz
  phase-4/data/phase4-target-dossier.csv
  phase-6-evidence-scoring/data/phase6-candidate-scores.csv

Outputs
  phase-8/data/phase8-validation-results.csv
  phase-8/data/phase8-validation-summary.json

Run from the repo root:
    python phase-8/scripts/phase8_validate.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

DISEASE_LEVEL = "(disease-level trial, no manifestation)"


def expression_strata(df: pd.DataFrame) -> set[tuple[str, str]]:
    """Phase 3 carries a pipe-joined manifestation list per contrast; expand it."""
    pairs = set()
    for _, r in df[["gene_symbol", "disease", "manifestations"]].dropna().iterrows():
        for m in str(r["manifestations"]).split("|"):
            pairs.add((r["gene_symbol"], r["disease"], m.strip()))
    return pairs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    data = repo / "phase-8" / "data"

    vset = pd.read_csv(data / "phase8-validation-set.csv")
    capped = pd.read_csv(repo / "phase-3/data/phase3-candidate-targets.csv")
    full = pd.read_csv(repo / "phase-3/data/phase3-expression-targets.csv.gz", low_memory=False)
    dossier = pd.read_csv(repo / "phase-4/data/phase4-target-dossier.csv", low_memory=False)
    scores = pd.read_csv(repo / "phase-6-evidence-scoring/data/phase6-candidate-scores.csv",
                         low_memory=False)

    cap_set = expression_strata(capped)
    full_set = expression_strata(full)
    dos_set = set(map(tuple, dossier[["gene_symbol", "disease", "manifestation"]].values))
    selected = set(map(tuple, scores[["disease", "manifestation"]].drop_duplicates().values))
    score_ix = scores.set_index(["gene_symbol", "disease", "manifestation"])

    combos = vset[["gene_symbol", "disease", "manifestation"]].drop_duplicates()
    rows = []
    for _, c in combos.iterrows():
        gene, disease, manif = c.gene_symbol, c.disease, c.manifestation
        drugs = sorted(set(vset[(vset.gene_symbol == gene) & (vset.disease == disease)
                                & (vset.manifestation == manif)].drug))
        ncts = sorted(set(vset[(vset.gene_symbol == gene) & (vset.disease == disease)
                               & (vset.manifestation == manif)].nct_id))
        rec = {"gene_symbol": gene, "disease": disease, "manifestation": manif,
               "drugs": ";".join(drugs), "nct_ids": ";".join(ncts),
               "n_drugs": len(drugs), "n_trials": len(ncts)}

        if manif == DISEASE_LEVEL:
            # The trial names no manifestation, so any stratum of that disease counts.
            hits = [(d, m) for (g, d, m) in dos_set if g == gene and d == disease]
            scored = [(d, m) for (d, m) in hits if (gene, d, m) in score_ix.index]
            rec.update(outcome="disease_level_only",
                       in_capped_expression=any(g == gene and d == disease for g, d, _ in cap_set),
                       in_full_expression=any(g == gene and d == disease for g, d, _ in full_set),
                       in_phase4=bool(hits), n_strata_scored=len(scored),
                       strata_scored=";".join(sorted(f"{d} / {m}" for d, m in scored)),
                       best_rank_in_stratum="", score="")
            rows.append(rec)
            continue

        key = (gene, disease, manif)
        rec["in_capped_expression"] = key in cap_set
        rec["in_full_expression"] = key in full_set
        rec["in_phase4"] = key in dos_set
        if key in score_ix.index:
            r = score_ix.loc[key]
            r = r.iloc[0] if isinstance(r, pd.DataFrame) else r
            rec.update(outcome="scored", score=round(float(r["score"]), 4),
                       best_rank_in_stratum=int(r["rank_in_stratum"]),
                       n_strata_scored=1, strata_scored=f"{disease} / {manif}")
        else:
            rec.update(score="", best_rank_in_stratum="", n_strata_scored=0, strata_scored="")
            if key in dos_set:
                rec["outcome"] = "annotated_not_scored"
            elif (disease, manif) not in selected:
                rec["outcome"] = "stratum_not_selected"
            elif key in full_set:
                rec["outcome"] = "below_cap"
            else:
                rec["outcome"] = "not_differentially_expressed"
        rows.append(rec)

    out = pd.DataFrame(rows).sort_values(["outcome", "gene_symbol", "disease", "manifestation"])
    out.to_csv(data / "phase8-validation-results.csv", index=False)

    counts = out.outcome.value_counts().to_dict()
    manif_level = out[out.outcome != "disease_level_only"]
    summary = {
        "validation_set": {
            "genes": int(vset.gene_symbol.nunique()),
            "drugs": int(vset.drug.nunique()),
            "trials": int(vset.nct_id.nunique()),
            "gene_disease_manifestation_combinations": int(len(combos)),
        },
        "outcomes": counts,
        "manifestation_level": {
            "combinations": int(len(manif_level)),
            "scored": int((manif_level.outcome == "scored").sum()),
            "recall_scored": round(float((manif_level.outcome == "scored").mean()), 4),
            "genes_scored_somewhere": int(out[out.n_strata_scored > 0].gene_symbol.nunique()),
            "genes_in_set": int(vset.gene_symbol.nunique()),
        },
        "list_used": {
            "ranking": "phase-3/data/phase3-candidate-targets.csv (capped top-200)",
            "measured_universe": "phase-3/data/phase3-expression-targets.csv.gz (full table)",
        },
        "limitation": ("Tests recall of the already-known. Parts of the pipeline were built from "
                       "the same trial evidence, so this is a sanity check, not an independent "
                       "validation."),
    }
    (data / "phase8-validation-summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    print(f"{len(combos)} gene x disease x manifestation combinations")
    for k, v in counts.items():
        print(f"  {k:24} {v}")
    print(f"\nmanifestation-level recall (scored): "
          f"{summary['manifestation_level']['scored']}/{summary['manifestation_level']['combinations']}"
          f" = {summary['manifestation_level']['recall_scored']:.1%}")
    print(f"genes scored in at least one stratum: "
          f"{summary['manifestation_level']['genes_scored_somewhere']}/"
          f"{summary['manifestation_level']['genes_in_set']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
