#!/usr/bin/env python3
"""Phase 4 step 2: resolve every target symbol to stable identifiers.

ChEMBL, Open Targets and the Guide to Pharmacology are keyed on UniProt
accessions and Ensembl gene ids, not on symbol strings, so a symbol that
resolves to nothing is a target the drug layer cannot query. Those are
recorded as explicit misses here rather than dropped, so the dossier can
say "not queryable" instead of "no drug found".

The mygene.info response is cached in phase-4/data/phase4-mygene-cache.json
and committed, so this script is deterministic and runs offline. The cache
was fetched through the genes-ontologies MCP connector; refresh it with
phase-4/scripts/phase4_fetch_identifiers.md.

Symbols that are not gene symbols at all, or that arrive corrupted from a
platform annotation, are handled through phase-4/data/phase4-symbol-corrections.csv
so the change is visible and reversible rather than buried in code.

Inputs:
  phase-4/data/phase4-targets.csv
  phase-4/data/phase4-symbol-corrections.csv
  phase-4/data/phase4-mygene-cache.json

Output:
  phase-4/data/phase4-identifiers.csv

Run from the repo root:
  python phase-4/scripts/phase4_identifiers.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def ensembl_gene(record: dict) -> str:
    value = record.get("ensembl")
    if isinstance(value, dict):
        return value.get("gene", "")
    if isinstance(value, list):
        return ";".join(sorted({v.get("gene", "") for v in value if v.get("gene")}))
    return ""


def swissprot(record: dict) -> str:
    value = (record.get("uniprot") or {}).get("Swiss-Prot", "")
    return ";".join(value) if isinstance(value, list) else (value or "")


def pick(candidates: list, term: str) -> tuple:
    """Prefer an official-symbol match over an alias match, then a record
    that actually carries the identifiers the drug APIs need."""
    exact = [c for c in candidates if str(c.get("symbol", "")).upper() == term.upper()]
    pool = exact or candidates
    pool = sorted(
        pool, key=lambda c: (not bool(ensembl_gene(c)), not bool(swissprot(c)), str(c.get("_id")))
    )
    return pool[0], ("exact_symbol" if exact else "alias_only")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    data = root / "phase-4/data"

    targets = pd.read_csv(data / "phase4-targets.csv")
    corrections = pd.read_csv(data / "phase4-symbol-corrections.csv").fillna("")
    cache = json.loads((data / "phase4-mygene-cache.json").read_text())

    corr = {row.gene_symbol: row for row in corrections.itertuples()}
    by_term: dict = {}
    for record in cache["records"]:
        by_term.setdefault(record["query"], []).append(record)
    not_found = set(cache["not_found"])

    rows = []
    for symbol in sorted(targets["gene_symbol"].unique()):
        correction = corr.get(symbol)
        queryable = True
        note = ""
        term = symbol
        if correction is not None:
            queryable = str(correction.queryable) == "True"
            note = correction.basis
            term = correction.corrected_symbol or symbol

        base = {
            "gene_symbol": symbol,
            "query_term": term if queryable else "",
            "corrected": bool(correction is not None and queryable and term != symbol),
            "note": note,
        }
        if not queryable:
            rows.append(
                {
                    **base,
                    "match_type": "not_a_gene_symbol",
                    "resolved_symbol": "",
                    "entrez_id": "",
                    "ensembl_gene_id": "",
                    "uniprot_accession": "",
                    "gene_name": "",
                    "n_candidate_records": 0,
                }
            )
            continue

        candidates = by_term.get(term, [])
        if not candidates:
            rows.append(
                {
                    **base,
                    "match_type": "unresolved" if term in not_found else "absent_from_cache",
                    "resolved_symbol": "",
                    "entrez_id": "",
                    "ensembl_gene_id": "",
                    "uniprot_accession": "",
                    "gene_name": "",
                    "n_candidate_records": 0,
                }
            )
            continue

        best, match_type = pick(candidates, term)
        rows.append(
            {
                **base,
                "match_type": match_type,
                "resolved_symbol": best.get("symbol", ""),
                "entrez_id": best.get("entrezgene", ""),
                "ensembl_gene_id": ensembl_gene(best),
                "uniprot_accession": swissprot(best),
                "gene_name": best.get("name", ""),
                "n_candidate_records": len(candidates),
            }
        )

    out = pd.DataFrame(rows)[
        [
            "gene_symbol",
            "query_term",
            "corrected",
            "match_type",
            "resolved_symbol",
            "gene_name",
            "entrez_id",
            "ensembl_gene_id",
            "uniprot_accession",
            "n_candidate_records",
            "note",
        ]
    ].sort_values("gene_symbol")
    out.to_csv(data / "phase4-identifiers.csv", index=False)

    if len(out) != targets["gene_symbol"].nunique():
        raise SystemExit("identifier table does not have one row per target symbol")

    print(f"symbols: {len(out)}")
    print(out["match_type"].value_counts().to_string())
    print(f"with Ensembl gene id: {int(out['ensembl_gene_id'].notna().sum() - (out['ensembl_gene_id'] == '').sum())}")
    print(f"with UniProt accession: {int((out['uniprot_accession'].fillna('') != '').sum())}")


if __name__ == "__main__":
    main()
