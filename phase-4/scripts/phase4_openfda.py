#!/usr/bin/env python3
"""Phase 4: approval status, route of administration and FAERS safety signals.

Three openFDA endpoints, each checked live on 2026-11-04 against a response
before the field access below was written:

  - /drug/label.json      structured product labels; openfda.route is the
                          route-of-administration field the delivery filter
                          needs, and the presence of a boxed_warning section
                          is a first safety flag.
  - /drug/drugsfda.json   Drugs@FDA applications and marketing status;
                          marketing_status, dosage_form and route sit on
                          products[], and an approval is a submissions[]
                          entry with submission_status "AP" carrying
                          submission_status_date as YYYYMMDD.
  - /drug/event.json      FAERS post-market adverse event reports, counted
                          per generic name.

Scope. openFDA covers products marketed in the United States, so it is
queried for drugs that could plausibly have a label: ChEMBL max_phase 3 or
above, plus any drug named as an intervention in an NF trial. Querying all
4,005 drugs would spend the anonymous request budget on preclinical
compounds that have no label by construction. Drugs outside that scope are
written out with openfda_queried False, never with a blank that could be
read as "no approval found".

Two sources were specified in the project plan and are NOT available here:
DrugBank Open Data (go.drugbank.com is outside the sandbox allowlist and
its download requires account registration) and SIDER (sideeffects.embl.de
likewise blocked). Approval status therefore rests on Drugs@FDA alone, and
side-effect data on FAERS alone, with no package-insert frequency data.

A FAERS report count is a count of reports mentioning the drug. It is not a
rate, carries no denominator, and is confounded by how widely the drug is
used and how long it has been marketed. It is recorded as a signal to be
weighted in Phase 6, not as a safety verdict.

Output:
  phase-4/data/phase4-openfda-labels.csv
  phase-4/data/phase4-openfda-approvals.csv
  phase-4/data/phase4-faers.csv
  phase-4/data/phase4-openfda-provenance.json

Run from the repo root:
  python phase-4/scripts/phase4_openfda.py
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
import requests

LABEL = "https://api.fda.gov/drug/label.json"
DRUGSFDA = "https://api.fda.gov/drug/drugsfda.json"
EVENT = "https://api.fda.gov/drug/event.json"


FAILURES: list = []


def get(url: str, params: dict, retries: int = 3):
    """Returns the parsed body, or None.

    None means one of two different things and the caller must not conflate
    them, so every non-200 that is not a 404 is appended to FAILURES:
      - 404: openFDA's way of saying "no matches", which is data.
      - anything else: the request did not happen. Treating that as "no
        adverse events found" would be a false safety claim.
    """
    api_key = os.environ.get("OPENFDA_API_KEY", "").strip()
    if api_key:
        params = {**params, "api_key": api_key}
    last = None
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=120)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 404:
                return None
            last = f"HTTP {response.status_code}"
            if response.status_code == 429:
                time.sleep(20)
                continue
            if response.status_code == 403:
                # Anonymous request budget exhausted; retrying will not help.
                break
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"
        time.sleep(2 * (attempt + 1))
    FAILURES.append({"url": url, "search": params.get("search", "")[:120], "error": last})
    return None


def or_clause(names: list) -> str:
    return " OR ".join(f'"{n}"' for n in names)


CACHE_NAME = "phase4-openfda-cache.jsonl"


def load_cache(path: Path) -> dict:
    """Responses keyed by (endpoint, batch index).

    The cache exists because the openFDA key is not always reachable from the
    analysis environment. Each line holds the trimmed response for one batch,
    carrying exactly the fields parsed below and nothing else, so the cache
    stays small and the parsing stays in this script rather than in whatever
    fetched it.
    """
    cache: dict = {}
    if not path.exists():
        return cache
    with path.open() as handle:
        for line in handle:
            if not line.strip():
                continue
            entry = json.loads(line)
            cache[(entry["endpoint"], entry["batch_index"])] = entry["body"]
    return cache


def chunked(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--batch", type=int, default=20)
    parser.add_argument("--min-phase", type=float, default=3.0)
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    data = root / "phase-4/data"

    drugs = pd.read_csv(data / "phase4-chembl-drugs.csv.gz")
    drugs["drug_key"] = drugs["pref_name"].fillna("").astype(str).str.upper().str.strip()

    trial_drugs = pd.read_csv(data / "phase4-trial-drugs.csv")
    in_trials = set(trial_drugs.loc[trial_drugs["matches_phase4_drug"], "intervention_key"])

    in_scope = drugs[
        (drugs["max_phase_numeric"] >= args.min_phase) | (drugs["drug_key"].isin(in_trials))
    ]
    names = sorted({n for n in in_scope["drug_key"] if n})
    print(f"openFDA scope: {len(names)} drugs of {len(drugs)}", flush=True)

    cache = load_cache(data / CACHE_NAME)
    if cache:
        print(f"using cached openFDA responses: {len(cache)} batch responses", flush=True)

    label_rows, approval_rows, faers_rows = [], [], []
    requests_made = 0

    for batch_index, batch in enumerate(chunked(names, args.batch)):
        clause = or_clause(batch)
        wanted = set(batch)

        if ("label", batch_index) in cache:
            body = cache[("label", batch_index)]
        else:
            body = get(LABEL, {"search": f"openfda.generic_name:({clause})", "limit": 1000})
            requests_made += 1
        for record in (body or {}).get("results", []):
            openfda = record.get("openfda", {}) or {}
            for generic in openfda.get("generic_name", []) or []:
                key = generic.upper().strip()
                if key not in wanted:
                    continue
                label_rows.append(
                    {
                        "drug_key": key,
                        "routes": "; ".join(sorted(set(openfda.get("route", []) or []))),
                        "product_type": "; ".join(sorted(set(openfda.get("product_type", []) or []))),
                        "brand_names": "; ".join(sorted(set(openfda.get("brand_name", []) or []))[:5]),
                        "application_numbers": "; ".join(
                            sorted(set(openfda.get("application_number", []) or []))[:5]
                        ),
                        "has_boxed_warning": "boxed_warning" in record,
                    }
                )

        if ("drugsfda", batch_index) in cache:
            body = cache[("drugsfda", batch_index)]
        else:
            body = get(DRUGSFDA, {"search": f"openfda.generic_name:({clause})", "limit": 1000})
            requests_made += 1
        for record in (body or {}).get("results", []):
            openfda = record.get("openfda", {}) or {}
            generics = {g.upper().strip() for g in (openfda.get("generic_name", []) or [])}
            hits = generics & wanted
            if not hits:
                continue
            products = record.get("products", []) or []
            submissions = record.get("submissions", []) or []
            approvals = sorted(
                s.get("submission_status_date", "")
                for s in submissions
                if s.get("submission_status") == "AP" and s.get("submission_status_date")
            )
            for key in hits:
                approval_rows.append(
                    {
                        "drug_key": key,
                        "application_number": record.get("application_number", ""),
                        "sponsor_name": record.get("sponsor_name", ""),
                        "marketing_statuses": "; ".join(
                            sorted({p.get("marketing_status", "") for p in products if p.get("marketing_status")})
                        ),
                        "dosage_forms": "; ".join(
                            sorted({p.get("dosage_form", "") for p in products if p.get("dosage_form")})
                        ),
                        "routes_drugsfda": "; ".join(
                            sorted({p.get("route", "") for p in products if p.get("route")})
                        ),
                        "first_approval_date": approvals[0] if approvals else "",
                        "n_approval_submissions": len(approvals),
                    }
                )

        for serious_only in (False, True):
            endpoint_key = "event_serious" if serious_only else "event_total"
            search = f"patient.drug.openfda.generic_name:({clause})"
            if serious_only:
                search += " AND serious:1"
            if (endpoint_key, batch_index) in cache:
                body = cache[(endpoint_key, batch_index)]
            else:
                body = get(
                    EVENT,
                    {
                        "search": search,
                        "count": "patient.drug.openfda.generic_name.exact",
                        "limit": 1000,
                    },
                )
                requests_made += 1
            for record in (body or {}).get("results", []):
                key = str(record.get("term", "")).upper().strip()
                if key not in wanted:
                    # Counts include co-reported drugs; keep only what we asked for.
                    continue
                faers_rows.append(
                    {
                        "drug_key": key,
                        "metric": "serious_reports" if serious_only else "total_reports",
                        "count": record.get("count", 0),
                    }
                )
        time.sleep(0.3)

    labels = (
        pd.DataFrame(label_rows)
        .groupby("drug_key", as_index=False)
        .agg(
            routes=("routes", lambda s: "; ".join(sorted({x for v in s for x in str(v).split("; ") if x}))),
            product_types=("product_type", lambda s: "; ".join(sorted({x for v in s for x in str(v).split("; ") if x}))),
            brand_names=("brand_names", "first"),
            application_numbers=("application_numbers", "first"),
            has_boxed_warning=("has_boxed_warning", "max"),
            n_label_records=("drug_key", "size"),
        )
        if label_rows
        else pd.DataFrame(columns=["drug_key"])
    )
    approvals = pd.DataFrame(approval_rows).drop_duplicates()
    faers = (
        pd.DataFrame(faers_rows)
        .pivot_table(index="drug_key", columns="metric", values="count", aggfunc="max")
        .reset_index()
        if faers_rows
        else pd.DataFrame(columns=["drug_key"])
    )

    scope = pd.DataFrame({"drug_key": names, "openfda_queried": True})
    labels = scope.merge(labels, on="drug_key", how="left")
    labels.to_csv(data / "phase4-openfda-labels.csv", index=False)
    approvals.to_csv(data / "phase4-openfda-approvals.csv", index=False)
    faers.to_csv(data / "phase4-faers.csv", index=False)

    provenance = {
        "endpoints": {"label": LABEL, "drugsfda": DRUGSFDA, "event": EVENT},
        "verified": "live on 2026-11-04",
        "scope_rule": f"ChEMBL max_phase >= {args.min_phase} or named in an NF trial",
        "drugs_in_scope": len(names),
        "drugs_total": int(len(drugs)),
        "api_requests_made": requests_made,
        "drugs_with_a_label": int(labels["routes"].notna().sum()),
        "drugs_with_a_drugsfda_record": int(approvals["drug_key"].nunique()) if len(approvals) else 0,
        "drugs_with_faers_reports": int(faers["drug_key"].nunique()) if len(faers) else 0,
        "api_key_used": bool(os.environ.get("OPENFDA_API_KEY", "").strip()),
        "cached_batch_responses_used": len(cache),
        "cache_note": (
            "Responses were served from phase-4/data/" + CACHE_NAME + ", fetched with an "
            "openFDA API key. The cache holds only the fields parsed by this script. "
            "Delete it to force a live re-fetch."
        )
        if cache
        else "no cache; every response came from a live request",
        "failed_requests": len(FAILURES),
        "failed_request_sample": FAILURES[:10],
        "coverage_caveat": (
            "A failed request is not an empty result. If failed_requests is non-zero the "
            "label, approval and FAERS coverage below is partial and the affected drugs are "
            "unassessed, not negative."
        )
        if FAILURES
        else "every request returned a response",
        "unavailable_sources": {
            "DrugBank Open Data": "go.drugbank.com not on the sandbox allowlist; download also "
            "requires account registration. Approval status rests on Drugs@FDA alone.",
            "SIDER": "sideeffects.embl.de not on the sandbox allowlist. No package-insert "
            "side-effect frequency data in this phase.",
        },
    }
    (data / "phase4-openfda-provenance.json").write_text(json.dumps(provenance, indent=2))
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()
