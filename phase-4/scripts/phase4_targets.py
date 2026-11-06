#!/usr/bin/env python3
"""Phase 4 step 1: assemble the target list the drug layer queries.

The Phase 3b decision selects every disease and manifestation combination
that produced an expression candidate. For those combinations this script
takes the union of:

  - the expression-derived candidates (Phase 3 candidate list), and
  - the literature-derived candidates (Phase 1b candidate list),

one row per gene x disease x manifestation, carrying the provenance of
both so every downstream drug claim traces back to the evidence that put
the target on the list.

Phase 1b targets can be family labels (for example "MAP2K1/2 (MEK1/2)").
They are expanded to their constituent genes, because a drug database is
queried on a gene, not on a family; the original label is kept in
lit_target_labels.

The route policy columns are set here rather than in the drug step, since
they are a property of the manifestation and not of any drug.

Inputs (committed):
  phase-3/data/phase3-candidate-targets.csv
  phase-1b/data/phase1b-candidate-targets.csv
  phase-3b/data/phase3b-coverage.csv

Output:
  phase-4/data/phase4-targets.csv

Run from the repo root:
  python phase-4/scripts/phase4_targets.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

# Per docs/project-plan.md: topical delivery is appropriate only for the
# skin-localised manifestations; everything else needs a systemic route.
TOPICAL_ELIGIBLE = {"Cutaneous neurofibroma", "ANNUBP / atypical neurofibroma"}
# CNS-relevant manifestations additionally require blood-brain-barrier
# penetration from a systemic drug.
CNS_RELEVANT = {
    "Optic pathway glioma",
    "High grade glioma",
    "Non-optic LGG",
    "Cognition / Behavioral / Learning",
}

TIER_RANK = {"A_aggregated": 0, "B_replicated": 1, "C_single_dataset": 2}
LIT_TIER_RANK = {"full text - supported": 0, "full text - partial": 1, "abstract only": 2}


def selected_combinations(coverage: pd.DataFrame) -> set:
    chosen = coverage[coverage["expr_targets"] > 0]
    return set(zip(chosen["disease"], chosen["manifestation"]))


def explode_manifestations(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    out = frame.assign(manifestation=frame[column].str.split("|")).explode("manifestation")
    out["manifestation"] = out["manifestation"].str.strip()
    return out


def join_unique(values) -> str:
    seen: list = []
    for value in values:
        for part in str(value).split(";"):
            part = part.strip()
            if part and part.lower() != "nan" and part not in seen:
                seen.append(part)
    return "; ".join(sorted(seen))


def expression_side(p3: pd.DataFrame, chosen: set) -> pd.DataFrame:
    rows = explode_manifestations(p3, "manifestations")
    rows = rows[[(d, m) in chosen for d, m in zip(rows["disease"], rows["manifestation"])]].copy()
    rows["tier_rank"] = rows["evidence_tier"].map(TIER_RANK)
    grouped = rows.sort_values(["tier_rank", "rank_in_stratum"]).groupby(
        ["gene_symbol", "disease", "manifestation"], as_index=False
    )
    out = grouped.agg(
        expr_best_tier=("evidence_tier", "first"),
        expr_best_rank_in_stratum=("rank_in_stratum", "min"),
        expr_directions=("direction", lambda s: "; ".join(sorted(set(s)))),
        expr_strata=("comparison_class", lambda s: "; ".join(sorted(set(s)))),
        expr_n_datasets_significant=("n_datasets_significant", "max"),
        expr_n_datasets_measuring=("n_datasets_measuring", "max"),
        expr_supporting_datasets=("supporting_datasets", join_unique),
        expr_min_dataset_fdr=("min_dataset_fdr", "min"),
        expr_median_log2fc=("median_log2fc", "median"),
    )
    out["in_expression"] = True
    return out


def literature_side(p1b: pd.DataFrame, chosen: set) -> pd.DataFrame:
    rows = p1b[[(d, m) in chosen for d, m in zip(p1b["disease"], p1b["manifestation"])]].copy()
    expanded = []
    for row in rows.itertuples():
        constituents = (
            [g.strip() for g in str(row.constituent_genes).split(";") if g.strip()]
            if isinstance(row.constituent_genes, str) and row.constituent_genes.strip()
            else [str(row.gene_target).strip()]
        )
        for gene in constituents:
            expanded.append(
                {
                    "gene_symbol": gene,
                    "disease": row.disease,
                    "manifestation": row.manifestation,
                    "lit_target_label": row.gene_target,
                    "lit_label_type": row.label_type,
                    "lit_tier": row.evidence_tier,
                    "lit_n_papers": row.n_supporting_papers,
                    "lit_pmids": row.supporting_pmids,
                }
            )
    frame = pd.DataFrame(expanded)
    if frame.empty:
        return frame
    frame["tier_rank"] = frame["lit_tier"].map(LIT_TIER_RANK)
    grouped = frame.sort_values("tier_rank").groupby(
        ["gene_symbol", "disease", "manifestation"], as_index=False
    )
    out = grouped.agg(
        lit_best_tier=("lit_tier", "first"),
        lit_target_labels=("lit_target_label", lambda s: "; ".join(sorted(set(s)))),
        lit_label_types=("lit_label_type", lambda s: "; ".join(sorted(set(s)))),
        lit_n_papers=("lit_n_papers", "max"),
        lit_pmids=("lit_pmids", join_unique),
    )
    out["in_literature"] = True
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()

    coverage = pd.read_csv(root / "phase-3b/data/phase3b-coverage.csv")
    p3 = pd.read_csv(root / "phase-3/data/phase3-candidate-targets.csv")
    p1b = pd.read_csv(root / "phase-1b/data/phase1b-candidate-targets.csv")

    chosen = selected_combinations(coverage)
    expr = expression_side(p3, chosen)
    lit = literature_side(p1b, chosen)

    targets = expr.merge(lit, on=["gene_symbol", "disease", "manifestation"], how="outer")
    for flag in ("in_expression", "in_literature"):
        targets[flag] = targets[flag].notna() & targets[flag].astype(bool)

    targets["evidence_source"] = [
        "both" if e and l else ("expression" if e else "literature")
        for e, l in zip(targets["in_expression"], targets["in_literature"])
    ]
    targets["topical_acceptable"] = targets["manifestation"].isin(TOPICAL_ELIGIBLE)
    targets["bbb_required"] = targets["manifestation"].isin(CNS_RELEVANT)

    order = [
        "gene_symbol",
        "disease",
        "manifestation",
        "evidence_source",
        "in_expression",
        "in_literature",
        "expr_best_tier",
        "expr_best_rank_in_stratum",
        "expr_directions",
        "expr_strata",
        "expr_n_datasets_significant",
        "expr_n_datasets_measuring",
        "expr_supporting_datasets",
        "expr_min_dataset_fdr",
        "expr_median_log2fc",
        "lit_best_tier",
        "lit_target_labels",
        "lit_label_types",
        "lit_n_papers",
        "lit_pmids",
        "topical_acceptable",
        "bbb_required",
    ]
    targets = targets[order].sort_values(
        ["disease", "manifestation", "evidence_source", "gene_symbol"]
    )

    outdir = root / "phase-4/data"
    outdir.mkdir(parents=True, exist_ok=True)
    targets.to_csv(outdir / "phase4-targets.csv", index=False)

    print(f"combinations selected: {len(chosen)}")
    print(f"target rows: {len(targets)}")
    print(f"distinct genes: {targets['gene_symbol'].nunique()}")
    print(targets["evidence_source"].value_counts().to_string())


if __name__ == "__main__":
    main()
