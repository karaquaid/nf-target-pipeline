#!/usr/bin/env python3
"""Phase 4: drug-gene interaction claims from DGIdb.

DGIdb aggregates interaction claims from roughly 40 upstream sources, so
it covers interactions that ChEMBL alone does not. The GraphQL schema was
verified by introspection against https://dgidb.org/api/graphql on
2026-11-04 rather than written from memory: the `interactions` query takes
geneNames and paginates with first/after, and each node carries the
interaction score, types, sources and publications.

Every interaction claim is kept with its source named. DGIdb mixes curated
pharmacology (DrugBank, TTD, ChEMBL, GuideToPharmacology) with
high-throughput screens (PRISM, NCI60), and the screens dominate by count,
so filtering is left to the scoring phase rather than applied here.

Output:
  phase-4/data/phase4-dgidb-interactions.csv.gz
  phase-4/data/phase4-dgidb-provenance.json

Run from the repo root:
  python phase-4/scripts/phase4_dgidb.py
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
import requests

ENDPOINT = "https://dgidb.org/api/graphql"

QUERY = """
query($genes:[String!], $first:Int, $after:String){
  interactions(geneNames:$genes, first:$first, after:$after){
    pageInfo{ hasNextPage endCursor }
    nodes{
      gene{ name conceptId }
      drug{ name conceptId approved immunotherapy antiNeoplastic }
      interactionScore
      interactionTypes{ type directionality }
      sources{ sourceDbName }
      publications{ pmid }
    }
  }
}
"""


def post(payload: dict, retries: int = 4) -> dict:
    last = None
    for attempt in range(retries):
        try:
            response = requests.post(ENDPOINT, json=payload, timeout=180)
            if response.status_code == 200:
                body = response.json()
                if "errors" in body:
                    raise RuntimeError(body["errors"])
                return body["data"]
            last = f"HTTP {response.status_code}"
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"
        time.sleep(2 * (attempt + 1))
    raise SystemExit(f"DGIdb request failed after {retries} attempts: {last}")


def fetch_batch(genes: list, page_size: int) -> list:
    rows, cursor = [], None
    while True:
        data = post(
            {"query": QUERY, "variables": {"genes": genes, "first": page_size, "after": cursor}}
        )
        block = data["interactions"]
        for node in block["nodes"]:
            rows.append(
                {
                    "gene_symbol": node["gene"]["name"],
                    "gene_concept_id": node["gene"]["conceptId"],
                    "drug_name": node["drug"]["name"],
                    "drug_concept_id": node["drug"]["conceptId"],
                    "drug_approved": node["drug"]["approved"],
                    "drug_immunotherapy": node["drug"]["immunotherapy"],
                    "drug_antineoplastic": node["drug"]["antiNeoplastic"],
                    "interaction_score": node["interactionScore"],
                    "interaction_types": "; ".join(
                        sorted(
                            {
                                f"{t['type']}"
                                + (f" ({t['directionality']})" if t.get("directionality") else "")
                                for t in node["interactionTypes"]
                            }
                        )
                    ),
                    "sources": "; ".join(sorted({s["sourceDbName"] for s in node["sources"]})),
                    "pmids": "; ".join(
                        sorted({str(p["pmid"]) for p in node["publications"] if p.get("pmid")})
                    ),
                }
            )
        if not block["pageInfo"]["hasNextPage"]:
            return rows
        cursor = block["pageInfo"]["endCursor"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--batch", type=int, default=40, help="genes per request")
    parser.add_argument("--page-size", type=int, default=500)
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    data = root / "phase-4/data"

    identifiers = pd.read_csv(data / "phase4-identifiers.csv")
    queryable = identifiers[identifiers["query_term"].notna() & (identifiers["query_term"] != "")]
    terms = sorted(queryable["query_term"].unique())

    rows, failed = [], []
    for i in range(0, len(terms), args.batch):
        chunk = terms[i : i + args.batch]
        try:
            rows.extend(fetch_batch(chunk, args.page_size))
        except SystemExit as exc:
            failed.extend(chunk)
            print(f"batch {i // args.batch}: {exc}")
        if (i // args.batch) % 10 == 0:
            print(f"  {i + len(chunk)}/{len(terms)} genes, {len(rows)} interactions", flush=True)

    frame = pd.DataFrame(rows).drop_duplicates()
    frame.to_csv(data / "phase4-dgidb-interactions.csv.gz", index=False, compression="gzip")

    provenance = {
        "endpoint": ENDPOINT,
        "schema_verified": "introspection on 2026-11-04",
        "query": QUERY.strip(),
        "genes_queried": len(terms),
        "genes_failed": sorted(failed),
        "genes_with_interaction": int(frame["gene_symbol"].nunique()) if len(frame) else 0,
        "interaction_rows": int(len(frame)),
        "distinct_drugs": int(frame["drug_name"].nunique()) if len(frame) else 0,
    }
    (data / "phase4-dgidb-provenance.json").write_text(json.dumps(provenance, indent=2))
    print(json.dumps({k: v for k, v in provenance.items() if k != "query"}, indent=2))


if __name__ == "__main__":
    main()
