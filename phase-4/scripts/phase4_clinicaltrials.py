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


def nf_specific_basis(query_label: str, title: str, conditions: str,
                      checked: dict | None = None, nct_id: str = "") -> str:
    """Which evidence qualified the trial as NF-specific. Three states.

    Added 2026-11-20 (Kara). `nf_specific` is one boolean over two unlike kinds of
    evidence, and only one of them was checkable from the committed columns.

      statement                     an NF disease is named in the title or conditions
      provenance_nf_in_eligibility  NF is named in the full registry record, usually
                                    in eligibility criteria, which this table does
                                    not carry. Verified per trial, not assumed
      provenance_no_nf_mention      came back from an NF-restricted query and the
                                    full record names NF nowhere

    All 21 provenance-only trials were checked against the registry on 2026-11-22
    through the ClinicalTrials.gov connector. 17 name NF in the full record; the
    provenance half of the rule is therefore mostly sound, which is the opposite of
    what the Phase 8 wrap first assumed from the committed columns alone. The four
    that do not are in phase-4/data/phase4-nf-provenance-check.csv: two are not NF
    trials at all (NCT03710564 age-related macular degeneration, NCT00588172 type 2
    diabetes), and two are MPNST trials that never state whether their patients
    have NF1 (NCT00427583, NCT02986919). Those two are kept and flagged rather than
    dropped, which is the standing rule for material that merely never states
    germline status.

    Consumers needing certainty filter on `statement`. Consumers wanting every
    genuine NF trial accept `statement` or `provenance_nf_in_eligibility`.
    """
    if NF_PATTERN.search(f"{title} {conditions}"):
        return "statement"
    if str(query_label).startswith("_disease_"):
        verdict = (checked or {}).get(str(nct_id))
        if verdict == "nf_in_eligibility":
            return "provenance_nf_in_eligibility"
        if verdict == "no_nf_mention":
            return "provenance_no_nf_mention"
        return "provenance_unchecked"
    return ""


def load_provenance_check(data: Path) -> dict:
    """Per-trial registry verdicts for provenance-only trials, retrieved 2026-11-22."""
    path = data / "phase4-nf-provenance-check.csv"
    if not path.exists():
        return {}
    chk = pd.read_csv(path)
    return dict(zip(chk["nct_id"].astype(str), chk["verdict"]))


def interaction_drug_keys(data: Path) -> set:
    """Drug names in the consolidated interaction table, which is what maps a drug
    to a target. `matches_phase4_drug` is computed against the ChEMBL drug universe
    alone, so a drug reached only through DGIdb or Open Targets is invisible to it."""
    ix = pd.read_csv(data / "phase4-drug-interactions.csv.gz", low_memory=False)
    keys = ix["drug_name"].fillna("").astype(str).str.upper().str.strip()
    return set(keys) - {""}


def annotate_nf_specific(data: Path) -> dict:
    """Recompute the derived flags on the committed tables without re-querying.

    Kept separate from the fetch so a flag can be added to the existing record
    without a data refresh, which would silently fold in every trial registered
    since the pinned run of 2026-11-04 and make the changes impossible to
    tell apart in review.

    Three columns are derived here. `nf_specific` is unchanged. `nf_specific_basis`
    (2026-11-20) says which half of the rule qualified the trial.
    `matches_phase4_interaction_drug` (2026-11-20) is the drug match against the
    interaction table, carried ALONGSIDE `matches_phase4_drug` rather than replacing
    it, so the two populations can never be conflated: the ChEMBL-universe match
    reports 40 distinct NF-specific interventions, the interaction-table match 68.
    The 28 it recovers include everolimus, sirolimus and temsirolimus, which is why
    mTOR reached the Phase 8 validation population only through a type 2 diabetes
    trial.
    """
    trials = pd.read_csv(data / "phase4-nf-trials.csv")
    trials["nf_specific"] = [
        is_nf_specific(q, t, c)
        for q, t, c in zip(trials["query_label"], trials["title"], trials["conditions"])
    ]
    checked = load_provenance_check(data)
    trials["nf_specific_basis"] = [
        nf_specific_basis(q, t, c, checked, n)
        for q, t, c, n in zip(trials["query_label"], trials["title"],
                              trials["conditions"], trials["nct_id"])
    ]
    nf_trials = set(trials.loc[trials["nf_specific"], "nct_id"])
    basis_by_trial = dict(zip(trials["nct_id"], trials["nf_specific_basis"]))

    drugs = pd.read_csv(data / "phase4-trial-drugs.csv")
    drugs["nf_specific"] = drugs["nct_id"].isin(nf_trials)
    drugs["nf_specific_basis"] = drugs["nct_id"].map(basis_by_trial).fillna("")
    ix_keys = interaction_drug_keys(data)
    drugs["matches_phase4_interaction_drug"] = drugs["intervention_key"].isin(ix_keys)

    trials.to_csv(data / "phase4-nf-trials.csv", index=False)
    drugs.to_csv(data / "phase4-trial-drugs.csv", index=False)
    nfd = drugs[drugs["nf_specific"]]
    return {
        "trial_rows": int(len(trials)),
        "trial_rows_nf_specific": int(trials["nf_specific"].sum()),
        "trial_rows_nf_by_statement": int((trials["nf_specific_basis"] == "statement").sum()),
        "trial_rows_nf_in_eligibility": int(
            (trials["nf_specific_basis"] == "provenance_nf_in_eligibility").sum()),
        "trial_rows_no_nf_mention": int(
            (trials["nf_specific_basis"] == "provenance_no_nf_mention").sum()),
        "trial_rows_provenance_unchecked": int(
            (trials["nf_specific_basis"] == "provenance_unchecked").sum()),
        "distinct_trials": int(trials["nct_id"].nunique()),
        "distinct_trials_nf_specific": int(len(nf_trials)),
        "drug_rows": int(len(drugs)),
        "drug_rows_nf_specific": int(drugs["nf_specific"].sum()),
        "nf_interventions_matching_chembl_universe": int(
            nfd.loc[nfd["matches_phase4_drug"], "intervention_key"].nunique()),
        "nf_interventions_matching_interaction_table": int(
            nfd.loc[nfd["matches_phase4_interaction_drug"], "intervention_key"].nunique()),
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
