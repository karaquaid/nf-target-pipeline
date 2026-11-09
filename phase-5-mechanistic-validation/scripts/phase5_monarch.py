#!/usr/bin/env python3
"""Phase 5, Monarch pass: resolve candidate symbols to HGNC CURIEs and pull
gene-disease and gene-phenotype associations from the Monarch KG.

Both passes checkpoint to JSONL in --cachedir and resume, because the full run
is roughly 6,000 requests. Nothing is inferred when a lookup fails: an
unresolved symbol is written as unresolved and stays distinguishable downstream
from a gene that resolved and simply has no associations.

Usage:
  python phase5_monarch.py --builddir build/phase5 --datadir <phase>/data
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from monarch_client import HUMAN, Monarch, NF_DISEASES  # noqa: E402

CAUSAL = "biolink:CausalGeneToDiseaseAssociation"
PHENO = "biolink:GeneToPhenotypicFeatureAssociation"


def _load_cache(path: Path) -> dict:
    out = {}
    if path.exists():
        for line in path.open():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            out[rec["symbol"]] = rec
    return out


def _append(path: Path, rec: dict) -> None:
    with path.open("a") as fh:
        fh.write(json.dumps(rec) + "\n")


def resolve_symbols(m: Monarch, symbols: list[str], cachefile: Path, pause: float) -> dict:
    cache = _load_cache(cachefile)
    todo = [s for s in symbols if s not in cache]
    print(f"resolve: {len(cache)} cached, {len(todo)} to do", flush=True)
    for i, sym in enumerate(todo, 1):
        rec = {"symbol": sym, "curie": None, "matched_label": None, "n_gene_hits": 0}
        try:
            hits = m.search(sym, "biolink:Gene", limit=20, in_taxon=HUMAN)
            rec["n_gene_hits"] = len(hits)
            for h in hits:
                if h["id"].startswith("HGNC:") and h["name"].upper() == sym.upper():
                    rec["curie"], rec["matched_label"] = h["id"], h["name"]
                    break
        except Exception as exc:  # network/5xx after the client's own retries
            rec["error"] = f"{type(exc).__name__}: {exc}"[:200]
        _append(cachefile, rec)
        cache[sym] = rec
        if i % 200 == 0:
            print(f"  resolved {i}/{len(todo)}", flush=True)
        time.sleep(pause)
    return cache


def fetch_associations(m: Monarch, curies: dict, cachefile: Path, pause: float) -> dict:
    cache = _load_cache(cachefile)
    todo = [s for s in curies if s not in cache]
    print(f"associations: {len(cache)} cached, {len(todo)} to do", flush=True)
    for i, sym in enumerate(todo, 1):
        curie = curies[sym]
        rec = {"symbol": sym, "curie": curie, "diseases": [], "phenotypes": []}
        try:
            rec["diseases"] = m.gene_diseases(curie)
            rec["phenotypes"] = m.gene_phenotypes(curie)
        except Exception as exc:
            rec["error"] = f"{type(exc).__name__}: {exc}"[:200]
        _append(cachefile, rec)
        cache[sym] = rec
        if i % 100 == 0:
            print(f"  fetched {i}/{len(todo)}", flush=True)
        time.sleep(pause)
    return cache


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--builddir", default="build/phase5")
    ap.add_argument("--datadir", default="phase-5-mechanistic-validation/data")
    ap.add_argument("--pause", type=float, default=0.05)
    args = ap.parse_args()
    build, data = Path(args.builddir), Path(args.datadir)
    data.mkdir(parents=True, exist_ok=True)

    dossier = pd.read_csv(build / "phase4-target-dossier.csv")
    symbols = sorted(dossier["gene_symbol"].dropna().unique())

    m = Monarch()
    version = m.version()
    print("Monarch", version, flush=True)

    res = resolve_symbols(m, symbols, build / "phase5-gene-curies.jsonl", args.pause)
    curies = {s: r["curie"] for s, r in res.items() if r.get("curie")}
    unresolved = sorted(s for s, r in res.items() if not r.get("curie"))
    print(f"resolved {len(curies)}/{len(symbols)}; unresolved {len(unresolved)}", flush=True)

    assoc = fetch_associations(m, curies, build / "phase5-gene-associations.jsonl", args.pause)

    # Long-form association table: one row per gene-object edge.
    rows = []
    for sym, rec in assoc.items():
        for d in rec.get("diseases", []):
            rows.append({"gene_symbol": sym, "gene_curie": rec["curie"], "edge": "gene_to_disease",
                         "object_curie": d["disease"], "object_label": d["label"],
                         "predicate": d["predicate"], "primary_knowledge_source": d["source"]})
        for p in rec.get("phenotypes", []):
            rows.append({"gene_symbol": sym, "gene_curie": rec["curie"], "edge": "gene_to_phenotype",
                         "object_curie": p["hpo"], "object_label": p["label"],
                         "predicate": "biolink:has_phenotype", "primary_knowledge_source": p["source"]})
    assoc_df = pd.DataFrame(rows).sort_values(["gene_symbol", "edge", "object_curie"])
    assoc_df.to_csv(data / "phase5-monarch-associations.csv.gz", index=False)

    # Disease phenotype profiles, for the stratum-level ground-truth flag.
    profiles = {}
    for label, curie in NF_DISEASES.items():
        profiles[label] = {"mondo": curie,
                           "hpo": sorted({p["hpo"] for p in m.disease_phenotypes(curie)})}
    json.dump(profiles, open(build / "phase5-disease-profiles.json", "w"), indent=2)

    json.dump({"monarch_kg_version": version["monarch_kg_version"],
               "monarch_api_version": version["monarch_api_version"],
               "n_symbols": len(symbols), "n_resolved": len(curies),
               "unresolved_symbols": unresolved,
               "n_association_rows": len(assoc_df),
               "n_genes_with_disease_edge": int(assoc_df.query("edge=='gene_to_disease'").gene_symbol.nunique()),
               "n_genes_with_phenotype_edge": int(assoc_df.query("edge=='gene_to_phenotype'").gene_symbol.nunique()),
               "errors": {s: r["error"] for s, r in {**res, **assoc}.items() if r.get("error")}},
              open(build / "phase5-monarch-summary.json", "w"), indent=2)
    print("association rows:", len(assoc_df), flush=True)


if __name__ == "__main__":
    main()
