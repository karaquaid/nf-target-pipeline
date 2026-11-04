#!/usr/bin/env python3
"""Phase 4: ChEMBL drug records and mechanisms of action.

The drug universe is the union of the ChEMBL identifiers reached two ways:
Open Targets drugAndClinicalCandidates (ChEMBL-derived, target-linked) and
the ChEMBL-namespaced drug concepts in the DGIdb interaction claims. DGIdb
drugs carrying only an RxNorm, NCIt or IUPHAR concept id cannot be looked
up here and are recorded as such rather than silently dropped.

Two things this supplies that nothing else in Phase 4 does:

  - max_phase, the plan's first-pass clinical-stage filter.
  - the oral / parenteral / topical route booleans on the molecule record,
    which feed the delivery-route filter alongside the openFDA labels.

Field names verified against https://www.ebi.ac.uk/chembl/api/data on
2026-11-04. Note that max_phase arrives as a string ("4.0"), and that
molecule_properties can be absent, so neither is assumed.

Output:
  phase-4/data/phase4-chembl-drugs.csv.gz
  phase-4/data/phase4-chembl-mechanisms.csv.gz
  phase-4/data/phase4-chembl-provenance.json

Run from the repo root:
  python phase-4/scripts/phase4_chembl.py
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
import requests

BASE = "https://www.ebi.ac.uk/chembl/api/data"
MOLECULE_FIELDS = [
    "molecule_chembl_id",
    "pref_name",
    "molecule_type",
    "max_phase",
    "first_approval",
    "oral",
    "parenteral",
    "topical",
    "black_box_warning",
    "withdrawn_flag",
    "natural_product",
    "prodrug",
    "therapeutic_flag",
    "indication_class",
    "chirality",
]


def get(path: str, params: dict, retries: int = 4):
    last = None
    for attempt in range(retries):
        try:
            response = requests.get(f"{BASE}/{path}", params=params, timeout=180)
            if response.status_code == 200:
                return response.json()
            last = f"HTTP {response.status_code}"
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(last)


def paged(path: str, key: str, params: dict):
    """Follow the API's own next-page links rather than assuming an offset
    scheme, and stop when it says there is no next page."""
    out, page = [], dict(params)
    page.setdefault("limit", 1000)
    offset = 0
    while True:
        page["offset"] = offset
        body = get(path, page)
        out.extend(body.get(key, []))
        meta = body.get("page_meta", {})
        if not meta.get("next"):
            return out
        offset += page["limit"]


def chunked(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--chunk", type=int, default=40, help="ids per __in query")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    data = root / "phase-4/data"

    dgidb = pd.read_csv(data / "phase4-dgidb-interactions.csv.gz")
    ot = pd.read_csv(data / "phase4-opentargets-drugs.csv.gz")

    from_dgidb = set(
        dgidb.loc[dgidb["drug_concept_id"].str.startswith("chembl:"), "drug_concept_id"]
        .str.split(":")
        .str[1]
        .str.upper()
    )
    from_ot = set(ot["chembl_id"].dropna().astype(str).str.upper()) - {""}
    ids = sorted(from_dgidb | from_ot)

    non_chembl = int(
        dgidb.loc[~dgidb["drug_concept_id"].str.startswith("chembl:"), "drug_concept_id"].nunique()
    )

    molecules, mechanisms, failed = [], [], []
    for n, chunk in enumerate(chunked(ids, args.chunk), start=1):
        joined = ",".join(chunk)
        try:
            for mol in paged("molecule.json", "molecules", {"molecule_chembl_id__in": joined}):
                molecules.append({field: mol.get(field) for field in MOLECULE_FIELDS})
        except RuntimeError as exc:
            failed.append({"stage": "molecule", "ids": chunk, "error": str(exc)})
        try:
            for mech in paged("mechanism.json", "mechanisms", {"molecule_chembl_id__in": joined}):
                mechanisms.append(
                    {
                        "molecule_chembl_id": mech.get("molecule_chembl_id"),
                        "parent_molecule_chembl_id": mech.get("parent_molecule_chembl_id"),
                        "target_chembl_id": mech.get("target_chembl_id"),
                        "action_type": mech.get("action_type"),
                        "mechanism_of_action": mech.get("mechanism_of_action"),
                        "direct_interaction": mech.get("direct_interaction"),
                        "disease_efficacy": mech.get("disease_efficacy"),
                        "molecular_mechanism": mech.get("molecular_mechanism"),
                        "selectivity_comment": mech.get("selectivity_comment"),
                        "binding_site_comment": mech.get("binding_site_comment"),
                        "mechanism_max_phase": mech.get("max_phase"),
                    }
                )
        except RuntimeError as exc:
            failed.append({"stage": "mechanism", "ids": chunk, "error": str(exc)})
        if n % 20 == 0:
            print(
                f"  chunk {n}/{(len(ids) + args.chunk - 1) // args.chunk}: "
                f"{len(molecules)} molecules, {len(mechanisms)} mechanisms",
                flush=True,
            )

    mol_frame = pd.DataFrame(molecules).drop_duplicates(subset=["molecule_chembl_id"])
    mech_frame = pd.DataFrame(mechanisms).drop_duplicates()
    # max_phase arrives as a string; keep the raw value and add a numeric one.
    mol_frame["max_phase_numeric"] = pd.to_numeric(mol_frame["max_phase"], errors="coerce")

    mol_frame.to_csv(data / "phase4-chembl-drugs.csv.gz", index=False, compression="gzip")
    mech_frame.to_csv(data / "phase4-chembl-mechanisms.csv.gz", index=False, compression="gzip")

    provenance = {
        "base_url": BASE,
        "fields_verified": "live record inspection on 2026-11-04",
        "drug_ids_requested": len(ids),
        "drug_ids_from_open_targets": len(from_ot),
        "drug_ids_from_dgidb": len(from_dgidb),
        "dgidb_drugs_without_a_chembl_id": non_chembl,
        "molecules_returned": int(len(mol_frame)),
        "mechanism_rows": int(len(mech_frame)),
        "drugs_with_a_mechanism": int(mech_frame["molecule_chembl_id"].nunique())
        if len(mech_frame)
        else 0,
        "approved_drugs": int((mol_frame["max_phase_numeric"] == 4).sum()),
        "failed_chunks": failed,
    }
    (data / "phase4-chembl-provenance.json").write_text(json.dumps(provenance, indent=2))
    print(json.dumps({k: v for k, v in provenance.items() if k != "failed_chunks"}, indent=2))
    print(f"failed chunks: {len(failed)}")


if __name__ == "__main__":
    main()
