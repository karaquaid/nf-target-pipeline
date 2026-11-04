#!/usr/bin/env python3
"""Phase 3b: evidence coverage per disease x manifestation.

Combines the literature-derived candidate list (Phase 1b) with the
expression-derived candidate list (Phase 3) and counts, for every
combination of disease and manifestation in the project's fixed
vocabulary, how much evidence of each kind exists.

Combinations with zero evidence are written out explicitly rather than
omitted: the point of the table is to show where the project has nothing.

Inputs (committed):
  phase-1b/data/phase1b-candidate-targets.csv
  phase-3/data/phase3-candidate-targets.csv
  phase-3/data/phase3-contrast-labels.csv

Outputs:
  phase-3b/data/phase3b-coverage.csv
  phase-3b/data/phase3b-stratum-summary.csv

Run from the repo root:
  python phase-3b/scripts/phase3b_coverage.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

# The fixed manifestation vocabulary from docs/project-plan.md, applied as-is.
MANIFESTATIONS = [
    "Bone defects",
    "Cardiovascular issues",
    "Cognition / Behavioral / Learning",
    "Sleep",
    "Cutaneous neurofibroma",
    "Ependymoma",
    "Gastrointestinal stromal tumor (GIST)",
    "Hematologic malignancies",
    "High grade glioma",
    "Malignant peripheral nerve sheath tumor (MPNST)",
    "Meningioma",
    "Optic pathway glioma",
    "Non-optic LGG",
    "Pain",
    "Plexiform neurofibroma",
    "ANNUBP / atypical neurofibroma",
    "Pulmonary disease",
    "Non-vestibular schwannoma",
    "Vestibular schwannoma",
    "Other",
]
DISEASES = ["NF1", "NF2-SWN", "SWN"]

TIER_COLS = {
    "A_aggregated": "expr_targets_tier_a",
    "B_replicated": "expr_targets_tier_b",
    "C_single_dataset": "expr_targets_tier_c",
}

# The tiers that mean more than one dataset backed the gene.
CROSS_DATASET_TIERS = ["A_aggregated", "B_replicated"]


def check_vocabulary(values, where: str) -> None:
    unknown = sorted(set(values) - set(MANIFESTATIONS))
    if unknown:
        raise SystemExit(f"{where}: manifestation outside the fixed vocabulary: {unknown}")


def load_literature(path: Path) -> pd.DataFrame:
    lit = pd.read_csv(path)
    check_vocabulary(lit["manifestation"], path.name)
    unknown_disease = sorted(set(lit["disease"]) - set(DISEASES))
    if unknown_disease:
        raise SystemExit(f"{path.name}: disease outside the fixed vocabulary: {unknown_disease}")
    return lit


def load_expression(path: Path) -> pd.DataFrame:
    """One row per candidate gene x direction x stratum, exploded to one
    row per manifestation, since a stratum can carry several labels."""
    expr = pd.read_csv(path)
    expr = expr.assign(manifestation=expr["manifestations"].str.split("|")).explode("manifestation")
    expr["manifestation"] = expr["manifestation"].str.strip()
    check_vocabulary(expr["manifestation"], path.name)
    return expr


def split_ids(series: pd.Series, sep: str) -> set:
    out: set = set()
    for value in series.dropna():
        out.update(part.strip() for part in str(value).split(sep) if part.strip())
    return out


def literature_cell(rows: pd.DataFrame) -> dict:
    if rows.empty:
        return {
            "lit_targets": 0,
            "lit_targets_fulltext": 0,
            "lit_papers": 0,
            "lit_top_targets": "",
        }
    fulltext = rows[rows["evidence_tier"] == "full text - supported"]
    top = rows.sort_values("n_supporting_papers", ascending=False)["gene_target"].head(5).tolist()
    return {
        "lit_targets": rows["gene_target"].nunique(),
        "lit_targets_fulltext": fulltext["gene_target"].nunique(),
        "lit_papers": len(split_ids(rows["supporting_pmids"], ";")),
        "lit_top_targets": "; ".join(top),
    }


def expression_cell(rows: pd.DataFrame) -> dict:
    if rows.empty:
        return {
            "expr_targets": 0,
            "expr_targets_tier_a": 0,
            "expr_targets_tier_b": 0,
            "expr_targets_tier_c": 0,
            "expr_targets_cross_dataset": 0,
            "expr_datasets": 0,
            "expr_strata": "",
            "expr_top_targets": "",
        }
    cell = {"expr_targets": rows["gene_symbol"].nunique()}
    for tier, col in TIER_COLS.items():
        cell[col] = rows.loc[rows["evidence_tier"] == tier, "gene_symbol"].nunique()
    # Distinct genes with cross-dataset support, counted here rather than left to
    # consumers to add the tier A and tier B columns together. A manifestation can
    # draw on several strata, and a gene can be tier A in one and tier B in another,
    # so those two columns overlap and their sum double-counts such a gene. Five
    # genes currently sit in both for NF1 MPNST and plexiform neurofibroma.
    cell["expr_targets_cross_dataset"] = rows.loc[
        rows["evidence_tier"].isin(CROSS_DATASET_TIERS), "gene_symbol"
    ].nunique()
    cell["expr_datasets"] = len(split_ids(rows["measuring_datasets"], ";"))
    cell["expr_strata"] = "; ".join(sorted(rows["comparison_class"].unique()))
    best = rows.sort_values(["evidence_tier", "rank_in_stratum"])
    cell["expr_top_targets"] = "; ".join(best["gene_symbol"].drop_duplicates().head(5).tolist())
    return cell


def constituent_set(lit_rows: pd.DataFrame) -> set:
    """Phase 1b targets can be family labels; compare on constituent genes."""
    genes: set = set()
    for _, row in lit_rows.iterrows():
        if isinstance(row.get("constituent_genes"), str) and row["constituent_genes"].strip():
            genes.update(g.strip() for g in row["constituent_genes"].split(";") if g.strip())
        else:
            genes.add(str(row["gene_target"]).strip())
    return genes


def build_coverage(lit: pd.DataFrame, expr: pd.DataFrame) -> pd.DataFrame:
    records = []
    for disease in DISEASES:
        for manifestation in MANIFESTATIONS:
            lit_rows = lit[(lit["disease"] == disease) & (lit["manifestation"] == manifestation)]
            expr_rows = expr[
                (expr["disease"] == disease) & (expr["manifestation"] == manifestation)
            ]
            record = {"disease": disease, "manifestation": manifestation}
            record.update(literature_cell(lit_rows))
            record.update(expression_cell(expr_rows))
            shared = sorted(constituent_set(lit_rows) & set(expr_rows["gene_symbol"]))
            record["overlap_genes"] = len(shared)
            record["overlap_gene_names"] = "; ".join(shared[:10])
            record["has_both_kinds"] = bool(record["lit_targets"] and record["expr_targets"])
            records.append(record)
    return pd.DataFrame.from_records(records)


def build_stratum_summary(expr: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    """Per Phase 3 stratum: how many contrasts and datasets fed it, and the
    tier breakdown of what came out. Strata that produced no candidate are
    kept as explicit zero rows."""
    used = labels[labels["usable_for_candidates"].astype(str).str.lower().isin({"true", "1"})]
    per_stratum = (
        used.groupby("comparison_class")
        .agg(
            disease=("disease", lambda s: "; ".join(sorted(set(s)))),
            n_contrasts=("contrast", "size"),
            n_datasets=("accession", "nunique"),
            datasets=("accession", lambda s: "; ".join(sorted(set(s)))),
        )
        .reset_index()
    )
    deduped = expr.drop_duplicates(subset=["comparison_class", "gene_symbol", "direction"])
    counts = (
        deduped.groupby("comparison_class")
        .agg(candidate_rows=("gene_symbol", "size"), candidate_genes=("gene_symbol", "nunique"))
        .reset_index()
    )
    tiers = (
        deduped.pivot_table(
            index="comparison_class",
            columns="evidence_tier",
            values="gene_symbol",
            aggfunc="size",
            fill_value=0,
        )
        .reindex(columns=list(TIER_COLS), fill_value=0)
        .rename(columns=TIER_COLS)
        .reset_index()
    )
    manifs = (
        expr.groupby("comparison_class")["manifestation"]
        .agg(lambda s: "; ".join(sorted(set(s))))
        .reset_index()
        .rename(columns={"manifestation": "manifestations"})
    )
    out = (
        per_stratum.merge(counts, on="comparison_class", how="left")
        .merge(tiers, on="comparison_class", how="left")
        .merge(manifs, on="comparison_class", how="left")
    )
    numeric = ["candidate_rows", "candidate_genes", *TIER_COLS.values()]
    out[numeric] = out[numeric].fillna(0).astype(int)
    out["manifestations"] = out["manifestations"].fillna("")
    return out.sort_values("candidate_rows", ascending=False).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="repo root")
    args = parser.parse_args()
    root = Path(args.repo).resolve()

    lit = load_literature(root / "phase-1b/data/phase1b-candidate-targets.csv")
    expr = load_expression(root / "phase-3/data/phase3-candidate-targets.csv")
    labels = pd.read_csv(root / "phase-3/data/phase3-contrast-labels.csv")

    coverage = build_coverage(lit, expr)
    strata = build_stratum_summary(expr, labels)

    outdir = root / "phase-3b/data"
    outdir.mkdir(parents=True, exist_ok=True)
    coverage.to_csv(outdir / "phase3b-coverage.csv", index=False)
    strata.to_csv(outdir / "phase3b-stratum-summary.csv", index=False)

    filled = coverage[(coverage["lit_targets"] > 0) | (coverage["expr_targets"] > 0)]
    print(f"coverage rows: {len(coverage)} ({len(filled)} with any evidence)")
    print(f"combinations with both kinds of evidence: {int(coverage['has_both_kinds'].sum())}")
    print(f"strata summarised: {len(strata)}")


if __name__ == "__main__":
    main()
