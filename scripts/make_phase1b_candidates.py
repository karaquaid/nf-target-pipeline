#!/usr/bin/env python3
"""Derive the Phase 1b candidate list from the full annotated target table.

`data/phase1b-literature-targets.csv` is the audit record: every row the phase
verified, whatever became of it. The candidate list is that table minus two
classes of row, and is what later phases consume:

* **Germline NF disease genes** (`driver_gene`). NF1, NF2, SMARCB1, LZTR1 and
  SPRED1 are excluded as targets because their role is established and
  re-prioritising them tells the project nothing.
* **Rows contradicted by full text** (`evidence_tier == "full text - not
  supported"`). The papers read do not support the claim, so the row is not a
  candidate even where a co-supporting paper is still unread.

Neither class is deleted. Both keep their rows, flags and tiers in the full
table, so an exclusion can be reversed or widened by changing this filter.

The script also refreshes the derived columns of the reference table: the
candidate-facing ones (`candidate_targets`, `n_candidate_rows`,
`supports_candidate_rows`), since a paper can stop backing any candidate once
these rows are removed, and the descriptive ones (`manifestations`,
`n_manifestations`), which list what each paper was found to speak to, in the
vocabulary's own order. Manifestations come from the full table rather than the
candidate list, so a paper whose only rows are germline driver rows still shows
its subject.

Usage (from the repository root), and the order the three scripts run in:

    python scripts/make_phase1b_candidates.py   # this script
    python scripts/build_phase1b_report.py      # write-up and coverage matrix
    python scripts/make_phase1b_figure.py       # Figure 1

Requires pandas.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_phase1b_figure import MANIFESTATIONS  # noqa: E402

EXCLUDED_TIERS = ("full text - not supported",)


def derive(targets: pd.DataFrame) -> pd.DataFrame:
    for column in ("driver_gene", "evidence_tier", "gene_target", "supporting_pmids"):
        if column not in targets.columns:
            raise ValueError(f"full target table is missing column {column!r}")

    keep = ~targets.driver_gene.astype(bool) & ~targets.evidence_tier.isin(EXCLUDED_TIERS)
    candidates = targets[keep].drop(columns=["driver_gene"]).reset_index(drop=True)
    candidates = candidates.sort_values(
        ["n_fulltext_supported", "n_supporting_papers", "gene_target"],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    return candidates


def annotate_references(refs: pd.DataFrame, targets: pd.DataFrame,
                        candidates: pd.DataFrame) -> pd.DataFrame:
    by_paper: dict[str, set[str]] = defaultdict(set)
    rows_per_paper: dict[str, int] = defaultdict(int)
    for row in candidates.itertuples():
        for pmid in str(row.supporting_pmids).split(";"):
            if pmid:
                by_paper[pmid].add(row.gene_target)
                rows_per_paper[pmid] += 1

    # Manifestations are taken from the full table, not the candidate list, so a
    # paper that speaks only to a germline driver row still shows what it is about.
    manifestations: dict[str, set[str]] = defaultdict(set)
    for row in targets.itertuples():
        for pmid in str(row.supporting_pmids).split(";"):
            if pmid:
                manifestations[pmid].add(row.manifestation)
    order = {m: i for i, m in enumerate(MANIFESTATIONS)}

    def in_vocabulary_order(pmid: str) -> str:
        found = manifestations.get(pmid, set())
        return ";".join(sorted(found, key=lambda m: order.get(m, len(order))))

    refs = refs.copy()
    pmids = refs.pmid.astype(str)
    refs["manifestations"] = pmids.map(in_vocabulary_order)
    refs["n_manifestations"] = pmids.map(lambda p: len(manifestations.get(p, set())))
    refs["candidate_targets"] = pmids.map(lambda p: ";".join(sorted(by_paper.get(p, set()))))
    refs["n_candidate_rows"] = pmids.map(lambda p: rows_per_paper.get(p, 0))
    refs["supports_candidate_rows"] = refs["n_candidate_rows"] > 0

    # Keep the descriptive columns next to the targets they describe.
    cols = list(refs.columns)
    for name in ("n_manifestations", "manifestations"):
        cols.insert(cols.index("n_targets") + 1, cols.pop(cols.index(name)))
    return refs[cols]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, default=Path("data"))
    args = parser.parse_args()

    targets = pd.read_csv(args.data / "phase1b-literature-targets.csv")
    refs = pd.read_csv(args.data / "phase1b-references.csv", dtype={"pmid": str})

    candidates = derive(targets)
    refs = annotate_references(refs, targets, candidates)

    candidates.to_csv(args.data / "phase1b-candidate-targets.csv", index=False)
    refs.to_csv(args.data / "phase1b-references.csv", index=False)

    excluded = len(targets) - len(candidates)
    drivers = int(targets.driver_gene.astype(bool).sum())
    contradicted = int(targets.evidence_tier.isin(EXCLUDED_TIERS).sum())
    print(
        f"{len(candidates)} candidate rows over {candidates.gene_target.nunique()} labels "
        f"({excluded} excluded from {len(targets)}: {drivers} germline driver rows, "
        f"{contradicted} contradicted by full text)"
    )
    print(
        f"{int((~refs.supports_candidate_rows).sum())} of {len(refs)} papers now back "
        "no candidate row"
    )


if __name__ == "__main__":
    main()
