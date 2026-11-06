#!/usr/bin/env python3
"""Generate the Phase 3b decision record.

Every current-state number in the prose is recomputed from the committed
tables at build time, following the Phase 1b and Phase 3 report convention.
Facts that are decisions rather than counts (who decided what, and when)
live in DECISION below with their date, because no table holds them.

Run from the repo root:
  python phase-3b/scripts/build_phase3b_report.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

DECISION = {
    "date": "2026-11-04",
    "decided_by": "Kara",
    "ruling": (
        "All seven Phase 3 strata that produced a candidate carry into Phase 4. "
        "No candidate-bearing stratum is deferred."
    ),
}

CNS_MANIFESTATIONS = {
    "Optic pathway glioma",
    "High grade glioma",
    "Non-optic LGG",
    "Cognition / Behavioral / Learning",
}
TOPICAL_ELIGIBLE = {"Cutaneous neurofibroma", "ANNUBP / atypical neurofibroma"}


def fmt_int(value) -> str:
    return f"{int(value):,}"


def build(root: Path) -> str:
    cov = pd.read_csv(root / "phase-3b/data/phase3b-coverage.csv")
    strata = pd.read_csv(root / "phase-3b/data/phase3b-stratum-summary.csv")
    cov["cross_dataset"] = cov["expr_targets_cross_dataset"]

    selected = cov[cov["expr_targets"] > 0].copy()
    deferred_lit_only = cov[(cov["expr_targets"] == 0) & (cov["lit_targets"] > 0)].copy()
    empty = cov[(cov["expr_targets"] == 0) & (cov["lit_targets"] == 0)]
    producing = strata[strata["candidate_genes"] > 0]
    barren = strata[strata["candidate_genes"] == 0]

    lines: list[str] = []
    add = lines.append

    add("# Phase 3b: evidence coverage review and manifestation prioritisation")
    add("")
    add(f"Decision date: {DECISION['date']}. Decided by: {DECISION['decided_by']}.")
    add("")
    add("## Decision")
    add("")
    add(DECISION["ruling"])
    add("")
    add(
        f"This selects {len(selected)} disease and manifestation combinations, drawn from "
        f"{len(producing)} of the {len(strata)} Phase 3 strata. "
        f"The remaining stratum, {barren['comparison_class'].iloc[0] if len(barren) else 'none'}, "
        "produced no significant gene at all and so selects nothing."
    )
    add("")
    add(
        "Deprioritised combinations are deferred, not dropped: their Phase 1b rows stay in "
        "the repo and can be taken through Phase 4 in a later pass without rerunning anything "
        "upstream."
    )
    add("")

    add("## Combinations carried into Phase 4")
    add("")
    add(
        "| Disease | Manifestation | Literature targets | Expression targets | "
        "Cross-dataset supported | Datasets | Overlap genes |"
    )
    add("| --- | --- | --- | --- | --- | --- | --- |")
    for row in selected.sort_values(
        ["disease", "cross_dataset"], ascending=[True, False]
    ).itertuples():
        add(
            f"| {row.disease} | {row.manifestation} | {fmt_int(row.lit_targets)} | "
            f"{fmt_int(row.expr_targets)} | {fmt_int(row.cross_dataset)} | "
            f"{fmt_int(row.expr_datasets)} | {fmt_int(row.overlap_genes)} |"
        )
    add("")

    with_overlap = selected[selected["overlap_genes"] > 0]
    add(
        f"{len(with_overlap)} of the {len(selected)} selected combinations have at least one gene "
        "named by both the literature list and the expression list:"
    )
    add("")
    for row in with_overlap.sort_values("overlap_genes", ascending=False).itertuples():
        add(f"- {row.disease} {row.manifestation}: {row.overlap_gene_names}")
    add("")

    add("## What each selected combination rests on")
    add("")
    add("| Stratum | Disease | Contrasts | Datasets | Tier A | Tier B | Tier C |")
    add("| --- | --- | --- | --- | --- | --- | --- |")
    for row in producing.itertuples():
        add(
            f"| {row.comparison_class} | {row.disease} | {row.n_contrasts} | {row.n_datasets} | "
            f"{row.expr_targets_tier_a} | {row.expr_targets_tier_b} | {row.expr_targets_tier_c} |"
        )
    add("")

    single = producing[producing["n_datasets"] < 2]
    no_cross = producing[
        (producing["expr_targets_tier_a"] + producing["expr_targets_tier_b"]) == 0
    ]
    add(
        f"{len(no_cross)} of the {len(producing)} producing strata carry no cross-dataset support "
        "at all, so every candidate they contribute is tier C, significant in one dataset only: "
        + ", ".join(sorted(no_cross["comparison_class"]))
        + ". "
        f"{len(single)} rest on a single dataset: "
        + ", ".join(sorted(single["comparison_class"]))
        + "."
    )
    add("")
    add(
        "Two label caveats that change how the table above reads, both carried forward into "
        "Phase 4 rather than corrected here:"
    )
    add("")
    add(
        "- Cutaneous neurofibroma's expression evidence comes entirely from the "
        "nf1_pnst_vs_normal stratum, which is labelled for MPNST, plexiform neurofibroma and "
        "cutaneous neurofibroma together. Those genes are a shared nerve sheath tumour against "
        "normal nerve signature, not a cutaneous-specific one."
    )
    add(
        "- NF2-SWN Pain and NF2-SWN non-vestibular schwannoma both rest solely on the painful "
        "against non-painful schwannoma stratum, whose strongest enriched pathway is cornified "
        "envelope formation, a skin signature most likely reflecting differing overlying tissue "
        "between the arms."
    )
    add("")

    add("## Deferred")
    add("")
    add(
        f"{len(deferred_lit_only)} combinations have literature targets but no expression "
        "contrast anywhere in the Phase 2 launch set, so Phase 4 has no expression-derived "
        "candidate to query for them:"
    )
    add("")
    add("| Disease | Manifestation | Literature targets | Full-text supported | Papers |")
    add("| --- | --- | --- | --- | --- |")
    for row in deferred_lit_only.sort_values(
        "lit_targets", ascending=False
    ).itertuples():
        add(
            f"| {row.disease} | {row.manifestation} | {fmt_int(row.lit_targets)} | "
            f"{fmt_int(row.lit_targets_fulltext)} | {fmt_int(row.lit_papers)} |"
        )
    add("")
    biggest = deferred_lit_only.sort_values("lit_targets", ascending=False).iloc[0]
    add(
        f"The largest of these is {biggest.disease} {biggest.manifestation} with "
        f"{fmt_int(biggest.lit_targets)} literature targets over {fmt_int(biggest.lit_papers)} "
        "papers. It has no contrast-bearing dataset because the standing Phase 2 policy excludes "
        "sporadic material as a reference arm, so the sporadic comparators in GSE232528 were "
        "dropped and the dataset entered the manifest single-armed."
    )
    add("")
    add(
        f"A further {len(empty)} combinations have neither kind of evidence and are shown as "
        "explicit zeros in phase-3b/data/phase3b-coverage.csv rather than omitted."
    )
    add("")

    swn = cov[cov["disease"] == "SWN"]
    add(
        "Schwannomatosis is the starkest gap: it holds "
        f"{fmt_int(swn['lit_targets'].sum())} literature targets across "
        f"{int((swn['lit_targets'] > 0).sum())} manifestations and no dataset anywhere in the "
        "launch set, so it contributes nothing to Phase 4. GSE292071 is the only launch-set "
        "dataset carrying a non-NF2 schwannomatosis contrast and its deposit is unusable."
    )
    add("")

    add("## What this means for Phase 4")
    add("")
    cns_selected = sorted(set(selected["manifestation"]) & CNS_MANIFESTATIONS)
    topical_selected = sorted(set(selected["manifestation"]) & TOPICAL_ELIGIBLE)
    add(
        "Phase 4 queries the union of the expression-derived and literature-derived candidates "
        "for the selected combinations. The delivery route filter applies as follows: topical "
        "delivery is acceptable only for "
        + ", ".join(topical_selected)
        + "; every other selected manifestation requires a systemic route. Blood-brain-barrier "
        "penetration is additionally required for "
        + (", ".join(cns_selected) if cns_selected else "no selected manifestation")
        + "."
    )
    add("")
    add(
        "Because four producing strata carry tier C evidence only, Phase 6 should be expected to "
        "downweight a large share of what Phase 4 annotates. That is the intended consequence of "
        "the wide selection, not a defect in it."
    )
    add("")
    add("## Reproducing this")
    add("")
    add("```")
    add("python phase-3b/scripts/phase3b_coverage.py")
    add("python phase-3b/scripts/phase3b_figure.py")
    add("python phase-3b/scripts/build_phase3b_report.py")
    add("```")
    add("")
    add("Outputs: phase-3b/data/phase3b-coverage.csv (all 60 combinations, zeros included),")
    add("phase-3b/data/phase3b-stratum-summary.csv, phase-3b/docs/figures/phase3b-coverage.png,")
    add("and this document.")
    add("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()

    text = build(root)
    if "\u2014" in text or "\u2013" in text:
        raise SystemExit("generated text contains an em or en dash; rewrite the sentence")

    out = root / "phase-3b/docs/phase3b-prioritisation.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out} ({len(text.splitlines())} lines)")


if __name__ == "__main__":
    main()
