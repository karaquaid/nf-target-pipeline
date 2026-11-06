#!/usr/bin/env python3
"""Phase 4: the delivery-route filter and the consolidated target dossier.

Two outputs.

phase4-drug-route-flags.csv.gz is one row per target x manifestation x drug
carrying the route verdict and the reason for it. Per the project plan,
topical delivery is acceptable only for Cutaneous neurofibroma and ANNUBP /
atypical neurofibroma; every other manifestation needs a systemic route;
and the CNS-relevant manifestations additionally need the drug to be
predicted blood-brain-barrier penetrant. Mismatches are FLAGGED, never
dropped, so Phase 6 can see what was excluded and why.

phase4-target-dossier.csv is one row per target x disease x manifestation:
the evidence that put the target on the list, what drugs exist for it, how
far they have got clinically, whether any has been tried in an NF trial,
what the target's tractability looks like when no drug exists, and the
safety signals attached to its drugs.

Three distinctions this file is careful about, because collapsing any of
them would turn an absence of data into a negative finding:

  - no_drug_match True means every source was queried and returned nothing.
  - target_not_queryable means the symbol never resolved to an identifier.
  - a source that failed (openFDA past its request budget, Guide to
    Pharmacology without a key) leaves "not assessed", not "none found".

Run from the repo root, after the fetch scripts:
  python phase-4/scripts/phase4_dossier.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

TOPICAL_ELIGIBLE = {"Cutaneous neurofibroma", "ANNUBP / atypical neurofibroma"}

# openFDA label routes that deliver a drug systemically.
SYSTEMIC_LABEL_ROUTES = {
    "ORAL",
    "INTRAVENOUS",
    "SUBCUTANEOUS",
    "INTRAMUSCULAR",
    "INTRAPERITONEAL",
    "INTRATHECAL",
    "TRANSDERMAL",
    "SUBLINGUAL",
    "RECTAL",
    "BUCCAL",
    "NASAL",
    "INTRAVENOUS DRIP",
    "PARENTERAL",
}
TOPICAL_LABEL_ROUTES = {"TOPICAL", "CUTANEOUS", "OPHTHALMIC", "OTIC", "DENTAL", "INTRALESIONAL"}

TRACTABILITY_PRIORITY = [
    "Approved Drug",
    "Advanced Clinical",
    "Phase 1 Clinical",
    "Structure with Ligand",
    "High-Quality Ligand",
    "High-Quality Pocket",
    "Med-Quality Pocket",
    "Druggable Family",
]


def read_optional(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def route_verdict(row) -> tuple:
    """Returns (flag, reason). Never drops a drug."""
    manifestation = row["manifestation"]
    topical_ok = manifestation in TOPICAL_ELIGIBLE

    chembl_oral = bool(row.get("oral") is True)
    chembl_parenteral = bool(row.get("parenteral") is True)
    chembl_topical = bool(row.get("topical") is True)
    label_routes = {
        r.strip().upper() for r in str(row.get("routes") or "").split(";") if r.strip()
    }
    systemic = chembl_oral or chembl_parenteral or bool(label_routes & SYSTEMIC_LABEL_ROUTES)
    topical = chembl_topical or bool(label_routes & TOPICAL_LABEL_ROUTES)

    if not systemic and not topical:
        phase = row.get("max_phase_numeric")
        if pd.isna(phase) or phase < 1:
            # ChEMBL sets the route booleans only for compounds with clinical
            # data, so a preclinical compound has no route by construction.
            # This is the expected state for most screening-derived hits.
            return (
                "route_unknown",
                "preclinical compound: no clinical route recorded, so the delivery filter "
                "cannot be applied yet",
            )
        return ("route_unknown", "no route recorded in ChEMBL or an openFDA label")

    if topical and not systemic:
        if topical_ok:
            return ("appropriate_topical", f"topical delivery is acceptable for {manifestation}")
        return (
            "excluded_topical_only",
            f"topical-only, excluded for {manifestation}, which needs a systemic route",
        )

    if not row.get("bbb_required"):
        return ("appropriate_systemic", "systemic route available")

    cns = row.get("cns_penetration_flag")
    if cns == "predicted_permeant":
        return (
            "appropriate_systemic_cns",
            "systemic route available and predicted blood-brain-barrier penetrant",
        )
    if cns == "not_applicable_biologic":
        return (
            "excluded_biologic_cns",
            f"biologic, not expected to cross an intact barrier, flagged for {manifestation}",
        )
    if cns == "predicted_non_permeant":
        return (
            "excluded_not_bbb_penetrant",
            f"systemic but predicted not blood-brain-barrier penetrant, flagged for {manifestation}",
        )
    return (
        "cns_penetration_unknown",
        "systemic route available; no calculated properties to predict barrier penetration",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    data = root / "phase-4/data"

    targets = pd.read_csv(data / "phase4-targets.csv")
    identifiers = pd.read_csv(data / "phase4-identifiers.csv")
    interactions = pd.read_csv(data / "phase4-drug-interactions.csv.gz")
    tract = pd.read_csv(data / "phase4-opentargets-tractability.csv")
    probes = read_optional(data / "phase4-opentargets-probes.csv")
    admet = pd.read_csv(data / "phase4-admet.csv.gz")
    labels = read_optional(data / "phase4-openfda-labels.csv")
    approvals = read_optional(data / "phase4-openfda-approvals.csv")
    faers = read_optional(data / "phase4-faers.csv")
    trial_drugs = read_optional(data / "phase4-trial-drugs.csv")
    selectivity = read_optional(data / "phase4-gtop-selectivity.csv")

    # ---------- drug-level attributes ----------
    drugs = interactions[interactions["has_any_interaction"]].copy()
    drugs["drug_key"] = drugs["drug_name"].fillna("").astype(str).str.upper().str.strip()

    if len(admet):
        drugs = drugs.merge(
            admet[["molecule_chembl_id", "cns_penetration_flag", "molecule_type"]].rename(
                columns={"molecule_chembl_id": "chembl_id", "molecule_type": "admet_molecule_type"}
            ),
            on="chembl_id",
            how="left",
        )
    if len(labels):
        drugs = drugs.merge(
            labels[["drug_key", "routes", "has_boxed_warning", "openfda_queried"]],
            on="drug_key",
            how="left",
        )
    else:
        drugs["routes"] = pd.NA
        drugs["has_boxed_warning"] = pd.NA
        drugs["openfda_queried"] = False
    if len(faers) and "drug_key" in faers.columns:
        drugs = drugs.merge(faers, on="drug_key", how="left")
    for col in ("total_reports", "serious_reports"):
        if col not in drugs.columns:
            drugs[col] = pd.NA
    if len(approvals):
        app = approvals.groupby("drug_key", as_index=False).agg(
            marketing_statuses=("marketing_statuses", "first"),
            first_approval_date=("first_approval_date", "min"),
        )
        drugs = drugs.merge(app, on="drug_key", how="left")
    else:
        drugs["marketing_statuses"] = pd.NA
        drugs["first_approval_date"] = pd.NA

    if len(trial_drugs):
        in_nf_trial = (
            trial_drugs[trial_drugs["matches_phase4_drug"]]
            .groupby("intervention_key", as_index=False)
            .agg(
                nf_trial_ids=("nct_id", lambda s: "; ".join(sorted(set(s))[:10])),
                n_nf_trials=("nct_id", "nunique"),
                nf_trial_phases=(
                    "phases",
                    lambda s: "; ".join(sorted({x for v in s.dropna() for x in str(v).split("; ") if x})),
                ),
            )
            .rename(columns={"intervention_key": "drug_key"})
        )
        drugs = drugs.merge(in_nf_trial, on="drug_key", how="left")
    else:
        drugs["n_nf_trials"] = pd.NA
        drugs["nf_trial_ids"] = pd.NA

    if len(selectivity):
        sel = selectivity.groupby("gene_symbol", as_index=False).agg(
            gtop_min_targets_within_window=("n_targets_within_window", "min"),
            gtop_best_affinity=("affinity_at_target", "max"),
            gtop_n_ligands=("ligand_id", "nunique"),
        )
    else:
        sel = pd.DataFrame(
            columns=[
                "gene_symbol",
                "gtop_min_targets_within_window",
                "gtop_best_affinity",
                "gtop_n_ligands",
            ]
        )

    # ---------- route filter, one row per target x manifestation x drug ----------
    pairs = targets[["gene_symbol", "disease", "manifestation", "bbb_required"]].merge(
        drugs, on="gene_symbol", how="inner"
    )
    verdicts = pairs.apply(route_verdict, axis=1, result_type="expand")
    pairs["route_flag"] = verdicts[0]
    pairs["route_reason"] = verdicts[1]
    pairs["route_appropriate"] = pairs["route_flag"].str.startswith("appropriate")
    keep = [
        "gene_symbol",
        "disease",
        "manifestation",
        "drug_name",
        "chembl_id",
        "evidence_sources",
        "max_phase_numeric",
        "oral",
        "parenteral",
        "topical",
        "routes",
        "cns_penetration_flag",
        "bbb_required",
        "route_flag",
        "route_reason",
        "route_appropriate",
        "withdrawn_flag",
        "black_box_warning",
        "has_boxed_warning",
        "total_reports",
        "serious_reports",
        "n_nf_trials",
        "nf_trial_ids",
        "marketing_statuses",
        "first_approval_date",
        "chembl_action_types",
        "chembl_mechanisms",
        "dgidb_sources",
        "openfda_queried",
    ]
    pairs[[c for c in keep if c in pairs.columns]].to_csv(
        data / "phase4-drug-route-flags.csv.gz", index=False, compression="gzip"
    )

    # ---------- tractability per target ----------
    tract_true = tract[tract["value"] == True]  # noqa: E712
    best_bucket = (
        tract_true.assign(
            priority=tract_true["bucket"].map(
                {b: i for i, b in enumerate(TRACTABILITY_PRIORITY)}
            ).fillna(99)
        )
        .sort_values("priority")
        .groupby("gene_symbol", as_index=False)
        .agg(
            top_tractability_bucket=("bucket", "first"),
            top_tractability_modality=("modality", "first"),
            tractable_modalities=("modality", lambda s: "; ".join(sorted(set(s)))),
            n_tractability_buckets=("bucket", "size"),
        )
    )
    probe_agg = (
        probes.groupby("gene_symbol", as_index=False).agg(
            n_chemical_probes=("probe_id", "nunique"),
            n_high_quality_probes=("is_high_quality", "sum"),
        )
        if len(probes)
        else pd.DataFrame(columns=["gene_symbol", "n_chemical_probes", "n_high_quality_probes"])
    )

    # ---------- per target x manifestation summary ----------
    def agg_pairs(frame: pd.DataFrame) -> pd.DataFrame:
        return frame.groupby(["gene_symbol", "disease", "manifestation"], as_index=False).agg(
            n_drugs=("drug_name", "nunique"),
            n_drugs_approved=("max_phase_numeric", lambda s: int((s == 4).sum())),
            best_max_phase=("max_phase_numeric", "max"),
            n_route_appropriate_drugs=("route_appropriate", "sum"),
            n_excluded_topical_only=("route_flag", lambda s: int((s == "excluded_topical_only").sum())),
            n_excluded_not_bbb=(
                "route_flag",
                lambda s: int(s.isin({"excluded_not_bbb_penetrant", "excluded_biologic_cns"}).sum()),
            ),
            n_route_unknown=("route_flag", lambda s: int((s == "route_unknown").sum())),
            n_drugs_in_nf_trials=("n_nf_trials", lambda s: int(s.notna().sum())),
            n_drugs_black_box=("has_boxed_warning", lambda s: int((s == True).sum())),  # noqa: E712
            n_drugs_withdrawn=("withdrawn_flag", lambda s: int((s == True).sum())),  # noqa: E712
            max_faers_reports=("total_reports", "max"),
            top_drugs=(
                "drug_name",
                lambda s: "; ".join(list(dict.fromkeys(str(x) for x in s if pd.notna(x)))[:8]),
            ),
        )

    summary = agg_pairs(pairs)
    dossier = (
        targets.merge(summary, on=["gene_symbol", "disease", "manifestation"], how="left")
        .merge(best_bucket, on="gene_symbol", how="left")
        .merge(probe_agg, on="gene_symbol", how="left")
        .merge(sel, on="gene_symbol", how="left")
        .merge(
            identifiers[["gene_symbol", "match_type", "uniprot_accession", "ensembl_gene_id"]],
            on="gene_symbol",
            how="left",
        )
    )

    count_cols = [
        "n_drugs",
        "n_drugs_approved",
        "n_route_appropriate_drugs",
        "n_excluded_topical_only",
        "n_excluded_not_bbb",
        "n_route_unknown",
        "n_drugs_in_nf_trials",
        "n_drugs_black_box",
        "n_drugs_withdrawn",
        "n_chemical_probes",
        "n_high_quality_probes",
        "n_tractability_buckets",
    ]
    for col in count_cols:
        dossier[col] = dossier[col].fillna(0).astype(int)

    dossier["target_not_queryable"] = dossier["match_type"].isin(
        {"not_a_gene_symbol", "unresolved"}
    )
    dossier["no_drug_match"] = (dossier["n_drugs"] == 0) & ~dossier["target_not_queryable"]
    dossier["drug_status"] = [
        "not queryable"
        if nq
        else ("no drug found in any source" if n == 0 else "drug found")
        for nq, n in zip(dossier["target_not_queryable"], dossier["n_drugs"])
    ]
    dossier["selectivity_status"] = (
        "assessed" if len(selectivity) else "not assessed: Guide to Pharmacology key not available"
    )
    dossier["tractability_status"] = [
        "assessed" if pd.notna(b) else "no tractability bucket returned"
        for b in dossier["top_tractability_bucket"]
    ]

    dossier = dossier.sort_values(
        ["disease", "manifestation", "n_route_appropriate_drugs", "n_drugs"],
        ascending=[True, True, False, False],
    )
    dossier.to_csv(data / "phase4-target-dossier.csv", index=False)

    stats = {
        "dossier_rows": int(len(dossier)),
        "distinct_targets": int(dossier["gene_symbol"].nunique()),
        "rows_with_a_drug": int((dossier["n_drugs"] > 0).sum()),
        "rows_with_no_drug_match": int(dossier["no_drug_match"].sum()),
        "rows_not_queryable": int(dossier["target_not_queryable"].sum()),
        "targets_with_a_drug": int(dossier.loc[dossier["n_drugs"] > 0, "gene_symbol"].nunique()),
        "targets_with_tractability_bucket": int(
            dossier.loc[dossier["top_tractability_bucket"].notna(), "gene_symbol"].nunique()
        ),
        "undrugged_but_tractable_targets": int(
            dossier.loc[
                (dossier["n_drugs"] == 0) & dossier["top_tractability_bucket"].notna(),
                "gene_symbol",
            ].nunique()
        ),
        "route_flag_counts": pairs["route_flag"].value_counts().to_dict(),
        "drug_rows_flagged": int(len(pairs)),
    }
    (data / "phase4-dossier-stats.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
