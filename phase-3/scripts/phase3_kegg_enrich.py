#!/usr/bin/env python3
"""Phase 3, step 4b: KEGG pathway over-representation for each stratum.

Enrichment is run per comparison_class and direction, on the genes that the
candidate rule selected for that stratum. Two choices make the result readable:

  Background. The universe is not "all human genes" but the symbols actually
  measured in that stratum, intersected with the genes KEGG annotates to at
  least one human pathway. Using all of KEGG as the background would score a
  pathway as enriched merely because the stratum's platforms covered it well,
  which is the usual way a targeted panel produces false enrichment. This matters
  most for nf1_atypical_vs_benign_pnst and nf1_benign_subtype_vs_pnf, where
  GSE239561's 770-gene panel is itself pathway-selected.

  Test. One-sided Fisher exact test per pathway (hypergeometric
  over-representation), Benjamini-Hochberg across the pathways tested within a
  stratum and direction. Pathways with fewer than 5 annotated genes in the
  stratum's background are not tested.

Inputs
  phase-3/data/phase3-kegg-gene-pathway.tsv.gz   from phase3_kegg_fetch.py
  phase-3/data/phase3-candidate-targets.csv      from phase3_candidates.py
  <build>/universe.csv                           measured symbols per stratum

Output
  phase-3/data/phase3-kegg-enrichment.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from scipy.stats import false_discovery_control, fisher_exact


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--build-dir", required=True)
    ap.add_argument("--min-pathway-genes", type=int, default=5)
    args = ap.parse_args()

    repo, build = Path(args.repo), Path(args.build_dir)

    kegg = pd.read_csv(repo / "phase-3/data/phase3-kegg-gene-pathway.tsv.gz", sep="\t")
    cand = pd.read_csv(repo / "phase-3/data/phase3-candidate-targets.csv")
    universe = pd.read_csv(build / "universe.csv")

    kegg_symbols = set(kegg.gene_symbol)
    pathway_members = kegg.groupby("pathway_id").gene_symbol.apply(set)
    pathway_names = kegg.drop_duplicates("pathway_id").set_index("pathway_id").pathway_name

    rows = []
    for cls, ug in universe.groupby("comparison_class"):
        background = set(ug.gene_symbol) & kegg_symbols
        for direction, cg in cand[cand.comparison_class == cls].groupby("direction"):
            selected = set(cg.gene_symbol) & background
            if not selected:
                continue
            tested = []
            for pid, members in pathway_members.items():
                in_bg = members & background
                if len(in_bg) < args.min_pathway_genes:
                    continue
                hits = selected & in_bg
                table = [[len(hits), len(selected) - len(hits)],
                         [len(in_bg) - len(hits), len(background) - len(selected) - len(in_bg) + len(hits)]]
                odds, p = fisher_exact(table, alternative="greater")
                tested.append({
                    "comparison_class": cls, "direction": direction,
                    "pathway_id": pid, "pathway_name": pathway_names[pid],
                    "n_candidates_in_pathway": len(hits),
                    "n_candidates_tested": len(selected),
                    "n_pathway_genes_in_background": len(in_bg),
                    "n_background": len(background),
                    "odds_ratio": odds, "p_value": p,
                    "genes": ";".join(sorted(hits)),
                })
            if not tested:
                continue
            t = pd.DataFrame(tested)
            t["fdr"] = false_discovery_control(t.p_value.values, method="bh")
            rows.append(t)
            print(f"{cls:<42} {direction:<4} {len(selected):4d} candidates in KEGG space, "
                  f"{len(t):3d} pathways tested, {int((t.fdr < 0.05).sum()):3d} at FDR < 0.05")

    out = repo / "phase-3/data/phase3-kegg-enrichment.csv"
    if not rows:
        print("no stratum had candidates inside the KEGG pathway space")
        pd.DataFrame(columns=["comparison_class", "direction", "pathway_id"]).to_csv(out, index=False)
        return 0

    enr = pd.concat(rows, ignore_index=True).sort_values(
        ["comparison_class", "direction", "p_value"])
    enr.to_csv(out, index=False)
    print(f"\nwrote {out} with {len(enr)} pathway tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
