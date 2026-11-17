#!/usr/bin/env python3
"""Phase 7 list comparison: expression-derived vs literature-derived candidates.

Regenerates, from committed repo inputs only:

  phase-7/data/phase7-list-comparison.csv    one row per gene x disease x manifestation
  phase-7/data/phase7-near-misses.csv        cross-manifestation and shared-pathway near misses
  phase-7/data/phase7-comparison-summary.json  counts per stratum and per match class

Authority for every methodological call made here is phase-7/docs/phase7-contract.md.
The Phase 6 scored table is deliberately NOT an input: its s_literature component is
derived from the same Phase 1b table, so using it to judge agreement would be circular.
Phase 6 is joined on at the end only to attach a score to a target whose match class was
already decided.

Run from the repo root:
    python phase-7/scripts/phase7_compare_lists.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Ratified constants
# ---------------------------------------------------------------------------

# Contract Call 3. The tier label travels with the number so every weight stays
# auditable back to a reading decision Phase 1b actually made. The 0.6 and 0.3
# steps are a judgement call, not a measurement. `preprint_only` is carried as
# its own flag and is NOT folded into the weight.
ACCESS_WEIGHT = {
    "full text - supported": 1.0,
    "full text - partial": 0.6,
    "abstract only": 0.3,
}

# Contract Call 2. Wording is part of the ruling: "found", never "exists".
NO_CONTRAST_CLASS = "literature_only_no_expression_contrast_found"

MATCH_CLASSES = [
    "both_exact_named_gene",
    "both_via_composite_label",
    "expression_only",
    "literature_only",
    NO_CONTRAST_CLASS,
]

# Phase 3 evidence tiers, best first.
EXPR_TIER_ORDER = ["A_aggregated", "B_replicated", "C_single_dataset"]

# Shared-pathway near-miss specificity rule (see module docstring of
# build_pathway_near_misses and phase7-literature-validation.md). A KEGG pathway
# is admitted only if it carries Phase 3 enrichment at FDR < 0.05 AND maps to no
# more than PATHWAY_SIZE_CUT distinct human genes in the Phase 3 KEGG mapping.
ENRICHMENT_FDR_CUT = 0.05
PATHWAY_SIZE_CUT = 100


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def split_set(value, sep=";") -> set:
    if not isinstance(value, str) or not value.strip():
        return set()
    return {part.strip() for part in value.split(sep) if part.strip()}


def load_expression(root: Path) -> pd.DataFrame:
    """Phase 3 candidates, exploded to one row per manifestation.

    `manifestations` is the label set of the source contrast, not a per-gene
    finding. A gene labelled `Cutaneous neurofibroma|MPNST|Plexiform
    neurofibroma` was found by one PNST-vs-normal contrast that cannot tell the
    three apart. `expr_manifestation_specific` records, per source row, whether
    the contrast named a single manifestation.
    """
    path = root / "phase-3" / "data" / "phase3-candidate-targets.csv"
    df = pd.read_csv(path)
    df["src_manifestations"] = df["manifestations"]
    df["expr_manifestation_specific"] = ~df["manifestations"].str.contains(r"\|", regex=True)
    df["manifestation"] = df["manifestations"].str.split("|")
    df = df.explode("manifestation")
    df["manifestation"] = df["manifestation"].str.strip()
    unknown = set(df["evidence_tier"]) - set(EXPR_TIER_ORDER)
    if unknown:
        raise SystemExit(f"unexpected Phase 3 evidence_tier(s): {sorted(unknown)}")
    return df


def load_literature(root: Path) -> pd.DataFrame:
    path = root / "phase-1b" / "data" / "phase1b-candidate-targets.csv"
    df = pd.read_csv(path)
    unknown = set(df["evidence_tier"]) - set(ACCESS_WEIGHT)
    if unknown:
        raise SystemExit(f"unexpected Phase 1b evidence_tier(s): {sorted(unknown)}")
    df["access_weight"] = df["evidence_tier"].map(ACCESS_WEIGHT)
    return df


def expand_literature(lit: pd.DataFrame) -> pd.DataFrame:
    """Contract Call 1: expand family/pathway/complex labels into constituents,
    but keep the label and its type on the row so a match reached only through a
    composite label stays distinguishable from a match on a named gene.

    Expansion follows `constituent_genes` wherever Phase 1b populated it. That is
    the same rule phase3b_coverage.py used, so the recomputed overlap reconciles
    against the Phase 3b coverage table. Note it is marginally wider than the
    enumeration in contract Call 1, which counted only family/pathway/complex
    labels: it also expands the `other`/`drug`/`miRNA` labels that carry
    constituents (this is what adds CEMIP, reached through `HYALURONAN`).
    """
    records = []
    for row in lit.itertuples(index=False):
        constituents = split_set(row.constituent_genes, ";")
        genes = sorted(constituents) if constituents else [str(row.gene_target).strip()]
        for gene in genes:
            records.append(
                {
                    "gene_symbol": gene,
                    "disease": row.disease,
                    "manifestation": row.manifestation,
                    "lit_matched_label": row.gene_target,
                    "lit_label_type": row.label_type,
                    "lit_evidence_tier": row.evidence_tier,
                    "lit_n_supporting_papers": row.n_supporting_papers,
                    "lit_supporting_pmids": row.supporting_pmids,
                    "lit_access_weight": row.access_weight,
                    "lit_preprint_only": bool(row.preprint_only),
                    "lit_n_papers_fulltext_read": row.n_papers_fulltext_read,
                    "lit_n_papers_abstract_only": row.n_papers_abstract_only,
                    "lit_label_is_named_gene": row.label_type == "gene",
                }
            )
    return pd.DataFrame.from_records(records)


# ---------------------------------------------------------------------------
# Side-level aggregation
# ---------------------------------------------------------------------------


def aggregate_expression(expr: pd.DataFrame) -> pd.DataFrame:
    """One row per gene x disease x manifestation.

    A gene can reach one stratum through more than one comparison class (e.g.
    MPNST from both nf1_mpnst_vs_benign_pnst and nf1_pnst_vs_normal). The best
    evidence is kept: strongest tier, best (lowest) rank, most significant
    datasets; directions and supporting datasets are unioned so a gene that moves
    both ways across contrasts is visible rather than silently resolved.

    `expr_rank_in_stratum` is Phase 3's rank, which is scoped to the comparison
    class, not to the exploded disease x manifestation stratum. It is carried
    unchanged and must be read that way.
    """
    tier_rank = {t: i for i, t in enumerate(EXPR_TIER_ORDER)}
    expr = expr.copy()
    expr["_tier"] = expr["evidence_tier"].map(tier_rank)
    out = []
    for (gene, disease, manifestation), grp in expr.groupby(
        ["gene_symbol", "disease", "manifestation"], sort=False
    ):
        best = grp.loc[grp["_tier"].idxmin()]
        datasets = set()
        for value in grp["supporting_datasets"]:
            datasets |= split_set(value, ";")
        out.append(
            {
                "gene_symbol": gene,
                "disease": disease,
                "manifestation": manifestation,
                "expr_evidence_tier": best["evidence_tier"],
                "expr_rank_in_stratum": int(grp["rank_in_stratum"].min()),
                "expr_n_datasets_significant": int(grp["n_datasets_significant"].max()),
                "expr_direction": ";".join(sorted(set(grp["direction"].dropna()))),
                "expr_supporting_datasets": ";".join(sorted(datasets)),
                "expr_comparison_classes": ";".join(sorted(set(grp["comparison_class"]))),
                "expr_source_manifestation_labels": " || ".join(
                    sorted(set(grp["src_manifestations"]))
                ),
                "expr_manifestation_specific": bool(grp["expr_manifestation_specific"].any()),
                "expr_n_source_rows": int(len(grp)),
            }
        )
    return pd.DataFrame.from_records(out)


def aggregate_literature(lit_x: pd.DataFrame) -> pd.DataFrame:
    """One row per gene x disease x manifestation on the literature side.

    Several Phase 1b labels can reach the same gene in one stratum (YAP1 is named
    outright and also sits inside `YAP1-TEAD` and `YAP1/WWTR1 (YAP/TAZ)`). The
    primary label is chosen as: a named-gene label first, then the strongest
    access weight, then the most supporting papers. Every label that reached the
    gene is still listed in `lit_all_labels`, so the choice is reversible.
    """
    lit_x = lit_x.sort_values(
        ["lit_label_is_named_gene", "lit_access_weight", "lit_n_supporting_papers"],
        ascending=[False, False, False],
        kind="mergesort",
    )
    out = []
    for (gene, disease, manifestation), grp in lit_x.groupby(
        ["gene_symbol", "disease", "manifestation"], sort=False
    ):
        primary = grp.iloc[0]
        record = primary.to_dict()
        record["lit_all_labels"] = "; ".join(sorted(set(grp["lit_matched_label"])))
        record["lit_n_labels_matched"] = int(len(grp))
        record["lit_matched_via_named_gene"] = bool(grp["lit_label_is_named_gene"].any())
        out.append(record)
    return pd.DataFrame.from_records(out).drop(columns=["lit_label_is_named_gene"])


# ---------------------------------------------------------------------------
# Comparison table
# ---------------------------------------------------------------------------

COMPARISON_COLUMNS = [
    "gene_symbol",
    "disease",
    "manifestation",
    "match_class",
    "expr_evidence_tier",
    "expr_rank_in_stratum",
    "expr_n_datasets_significant",
    "expr_direction",
    "expr_supporting_datasets",
    "expr_comparison_classes",
    "expr_source_manifestation_labels",
    "expr_manifestation_specific",
    "expr_n_source_rows",
    "lit_evidence_tier",
    "lit_matched_label",
    "lit_label_type",
    "lit_matched_via_named_gene",
    "lit_all_labels",
    "lit_n_labels_matched",
    "lit_n_supporting_papers",
    "lit_supporting_pmids",
    "lit_access_weight",
    "lit_preprint_only",
    "lit_n_papers_fulltext_read",
    "lit_n_papers_abstract_only",
    "phase6_score",
    "phase6_rank_in_stratum",
]


def build_comparison(expr_agg: pd.DataFrame, lit_agg: pd.DataFrame, strata: set) -> pd.DataFrame:
    df = expr_agg.merge(
        lit_agg, on=["gene_symbol", "disease", "manifestation"], how="outer", indicator=True
    )
    has_expr = df["_merge"].isin(["left_only", "both"])
    has_lit = df["_merge"].isin(["right_only", "both"])
    in_expr_stratum = [
        (d, m) in strata for d, m in zip(df["disease"], df["manifestation"])
    ]

    match_class = []
    for i, (e_side, l_side, in_stratum) in enumerate(zip(has_expr, has_lit, in_expr_stratum)):
        if e_side and l_side:
            named = bool(df["lit_matched_via_named_gene"].iloc[i])
            match_class.append("both_exact_named_gene" if named else "both_via_composite_label")
        elif e_side:
            match_class.append("expression_only")
        else:
            match_class.append("literature_only" if in_stratum else NO_CONTRAST_CLASS)
    df["match_class"] = match_class
    df = df.drop(columns=["_merge"])
    return df


def attach_phase6(df: pd.DataFrame, root: Path) -> pd.DataFrame:
    """Phase 6 is attached only after the match class is decided (see contract)."""
    path = root / "phase-6-evidence-scoring" / "data" / "phase6-candidate-scores.csv"
    p6 = pd.read_csv(path)[
        ["gene_symbol", "disease", "manifestation", "score", "rank_in_stratum"]
    ].rename(columns={"score": "phase6_score", "rank_in_stratum": "phase6_rank_in_stratum"})
    p6 = p6.drop_duplicates(["gene_symbol", "disease", "manifestation"])
    return df.merge(p6, on=["gene_symbol", "disease", "manifestation"], how="left")


# ---------------------------------------------------------------------------
# Near misses
# ---------------------------------------------------------------------------


def build_cross_manifestation(expr: pd.DataFrame, lit_x: pd.DataFrame) -> pd.DataFrame:
    """Same gene on both sides but a different manifestation, within or across disease.

    Artefact exclusion (contract, "recorded asymmetry"): if the literature
    manifestation is already inside the label set of the expression row's own
    source contrast, the pairing is not an independent cross-manifestation
    finding — it is the same contrast speaking to both labels at once, and the
    gene is already recorded as a match under the literature's manifestation.
    Those pairs are dropped.
    """
    lit_small = lit_x[
        [
            "gene_symbol",
            "disease",
            "manifestation",
            "lit_matched_label",
            "lit_label_type",
            "lit_evidence_tier",
            "lit_n_supporting_papers",
            "lit_access_weight",
            "lit_preprint_only",
        ]
    ].rename(columns={"disease": "lit_disease", "manifestation": "lit_manifestation"})

    expr_small = expr[
        [
            "gene_symbol",
            "disease",
            "manifestation",
            "src_manifestations",
            "comparison_class",
            "evidence_tier",
            "rank_in_stratum",
            "expr_manifestation_specific",
        ]
    ].rename(
        columns={
            "disease": "expr_disease",
            "manifestation": "expr_manifestation",
            "evidence_tier": "expr_evidence_tier",
            "rank_in_stratum": "expr_rank_in_stratum",
        }
    )

    merged = expr_small.merge(lit_small, on="gene_symbol", how="inner")
    if merged.empty:
        return merged

    same_cell = (merged["expr_disease"] == merged["lit_disease"]) & (
        merged["expr_manifestation"] == merged["lit_manifestation"]
    )
    artefact = [
        lm in split_set(src, "|")
        for lm, src in zip(merged["lit_manifestation"], merged["src_manifestations"])
    ]
    merged["same_contrast_artefact"] = artefact
    keep = merged[~same_cell & ~merged["same_contrast_artefact"]].copy()
    keep["cross_disease"] = keep["expr_disease"] != keep["lit_disease"]
    keep["near_miss_type"] = "cross_manifestation"

    keep = keep.sort_values(["expr_rank_in_stratum"], kind="mergesort").drop_duplicates(
        [
            "gene_symbol",
            "expr_disease",
            "expr_manifestation",
            "lit_disease",
            "lit_manifestation",
            "lit_matched_label",
        ]
    )
    return keep


def build_pathway_near_misses(
    root: Path, expr: pd.DataFrame, lit_x: pd.DataFrame
) -> pd.DataFrame:
    """Expression candidate sharing a KEGG pathway with a literature target.

    SPECIFICITY RULE (stated here and in phase7-literature-validation.md):

    1. The pathway must carry Phase 3 KEGG enrichment at FDR < 0.05 in the
       comparison class that produced the expression candidate. Shared membership
       alone is not evidence; the pathway has to have come up in this data.
    2. The pathway must map to <= 100 distinct human genes in the Phase 3 KEGG
       gene-pathway table. The median human KEGG pathway in that table holds 78
       genes, so this keeps pathways whose membership is a mechanistic statement
       and drops the broad umbrellas ("Pathways in cancer", 531 genes) where
       co-membership means almost nothing. Relaxing the cut to 150 genes takes the
       output from 56 rows to 540, which is the behaviour this rule exists to stop.
    3. The expression gene must be one of the candidate genes that actually drove
       that enrichment row, not merely a pathway member.
    4. The literature target must be annotated to the same pathway, must sit in a
       manifestation the comparison class speaks to, and must NOT itself be an
       expression candidate in that stratum (that would be an exact match, not a
       near miss).

    Rows are ranked by specificity: pathway size ascending, then enrichment FDR.
    """
    kegg = pd.read_csv(
        root / "phase-3" / "data" / "phase3-kegg-gene-pathway.tsv.gz", sep="\t"
    )
    enr = pd.read_csv(root / "phase-3" / "data" / "phase3-kegg-enrichment.csv")

    pathway_size = kegg.groupby("pathway_id")["gene_symbol"].nunique()
    pathway_members = kegg.groupby("pathway_id")["gene_symbol"].apply(set).to_dict()

    cc_manifestations = (
        expr.groupby("comparison_class")["manifestation"].apply(lambda s: sorted(set(s))).to_dict()
    )
    cc_disease = expr.groupby("comparison_class")["disease"].first().to_dict()
    expr_stratum_genes = expr.groupby(["disease", "manifestation"])["gene_symbol"].apply(set).to_dict()
    expr_lookup = (
        expr.sort_values("rank_in_stratum")
        .drop_duplicates(["gene_symbol", "comparison_class"])
        .set_index(["gene_symbol", "comparison_class"])
    )
    lit_lookup = lit_x.sort_values("lit_access_weight", ascending=False).drop_duplicates(
        ["gene_symbol", "disease", "manifestation"]
    ).set_index(["gene_symbol", "disease", "manifestation"])

    sig = enr[enr["fdr"] < ENRICHMENT_FDR_CUT].copy()
    sig["pathway_size"] = sig["pathway_id"].map(pathway_size)
    sig = sig[sig["pathway_size"] <= PATHWAY_SIZE_CUT]

    records = []
    for row in sig.itertuples(index=False):
        cc = row.comparison_class
        disease = cc_disease.get(cc)
        if disease is None:
            continue
        members = pathway_members.get(row.pathway_id, set())
        driver_genes = sorted(split_set(row.genes, ";"))
        for manifestation in cc_manifestations.get(cc, []):
            lit_here = lit_x[
                (lit_x["disease"] == disease) & (lit_x["manifestation"] == manifestation)
            ]
            lit_genes = (set(lit_here["gene_symbol"]) & members) - expr_stratum_genes.get(
                (disease, manifestation), set()
            )
            for lit_gene in sorted(lit_genes):
                lrec = lit_lookup.loc[(lit_gene, disease, manifestation)]
                for expr_gene in driver_genes:
                    try:
                        erec = expr_lookup.loc[(expr_gene, cc)]
                    except KeyError:
                        continue
                    records.append(
                        {
                            "near_miss_type": "shared_pathway",
                            "gene_symbol": expr_gene,
                            "expr_disease": disease,
                            "expr_manifestation": manifestation,
                            "expr_comparison_class": cc,
                            "expr_evidence_tier": erec["evidence_tier"],
                            "expr_rank_in_stratum": int(erec["rank_in_stratum"]),
                            "expr_manifestation_specific": bool(
                                erec["expr_manifestation_specific"]
                            ),
                            "lit_gene_symbol": lit_gene,
                            "lit_disease": disease,
                            "lit_manifestation": manifestation,
                            "lit_matched_label": lrec["lit_matched_label"],
                            "lit_label_type": lrec["lit_label_type"],
                            "lit_evidence_tier": lrec["lit_evidence_tier"],
                            "lit_n_supporting_papers": lrec["lit_n_supporting_papers"],
                            "lit_access_weight": lrec["lit_access_weight"],
                            "lit_preprint_only": bool(lrec["lit_preprint_only"]),
                            "pathway_id": row.pathway_id,
                            "pathway_name": row.pathway_name,
                            "pathway_size": int(row.pathway_size),
                            "pathway_specificity": round(1.0 / int(row.pathway_size), 5),
                            "enrichment_direction": row.direction,
                            "enrichment_fdr": row.fdr,
                            "cross_disease": False,
                        }
                    )
    out = pd.DataFrame.from_records(records)
    if out.empty:
        return out
    out = out.drop_duplicates(
        [
            "gene_symbol",
            "expr_disease",
            "expr_manifestation",
            "lit_gene_symbol",
            "pathway_id",
            "enrichment_direction",
        ]
    )
    return out.sort_values(
        ["pathway_size", "enrichment_fdr", "expr_rank_in_stratum"], kind="mergesort"
    )


NEAR_MISS_COLUMNS = [
    "near_miss_type",
    "gene_symbol",
    "expr_disease",
    "expr_manifestation",
    "expr_comparison_class",
    "expr_evidence_tier",
    "expr_rank_in_stratum",
    "expr_manifestation_specific",
    "expr_source_manifestation_labels",
    "lit_gene_symbol",
    "lit_disease",
    "lit_manifestation",
    "lit_matched_label",
    "lit_label_type",
    "lit_evidence_tier",
    "lit_n_supporting_papers",
    "lit_access_weight",
    "lit_preprint_only",
    "cross_disease",
    "also_matched_in_lit_manifestation",
    "pathway_id",
    "pathway_name",
    "pathway_size",
    "pathway_specificity",
    "enrichment_direction",
    "enrichment_fdr",
]


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def build_summary(
    comparison: pd.DataFrame,
    near: pd.DataFrame,
    lit: pd.DataFrame,
    strata: set,
    reconciliation: dict,
    label_summary: dict,
) -> dict:
    lit_only_classes = {"literature_only", NO_CONTRAST_CLASS}
    per_stratum = []
    for (disease, manifestation), grp in comparison.groupby(["disease", "manifestation"]):
        lit_only = grp[grp["match_class"].isin(lit_only_classes)]
        tiers = lit_only["lit_evidence_tier"].value_counts().to_dict()
        per_stratum.append(
            {
                "disease": disease,
                "manifestation": manifestation,
                "has_expression_candidates": (disease, manifestation) in strata,
                "n_rows": int(len(grp)),
                "counts_by_match_class": {
                    cls: int((grp["match_class"] == cls).sum()) for cls in MATCH_CLASSES
                },
                # Two denominators, both reported, because they answer different
                # questions. The gene count counts constituents of expanded
                # composite labels; the label count counts the Phase 1b rows a
                # curator actually read papers for.
                "n_literature_only_genes": int(len(lit_only)),
                "n_literature_only_labels": int(lit_only["lit_matched_label"].nunique()),
                "n_literature_only_named_gene_labels": int(
                    lit_only.loc[lit_only["lit_label_type"] == "gene", "lit_matched_label"].nunique()
                ),
                "literature_only_labels_by_tier": {
                    tier: int(
                        lit_only.loc[
                            lit_only["lit_evidence_tier"] == tier, "lit_matched_label"
                        ].nunique()
                    )
                    for tier in ACCESS_WEIGHT
                },
                "literature_only_access_profile": {
                    "full text - supported": int(tiers.get("full text - supported", 0)),
                    "full text - partial": int(tiers.get("full text - partial", 0)),
                    "abstract only": int(tiers.get("abstract only", 0)),
                    "n_abstract_only": int(tiers.get("abstract only", 0)),
                    "n_any_full_text": int(
                        tiers.get("full text - supported", 0) + tiers.get("full text - partial", 0)
                    ),
                    "n_preprint_only_flag": int(lit_only["lit_preprint_only"].sum()),
                    "mean_access_weight": (
                        round(float(lit_only["lit_access_weight"].mean()), 4)
                        if len(lit_only)
                        else None
                    ),
                },
            }
        )

    lit_only_all = comparison[comparison["match_class"].isin(lit_only_classes)]
    summary = {
        "inputs": {
            "expression": "phase-3/data/phase3-candidate-targets.csv (manifestations exploded)",
            "literature": "phase-1b/data/phase1b-candidate-targets.csv (all 303 rows)",
            "phase6_role": "score attached after match class decided; not a comparison input",
        },
        "access_weight_rule": ACCESS_WEIGHT,
        "pathway_specificity_rule": {
            "enrichment_fdr_cut": ENRICHMENT_FDR_CUT,
            "pathway_size_cut": PATHWAY_SIZE_CUT,
            "rank_by": "pathway_size ascending, then enrichment fdr",
        },
        "totals": {
            "n_comparison_rows": int(len(comparison)),
            "counts_by_match_class": {
                cls: int((comparison["match_class"] == cls).sum()) for cls in MATCH_CLASSES
            },
            "n_literature_only_rows": int(len(lit_only_all)),
            # Label x stratum pairs, i.e. Phase 1b rows reached, not distinct label
            # strings (a label used in two strata is two curated rows).
            "n_literature_only_label_stratum_pairs": int(
                len(lit_only_all.drop_duplicates(["disease", "manifestation", "lit_matched_label"]))
            ),
            "n_literature_only_label_stratum_pairs_abstract_only": int(
                len(
                    lit_only_all[lit_only_all["lit_evidence_tier"] == "abstract only"]
                    .drop_duplicates(["disease", "manifestation", "lit_matched_label"])
                )
            ),
            "n_literature_only_abstract_only": int(
                (lit_only_all["lit_evidence_tier"] == "abstract only").sum()
            ),
            "n_literature_only_any_full_text": int(
                lit_only_all["lit_evidence_tier"]
                .isin(["full text - supported", "full text - partial"])
                .sum()
            ),
            "n_near_misses": int(len(near)),
            "n_near_misses_cross_manifestation": int(
                (near["near_miss_type"] == "cross_manifestation").sum()
            ),
            "n_near_misses_shared_pathway": int(
                (near["near_miss_type"] == "shared_pathway").sum()
            ),
        },
        "phase1b_source_profile": {
            "n_rows": int(len(lit)),
            "n_rows_in_expression_stratum": int(
                sum((d, m) in strata for d, m in zip(lit["disease"], lit["manifestation"]))
            ),
            "n_rows_no_expression_contrast_found": int(
                sum((d, m) not in strata for d, m in zip(lit["disease"], lit["manifestation"]))
            ),
        },
        "literature_label_rows": label_summary,
        "phase3b_reconciliation": reconciliation,
        "per_stratum": sorted(per_stratum, key=lambda r: (r["disease"], r["manifestation"])),
    }
    return summary


def label_row_status(lit: pd.DataFrame, expr: pd.DataFrame) -> pd.DataFrame:
    """Match status of each of the 303 Phase 1b rows, at label level.

    The comparison table is keyed on gene, so one curated row about a 14-gene
    family becomes 14 rows there. For the access-weighting question ("how many
    literature-only targets rest on abstract-only evidence?") the honest
    denominator is the curated row — one reading decision, one access tier — so
    it is computed here directly from Phase 1b rather than read back off the
    gene-level table.
    """
    expr_sets = expr.groupby(["disease", "manifestation"])["gene_symbol"].apply(set).to_dict()
    status = []
    for row in lit.itertuples(index=False):
        constituents = split_set(row.constituent_genes, ";") or {str(row.gene_target).strip()}
        key = (row.disease, row.manifestation)
        if key not in expr_sets:
            status.append("no_expression_contrast_found")
        elif constituents & expr_sets[key]:
            status.append("matched")
        else:
            status.append("unmatched_despite_expression_contrast")
    out = lit.copy()
    out["label_status"] = status
    return out


def summarise_label_rows(lit_status: pd.DataFrame) -> dict:
    def profile(frame: pd.DataFrame) -> dict:
        tiers = frame["evidence_tier"].value_counts().to_dict()
        return {
            "n_label_rows": int(len(frame)),
            "full text - supported": int(tiers.get("full text - supported", 0)),
            "full text - partial": int(tiers.get("full text - partial", 0)),
            "abstract only": int(tiers.get("abstract only", 0)),
            "n_preprint_only_flag": int(frame["preprint_only"].sum()),
            "n_no_full_text_read": int((frame["n_papers_fulltext_read"] == 0).sum()),
            "mean_access_weight": (
                round(float(frame["access_weight"].mean()), 4) if len(frame) else None
            ),
        }

    overall = {
        status: profile(grp) for status, grp in lit_status.groupby("label_status")
    }
    per_stratum = {}
    lit_only = lit_status[lit_status["label_status"] != "matched"]
    for (disease, manifestation), grp in lit_only.groupby(["disease", "manifestation"]):
        per_stratum[f"{disease} | {manifestation}"] = profile(grp)
    return {
        "n_phase1b_rows": int(len(lit_status)),
        "by_status": overall,
        "literature_only_label_rows_per_stratum": dict(sorted(per_stratum.items())),
    }


def reconcile_with_phase3b(root: Path, comparison: pd.DataFrame) -> dict:
    """Recompute the Phase 3b overlap count and reconcile, rather than diverge quietly."""
    cov = pd.read_csv(root / "phase-3b" / "data" / "phase3b-coverage.csv")
    recorded = {
        (r.disease, r.manifestation): int(r.overlap_genes)
        for r in cov.itertuples(index=False)
        if r.overlap_genes > 0
    }
    both = comparison[comparison["match_class"].str.startswith("both_")]
    recomputed = both.groupby(["disease", "manifestation"]).size().to_dict()
    agrees = recorded == {k: int(v) for k, v in recomputed.items()}
    return {
        "phase3b_recorded_total": int(sum(recorded.values())),
        "phase7_recomputed_total": int(sum(recomputed.values())),
        "per_stratum_recorded": {f"{d} | {m}": v for (d, m), v in sorted(recorded.items())},
        "per_stratum_recomputed": {f"{d} | {m}": int(v) for (d, m), v in sorted(recomputed.items())},
        "per_stratum_agrees": bool(agrees),
        "unique_genes_in_both": int(both["gene_symbol"].nunique()),
        "unique_genes_exact_named": int(
            both.loc[both["match_class"] == "both_exact_named_gene", "gene_symbol"].nunique()
        ),
        "gene_stratum_pairs_exact_named": int(
            (both["match_class"] == "both_exact_named_gene").sum()
        ),
        "gene_stratum_pairs_via_composite": int(
            (both["match_class"] == "both_via_composite_label").sum()
        ),
        "composite_only_genes": sorted(
            set(both["gene_symbol"]) - set(
                both.loc[both["match_class"] == "both_exact_named_gene", "gene_symbol"]
            )
        ),
        "divergence_from_contract_call_1": {
            "contract_states": "16 exact_named_gene + 6 via_composite_label = 22 unique genes",
            "phase7_recomputes": "16 exact_named_gene + 7 composite-only = 23 unique genes",
            "extra_gene": "CEMIP",
            "cause": (
                "Contract Call 1 enumerated only the family/pathway/complex labels (56 of the 212 "
                "in-stratum Phase 1b rows). CEMIP is reached through `HYALURONAN`, whose label_type "
                "is `other`, so Call 1's enumeration did not cover it. Phase 7 expands every Phase 1b "
                "row that carries constituent_genes, which is the rule phase3b_coverage.py used and "
                "is why the 27 gene-per-stratum total reconciles exactly; narrowing expansion to "
                "family/pathway/complex would reproduce Call 1's 22 but break the 27."
            ),
            "resolution": (
                "Kept the wider expansion and classified CEMIP as both_via_composite_label, since it "
                "was not named by a paper. A reviewer wanting Call 1's exact set should drop rows "
                "where lit_label_type is not in {family, pathway, complex, gene}."
            ),
        },
        "note": (
            "27 is a gene-per-stratum count. Four genes are counted in two strata each "
            "(BIRC5, SOX10 and SPP1 in both NF1 MPNST and NF1 plexiform neurofibroma; EGFR in "
            "NF1 plexiform neurofibroma and NF2-SWN vestibular schwannoma), so 27 pairs collapse "
            "to 23 unique genes. Contract Call 1 "
            "enumerated 16 exact + 6 composite-only = 22 unique genes because it expanded only "
            "family/pathway/complex labels; expanding every label that carries constituent_genes "
            "(as phase3b_coverage.py does) adds CEMIP via the `other` label HYALURONAN, giving 23."
        ),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="repository root (default: inferred from this script's location)",
    )
    parser.add_argument("--outdir", type=Path, default=None, help="default: <repo>/phase-7/data")
    args = parser.parse_args()

    root = args.repo_root.resolve()
    outdir = args.outdir or (root / "phase-7" / "data")
    outdir.mkdir(parents=True, exist_ok=True)

    expr = load_expression(root)
    lit = load_literature(root)
    lit_x = expand_literature(lit)

    strata = set(map(tuple, expr[["disease", "manifestation"]].drop_duplicates().values))

    comparison = build_comparison(aggregate_expression(expr), aggregate_literature(lit_x), strata)
    comparison = attach_phase6(comparison, root)
    comparison = comparison.reindex(columns=COMPARISON_COLUMNS)
    comparison = comparison.sort_values(
        ["disease", "manifestation", "match_class", "expr_rank_in_stratum", "gene_symbol"],
        kind="mergesort",
    )

    cross = build_cross_manifestation(expr, lit_x)
    if not cross.empty:
        cross = cross.rename(
            columns={"src_manifestations": "expr_source_manifestation_labels",
                     "comparison_class": "expr_comparison_class"}
        )
        cross["lit_gene_symbol"] = cross["gene_symbol"]
        # A gene can be a near miss here AND already an exact match in the
        # literature's own manifestation, when a manifestation-specific contrast
        # supplies the near-miss side. Flag it rather than drop it: the row still
        # says something (manifestation-specific expression support for a gene the
        # literature placed elsewhere), but it is not independent of the match.
        both_cells = set(
            map(
                tuple,
                comparison.loc[
                    comparison["match_class"].str.startswith("both_"),
                    ["gene_symbol", "disease", "manifestation"],
                ].values,
            )
        )
        cross["also_matched_in_lit_manifestation"] = [
            (g, d, m) in both_cells
            for g, d, m in zip(cross["gene_symbol"], cross["lit_disease"], cross["lit_manifestation"])
        ]
    pathway = build_pathway_near_misses(root, expr, lit_x)
    if not pathway.empty:
        pathway["also_matched_in_lit_manifestation"] = False
    near = pd.concat([cross, pathway], ignore_index=True).reindex(columns=NEAR_MISS_COLUMNS)

    reconciliation = reconcile_with_phase3b(root, comparison)
    label_summary = summarise_label_rows(label_row_status(lit, expr))
    summary = build_summary(comparison, near, lit, strata, reconciliation, label_summary)

    # Contract Call 2: the forbidden wording must never reach a file.
    for frame in (comparison, near):
        for col in ("match_class", "near_miss_type"):
            if col in frame.columns:
                bad = frame[col].astype(str).str.contains("exists", case=False, na=False)
                if bad.any():
                    raise SystemExit(f"forbidden wording 'exists' in {col}")

    comparison.to_csv(outdir / "phase7-list-comparison.csv", index=False)
    near.to_csv(outdir / "phase7-near-misses.csv", index=False)
    (outdir / "phase7-comparison-summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    totals = summary["totals"]["counts_by_match_class"]
    print(f"comparison rows: {len(comparison)}")
    for cls in MATCH_CLASSES:
        print(f"  {cls}: {totals[cls]}")
    print(
        f"near misses: {len(near)} "
        f"(cross_manifestation {summary['totals']['n_near_misses_cross_manifestation']}, "
        f"shared_pathway {summary['totals']['n_near_misses_shared_pathway']})"
    )
    print(
        "Phase 3b overlap recorded "
        f"{reconciliation['phase3b_recorded_total']} vs recomputed "
        f"{reconciliation['phase7_recomputed_total']}; per-stratum agrees: "
        f"{reconciliation['per_stratum_agrees']}"
    )


if __name__ == "__main__":
    main()
