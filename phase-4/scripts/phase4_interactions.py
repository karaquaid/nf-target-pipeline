#!/usr/bin/env python3
"""Phase 4: one consolidated target-drug interaction table.

Joins the three interaction sources into one row per target x drug, with
the provenance of every claim kept so the scoring phase can weight a
curated pharmacology claim differently from a high-throughput screen hit:

  - DGIdb interaction claims, each naming its upstream source databases.
  - Open Targets drug and clinical candidate rows, which are ChEMBL-derived
    and carry the clinical stage reached for that specific target.
  - ChEMBL mechanism of action records, which say what the drug does to the
    target rather than only that a relationship exists.

Drugs are keyed on ChEMBL id where one exists. DGIdb drugs carrying only an
RxNorm, NCIt or IUPHAR concept id keep that id and are marked, because they
cannot be joined to the ChEMBL drug record.

A target with no interaction from any source gets an explicit row with
has_any_interaction False, so the dossier can distinguish "queried, nothing
found" from "not queried".

Output:
  phase-4/data/phase4-drug-interactions.csv.gz
  phase-4/data/phase4-interaction-summary.csv

Run from the repo root:
  python phase-4/scripts/phase4_interactions.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

# DGIdb aggregates curated pharmacology alongside large screening panels.
# The split is recorded, not applied: filtering belongs to Phase 6.
SCREENING_SOURCES = {"PRISM", "NCI60", "Drug Repurposing Hub", "DTC"}


def norm_name(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().str.upper()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    data = root / "phase-4/data"

    identifiers = pd.read_csv(data / "phase4-identifiers.csv")
    dgidb = pd.read_csv(data / "phase4-dgidb-interactions.csv.gz")
    ot = pd.read_csv(data / "phase4-opentargets-drugs.csv.gz")
    mech = pd.read_csv(data / "phase4-chembl-mechanisms.csv.gz")
    drugs = pd.read_csv(data / "phase4-chembl-drugs.csv.gz")

    # Map the query term each source was asked about back to the project's
    # own gene symbol, so a corrected symbol does not split into two rows.
    term_to_symbol = dict(
        zip(identifiers["query_term"].fillna(""), identifiers["gene_symbol"])
    )

    dg = dgidb.copy()
    dg["gene_symbol"] = dg["gene_symbol"].map(term_to_symbol).fillna(dg["gene_symbol"])
    dg["chembl_id"] = (
        dg["drug_concept_id"]
        .where(dg["drug_concept_id"].str.startswith("chembl:"), "")
        .str.split(":")
        .str[-1]
        .str.upper()
        .replace("", pd.NA)
    )
    dg["source_namespace"] = dg["drug_concept_id"].str.split(":").str[0]
    dg["dgidb_screening_only"] = dg["sources"].fillna("").apply(
        lambda s: bool(set(x.strip() for x in s.split(";") if x.strip()))
        and set(x.strip() for x in s.split(";") if x.strip()) <= SCREENING_SOURCES
    )
    dg_agg = dg.groupby(["gene_symbol", "drug_name"], as_index=False).agg(
        dgidb_chembl_id=("chembl_id", "first"),
        dgidb_concept_id=("drug_concept_id", "first"),
        dgidb_namespace=("source_namespace", "first"),
        dgidb_approved=("drug_approved", "max"),
        dgidb_antineoplastic=("drug_antineoplastic", "max"),
        dgidb_max_score=("interaction_score", "max"),
        dgidb_interaction_types=(
            "interaction_types",
            lambda s: "; ".join(sorted({x for v in s.dropna() for x in str(v).split("; ") if x})),
        ),
        dgidb_sources=(
            "sources",
            lambda s: "; ".join(sorted({x for v in s.dropna() for x in str(v).split("; ") if x})),
        ),
        dgidb_pmids=(
            "pmids",
            lambda s: "; ".join(sorted({x for v in s.dropna() for x in str(v).split("; ") if x})),
        ),
        dgidb_screening_only=("dgidb_screening_only", "min"),
    )
    dg_agg["in_dgidb"] = True

    ot_agg = ot.copy()
    ot_agg["gene_symbol"] = ot_agg["gene_symbol"].map(term_to_symbol).fillna(ot_agg["gene_symbol"])
    ot_agg["drug_name_key"] = norm_name(ot_agg["drug_name"])
    ot_agg = ot_agg.groupby(["gene_symbol", "chembl_id"], as_index=False).agg(
        ot_drug_name=("drug_name", "first"),
        ot_drug_type=("drug_type", "first"),
        ot_max_stage_for_target=("max_clinical_stage_for_target", "first"),
        ot_drug_max_stage=("drug_max_clinical_stage", "first"),
        ot_n_diseases=("n_diseases", "max"),
        ot_diseases=("diseases", "first"),
    )
    ot_agg["in_open_targets"] = True

    # ChEMBL mechanisms are keyed on a ChEMBL target, not a gene symbol, so
    # they attach to the drug and are summarised per drug here.
    mech_agg = mech.groupby("molecule_chembl_id", as_index=False).agg(
        chembl_action_types=(
            "action_type",
            lambda s: "; ".join(sorted({str(x) for x in s.dropna()})),
        ),
        chembl_mechanisms=(
            "mechanism_of_action",
            lambda s: "; ".join(sorted({str(x) for x in s.dropna()})),
        ),
        chembl_selectivity_comment=(
            "selectivity_comment",
            lambda s: "; ".join(sorted({str(x) for x in s.dropna()})),
        ),
        chembl_direct_interaction=("direct_interaction", "max"),
        chembl_disease_efficacy=("disease_efficacy", "max"),
    )

    merged = dg_agg.merge(
        ot_agg,
        left_on=["gene_symbol", "dgidb_chembl_id"],
        right_on=["gene_symbol", "chembl_id"],
        how="outer",
    )
    merged["chembl_id"] = merged["chembl_id"].fillna(merged["dgidb_chembl_id"])
    merged["drug_name"] = merged["drug_name"].fillna(merged["ot_drug_name"])
    for flag in ("in_dgidb", "in_open_targets"):
        merged[flag] = merged[flag].notna() & merged[flag].astype(bool)

    merged = merged.merge(
        mech_agg, left_on="chembl_id", right_on="molecule_chembl_id", how="left"
    )
    merged["in_chembl_mechanism"] = merged["molecule_chembl_id"].notna()
    merged = merged.merge(
        drugs.rename(columns={"molecule_chembl_id": "chembl_id"}),
        on="chembl_id",
        how="left",
        suffixes=("", "_drug"),
    )

    merged["evidence_sources"] = [
        "; ".join(
            [s for s, flag in (("DGIdb", d), ("OpenTargets", o), ("ChEMBL", c)) if flag]
        )
        for d, o, c in zip(
            merged["in_dgidb"], merged["in_open_targets"], merged["in_chembl_mechanism"]
        )
    ]
    merged["has_any_interaction"] = True

    # Targets queried but with nothing from any source.
    queried = identifiers[identifiers["query_term"].fillna("") != ""]["gene_symbol"]
    with_hits = set(merged["gene_symbol"])
    empties = pd.DataFrame(
        {
            "gene_symbol": sorted(set(queried) - with_hits),
            "has_any_interaction": False,
            "evidence_sources": "",
        }
    )
    not_queried = identifiers[identifiers["query_term"].fillna("") == ""][["gene_symbol"]].copy()
    not_queried["has_any_interaction"] = False
    not_queried["evidence_sources"] = "not queryable"

    out = pd.concat([merged, empties, not_queried], ignore_index=True)
    out = out.drop(columns=["molecule_chembl_id", "ot_drug_name"], errors="ignore")
    out = out.sort_values(["gene_symbol", "drug_name"], na_position="last")
    out.to_csv(data / "phase4-drug-interactions.csv.gz", index=False, compression="gzip")

    hits = out[out["has_any_interaction"]]
    summary = (
        hits.groupby("gene_symbol")
        .agg(
            n_drugs=("drug_name", "nunique"),
            n_drugs_with_chembl_id=("chembl_id", "nunique"),
            n_drugs_approved=("max_phase_numeric", lambda s: int((s == 4).sum())),
            n_drugs_with_mechanism=("in_chembl_mechanism", "sum"),
            sources=("evidence_sources", lambda s: "; ".join(sorted({x for v in s for x in str(v).split("; ") if x}))),
        )
        .reset_index()
        .sort_values("n_drugs", ascending=False)
    )
    summary.to_csv(data / "phase4-interaction-summary.csv", index=False)

    print(f"interaction rows: {len(hits)}")
    print(f"targets with at least one drug: {hits['gene_symbol'].nunique()}")
    print(f"targets queried with nothing found: {len(empties)}")
    print(f"targets not queryable: {len(not_queried)}")
    print(f"distinct drugs: {hits['drug_name'].nunique()}")
    print(
        "drugs approved (ChEMBL max_phase 4): "
        f"{int((hits.drop_duplicates('chembl_id')['max_phase_numeric'] == 4).sum())}"
    )


if __name__ == "__main__":
    main()
