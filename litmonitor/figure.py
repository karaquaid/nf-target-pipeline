#!/usr/bin/env python3
"""Coverage figure: rows per manifestation, stacked by verification depth, one panel per disease.

    python litmonitor/figure.py --config mystudy.toml
"""

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfgmod  # noqa: E402

TIERS = ["full text - supported", "full text - partial", "abstract only"]
SHADES = {"full text - supported": "#2b5d8a", "full text - partial": "#7fa8c9",
          "abstract only": "#d9d9d9"}
LABELS = {"full text - supported": "read in full, supported",
          "full text - partial": "read in full, partial",
          "abstract only": "abstract only"}


def counts(cfg, candidates):
    present = [t for t in TIERS if (candidates.evidence_tier == t).any()]
    idx = pd.MultiIndex.from_product([cfg.manifestations, cfg.diseases],
                                     names=["manifestation", "disease"])
    c = (candidates[candidates.evidence_tier.isin(present)]
         .groupby(["manifestation", "disease", "evidence_tier"]).size()
         .unstack("evidence_tier").reindex(idx).fillna(0).astype(int))
    for t in present:
        if t not in c.columns:
            c[t] = 0
    return c[present], present


def make_figure(cfg, c, present, total_rows):
    diseases = cfg.diseases
    manifs = list(cfg.manifestations)[::-1]
    fig, axes = plt.subplots(1, len(diseases), figsize=(4.2 * len(diseases), 0.42 * len(manifs) + 1.8),
                             sharey=True)
    axes = [axes] if len(diseases) == 1 else list(axes)
    xmax = max(1, int(c.groupby("manifestation").sum().sum(axis=1).max()))
    for ax, disease in zip(axes, diseases):
        left = pd.Series(0, index=manifs, dtype=float)
        for tier in present:
            vals = pd.Series([c.loc[(m, disease), tier] for m in manifs], index=manifs, dtype=float)
            ax.barh(manifs, vals, left=left, color=SHADES[tier], edgecolor="white", linewidth=0.5,
                    label=LABELS[tier] if ax is axes[0] else None)
            left += vals
        n = int(sum(c.loc[(m, disease), t] for m in manifs for t in present))
        ax.set_title("%s (%d rows)" % (disease, n), fontsize=11)
        ax.set_xlabel("candidate rows")
        ax.set_xlim(0, xmax * 1.08)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
    axes[0].legend(frameon=False, fontsize=9, loc="lower right")
    fig.suptitle("%s: candidate target rows by manifestation and verification depth (%d rows)"
                 % (cfg.study, total_rows), fontsize=12, y=1.0)
    fig.tight_layout()
    return fig


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True, type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--dpi", type=int, default=200)
    args = p.parse_args()
    cfg = cfgmod.load(args.config)
    cand = pd.read_csv(cfg.workdir / "data" / "candidates.csv")
    c, present = counts(cfg, cand)
    plotted = int(c.to_numpy().sum())
    if plotted != len(cand):
        raise AssertionError("plotted %d rows but the table holds %d" % (plotted, len(cand)))
    fig = make_figure(cfg, c, present, len(cand))
    out = args.out or (cfg.workdir / "docs" / "figures" / ("%s-coverage.png" % cfg.study))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=args.dpi, bbox_inches="tight")
    plt.close(fig)
    print("wrote %s from %d rows" % (out, len(cand)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
