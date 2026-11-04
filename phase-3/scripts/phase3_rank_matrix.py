#!/usr/bin/env python3
"""Phase 3, step 2: turn the Phase 2 ranked lists into per-stratum rank matrices.

What this step is for. The launch set spans 28 platforms and most contrasts are
between-subtype rather than tumour versus normal, so effect sizes are not
comparable on a common scale. Phase 3 therefore combines datasets by rank, not
by effect size, and this script produces the input that aggregation reads.

Three rules the project plan sets, implemented here:

1. A gene outside a dataset's measured space is ABSENT from that dataset's
   ranking, never a low rank in it. Each contrast's measured space is the set of
   HGNC symbols its own ranked list carries, so the 770-gene panel space of
   GSE239561 and the per-platform gaps of every array are handled by the same
   rule with no special case.
2. A stratum never mixes a disease-vs-normal reading with a between-state
   reading. Strata come from phase3-contrast-labels.csv, which enforces that.
3. Ranking is direction-aware. A gene up in one dataset and down in another must
   not reinforce, so up and down are ranked and aggregated separately.

Two collapsing steps, both of which would otherwise inflate a gene's support:

  probe to symbol   A platform may carry several probes or transcripts per gene.
                    Per contrast, the row with the largest absolute test
                    statistic is kept and the rest are dropped.
  contrast to dataset
                    A dataset contributing several contrasts to the same stratum
                    (GSE207400 has two MPNST grades, GSE239561 has two atypical
                    arms, GSE41747 has two tumour arms) would otherwise enter
                    aggregation as several independent lists and be counted more
                    than once. Its contrasts are averaged into one dataset-level
                    normalized rank first, so one dataset is always one list.

Inputs
  phase-3/data/phase3-contrast-labels.csv
  <ranked-lists dir>/<acc>_de.csv

Outputs (build directory, not committed: these are large intermediates)
  rank-long.csv.gz        comparison_class, direction, accession, gene_symbol, norm_rank
  contrast-stats.csv.gz   per contrast, the symbol-collapsed statistic/log2fc/fdr
  universe.csv            measured-symbol universe per comparison_class
Output (committed)
  phase-3/data/phase3-rank-input-summary.csv   per contrast, what went in and what was dropped
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--ranked-dir", required=True)
    ap.add_argument("--build-dir", required=True)
    args = ap.parse_args()

    repo, ranked, build = Path(args.repo), Path(args.ranked_dir), Path(args.build_dir)
    build.mkdir(parents=True, exist_ok=True)

    labels = pd.read_csv(repo / "phase-3/data/phase3-contrast-labels.csv")
    manifest = pd.read_csv(repo / "phase-2/data/phase2-ingestion-manifest.csv").set_index("accession")

    summary, stats_frames, rank_rows = [], [], []

    for acc, g in labels.groupby("accession"):
        de = pd.read_csv(ranked / manifest.loc[acc, "de_file"])
        for _, lab in g.iterrows():
            d = de[de.contrast == lab.contrast]
            n_rows = len(d)

            # Rows whose probe never mapped to an HGNC symbol carry no gene identity
            # and cannot enter a gene-level aggregation.
            d = d[d.gene_symbol.notna() & (d.gene_symbol.astype(str).str.strip() != "")]
            n_with_symbol = len(d)
            d = d[d.statistic.notna()]
            n_with_stat = len(d)

            # Probe to symbol: keep the most extreme statistic per symbol.
            d = d.assign(_abs=d.statistic.abs())
            d = d.sort_values("_abs", ascending=False).drop_duplicates("gene_symbol", keep="first")
            d = d.drop(columns="_abs")
            n_symbols = len(d)

            stats_frames.append(d.assign(accession=acc)[
                ["accession", "contrast", "gene_symbol", "source_id", "statistic", "log2fc", "fdr", "direction"]])

            # Direction-aware normalized ranks in (0, 1]. The "up" ranking puts the most
            # strongly up-regulated gene first; "down" is the same list reversed. Rank is
            # normalized by this contrast's own measured-symbol count, which is what makes
            # lists of 750 and 53,000 genes comparable.
            n = n_symbols
            order_up = d.statistic.rank(ascending=False, method="first")
            for direction, r in (("up", order_up), ("down", n + 1 - order_up)):
                rank_rows.append(pd.DataFrame({
                    "comparison_class": lab.comparison_class,
                    "direction": direction,
                    "accession": acc,
                    "contrast": lab.contrast,
                    "gene_symbol": d.gene_symbol.values,
                    "norm_rank": (r.values / n),
                }))

            summary.append({
                "accession": acc, "contrast": lab.contrast,
                "comparison_class": lab.comparison_class,
                "usable_for_candidates": lab.usable_for_candidates,
                "gene_space": lab.gene_space,
                "rows_in_ranked_list": n_rows,
                "rows_with_symbol": n_with_symbol,
                "rows_dropped_no_symbol": n_rows - n_with_symbol,
                "rows_dropped_no_statistic": n_with_symbol - n_with_stat,
                "symbols_measured": n_symbols,
                "rows_collapsed_to_symbol": n_with_stat - n_symbols,
            })

    rank_long = pd.concat(rank_rows, ignore_index=True)
    stats = pd.concat(stats_frames, ignore_index=True)
    summary = pd.DataFrame(summary).sort_values(["comparison_class", "accession", "contrast"])

    # Contrast to dataset: average a dataset's normalized ranks within a stratum.
    usable = set(labels.loc[labels.usable_for_candidates, ["accession", "contrast"]]
                 .itertuples(index=False, name=None))
    rank_long["usable"] = [
        (a, c) in usable for a, c in zip(rank_long.accession, rank_long.contrast)]
    keep = rank_long[rank_long.usable]
    per_dataset = (keep.groupby(["comparison_class", "direction", "accession", "gene_symbol"],
                                as_index=False)
                       .agg(norm_rank=("norm_rank", "mean"), n_contrasts=("norm_rank", "size")))

    per_dataset.to_csv(build / "rank-long.csv.gz", index=False)
    stats.to_csv(build / "contrast-stats.csv.gz", index=False)

    universe = (per_dataset.groupby("comparison_class")["gene_symbol"]
                           .apply(lambda s: sorted(set(s))).explode().reset_index())
    universe.columns = ["comparison_class", "gene_symbol"]
    universe.to_csv(build / "universe.csv", index=False)

    out = repo / "phase-3/data/phase3-rank-input-summary.csv"
    summary.to_csv(out, index=False)

    print(f"wrote {out}")
    print(f"wrote {build/'rank-long.csv.gz'}: {len(per_dataset):,} dataset-level gene ranks")
    print(f"wrote {build/'contrast-stats.csv.gz'}: {len(stats):,} symbol-collapsed rows")
    print()
    shape = (per_dataset[per_dataset.direction == "up"]
             .groupby("comparison_class")
             .agg(datasets=("accession", "nunique"), genes=("gene_symbol", "nunique")))
    shape["genes_in_all_datasets"] = [
        (per_dataset[(per_dataset.comparison_class == c) & (per_dataset.direction == "up")]
         .groupby("gene_symbol").accession.nunique() == shape.loc[c, "datasets"]).sum()
        for c in shape.index]
    print(shape.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
