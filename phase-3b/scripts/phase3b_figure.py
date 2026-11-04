#!/usr/bin/env python3
"""Phase 3b coverage figure: evidence per disease x manifestation.

Three panels over the same grid (20 manifestations x 3 diseases), so a
combination with nothing is visible as an explicit zero rather than a
missing row:

  a  literature-derived targets (Phase 1b candidate list)
  b  expression-derived targets (Phase 3 candidate list)
  c  expression targets with cross-dataset support (tier A or B)

Every claim in a title is computed from the plotted table at render time.

Run from the repo root:
  python phase-3b/scripts/phase3b_figure.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MANIFESTATION_ORDER = [
    "Malignant peripheral nerve sheath tumor (MPNST)",
    "Plexiform neurofibroma",
    "ANNUBP / atypical neurofibroma",
    "Cutaneous neurofibroma",
    "Vestibular schwannoma",
    "Non-vestibular schwannoma",
    "Meningioma",
    "Optic pathway glioma",
    "Non-optic LGG",
    "High grade glioma",
    "Ependymoma",
    "Bone defects",
    "Pain",
    "Cognition / Behavioral / Learning",
    "Cardiovascular issues",
    "Gastrointestinal stromal tumor (GIST)",
    "Hematologic malignancies",
    "Pulmonary disease",
    "Sleep",
    "Other",
]
DISEASES = ["NF1", "NF2-SWN", "SWN"]

SHORT = {
    "Malignant peripheral nerve sheath tumor (MPNST)": "MPNST",
    "Gastrointestinal stromal tumor (GIST)": "GIST",
    "ANNUBP / atypical neurofibroma": "ANNUBP / atypical NF",
    "Cognition / Behavioral / Learning": "Cognition / behavioural",
}

PANELS = [
    ("lit_targets", "literature targets", "Blues"),
    ("expr_targets", "expression targets", "Blues"),
    ("cross_dataset", "with cross-dataset support", "Blues"),
]


def grid(coverage: pd.DataFrame, column: str) -> np.ndarray:
    wide = coverage.pivot(index="manifestation", columns="disease", values=column)
    wide = wide.reindex(index=MANIFESTATION_ORDER, columns=DISEASES).fillna(0)
    return wide.to_numpy(dtype=float)


def draw_panel(ax, values: np.ndarray, cmap: str, show_ylabels: bool) -> None:
    masked = np.ma.masked_where(values == 0, values)
    norm = mpl.colors.LogNorm(vmin=1, vmax=max(values.max(), 2))
    cmap_obj = mpl.colormaps[cmap].copy()
    cmap_obj.set_bad("#f4f4f4")
    ax.imshow(masked, cmap=cmap_obj, norm=norm, aspect="auto")

    for (row, col), value in np.ndenumerate(values):
        if value == 0:
            text, colour = "0", "#9a9a9a"
        else:
            text = f"{int(value)}"
            rgba = cmap_obj(norm(value))
            luminance = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
            colour = "white" if luminance < 0.55 else "#1a1a1a"
        ax.text(col, row, text, ha="center", va="center", color=colour, fontsize=6)

    ax.set_xticks(range(len(DISEASES)), DISEASES)
    ax.set_yticks(range(len(MANIFESTATION_ORDER)))
    if show_ylabels:
        ax.set_yticklabels([SHORT.get(m, m) for m in MANIFESTATION_ORDER])
    else:
        # The y-axis is shared, so blanking the labels here would blank them
        # on the labelled panel too.
        ax.tick_params(labelleft=False)
    ax.set_xticks(np.arange(-0.5, len(DISEASES), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(MANIFESTATION_ORDER), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(which="major", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()

    coverage = pd.read_csv(root / "phase-3b/data/phase3b-coverage.csv")
    coverage["cross_dataset"] = coverage["expr_targets_cross_dataset"]

    try:
        from figure_style import apply_figure_style, panel_letter

        apply_figure_style(sizes=(8, 7, 6))
    except Exception:
        mpl.rcParams.update(
            {"font.size": 8, "axes.spines.top": False, "axes.spines.right": False}
        )

        def panel_letter(ax, letter, **kw):
            ax.text(
                -0.08,
                1.06,
                letter,
                transform=ax.transAxes,
                fontsize=10,
                fontweight="bold",
                va="bottom",
                ha="right",
            )

    fig, axes = plt.subplots(1, 3, figsize=(7.2, 5.2), sharey=True)
    for ax, (column, subtitle, cmap) in zip(axes, PANELS):
        draw_panel(ax, grid(coverage, column), cmap, show_ylabels=ax is axes[0])
        ax.set_title(subtitle, fontsize=7, loc="left", pad=6)

    for ax, letter in zip(axes, "abc"):
        panel_letter(ax, letter)

    both = coverage[(coverage["lit_targets"] > 0) & (coverage["cross_dataset"] > 0)]
    both_labels = sorted(
        f"{row.disease} {SHORT.get(row.manifestation, row.manifestation)}"
        for row in both.itertuples()
    )
    headline = (
        f"{len(both)} of {len(coverage)} disease-manifestation combinations carry both "
        "literature and cross-dataset expression evidence"
    )
    fig.suptitle(headline, fontsize=8, x=0.012, ha="left", y=0.985)
    fig.text(
        0.012,
        0.028,
        "Counts are distinct targets; grey cells are explicit zeros. "
        + ("Both kinds of evidence: " + "; ".join(both_labels) if both_labels else ""),
        fontsize=6,
        color="#4a4a4a",
    )

    fig.tight_layout(rect=(0, 0.045, 1, 0.955))
    outdir = root / "phase-3b/docs/figures"
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / "phase3b-coverage.png"
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
    print(headline)


if __name__ == "__main__":
    main()
