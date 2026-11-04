#!/usr/bin/env python3
"""Phase 3, step 6: Figure 1, where the expression evidence is and what it says.

Panel a answers the question Phase 3b has to act on: how much of each stratum's
candidate list rests on aggregation across datasets, how much on replication
between datasets, and how much on a single dataset. Panel b shows the KEGG
pathways those candidates fall in, so the strata can be compared on biology as
well as on count.

Written for GitHub rendering, so the output goes to phase-3/docs/figures/ and is
referenced from the write-up by repository-relative path.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

TIERS = ["A_aggregated", "B_replicated", "C_single_dataset"]
TIER_LABEL = {
    "A_aggregated": "rank aggregation across datasets",
    "B_replicated": "replicated between datasets",
    "C_single_dataset": "one dataset only",
}
# Stratum names for a reader who has not read the schema.
PRETTY = {
    "nf1_mpnst_vs_benign_pnst": "NF1  MPNST vs benign\nnerve sheath tumour",
    "nf1_atypical_vs_benign_pnst": "NF1  atypical neurofibroma\nvs benign",
    "nf1_benign_subtype_vs_pnf": "NF1  benign subtype\nvs plexiform",
    "nf1_pnst_vs_normal": "NF1  nerve sheath tumour\nvs normal nerve",
    "nf1_bone_vs_normal": "NF1  bone lesion\nvs unaffected bone",
    "nf1_glioma_vs_normal_brain": "NF1  glioma vs\nnon-neoplastic brain",
    "nf2swn_schwannoma_vs_normal": "NF2-SWN  schwannoma\nvs normal nerve",
    "nf2swn_painful_vs_non_painful_schwannoma": "NF2-SWN  painful vs\nnon-painful schwannoma",
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--top-pathways", type=int, default=4)
    args = ap.parse_args()
    repo = Path(args.repo)

    try:
        from figure_style import apply_figure_style, panel_letter
        apply_figure_style(sizes=(8, 7, 6))
    except Exception:
        mpl.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False})
        def panel_letter(ax, letter, **kw):
            ax.text(-0.08, 1.06, letter, transform=ax.transAxes, fontsize=10,
                    fontweight="bold", va="bottom", ha="right")

    cand = pd.read_csv(repo / "phase-3/data/phase3-candidate-targets.csv")
    labels = pd.read_csv(repo / "phase-3/data/phase3-contrast-labels.csv")
    labels = labels[labels.usable_for_candidates]
    enr = pd.read_csv(repo / "phase-3/data/phase3-kegg-enrichment.csv")

    n_datasets = labels.groupby("comparison_class").accession.nunique()
    # Every stratum with a usable contrast appears, including the one that produced
    # no candidates: an absent row would read as "not examined".
    strata = sorted(labels.comparison_class.unique(),
                    key=lambda c: -cand[cand.comparison_class == c].shape[0])

    counts = (cand.groupby(["comparison_class", "evidence_tier"]).size()
                  .unstack(fill_value=0).reindex(index=strata, columns=TIERS, fill_value=0))

    fig = plt.figure(figsize=(7.2, 6.4))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.25], hspace=0.42)
    ax = fig.add_subplot(gs[0])

    colors = ["#1b4965", "#5fa8d3", "#bee9e8"]
    y = np.arange(len(strata))
    left = np.zeros(len(strata))
    for tier, colour in zip(TIERS, colors):
        v = counts[tier].values
        ax.barh(y, v, left=left, color=colour, height=0.62,
                label=TIER_LABEL[tier], edgecolor="white", linewidth=0.6)
        left += v
    for yi, (cls, total) in enumerate(zip(strata, left)):
        nd = n_datasets[cls]
        if total == 0:
            ax.plot(0, yi, marker="o", ms=3.2, color="#6b6b6b", zorder=5)
            ax.text(6, yi, f"no candidates  ({nd} dataset{'s' if nd > 1 else ''})",
                    va="center", fontsize=6, color="#3d3d3d")
        else:
            ax.text(total + 8, yi, f"{int(total)}  ({nd} dataset{'s' if nd > 1 else ''})",
                    va="center", fontsize=6, color="#3d3d3d")

    ax.set_yticks(y, [PRETTY[c] for c in strata], fontsize=6)
    ax.invert_yaxis()
    ax.set_xlabel("candidate target rows (gene and direction)")
    # Claim-title, checked against the plotted rows below before rendering.
    with_cand = counts[counts.sum(axis=1) > 0]
    no_cross = int(((with_cand.A_aggregated == 0) & (with_cand.B_replicated == 0)).sum())
    ax.set_title(f"{no_cross} of the {len(with_cand)} strata with candidates have no cross-dataset support",
                 loc="left")
    ax.set_xlim(0, max(left.max() * 1.22, 100))
    ax.legend(frameon=False, fontsize=6, loc="lower right", handlelength=1.1,
              title="strongest support per candidate", title_fontsize=6)
    panel_letter(ax, "a")

    # Panel b: the strongest enriched pathways per stratum and direction.
    axb = fig.add_subplot(gs[1])
    sig = enr[enr.fdr < 0.05].copy()
    if sig.empty:
        axb.text(0.5, 0.5, "no KEGG pathway reached FDR < 0.05", ha="center", va="center",
                 transform=axb.transAxes)
    else:
        sig["key"] = sig.comparison_class + "|" + sig.direction
        sig = (sig.sort_values("fdr").groupby("key", sort=False)
                  .head(args.top_pathways).sort_values(["comparison_class", "direction", "fdr"]))
        sig["short"] = sig.pathway_name.str.replace(" - Homo sapiens (human)", "", regex=False)
        order = list(sig.index)
        yy = np.arange(len(order))
        up = sig.direction.values == "up"
        axb.scatter(-np.log10(sig.fdr.values[up]), yy[up], s=18 + 6 * sig.n_candidates_in_pathway.values[up],
                    color="#b5452e", edgecolor="white", linewidth=0.5, label="higher in the test arm", zorder=3)
        axb.scatter(-np.log10(sig.fdr.values[~up]), yy[~up], s=18 + 6 * sig.n_candidates_in_pathway.values[~up],
                    color="#1b4965", edgecolor="white", linewidth=0.5, label="lower in the test arm", zorder=3)
        axb.hlines(yy, 0, -np.log10(sig.fdr.values), color="#d8d8d8", linewidth=0.7, zorder=1)
        axb.set_yticks(yy, sig.short.values, fontsize=6)
        axb.invert_yaxis()
        axb.axvline(-np.log10(0.05), color="#8a8a8a", linestyle=":", linewidth=0.8)
        axb.annotate("FDR 0.05", xy=(-np.log10(0.05), len(order) - 0.4), fontsize=5.5,
                     color="#5a5a5a", ha="center", va="top", annotation_clip=False)
        axb.set_xlabel("pathway over-representation, $-\\log_{10}$ FDR")
        axb.set_title("Cell cycle in MPNST, immune pathways in glioma, cytokine signalling lost in atypical NF",
                      loc="left")
        axb.legend(frameon=False, fontsize=6, loc="upper right", handlelength=0.8,
                   title="marker area is candidates in the pathway", title_fontsize=6)
        axb.margins(y=0.04)
        axb.set_xlim(left=0)
        # Stratum bands, so a reader can see which rows belong together.
        start = 0
        for cls, g in sig.groupby("comparison_class", sort=False):
            end = start + len(g)
            axb.text(1.012, 1 - (start + end) / 2 / len(order), PRETTY[cls].replace("\n", " "),
                     transform=axb.transAxes, rotation=0, fontsize=5.5, va="center",
                     ha="left", color="#3d3d3d")
            if end < len(order):
                axb.axhline(end - 0.5, color="#e2e2e2", linewidth=0.7)
            start = end
    panel_letter(axb, "b")

    out = repo / "phase-3/docs/figures/phase3-expression-evidence.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print(f"wrote {out}")

    r = fig.canvas.get_renderer()
    texts = [(t, t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text)
             if t.get_text().strip() and t.get_visible()]
    bad = [(a.get_text(), b.get_text()) for i, (a, ba) in enumerate(texts)
           for b, bb in texts[i + 1:] if ba.overlaps(bb)]
    print(f"  text overlap pairs: {len(bad)}")
    for pair in bad[:8]:
        print("   ", pair)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
