#!/usr/bin/env python3
"""Phase 4: NF-relevant clinical trials and the drugs tested in them.

ChEMBL max_phase says how far a drug has got in any indication. It does not
say whether anyone has ever tried it in a neurofibromatosis population, and
that is the question that matters for prioritisation here. So this script
works from the condition side: it pulls every interventional trial recorded
for each selected manifestation, extracts the drug interventions, and marks
which Phase 4 candidate drugs appear.

A drug with ChEMBL max_phase 4 and no NF trial is a repurposing candidate.
A drug with an NF trial is already a clinical fact about this disease. The
dossier keeps the two apart.

Query syntax verified against the ClinicalTrials.gov API v2 on 2026-11-04;
counts were cross-checked against the Clinical Trials MCP connector and
matched (plexiform neurofibroma: 59 interventional studies by both routes).

Output:
  phase-4/data/phase4-nf-trials.csv
  phase-4/data/phase4-trial-drugs.csv
  phase-4/data/phase4-trials-provenance.json

Run from the repo root:
  python phase-4/scripts/phase4_clinicaltrials.py
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import pandas as pd
import requests

ENDPOINT = "https://clinicaltrials.gov/api/v2/studies"

# One query per selected manifestation, plus three disease-level umbrellas so
# a trial labelled only "neurofibromatosis type 1" is not missed.
QUERIES = {
    "Malignant peripheral nerve sheath tumor (MPNST)": "malignant peripheral nerve sheath tumor",
    "Plexiform neurofibroma": "plexiform neurofibroma",
    "Cutaneous neurofibroma": "cutaneous neurofibroma",
    "ANNUBP / atypical neurofibroma": "atypical neurofibroma OR atypical neurofibromatous neoplasm",
    "Optic pathway glioma": "optic pathway glioma OR optic nerve glioma",
    "Bone defects": "neurofibromatosis AND (pseudarthrosis OR tibial dysplasia)",
    "Vestibular schwannoma": "vestibular schwannoma OR acoustic neuroma",
    "Non-vestibular schwannoma": "schwannoma NOT vestibular",
    "Pain": "schwannomatosis AND pain",
    "_disease_NF1": "neurofibromatosis type 1",
    "_disease_NF2-SWN": "neurofibromatosis type 2 OR NF2-related schwannomatosis",
    "_disease_SWN": "schwannomatosis",
}

FIELDS = (
    "NCTId,BriefTitle,OverallStatus,Phase,Condition,InterventionName,"
    "InterventionType,LeadSponsorName,StartDate,EnrollmentCount"
)

# Intervention types that are not a drug being tested.
NON_DRUG_TYPES = {"DEVICE", "PROCEDURE", "RADIATION", "BEHAVIORAL", "DIAGNOSTIC_TEST", "OTHER"}


def fetch(condition: str) -> list:
    studies, token = [], None
    while True:
        params = {
            "query.cond": condition,
            "filter.advanced": "AREA[StudyType]INTERVENTIONAL",
            "pageSize": 200,
            "fields": FIELDS,
        }
        if token:
            params["pageToken"] = token
        response = requests.get(ENDPOINT, params=params, timeout=120)
        response.raise_for_status()
        body = response.json()
        studies.extend(body.get("studies", []))
        token = body.get("nextPageToken")
        if not token:
            return studies
        time.sleep(0.3)


def flatten(study: dict) -> dict:
    protocol = study.get("protocolSection", {})
    arms = protocol.get("armsInterventionsModule", {}) or {}
    interventions = arms.get("interventions", []) or []
    return {
        "nct_id": protocol.get("identificationModule", {}).get("nctId", ""),
        "title": protocol.get("identificationModule", {}).get("briefTitle", ""),
        "status": protocol.get("statusModule", {}).get("overallStatus", ""),
        "start_date": (protocol.get("statusModule", {}).get("startDateStruct") or {}).get(
            "date", ""
        ),
        "phases": "; ".join(protocol.get("designModule", {}).get("phases", []) or []),
        "enrollment": (protocol.get("designModule", {}).get("enrollmentInfo") or {}).get(
            "count", ""
        ),
        "conditions": "; ".join(protocol.get("conditionsModule", {}).get("conditions", []) or []),
        "sponsor": (protocol.get("sponsorCollaboratorsModule", {}).get("leadSponsor") or {}).get(
            "name", ""
        ),
        "interventions": [
            {"name": i.get("name", ""), "type": i.get("type", "")} for i in interventions
        ],
    }


# Most of these queries are MANIFESTATION terms, not NF terms, so the table they
# build is a manifestation-trial table and not an NF-trial table. 312 of its 716
# rows name neurofibromatosis nowhere - 91% of the optic pathway glioma rows and
# 88% of the MPNST rows - because a query like "optic pathway glioma OR optic
# nerve glioma" also returns general paediatric CNS and soft-tissue-sarcoma
# trials. That is correct for some uses and wrong for others: a non-NF paediatric
# CNS trial is perfectly good evidence that a drug reaches the CNS (Phase 5 uses
# it exactly that way), but it is NOT evidence that a drug has been tried in NF.
#
# So both facts are carried, and consumers pick the one they mean.
NF_PATTERN = re.compile(
    r"neurofibromatos|\bNF1\b|\bNF-1\b|\bNF2\b|\bNF-2\b|schwannomatos|von Recklinghausen",
    re.I,
)


def is_nf_specific(query_label: str, title: str, conditions: str) -> bool:
    """True when the trial is actually an NF trial.

    Two ways to qualify: it came from one of the NF-restricted `_disease_*`
    queries (NF by provenance), or its title or condition list names an NF
    disease (NF by statement). Provenance alone is not enough, because the
    manifestation queries are not NF-restricted.
    """
    if str(query_label).startswith("_disease_"):
        return True
    return bool(NF_PATTERN.search(f"{title} {conditions}"))


def annotate_nf_specific(data: Path) -> dict:
    """Recompute `nf_specific` on the committed tables without re-querying.

    Kept separate from the fetch so the flag can be added to the existing record
    without a data refresh, which would silently fold in every trial registered
    since the pinned run of 2026-11-04 and make the two changes impossible to
    tell apart in review.
    """
    trials = pd.read_csv(data / "phase4-nf-trials.csv")
    trials["nf_specific"] = [
        is_nf_specific(q, t, c)
        for q, t, c in zip(trials["query_label"], trials["title"], trials["conditions"])
    ]
    nf_trials = set(trials.loc[trials["nf_specific"], "nct_id"])

    drugs = pd.read_csv(data / "phase4-trial-drugs.csv")
    drugs["nf_specific"] = drugs["nct_id"].isin(nf_trials)

    trials.to_csv(data / "phase4-nf-trials.csv", index=False)
    drugs.to_csv(data / "phase4-trial-drugs.csv", index=False)
    return {
        "trial_rows": int(len(trials)),
        "trial_rows_nf_specific": int(trials["nf_specific"].sum()),
        "distinct_trials": int(trials["nct_id"].nunique()),
        "distinct_trials_nf_specific": int(len(nf_trials)),
        "drug_rows": int(len(drugs)),
        "drug_rows_nf_specific": int(drugs["nf_specific"].sum()),
    }


def normalise(name: str) -> str:
    """Trial intervention names carry dose and formulation text; reduce to a
    comparable token so 'Selumetinib 25 mg/m2' matches 'SELUMETINIB'."""
    text = re.sub(r"\(.*?\)", " ", str(name))
    text = re.sub(r"[^A-Za-z\- ]", " ", text)
    text = re.sub(r"\b(mg|kg|ml|mcg|iu|po|iv|qd|bid|tid|oral|tablet|capsule|injection|"
                  r"infusion|placebo|solution|gel|cream|dose|daily|weekly)\b", " ", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip().upper()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--annotate-only", action="store_true",
                        help="recompute nf_specific on the committed tables; no network, "
                             "no refetch, no change to which trials are in the record")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    data = root / "phase-4/data"

    if args.annotate_only:
        stats = annotate_nf_specific(data)
        for k, v in stats.items():
            print(f"  {k}: {v}")
        return

    rows, trial_drugs, errors = [], [], {}
    for label, condition in QUERIES.items():
        try:
            studies = fetch(condition)
        except Exception as exc:  # noqa: BLE001
            errors[label] = f"{type(exc).__name__}: {exc}"
            continue
        for study in studies:
            flat = flatten(study)
            rows.append(
                {
                    "query_label": label,
                    "manifestation": "" if label.startswith("_disease_") else label,
                    "disease_scope": label.replace("_disease_", "") if label.startswith("_disease_") else "",
                    **{k: v for k, v in flat.items() if k != "interventions"},
                    "nf_specific": is_nf_specific(label, flat["title"], flat["conditions"]),
                    "n_interventions": len(flat["interventions"]),
                }
            )
            for intervention in flat["interventions"]:
                if intervention["type"].upper() in NON_DRUG_TYPES:
                    continue
                trial_drugs.append(
                    {
                        "query_label": label,
                        "nct_id": flat["nct_id"],
                        "phases": flat["phases"],
                        "status": flat["status"],
                        "intervention_name": intervention["name"],
                        "intervention_type": intervention["type"],
                        "intervention_key": normalise(intervention["name"]),
                        "nf_specific": is_nf_specific(label, flat["title"], flat["conditions"]),
                    }
                )
        print(f"  {label[:45]:47s} {len(studies)} studies", flush=True)

    trials = pd.DataFrame(rows)
    drugs_in_trials = pd.DataFrame(trial_drugs).drop_duplicates()

    # Mark which Phase 4 candidate drugs appear in an NF trial.
    chembl = pd.read_csv(data / "phase4-chembl-drugs.csv.gz")
    chembl["drug_key"] = chembl["pref_name"].fillna("").astype(str).str.upper().str.strip()
    known = set(chembl.loc[chembl["drug_key"] != "", "drug_key"])
    drugs_in_trials["matches_phase4_drug"] = drugs_in_trials["intervention_key"].isin(known)

    trials.to_csv(data / "phase4-nf-trials.csv", index=False)
    drugs_in_trials.to_csv(data / "phase4-trial-drugs.csv", index=False)

    matched = drugs_in_trials[drugs_in_trials["matches_phase4_drug"]]
    provenance = {
        "endpoint": ENDPOINT,
        "syntax_verified": "ClinicalTrials.gov API v2 on 2026-11-04; counts cross-checked "
        "against the Clinical Trials MCP connector",
        "queries": QUERIES,
        "errors": errors,
        "trial_rows": int(len(trials)),
        "distinct_trials": int(trials["nct_id"].nunique()),
        "drug_intervention_rows": int(len(drugs_in_trials)),
        "distinct_interventions": int(drugs_in_trials["intervention_key"].nunique()),
        "interventions_matching_a_phase4_drug": int(matched["intervention_key"].nunique()),
    }
    (data / "phase4-trials-provenance.json").write_text(json.dumps(provenance, indent=2))
    print(json.dumps({k: v for k, v in provenance.items() if k != "queries"}, indent=2))


if __name__ == "__main__":
    main()
