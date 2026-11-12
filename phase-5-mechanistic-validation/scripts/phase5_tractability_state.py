#!/usr/bin/env python3
"""Three-state tractability for the Phase 5 target set (decided 2026-11-11).

Phase 4 records `tractability_status` as either `assessed` or `no tractability
bucket returned`. The second value collapses two different situations and, read
as a negative, contradicts the data: 33 of the 291 rows with no bucket have a
known drug from DGIdb or ChEMBL. Open Targets tractability buckets are
POSITIVE-evidence assertions - has ligand, structure with ligand, predicted
tractable - so the absence of a positive assertion is not an assertion of
absence. This is the same shape as the Phase 6 CNS-delivery rule, for the same
reason.

States, per gene:
  evidence_present      at least one Open Targets bucket is True, OR the gene
                        has a known drug or chemical probe. A drug IS
                        tractability evidence, and it comes from sources the
                        buckets do not fully cover, so it overrides a missing
                        or all-False bucket rather than being contradicted by it
  assessed_no_evidence  the gene is in the Open Targets response and every
                        bucket came back False, with no drug or probe. A genuine
                        look that found nothing; mildly downweightable, but NOT
                        'untractable'
  not_assessed          the gene is absent from the Open Targets response, or
                        was never queryable for want of an identifier, with no
                        drug or probe. Unassessed, never scored as a negative

Additive by design: Phase 4's `tractability_status` is left intact and this
writes a separate per-gene table for Phase 6 to join.

Usage:
  python phase5_tractability_state.py --builddir build/phase5 --datadir <phase>/data
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--builddir", default="build/phase5")
    ap.add_argument("--datadir", default="phase-5-mechanistic-validation/data")
    args = ap.parse_args()
    build, data = Path(args.builddir), Path(args.datadir)

    surv = pd.read_csv(data / "phase5-drug-candidate-set.csv")
    tr = pd.read_csv(build / "phase4-opentargets-tractability.csv.gz")

    is_true = tr.value.astype(str).str.lower() == "true"
    true_buckets = (tr[is_true].groupby("gene_symbol")
                    .apply(lambda g: "|".join(sorted(set(g.modality + ":" + g.bucket))),
                           include_groups=False))
    n_true = tr.assign(_t=is_true).groupby("gene_symbol")._t.sum()
    in_ot = set(tr.gene_symbol)

    # gene-level roll-up of the row-level drug and probe evidence
    per_gene = (surv.groupby("gene_symbol")
                .agg(rows=("gene_symbol", "size"),
                     n_drugs=("n_drugs", "max"),
                     n_chemical_probes=("n_chemical_probes", "max"),
                     n_high_quality_probes=("n_high_quality_probes", "max"),
                     top_tractability_bucket=("top_tractability_bucket", "first"),
                     tractability_status=("tractability_status", "first"),
                     target_not_queryable=("target_not_queryable", "first"))
                .reset_index())
    per_gene["n_true_buckets"] = per_gene.gene_symbol.map(n_true).fillna(0).astype(int)
    per_gene["true_buckets"] = per_gene.gene_symbol.map(true_buckets)
    per_gene["in_open_targets_response"] = per_gene.gene_symbol.isin(in_ot)
    per_gene["has_drug_or_probe"] = ((per_gene.n_drugs.fillna(0) > 0)
                                     | (per_gene.n_chemical_probes.fillna(0) > 0))

    def state(r) -> str:
        if r.n_true_buckets > 0 or r.has_drug_or_probe:
            return "evidence_present"
        return "assessed_no_evidence" if r.in_open_targets_response else "not_assessed"

    def why(r) -> str:
        if r.n_true_buckets > 0:
            return f"{r.n_true_buckets} Open Targets bucket(s) true"
        if r.has_drug_or_probe:
            return ("no true bucket, but a known drug or chemical probe is itself "
                    "tractability evidence")
        if r.in_open_targets_response:
            return "in the Open Targets response with every bucket false; no drug or probe"
        if str(r.target_not_queryable).lower() == "true":
            return "symbol never resolved, so Open Targets was never queried"
        return "absent from the Open Targets response; no drug or probe"

    per_gene["tractability_evidence"] = per_gene.apply(state, axis=1)
    per_gene["tractability_rationale"] = per_gene.apply(why, axis=1)
    per_gene = per_gene.sort_values(["tractability_evidence", "gene_symbol"])
    per_gene.to_csv(data / "phase5-tractability-state.csv", index=False)

    row_state = surv[["gene_symbol"]].merge(
        per_gene[["gene_symbol", "tractability_evidence"]], on="gene_symbol", how="left")
    summary = {
        "rule": "three-state tractability; Open Targets buckets are positive-evidence "
                "assertions, so a missing bucket is not evidence of untractability",
        "genes": int(len(per_gene)),
        "candidate_rows": int(len(surv)),
        "genes_by_state": per_gene.tractability_evidence.value_counts().to_dict(),
        "rows_by_state": row_state.tractability_evidence.value_counts().to_dict(),
        "genes_rescued_by_drug_or_probe": int(((per_gene.n_true_buckets == 0)
                                               & per_gene.has_drug_or_probe).sum()),
        "phase4_status_disagreement": {
            "phase4_called_assessed_but_state_is_not_assessed": int(
                ((per_gene.tractability_status == "assessed")
                 & (per_gene.tractability_evidence == "not_assessed")).sum()),
            "phase4_called_no_bucket_but_state_is_evidence_present": int(
                ((per_gene.tractability_status != "assessed")
                 & (per_gene.tractability_evidence == "evidence_present")).sum()),
        },
    }
    json.dump(summary, open(data / "phase5-tractability-state-summary.json", "w"), indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
