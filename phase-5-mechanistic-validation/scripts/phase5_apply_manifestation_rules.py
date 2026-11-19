#!/usr/bin/env python3
"""Propagate the Phase 4 manifestation rules into the Phase 5 drug table.

Two rules changed on 2026-11-17 (Kara): ANNUBP left TOPICAL_ELIGIBLE, and
Vestibular schwannoma joined CNS_RELEVANT. Both are defined once, in
phase4_targets.py, and this script imports them rather than restating them.

It exists because a full Phase 5 re-run needs ClinicalTrials.gov build artifacts
that are not in the repo (phase5_drug_search.py fails on the missing
nf_trial_ids column), so the two affected columns are recomputed in place from
the same functions Phase 4 uses. Everything else in the table is untouched.

Run from the repo root. Prints what changed.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "phase-4" / "scripts"))
from phase4_targets import CNS_RELEVANT, TOPICAL_ELIGIBLE  # noqa: E402
from phase4_dossier import route_verdict  # noqa: E402

MATCHES = ROOT / "phase-5-mechanistic-validation" / "data" / "phase5-drug-matches.csv.gz"


def main() -> None:
    df = pd.read_csv(MATCHES, low_memory=False)
    before_bbb = df["bbb_required"].astype(str).str.lower().eq("true").sum()
    before_flags = df["route_flag"].value_counts(dropna=False).to_dict()

    df["bbb_required"] = df["manifestation"].isin(CNS_RELEVANT)
    # Only rows that actually carry a drug get a route verdict. Applying it to
    # drugless rows gave 2,060 of them a route_unknown flag they never had.
    has_drug = df["drug_name"].notna()
    verdicts = df.loc[has_drug].apply(route_verdict, axis=1, result_type="expand")
    df.loc[has_drug, "route_flag"] = verdicts[0]
    df.loc[has_drug, "route_reason"] = verdicts[1]
    df.loc[has_drug, "route_appropriate"] = df.loc[has_drug, "route_flag"].isin(
        {"appropriate_systemic", "appropriate_topical", "appropriate_systemic_cns"})

    df.to_csv(MATCHES, index=False, compression="gzip")
    print({
        "bbb_required_true": {"before": int(before_bbb),
                              "after": int(df["bbb_required"].sum())},
        "route_flag_before": before_flags,
        "route_flag_after": df["route_flag"].value_counts(dropna=False).to_dict(),
        "topical_eligible": sorted(TOPICAL_ELIGIBLE),
        "cns_relevant": sorted(CNS_RELEVANT),
    })


if __name__ == "__main__":
    main()
