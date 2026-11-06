#!/usr/bin/env python3
"""Phase 4: ChEMBL molecular properties and a CNS-penetration flag.

What ChEMBL's ADMET data actually is matters here. ChEMBL returns
CALCULATED molecular properties derived from structure, not measured
pharmacokinetics. There is no experimental blood-brain-barrier measurement
in it. So the CNS flag this script produces is a prediction from physico-
chemical properties, labelled as such everywhere it appears, and a drug
flagged predicted_permeant has not been shown to cross the barrier.

The rule applied, stated once so it can be argued with:

  predicted_permeant        TPSA <= 90, MW <= 450, 1 <= cLogP <= 5, HBD <= 3
  predicted_non_permeant    a small molecule failing any of those
  not_applicable            antibodies, proteins, oligonucleotides and other
                            large biologics, which do not cross an intact
                            barrier at therapeutic concentrations
  unknown                   no calculated properties in ChEMBL

These are the conventional CNS drug-likeness thresholds (TPSA and HBD from
the Kelder/Pajouhesh-Lenz CNS criteria, MW and logP from the same
literature). They are a filter for triage, not a substitute for a
permeability assay.

Output:
  phase-4/data/phase4-admet.csv.gz
  phase-4/data/phase4-admet-provenance.json

Run from the repo root:
  python phase-4/scripts/phase4_admet.py
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
import requests

BASE = "https://www.ebi.ac.uk/chembl/api/data"

PROPERTY_FIELDS = [
    "full_mwt",
    "mw_freebase",
    "alogp",
    "cx_logp",
    "cx_logd",
    "psa",
    "hba",
    "hbd",
    "rtb",
    "aromatic_rings",
    "heavy_atoms",
    "qed_weighted",
    "num_ro5_violations",
    "ro3_pass",
    "molecular_species",
]

BIOLOGIC_TYPES = {
    "Antibody",
    "Protein",
    "Oligonucleotide",
    "Oligosaccharide",
    "Enzyme",
    "Cell",
    "Gene",
}

# CNS drug-likeness thresholds; see module docstring.
CNS_MAX_TPSA = 90.0
CNS_MAX_MW = 450.0
CNS_MIN_LOGP = 1.0
CNS_MAX_LOGP = 5.0
CNS_MAX_HBD = 3


def get(path: str, params: dict, retries: int = 4):
    for attempt in range(retries):
        try:
            response = requests.get(f"{BASE}/{path}", params=params, timeout=180)
            if response.status_code == 200:
                return response.json()
        except Exception:  # noqa: BLE001
            pass
        time.sleep(2 * (attempt + 1))
    return None


def chunked(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def cns_flag(row) -> str:
    if row["molecule_type"] in BIOLOGIC_TYPES:
        return "not_applicable_biologic"
    tpsa, mw, hbd = row.get("psa"), row.get("mw_freebase"), row.get("hbd")
    logp = row.get("cx_logp") if pd.notna(row.get("cx_logp")) else row.get("alogp")
    if pd.isna(tpsa) or pd.isna(mw) or pd.isna(hbd) or pd.isna(logp):
        return "unknown"
    passes = (
        tpsa <= CNS_MAX_TPSA
        and mw <= CNS_MAX_MW
        and CNS_MIN_LOGP <= logp <= CNS_MAX_LOGP
        and hbd <= CNS_MAX_HBD
    )
    return "predicted_permeant" if passes else "predicted_non_permeant"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--chunk", type=int, default=40)
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    data = root / "phase-4/data"

    drugs = pd.read_csv(data / "phase4-chembl-drugs.csv.gz")
    ids = sorted(drugs["molecule_chembl_id"].dropna().unique())

    rows = []
    for n, chunk in enumerate(chunked(ids, args.chunk), start=1):
        body = get(
            "molecule.json",
            {"molecule_chembl_id__in": ",".join(chunk), "limit": 1000},
        )
        for molecule in (body or {}).get("molecules", []):
            props = molecule.get("molecule_properties") or {}
            record = {
                "molecule_chembl_id": molecule.get("molecule_chembl_id"),
                "molecule_type": molecule.get("molecule_type"),
            }
            for field in PROPERTY_FIELDS:
                value = props.get(field)
                record[field] = pd.to_numeric(value, errors="coerce") if field != "ro3_pass" and field != "molecular_species" else value
            rows.append(record)
        if n % 25 == 0:
            print(f"  chunk {n}/{(len(ids) + args.chunk - 1) // args.chunk}: {len(rows)} molecules", flush=True)

    admet = pd.DataFrame(rows).drop_duplicates(subset=["molecule_chembl_id"])
    admet["cns_penetration_flag"] = admet.apply(cns_flag, axis=1)
    admet.to_csv(data / "phase4-admet.csv.gz", index=False, compression="gzip")

    provenance = {
        "base_url": BASE,
        "data_kind": "ChEMBL calculated molecular properties, not measured pharmacokinetics",
        "cns_rule": {
            "max_tpsa": CNS_MAX_TPSA,
            "max_mw_freebase": CNS_MAX_MW,
            "logp_range": [CNS_MIN_LOGP, CNS_MAX_LOGP],
            "max_hbd": CNS_MAX_HBD,
            "logp_source": "cx_logp where present, otherwise alogp",
            "caveat": "a prediction from physicochemical properties, never a permeability measurement",
        },
        "molecules_requested": len(ids),
        "molecules_returned": int(len(admet)),
        "flag_counts": admet["cns_penetration_flag"].value_counts().to_dict(),
    }
    (data / "phase4-admet-provenance.json").write_text(json.dumps(provenance, indent=2))
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()
