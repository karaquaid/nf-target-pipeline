#!/usr/bin/env python3
"""Phase 3, step 5: assemble the expression-derived candidate target list.

Evidence tiers. The launch set gives very different amounts of replication per
stratum, so a single significance threshold would hide the difference instead of
showing it. Every gene that is significant anywhere in a stratum is kept, with
the strength of its support recorded as a tier:

  A_aggregated    Robust Rank Aggregation rho passes FDR < 0.05 within the
                  stratum. Reachable only where enough datasets measured the
                  gene; with two datasets per stratum RRA has almost no power at
                  this level, so an empty tier A is a statement about the launch
                  set, not about the biology.
  B_replicated    Significant in its own dataset's differential expression
                  (FDR < 0.05) in two or more datasets of the stratum, in the
                  same direction, with no dataset of the stratum significant in
                  the opposite direction.
  C_single_dataset
                  Significant in exactly one dataset of the stratum. This is
                  every gene from the three single-dataset strata, and genes in
                  multi-dataset strata that only one dataset supports.

Fold change is deliberately not thresholded. The launch set's log2 fold changes
come from limma, DESeq2, two-colour limma, NanoString housekeeping limma and
pseudobulk limma on 28 platforms, and are not on a common scale, which is the
reason this phase ranks instead of pooling. A shared |log2FC| cutoff would
therefore be stricter for some engines than others. Per-dataset fold changes are
reported in the table for reference.

Prioritisation cap. The candidate deliverable keeps the top N genes per stratum
per direction (default 200), ordered by rho where the stratum has aggregation and
by best own-dataset FDR otherwise. The cap exists so one deeply sequenced single
dataset cannot dominate the Phase 3b coverage picture against a replicated
stratum. It is applied as a flag column on the full table plus a separate
filtered file, never as a deletion, so raising N changes one argument.

Germline NF disease genes. NF1, NF2, SMARCB1, LZTR1 and SPRED1 are flagged
driver_gene and excluded from the candidate deliverable, the same scope decision
and the same gene set as Phase 1b.

Inputs
  phase-3/data/phase3-contrast-labels.csv
  <build>/rra-scores.csv.gz, <build>/contrast-stats.csv.gz
Outputs
  phase-3/data/phase3-expression-targets.csv   full table, every significant gene
  phase-3/data/phase3-candidate-targets.csv    the filtered deliverable
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# Same germline disease gene set Phase 1b excludes, for the same reason.
DRIVER_GENES = {"NF1", "NF2", "SMARCB1", "LZTR1", "SPRED1"}
TIER_ORDER = {"A_aggregated": 0, "B_replicated": 1, "C_single_dataset": 2}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--build-dir", required=True)
    ap.add_argument("--top-n", type=int, default=200,
                    help="candidates kept per stratum per direction")
    args = ap.parse_args()

    repo, build = Path(args.repo), Path(args.build_dir)
    labels = pd.read_csv(repo / "phase-3/data/phase3-contrast-labels.csv")
    labels = labels[labels.usable_for_candidates]
    stats = pd.read_csv(build / "contrast-stats.csv.gz")
    rra = pd.read_csv(build / "rra-scores.csv.gz")

    stats = stats.merge(labels[["accession", "contrast", "comparison_class", "disease",
                                "manifestations", "effect_type", "gene_space"]],
                        on=["accession", "contrast"], how="inner")

    # Dataset-level significance. A dataset counts as supporting a direction when at
    # least one of its contrasts in the stratum is significant that way; the fold
    # change and FDR reported are from that dataset's most significant such contrast.
    sig = stats[stats.fdr.notna() & (stats.fdr < 0.05)].copy()
    sig = sig.sort_values("fdr").drop_duplicates(
        ["comparison_class", "direction", "accession", "gene_symbol"], keep="first")

    agg = (sig.groupby(["comparison_class", "direction", "gene_symbol"])
              .agg(n_datasets_significant=("accession", "nunique"),
                   supporting_datasets=("accession", lambda s: ";".join(sorted(set(s)))),
                   min_dataset_fdr=("fdr", "min"),
                   median_log2fc=("log2fc", "median"))
              .reset_index())

    # Rank aggregation can call a gene that no single dataset calls: consistently
    # high ranks across many datasets without clearing FDR in any one of them is
    # exactly the signal RRA exists to find. Those genes have no row in the
    # significance table above, so they are added here before tiering.
    rra_sig = rra[rra.rho_fdr < 0.05][["comparison_class", "direction", "gene_symbol"]]
    extra = rra_sig.merge(agg[["comparison_class", "direction", "gene_symbol"]],
                          on=["comparison_class", "direction", "gene_symbol"],
                          how="left", indicator=True)
    extra = extra[extra._merge == "left_only"].drop(columns="_merge")
    if len(extra):
        extra = extra.assign(n_datasets_significant=0, supporting_datasets="",
                             min_dataset_fdr=np.nan, median_log2fc=np.nan)
        print(f"  {len(extra)} aggregation-significant rows with no single-dataset call, kept")
        agg = pd.concat([agg, extra], ignore_index=True)

    # A gene significant in both directions within a stratum is inconsistent across
    # datasets and cannot be called a replicated candidate in either direction.
    both = (agg[agg.n_datasets_significant > 0]
            .groupby(["comparison_class", "gene_symbol"]).direction.nunique()
            .rename("n_directions_significant").reset_index())
    agg = agg.merge(both, on=["comparison_class", "gene_symbol"], how="left")
    agg["n_directions_significant"] = agg.n_directions_significant.fillna(0).astype(int)

    # Datasets measuring the gene, and the RRA statistic, from the aggregation step.
    agg = agg.merge(rra[["comparison_class", "direction", "gene_symbol", "n_datasets",
                         "n_datasets_in_class", "rho", "rho_fdr", "best_rank", "median_rank"]],
                    on=["comparison_class", "direction", "gene_symbol"], how="left")

    # Which datasets measured the gene, for labelling the rows that no single
    # dataset called significant.
    rank_long = pd.read_csv(build / "rank-long.csv.gz",
                            usecols=["comparison_class", "direction", "accession", "gene_symbol"])
    measuring = (rank_long.groupby(["comparison_class", "direction", "gene_symbol"])
                          .accession.apply(lambda s: ";".join(sorted(set(s))))
                          .rename("measuring_datasets").reset_index())
    agg = agg.merge(measuring, on=["comparison_class", "direction", "gene_symbol"], how="left")
    agg["measuring_datasets"] = agg.measuring_datasets.fillna("")
    n_in_class = labels.groupby("comparison_class").accession.nunique()
    agg["n_datasets_in_class"] = agg.n_datasets_in_class.fillna(
        agg.comparison_class.map(n_in_class)).astype(int)
    agg["n_datasets_measuring"] = agg.n_datasets.fillna(1).astype(int)
    agg = agg.drop(columns="n_datasets")

    # Tier A has to mean aggregation. A gene only one dataset of a multi-dataset
    # stratum measured still gets an RRA score, computed from a single normalized
    # rank, and a top rank in one deep list can pass FDR on its own. That is not an
    # aggregated call, so tier A additionally requires two measuring datasets.
    tier = np.where(agg.rho_fdr.notna() & (agg.rho_fdr < 0.05) & (agg.n_datasets_measuring >= 2),
                    "A_aggregated",
             np.where((agg.n_datasets_significant >= 2) & (agg.n_directions_significant == 1),
                      "B_replicated", "C_single_dataset"))
    agg["evidence_tier"] = tier

    # A row that lost tier A to the two-dataset requirement and that no dataset
    # called significant carries no evidence at all, so it is not a candidate.
    dropped = agg[(agg.evidence_tier != "A_aggregated") & (agg.n_datasets_significant == 0)]
    if len(dropped):
        print(f"  {len(dropped)} rows dropped: aggregation score from a single measuring "
              f"dataset, no single-dataset call "
              f"({sorted(dropped.gene_symbol)})")
        agg = agg.drop(index=dropped.index)

    # Disease and manifestation labels come from the contrasts that actually support
    # the gene, not from the stratum as a whole.
    # For a gene some dataset called significant, the label comes from those
    # datasets. For an aggregation-only call, no single dataset is the source, so
    # the label comes from every dataset that measured the gene.
    lab_by_ds = labels.set_index(["accession", "comparison_class"]).sort_index()
    def label_for(row, field):
        source = row.supporting_datasets or row.measuring_datasets
        vals = []
        for acc in source.split(";"):
            if not acc:
                continue
            v = lab_by_ds.loc[(acc, row.comparison_class), field]
            v = v.iloc[0] if isinstance(v, pd.Series) else v
            vals.extend(str(v).split("|"))
        return "|".join(sorted(set(vals)))
    agg["disease"] = agg.apply(lambda r: label_for(r, "disease"), axis=1)
    agg["manifestations"] = agg.apply(lambda r: label_for(r, "manifestations"), axis=1)
    agg["effect_type"] = agg.comparison_class.map(
        labels.drop_duplicates("comparison_class").set_index("comparison_class").effect_type)

    agg["driver_gene"] = agg.gene_symbol.isin(DRIVER_GENES)
    agg["unreplicated"] = agg.evidence_tier == "C_single_dataset"

    # Priority: rho where the stratum has aggregation, best own-dataset FDR otherwise.
    agg["priority_statistic"] = np.where(agg.rho.notna(), "rra_rho", "min_dataset_fdr")
    agg["priority_value"] = agg.rho.where(agg.rho.notna(), agg.min_dataset_fdr)
    if agg.priority_value.isna().any():
        raise ValueError("a row has neither an RRA rho nor a dataset FDR to prioritise on")
    agg["tier_order"] = agg.evidence_tier.map(TIER_ORDER)
    agg = agg.sort_values(["comparison_class", "direction", "tier_order", "priority_value"])
    agg["rank_in_stratum"] = (agg.groupby(["comparison_class", "direction"]).cumcount() + 1)
    agg["in_candidate_list"] = (~agg.driver_gene) & (agg.rank_in_stratum <= args.top_n)

    cols = ["comparison_class", "direction", "gene_symbol", "disease", "manifestations",
            "effect_type", "evidence_tier", "n_datasets_significant", "n_datasets_measuring",
            "n_datasets_in_class", "supporting_datasets", "measuring_datasets",
            "min_dataset_fdr", "median_log2fc",
            "rho", "rho_fdr", "best_rank", "median_rank", "priority_statistic",
            "priority_value", "rank_in_stratum", "driver_gene", "unreplicated",
            "in_candidate_list"]
    full = agg[cols].reset_index(drop=True)
    # Gzipped: the full table is several megabytes of derived gene-level statistics,
    # and the repository keeps large reference files compressed.
    full_out = repo / "phase-3/data/phase3-expression-targets.csv.gz"
    full.to_csv(full_out, index=False)

    cand = full[full.in_candidate_list].drop(columns=["in_candidate_list", "driver_gene"])
    cand_out = repo / "phase-3/data/phase3-candidate-targets.csv"
    cand.to_csv(cand_out, index=False)

    print(f"wrote {full_out}: {len(full):,} gene by stratum by direction rows, "
          f"{full.gene_symbol.nunique():,} distinct genes")
    print(f"wrote {cand_out}: {len(cand):,} candidate rows, "
          f"{cand.gene_symbol.nunique():,} distinct genes")
    print(f"  driver genes flagged out: {int(full.driver_gene.sum())} rows "
          f"({sorted(set(full.loc[full.driver_gene, 'gene_symbol']))})")
    print()
    print(full.groupby(["comparison_class", "evidence_tier"]).size()
              .unstack(fill_value=0).to_string())
    print()
    print(cand.groupby(["comparison_class", "direction"]).size().unstack(fill_value=0).to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
