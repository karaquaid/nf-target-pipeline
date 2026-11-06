#!/usr/bin/env python3
"""Phase 4 figure: what the drug layer found for each selected combination.

Panel a counts distinct targets per disease and manifestation in four
mutually exclusive states, so the undrugged-but-tractable band is visible
as the repurposing-gap it represents rather than hidden inside a single
"no drug" bar.

Panel b shows the delivery-route verdict for the drugs where a route is
actually recorded. Preclinical compounds carry no route in ChEMBL by
construction and would swamp the panel, so they are counted in the caption
instead of plotted.

Every claim in a title is computed from the plotted table at render time.

Run from the repo root:
  python phase-4/scripts/phase4_figure.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SHORT = {
    "Malignant peripheral nerve sheath tumor (MPNST)": "MPNST",
    "ANNUBP / atypical neurofibroma": "ANNUBP / atypical NF",
    "Plexiform neurofibroma": "Plexiform NF",
    "Cutaneous neurofibroma": "Cutaneous NF",
    "Optic pathway glioma": "Optic pathway glioma",
    "Non-vestibular schwannoma": "Non-vestibular schwannoma",
    "Vestibular schwannoma": "Vestibular schwannoma",
}

STATES = [
    ("approved drug exists", "#1f4e79"),
    ("drug exists, none approved", "#4e94c8"),
    ("no drug, target tractable", "#9ecae1"),
    ("no drug, no tractability call", "#e3e3e3"),
]

ROUTE_ORDER = [
    ("appropriate_systemic", "systemic, appropriate", "#1f4e79"),
    ("appropriate_systemic_cns", "systemic and predicted CNS-penetrant", "#2e75b6"),
    ("appropriate_topical", "topical, appropriate here", "#4e94c8"),
    ("cns_penetration_unknown", "systemic, CNS penetration unknown", "#bdd7ee"),
    ("excluded_not_bbb_penetrant", "excluded: not CNS-penetrant", "#d9a441"),
    ("excluded_biologic_cns", "excluded: biologic for a CNS target", "#c97b24"),
    ("excluded_topical_only", "excluded: topical only", "#a5541f"),
]


def target_state(row) -> str:
    if row["n_drugs_approved"] > 0:
        return "approved drug exists"
    if row["n_drugs"] > 0:
        return "drug exists, none approved"
    if pd.notna(row["top_tractability_bucket"]):
        return "no drug, target tractable"
    return "no drug, no tractability call"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    data = root / "phase-4/data"

    dossier = pd.read_csv(data / "phase4-target-dossier.csv")
    routes = pd.read_csv(data / "phase4-drug-route-flags.csv.gz")

    try:
        from figure_style import apply_figure_style, panel_letter

        apply_figure_style(sizes=(8, 7, 6))
    except Exception:
        mpl.rcParams.update(
            {"font.size": 8, "axes.spines.top": False, "axes.spines.right": False}
        )

        def panel_letter(ax, letter, **kw):
            ax.text(
                -0.08, 1.06, letter, transform=ax.transAxes, fontsize=10,
                fontweight="bold", va="bottom", ha="right",
            )

    dossier = dossier.copy()
    dossier["state"] = dossier.apply(target_state, axis=1)
    dossier["label"] = [
        f"{d}  {SHORT.get(m, m)}" for d, m in zip(dossier["disease"], dossier["manifestation"])
    ]

    counts = (
        dossier.groupby(["label", "state"])["gene_symbol"]
        .nunique()
        .unstack(fill_value=0)
        .reindex(columns=[s for s, _ in STATES], fill_value=0)
    )
    counts = counts.loc[counts.sum(axis=1).sort_values(ascending=True).index]

    plotted_routes = routes[routes["route_flag"] != "route_unknown"].copy()
    plotted_routes["label"] = [
        f"{d}  {SHORT.get(m, m)}"
        for d, m in zip(plotted_routes["disease"], plotted_routes["manifestation"])
    ]
    route_counts = (
        plotted_routes.groupby(["label", "route_flag"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=counts.index, fill_value=0)
        .reindex(columns=[f for f, _, _ in ROUTE_ORDER], fill_value=0)
    )

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.0))

    ax = axes[0]
    left = np.zeros(len(counts))
    y = np.arange(len(counts))
    for state, colour in STATES:
        values = counts[state].to_numpy()
        ax.barh(y, values, left=left, color=colour, label=state, height=0.68)
        left += values
    ax.set_yticks(y, counts.index)
    ax.set_xlabel("distinct candidate targets")
    ax.set_title("target state after the drug layer", loc="left", fontsize=7, pad=6)
    for i, total in enumerate(counts.sum(axis=1)):
        ax.text(total + max(counts.sum(axis=1)) * 0.012, i, f"{int(total)}", va="center", fontsize=6)
    ax.margins(x=0.12, y=0.04)
    ax.legend(frameon=False, fontsize=6, loc="lower right")

    ax = axes[1]
    left = np.zeros(len(route_counts))
    for flag, label, colour in ROUTE_ORDER:
        values = route_counts[flag].to_numpy()
        ax.barh(y, values, left=left, color=colour, label=label, height=0.68)
        left += values
    ax.set_yticks(y, ["" for _ in route_counts.index])
    ax.set_xlabel("target-drug pairs with a recorded route")
    ax.set_title("delivery-route verdict", loc="left", fontsize=7, pad=6)
    ax.margins(x=0.08, y=0.04)
    ax.legend(frameon=False, fontsize=6, loc="lower right")

    for ax, letter in zip(axes, "ab"):
        panel_letter(ax, letter)

    n_undrugged_tractable = int(
        dossier.loc[dossier["state"] == "no drug, target tractable", "gene_symbol"].nunique()
    )
    n_with_drug = int(dossier.loc[dossier["n_drugs"] > 0, "gene_symbol"].nunique())
    n_total = int(dossier["gene_symbol"].nunique())
    headline = (
        f"{n_with_drug} of {n_total} candidate targets have a known drug; a further "
        f"{n_undrugged_tractable} are undrugged but carry a tractability call"
    )
    fig.suptitle(headline, fontsize=8, x=0.012, ha="left", y=0.985)

    excluded = int(
        routes["route_flag"].isin(
            {"excluded_topical_only", "excluded_not_bbb_penetrant", "excluded_biologic_cns"}
        ).sum()
    )
    preclinical = int((routes["route_flag"] == "route_unknown").sum())
    fig.text(
        0.012,
        0.022,
        f"Panel b omits {preclinical:,} target-drug pairs whose compound has no clinical route "
        f"recorded in ChEMBL. {excluded:,} pairs are flagged as delivery-inappropriate and kept "
        "for audit rather than dropped.",
        fontsize=6,
        color="#4a4a4a",
    )

    fig.tight_layout(rect=(0, 0.045, 1, 0.95))
    outdir = root / "phase-4/docs/figures"
    outdir.mkdir(parents=True, exist_ok=True)
    out = outdir / "phase4-tractability.png"
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
    print(headline)


if __name__ == "__main__":
    main()
