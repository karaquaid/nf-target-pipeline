#!/usr/bin/env python3
"""Apply Phase 1b's target rules to the Phase 5 target set before drug-finding.

Phase 1b filters its candidate list with three exclusions and carries three
curated flags. Kara's rulings (2026-11-09) on how each carries into drug-finding:

  R1 germline NF disease genes      EXCLUDE. NF1, NF2, SMARCB1, LZTR1, SPRED1.
                                   SPRED2 is not a germline NF gene and is not
                                   excluded by this rule.
  R2 likely_biomarker              EXCLUDE at drug-finding (Phase 1b only flags
                                   it). A tumour-suppressor deletion cannot be
                                   drugged, so a drug search against it is
                                   misleading rather than merely empty.
  R3 mutation_restricted           EXCLUDE at drug-finding.
  R4 tme_target                    KEEP and carry the flag. Microenvironment
                                   targets are a legitimate axis in plexiform
                                   neurofibroma (mast-cell and macrophage
                                   directed), so they stay in.
  R5 full-text-not-supported and out-of-scope-paper rows: already absent from
     the Phase 4 dossier at row level; verified here rather than assumed.
     Literature exclusions do NOT bind expression-derived rows - NRG1 keeps its
     three NF2-SWN expression rows, flagged so the write-up can explain why it
     reads as excluded in the Phase 1b table and present here.

Flag scope (R2/R3): the flags are a property of the target, per Phase 1b's own
annotation design, so they apply to any dossier row whose gene matches a flagged
Phase 1b label - including expression-derived rows that were never literature
reviewed. A composite label carries its flag to every constituent gene, which is
why both SPRED1 and SPRED2 leave under R2: the SPRED1/2 label is flagged
likely_biomarker.

Nothing is deleted. Every excluded row is written to the exclusions table with
the rule(s) that fired and the curator's note, so any ruling can be reversed by
changing this filter and re-running.

Usage:
  python phase5_drug_candidates.py --builddir build/phase5 --datadir <phase>/data
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

GERMLINE_DRIVERS = {"NF1", "NF2", "SMARCB1", "LZTR1", "SPRED1"}
PHASE1B = "https://raw.githubusercontent.com/karaquaid/nf-target-pipeline/main/phase-1b/data"


def _labels(value) -> set[str]:
    return set(str(value).split("|")) if isinstance(value, str) else set()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--builddir", default="build/phase5")
    ap.add_argument("--datadir", default="phase-5-mechanistic-validation/data")
    args = ap.parse_args()
    build, data = Path(args.builddir), Path(args.datadir)

    doss = pd.read_csv(build / "phase4-target-dossier.csv")
    sup = pd.read_csv(data / "phase5-target-support.csv")
    ann = pd.read_csv(build / "phase1b-target-annotations.csv")
    cand = pd.read_csv(build / "phase1b-candidate-targets.csv")
    full = pd.read_csv(build / "phase1b-literature-targets.csv")

    flagged = {c: set(ann[ann[c].fillna(False).astype(bool)].gene_target)
               for c in ("likely_biomarker", "mutation_restricted", "tme_target")}
    plain_gene = set(cand[cand.label_type == "gene"].gene_target)
    notes = dict(zip(ann.gene_target, ann.annotation_note))

    # R5 verification: no dossier row may rest on a Phase 1b row that Phase 1b
    # itself excluded. Compare on label x disease x manifestation, not label alone.
    excluded_rows = (set(zip(full.gene_target, full.disease, full.manifestation))
                     - set(zip(cand.gene_target, cand.disease, cand.manifestation)))
    leaks = []
    for r in doss.itertuples():
        for lab in _labels(r.lit_target_labels):
            if (lab, r.disease, r.manifestation) in excluded_rows:
                leaks.append({"gene_symbol": r.gene_symbol, "label": lab,
                              "disease": r.disease, "manifestation": r.manifestation})

    df = doss.merge(sup[["gene_symbol", "disease", "manifestation", "phase5_support_tier",
                         "dismech_entries", "manifestation_hpo_terms", "coverage_dismech",
                         "coverage_monarch", "gene_curie"]],
                    on=["gene_symbol", "disease", "manifestation"], how="left")

    def rules_for(row) -> tuple[list[str], list[str]]:
        labs = _labels(row.lit_target_labels)
        fired, why = [], []
        if row.gene_symbol in GERMLINE_DRIVERS:
            fired.append("R1_germline_driver")
            why.append(f"{row.gene_symbol} is a germline NF disease gene")
        for rule, col in (("R2_likely_biomarker", "likely_biomarker"),
                          ("R3_mutation_restricted", "mutation_restricted")):
            hit = (labs & flagged[col]) or ({row.gene_symbol} & flagged[col] & plain_gene)
            if hit:
                lab = sorted(hit)[0]
                fired.append(rule)
                why.append(f"Phase 1b label '{lab}' flagged {col}: {notes.get(lab)}")
        return fired, why

    applied = df.apply(rules_for, axis=1)
    df["rules_fired"] = ["|".join(a) for a, _ in applied]
    df["exclusion_reason"] = [" ;; ".join(b) for _, b in applied]
    tme_labels = flagged["tme_target"]
    df["tme_target"] = df.apply(
        lambda r: bool((_labels(r.lit_target_labels) & tme_labels)
                       or ({r.gene_symbol} & tme_labels & plain_gene)), axis=1)
    df["phase1b_literature_exclusion_note"] = ""
    df.loc[df.gene_symbol == "NRG1", "phase1b_literature_exclusion_note"] = (
        "Excluded from the Phase 1b candidate list: its only literature support was "
        "PMID 30306639, ruled not NF-relevant. Kept here on expression evidence alone, "
        "which that ruling does not bear on. No literature support is claimed for it.")

    keep = df.rules_fired == ""
    survivors = df[keep].copy()
    excluded = df[~keep].copy()
    survivors.to_csv(data / "phase5-drug-candidate-set.csv", index=False)
    excluded[["gene_symbol", "disease", "manifestation", "evidence_source",
              "lit_target_labels", "phase5_support_tier", "rules_fired",
              "exclusion_reason"]].to_csv(data / "phase5-drug-candidate-exclusions.csv", index=False)

    summary = {
        "input_rows": len(df),
        "surviving_rows": int(keep.sum()),
        "excluded_rows": int((~keep).sum()),
        "excluded_by_rule": {r: int(df.rules_fired.str.contains(r).sum())
                             for r in ("R1_germline_driver", "R2_likely_biomarker",
                                       "R3_mutation_restricted")},
        "excluded_distinct_genes": int(excluded.gene_symbol.nunique()),
        "tme_rows_kept": int(survivors.tme_target.sum()),
        "r5_phase1b_row_leaks": leaks,
        "surviving_by_stratum": {f"{d} | {m}": int(n) for (d, m), n in
                                 survivors.groupby(["disease", "manifestation"]).size().items()},
        "surviving_by_tier": survivors.phase5_support_tier.value_counts().to_dict(),
    }
    json.dump(summary, open(data / "phase5-drug-candidate-summary.json", "w"), indent=2)
    print(json.dumps(summary, indent=2)[:1600])


if __name__ == "__main__":
    main()
