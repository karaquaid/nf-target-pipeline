#!/usr/bin/env python3
"""Drug search over the Phase 1b-filtered Phase 5 target set.

This is a JOIN, not a re-query. Phase 4 ran every drug source live on
2026-11-04 (ChEMBL, DGIdb, Open Targets, Guide to Pharmacology, openFDA,
ClinicalTrials.gov) and its coverage over the surviving rows is complete:
selectivity assessed on all of them, tractability on all but 291, and only the
46 rows whose symbol never resolved are 'not queryable'. Six days of database
drift cannot change a candidate's standing, so re-querying would spend hours of
API time to reproduce the same answers. What Phase 4 did NOT provide is
drug-level detail per surviving candidate - the dossier carries summary counts
(n_drugs, top_drugs) - so this script projects phase4-drug-route-flags.csv.gz
onto the filtered set and attaches the Phase 5 support tier, the TME flag and
the per-gene Guide to Pharmacology selectivity summary.

Rows with no drug are kept explicitly rather than dropped, and the two reasons a
candidate can have no drug stay distinguishable:
  no_drug_found   queried in every source, nothing came back
  not_queryable   symbol never resolved, so no source was asked

Usage:
  python phase5_drug_search.py --builddir build/phase5 --datadir <phase>/data
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

KEY = ["gene_symbol", "disease", "manifestation"]
CARRY = ["phase5_support_tier", "tme_target", "coverage_dismech", "dismech_entries",
         "manifestation_hpo_terms", "drug_status", "tractability_status",
         "top_tractability_bucket", "n_chemical_probes", "n_high_quality_probes",
         "target_not_queryable"]


def _true(s: pd.Series) -> pd.Series:
    return s.astype(str).str.lower() == "true"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--builddir", default="build/phase5")
    ap.add_argument("--datadir", default="phase-5-mechanistic-validation/data")
    args = ap.parse_args()
    build, data = Path(args.builddir), Path(args.datadir)

    surv = pd.read_csv(data / "phase5-drug-candidate-set.csv")
    rf = pd.read_csv(build / "phase4-drug-route-flags.csv.gz")
    gtop = pd.read_csv(build / "phase4-gtop-selectivity.csv")

    keys = surv[KEY].drop_duplicates()
    drugs = rf.merge(keys, on=KEY, how="inner")
    drugs = drugs.merge(surv[KEY + CARRY].drop_duplicates(KEY), on=KEY, how="left")

    sel = (gtop.groupby("gene_symbol")
           .agg(gtop_n_ligands=("ligand_id", "nunique"),
                gtop_best_affinity=("affinity_at_target", "max"),
                gtop_min_targets_within_window=("n_targets_within_window", "min"))
           .reset_index())
    drugs = drugs.merge(sel, on="gene_symbol", how="left")
    # --- CNS delivery: clinical evidence overrides the calculated flag ---------
    # Phase 4's cns_penetration_flag comes from ChEMBL CALCULATED properties
    # ("not measured pharmacokinetics", per phase4-admet-provenance.json) and it
    # is wrong on the drugs that matter here: selumetinib, the FDA-approved NF1
    # agent with 18 NF trials, is flagged predicted_non_permeant, as are
    # trametinib, dabrafenib, tovorafenib and lamotrigine - an antiepileptic.
    # A drug tested in a trial for a CNS manifestation has demonstrated delivery
    # whatever a descriptor model predicts, so that evidence is recorded here and
    # the override is reported in its own columns. Phase 4's flag is left intact.
    in_cns_trial = pd.to_numeric(drugs.n_nf_trials, errors="coerce").fillna(0) > 0
    drugs["cns_delivery_evidence"] = "predicted_only"
    drugs.loc[in_cns_trial & _true(drugs.bbb_required),
              "cns_delivery_evidence"] = "clinical_trial_in_cns_manifestation"
    drugs["route_appropriate_clinical"] = (
        _true(drugs.route_appropriate)
        | ((drugs.route_flag == "excluded_not_bbb_penetrant") & in_cns_trial))
    drugs["no_drug_reason"] = pd.NA

    with_drug = set(map(tuple, drugs[KEY].drop_duplicates().values))
    missing = surv[~surv[KEY].apply(tuple, axis=1).isin(with_drug)].copy()
    missing["drug_name"] = pd.NA
    missing["no_drug_reason"] = _true(missing.target_not_queryable).map(
        {True: "not_queryable", False: "no_drug_found"})

    out = pd.concat([drugs, missing[KEY + CARRY + ["drug_name", "no_drug_reason"]]],
                    ignore_index=True, sort=False)
    order = {"A_mechanism": 0, "B_phenotype": 1, "C_other_only": 2, "D_no_edges": 3, "unassessed": 4}
    out["_t"] = out.phase5_support_tier.map(order)
    out = (out.sort_values(["disease", "manifestation", "_t", "gene_symbol",
                            "max_phase_numeric", "drug_name"],
                           ascending=[True, True, True, True, False, True])
           .drop(columns="_t"))
    out.to_csv(data / "phase5-drug-matches.csv.gz", index=False)

    has = out[out.drug_name.notna()]
    phase = pd.to_numeric(has.max_phase_numeric, errors="coerce")
    appropriate = has[_true(has.route_appropriate)]
    clinical = appropriate[pd.to_numeric(appropriate.max_phase_numeric, errors="coerce") >= 3]
    appropriate_ov = has[_true(has.route_appropriate_clinical)]
    clinical_ov = appropriate_ov[pd.to_numeric(appropriate_ov.max_phase_numeric, errors="coerce") >= 3]

    rows = []
    for (dz, man), g in out.groupby(["disease", "manifestation"]):
        gh_ = g[g.drug_name.notna()]
        ph = pd.to_numeric(gh_.max_phase_numeric, errors="coerce")
        rows.append({
            "disease": dz, "manifestation": man,
            "candidate_rows": g[KEY].drop_duplicates().shape[0],
            "rows_with_a_drug": gh_[KEY].drop_duplicates().shape[0],
            "drug_rows": int(len(gh_)),
            "distinct_drugs": int(gh_.drug_name.nunique()),
            "route_appropriate_drug_rows": int(_true(gh_.route_appropriate).sum()),
            "approved_or_phase3_appropriate": int((_true(gh_.route_appropriate) & (ph >= 3)).sum()),
            "drug_rows_in_nf_trials": int((pd.to_numeric(gh_.n_nf_trials, errors="coerce").fillna(0) > 0).sum()),
        })
    by_stratum = pd.DataFrame(rows)
    by_stratum.to_csv(data / "phase5-drugs-by-stratum.csv", index=False)

    short = clinical_ov[clinical_ov.phase5_support_tier.isin(["A_mechanism", "B_phenotype"])]
    short = (short[["gene_symbol", "disease", "manifestation", "phase5_support_tier",
                    "tme_target", "drug_name", "chembl_id", "max_phase_numeric", "routes",
                    "cns_penetration_flag", "bbb_required", "n_nf_trials", "nf_trial_ids",
                    "has_boxed_warning", "serious_reports", "chembl_mechanisms",
                    "evidence_sources", "route_flag", "cns_delivery_evidence"]]
             .sort_values(["disease", "manifestation", "phase5_support_tier",
                           "gene_symbol", "drug_name"]))
    short.to_csv(data / "phase5-supported-target-drugs.csv", index=False)

    summary = {
        "method": "join of phase4-drug-route-flags.csv.gz (sources queried live 2026-11-04) "
                  "onto the Phase 1b-filtered candidate set; no source re-queried",
        "candidate_rows": int(len(surv)),
        "candidate_rows_with_a_drug": int(has[KEY].drop_duplicates().shape[0]),
        "candidate_rows_no_drug_found": int((out.no_drug_reason == "no_drug_found").sum()),
        "candidate_rows_not_queryable": int((out.no_drug_reason == "not_queryable").sum()),
        "drug_rows": int(len(has)),
        "distinct_drugs": int(has.drug_name.nunique()),
        "route_appropriate_drug_rows": int(len(appropriate)),
        "route_appropriate_clinical_stage_rows": int(len(clinical)),
        "route_appropriate_rows_with_clinical_cns_override": int(len(appropriate_ov)),
        "clinical_stage_rows_with_clinical_cns_override": int(len(clinical_ov)),
        "cns_rows_excluded_by_calculated_flag_but_in_an_nf_trial": int(
            ((has.route_flag == "excluded_not_bbb_penetrant")
             & (pd.to_numeric(has.n_nf_trials, errors="coerce").fillna(0) > 0)).sum()),
        "drug_rows_in_nf_trials": int((pd.to_numeric(has.n_nf_trials, errors="coerce").fillna(0) > 0).sum()),
        "shortlist_rows": int(len(short)),
        "shortlist_distinct_drugs": int(short.drug_name.nunique()),
    }
    json.dump(summary, open(data / "phase5-drug-search-summary.json", "w"), indent=2)
    print(json.dumps(summary, indent=2))
    print("\nby stratum:\n", by_stratum.to_string(index=False))


if __name__ == "__main__":
    main()
