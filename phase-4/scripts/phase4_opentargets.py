#!/usr/bin/env python3
"""Phase 4: Open Targets known drugs, tractability and chemical probes.

This closes the tractability gap the project plan left open. Open Targets
assigns each target a set of tractability buckets per modality (small
molecule, antibody, PROTAC, other), which is an assessment a target can
carry even when no drug exists for it, so it is the one source here that
says something useful about an undrugged target.

Schema notes, verified against the live API on 2026-11-04 rather than
written from memory. The current release does NOT have the fields older
documentation describes:
  - Target.knownDrugs no longer exists; the field is
    Target.drugAndClinicalCandidates, returning clinicalTargets.
  - Drug.isApproved, Drug.maximumClinicalTrialPhase and
    Drug.hasBeenWithdrawn no longer exist; clinical stage is
    Drug.maximumClinicalStage, a string such as "PHASE_3".
  - ClinicalDiseaseListItem has no id; the disease sits under
    .disease { id name }.

Output:
  phase-4/data/phase4-opentargets-tractability.csv
  phase-4/data/phase4-opentargets-drugs.csv.gz
  phase-4/data/phase4-opentargets-provenance.json

Run from the repo root:
  python phase-4/scripts/phase4_opentargets.py
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
import requests

ENDPOINT = "https://api.platform.opentargets.org/api/v4/graphql"

QUERY = """
query($id:String!){
  target(ensemblId:$id){
    id approvedSymbol
    tractability{ label value modality }
    chemicalProbes{ id isHighQuality }
    drugAndClinicalCandidates{
      count
      rows{
        maxClinicalStage
        drug{ id name drugType maximumClinicalStage }
        diseases{ disease{ id name } }
      }
    }
  }
}
"""


def post(ensembl_id: str, retries: int = 4) -> dict:
    last = None
    for attempt in range(retries):
        try:
            response = requests.post(
                ENDPOINT, json={"query": QUERY, "variables": {"id": ensembl_id}}, timeout=120
            )
            if response.status_code == 200:
                body = response.json()
                if body.get("errors"):
                    raise RuntimeError(body["errors"])
                return body["data"]["target"]
            last = f"HTTP {response.status_code}"
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"{ensembl_id}: {last}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    data = root / "phase-4/data"

    identifiers = pd.read_csv(data / "phase4-identifiers.csv")
    have_ensembl = identifiers[identifiers["ensembl_gene_id"].notna()].copy()
    have_ensembl = have_ensembl[have_ensembl["ensembl_gene_id"] != ""]
    # A symbol can map to several Ensembl ids; query the first and record it.
    have_ensembl["primary_ensembl"] = have_ensembl["ensembl_gene_id"].str.split(";").str[0]
    jobs = have_ensembl[["gene_symbol", "primary_ensembl"]].drop_duplicates()

    tract_rows, drug_rows, probe_rows, failed, missing = [], [], [], [], []
    for n, job in enumerate(jobs.itertuples(), start=1):
        try:
            target = post(job.primary_ensembl)
        except RuntimeError as exc:
            failed.append({"gene_symbol": job.gene_symbol, "error": str(exc)})
            continue
        if target is None:
            missing.append(job.gene_symbol)
            continue

        for entry in target["tractability"]:
            tract_rows.append(
                {
                    "gene_symbol": job.gene_symbol,
                    "ensembl_gene_id": target["id"],
                    "approved_symbol": target["approvedSymbol"],
                    "modality": entry["modality"],
                    "bucket": entry["label"],
                    "value": entry["value"],
                }
            )
        for probe in target["chemicalProbes"]:
            probe_rows.append(
                {
                    "gene_symbol": job.gene_symbol,
                    "probe_id": probe["id"],
                    "is_high_quality": probe["isHighQuality"],
                }
            )
        for row in target["drugAndClinicalCandidates"]["rows"]:
            drug = row["drug"] or {}
            diseases = [
                d["disease"]["name"] for d in row["diseases"] if d.get("disease")
            ]
            disease_ids = [d["disease"]["id"] for d in row["diseases"] if d.get("disease")]
            drug_rows.append(
                {
                    "gene_symbol": job.gene_symbol,
                    "ensembl_gene_id": target["id"],
                    "chembl_id": drug.get("id", ""),
                    "drug_name": drug.get("name", ""),
                    "drug_type": drug.get("drugType", ""),
                    "max_clinical_stage_for_target": row["maxClinicalStage"],
                    "drug_max_clinical_stage": drug.get("maximumClinicalStage", ""),
                    "n_diseases": len(diseases),
                    "diseases": "; ".join(sorted(set(diseases))),
                    "disease_ids": "; ".join(sorted(set(disease_ids))),
                }
            )
        if n % 200 == 0:
            print(f"  {n}/{len(jobs)} targets, {len(drug_rows)} drug rows", flush=True)

    tract = pd.DataFrame(tract_rows)
    drugs = pd.DataFrame(drug_rows)
    probes = pd.DataFrame(probe_rows)

    tract.to_csv(data / "phase4-opentargets-tractability.csv", index=False)
    drugs.to_csv(data / "phase4-opentargets-drugs.csv.gz", index=False, compression="gzip")
    probes.to_csv(data / "phase4-opentargets-probes.csv", index=False)

    provenance = {
        "endpoint": ENDPOINT,
        "schema_verified": "live introspection on 2026-11-04",
        "query": QUERY.strip(),
        "targets_queried": int(len(jobs)),
        "targets_returned_null": sorted(missing),
        "targets_failed": failed,
        "tractability_rows": int(len(tract)),
        "drug_rows": int(len(drugs)),
        "probe_rows": int(len(probes)),
        "targets_with_a_drug": int(drugs["gene_symbol"].nunique()) if len(drugs) else 0,
        "distinct_drugs": int(drugs["chembl_id"].nunique()) if len(drugs) else 0,
    }
    (data / "phase4-opentargets-provenance.json").write_text(json.dumps(provenance, indent=2))
    print(
        json.dumps(
            {k: v for k, v in provenance.items() if k not in {"query", "targets_returned_null"}},
            indent=2,
        )
    )
    print(f"targets returning null: {len(missing)}")


if __name__ == "__main__":
    main()
