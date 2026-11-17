#!/usr/bin/env python3
"""Phase 6: fetch drug synonyms from ChEMBL for the adjudication prompt.

Papers name these drugs by development code as often as by INN - STI-571 for
imatinib, MLN2480/TAK-580/DAY101 for tovorafenib, PLX4032 for vemurafenib. An
adjudicator that only knows the INN reads such a paper as being about a different
compound and under-calls the claim. That happened in the first adjudication run
(CNS-095: the model ruled an MLN2480 paper irrelevant to tovorafenib, which is the
same molecule), so the synonym list is supplied in the prompt.

Writes data/phase6-drug-synonyms.json keyed by the Phase 5 active moiety.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "phase-6-evidence-scoring" / "data"
CHEMBL = "https://www.ebi.ac.uk/chembl/api/data/molecule/search"


def main() -> None:
    rollup = pd.read_csv(DATA / "phase6-cns-adjudication-rollup.csv")
    session = requests.Session()
    out: dict[str, dict] = {}
    for moiety in rollup["moiety"]:
        syns, chembl_id = [], None
        try:
            r = session.get(CHEMBL, params={"q": moiety, "format": "json"}, timeout=60)
            r.raise_for_status()
            mols = r.json().get("molecules", [])
            mol = next(
                (m for m in mols if (m.get("pref_name") or "").upper() == moiety.upper()),
                None,
            )
            if mol:
                chembl_id = mol.get("molecule_chembl_id")
                syns = sorted(
                    {s["molecule_synonym"] for s in (mol.get("molecule_synonyms") or [])}
                )
        except Exception as exc:
            print(f"  ! {moiety}: {type(exc).__name__}")
        out[moiety] = {"chembl_id": chembl_id, "synonyms": syns}
        time.sleep(0.2)

    (DATA / "phase6-drug-synonyms.json").write_text(
        json.dumps(
            {"source": "ChEMBL molecule search (www.ebi.ac.uk/chembl/api/data)", "drugs": out},
            indent=1,
        )
        + "\n"
    )
    print(json.dumps({k: len(v["synonyms"]) for k, v in out.items()}, indent=0))


if __name__ == "__main__":
    main()
