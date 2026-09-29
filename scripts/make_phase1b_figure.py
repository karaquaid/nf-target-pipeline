#!/usr/bin/env python3
"""Regenerate Figure 1 of the Phase 1b write-up.

Coverage per manifestation, stacked by verification depth, one panel per disease.

The figure is built from the candidate list (germline NF disease genes excluded),
which is what later phases consume; the full annotated table exists for audit and
is not plotted. Manifestations keep the project's fixed vocabulary order rather
than being sorted by size, so the figure reads row for row against the coverage
table it sits under in the write-up. Panels share an x axis, so bar lengths are
comparable across diseases.

Usage (from the repository root):

    python scripts/make_phase1b_figure.py
    python scripts/make_phase1b_figure.py --targets data/phase1b-candidate-targets.csv \
        --out docs/figures/phase1b-coverage-verification.png

Requires pandas, numpy and matplotlib.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# The project's fixed manifestation vocabulary, applied verbatim and in this order.
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

# Ordered weakest to strongest, so the dark end of the stack is the confirmed evidence.
TIERS = [
    "abstract only",
    "full text - not supported",
    "full text - partial",
    "full text - supported",
]
TIER_COLOURS = ["#cfd8e3", "#b8562f", "#6b8fb5", "#1f3a5f"]

# Only where the vocabulary term is too long for an axis tick.
SHORT_LABELS = {
    "Cognition / Behavioral / Learning": "Cognition / behavioural / learning",
    "Gastrointestinal stromal tumor (GIST)": "GIST",
    "Malignant peripheral nerve sheath tumor (MPNST)": "MPNST",
}

META_GREY = "#8a8f98"

REQUIRED_COLUMNS = {"disease", "manifestation", "evidence_tier"}


def apply_style() -> None:
    """Publication-grade defaults, kept local so the script needs no house style module."""
    plt.rcParams.update(
        {
            "figure.dpi": 110,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
            "font.size": 7,
            "axes.titlesize": 8,
            "axes.labelsize": 7,
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
            "legend.fontsize": 6,
            "legend.title_fontsize": 6,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.6,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "figure.titlesize": 9,
        }
    )


def tier_counts(targets: pd.DataFrame) -> pd.DataFrame:
    """Rows per (disease, manifestation, evidence tier), zero-filled over the vocabulary."""
    missing = REQUIRED_COLUMNS - set(targets.columns)
    if missing:
        raise ValueError(f"target table is missing columns: {sorted(missing)}")

    unknown_manifestations = set(targets.manifestation) - set(MANIFESTATIONS)
    if unknown_manifestations:
        raise ValueError(
            "manifestation values outside the fixed vocabulary: "
            f"{sorted(unknown_manifestations)}"
        )
    unknown_tiers = set(targets.evidence_tier) - set(TIERS)
    if unknown_tiers:
        raise ValueError(f"unexpected evidence_tier values: {sorted(unknown_tiers)}")

    counts = (
        targets.groupby(["disease", "manifestation", "evidence_tier"])
        .size()
        .unstack("evidence_tier")
        .reindex(columns=TIERS)
        .fillna(0)
        .astype(int)
    )
    index = pd.MultiIndex.from_product(
        [DISEASES, MANIFESTATIONS], names=["disease", "manifestation"]
    )
    return counts.reindex(index).fillna(0).astype(int)


def make_figure(counts: pd.DataFrame, n_rows: int) -> plt.Figure:
    supported = counts["full text - supported"].sum()
    pct_supported = round(100 * supported / n_rows) if n_rows else 0
    totals = counts.sum(axis=1)
    x_max = max(int(totals.groupby(level=0).max().max()), 1)
    y = np.arange(len(MANIFESTATIONS))[::-1]

    fig, axes = plt.subplots(1, 3, figsize=(9.6, 5.0), sharex=True, sharey=True)
    for ax, disease in zip(axes, DISEASES):
        panel = counts.loc[disease].reindex(MANIFESTATIONS).fillna(0).astype(int)
        left = np.zeros(len(MANIFESTATIONS))
        for tier, colour in zip(TIERS, TIER_COLOURS):
            width = panel[tier].to_numpy()
            ax.barh(
                y,
                width,
                left=left,
                height=0.68,
                color=colour,
                edgecolor="white",
                linewidth=0.4,
                label=tier if ax is axes[2] else None,
                zorder=2,
            )
            left = left + width
        # A dot distinguishes "no rows in this disease" from "bar too short to see".
        for y_pos, total in zip(y, panel.sum(axis=1).to_numpy()):
            if total == 0:
                ax.plot([0], [y_pos], marker="o", ms=2.2, color=META_GREY, zorder=3)
        ax.set_title(f"{disease}  (n = {int(panel.to_numpy().sum())} rows)", loc="left")
        ax.set_xlim(-1.9, x_max * 1.06)
        ax.grid(axis="x", lw=0.4, alpha=0.35, zorder=0)
        ax.tick_params(length=2.5)

    axes[0].set_yticks(y)
    axes[0].set_yticklabels([SHORT_LABELS.get(m, m) for m in MANIFESTATIONS])
    axes[1].set_xlabel("candidate target rows (one gene x disease x manifestation claim)")
    axes[2].legend(
        title="provenance of the\nstrongest supporting paper",
        frameon=False,
        loc="upper left",
        bbox_to_anchor=(0.30, 0.99),
        handlelength=1.0,
        borderpad=0,
        labelspacing=0.45,
        alignment="left",
    )
    fig.suptitle(
        f"After excluding the germline NF genes: {n_rows} candidate rows, "
        f"{pct_supported}% anchored in full text",
        x=0.006,
        ha="left",
        y=0.99,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.945))
    return fig


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--targets",
        type=Path,
        default=Path("data/phase1b-candidate-targets.csv"),
        help="candidate target table (default: %(default)s)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/figures/phase1b-coverage-verification.png"),
        help="output PNG path (default: %(default)s)",
    )
    parser.add_argument("--dpi", type=int, default=300, help="output resolution")
    args = parser.parse_args()

    targets = pd.read_csv(args.targets)
    counts = tier_counts(targets)
    if int(counts.to_numpy().sum()) != len(targets):
        raise AssertionError(
            f"plotted {int(counts.to_numpy().sum())} rows but the table holds {len(targets)}"
        )

    apply_style()
    fig = make_figure(counts, len(targets))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=args.dpi)
    plt.close(fig)
    print(f"wrote {args.out} from {len(targets)} rows in {args.targets}")


if __name__ == "__main__":
    main()
