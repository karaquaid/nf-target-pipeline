#!/usr/bin/env python3
"""Phase 5, Monarch pass: resolve candidate symbols to HGNC CURIEs and pull
gene-disease and gene-phenotype associations from the Monarch KG.

Both passes checkpoint to JSONL in --builddir and resume, because the full run
is roughly 6,000 requests. Nothing is inferred when a lookup fails: an
unresolved symbol is written as unresolved and stays distinguishable downstream
from a gene that resolved and simply has no associations.

Resolution is tried twice per symbol. Many Phase 1b/Phase 4 labels are
withdrawn or alias HGNC symbols that Monarch does not index under the old name
(GBA, SEPT9, MLLT4, KIAA0101, C10orf11 and 38 others), so when the literal
symbol misses, the pass retries with phase4-identifiers.csv's `resolved_symbol`
and records which spelling worked in `resolved_via`. Without that fallback 43
real genes were silently excluded from assessment.

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


def _lookup(m: Monarch, query: str) -> tuple[str | None, str | None, int]:
    """Exact human HGNC match for one spelling. Returns (curie, label, n_hits)."""
    hits = m.search(query, "biolink:Gene", limit=20, in_taxon=HUMAN)
    for h in hits:
        if h["id"].startswith("HGNC:") and h["name"].upper() == query.upper():
            return h["id"], h["name"], len(hits)
    return None, None, len(hits)


def resolve_symbols(m: Monarch, symbols: list[str], aliases: dict[str, str],
                    cachefile: Path, pause: float) -> dict:
    cache = _load_cache(cachefile)
    todo = [s for s in symbols if s not in cache]
    # symbols already cached as unresolved that have an untried alias spelling
    retry = [s for s in symbols
             if s in cache and not cache[s].get("curie")
             and not cache[s].get("alias_tried")
             and aliases.get(s) and aliases[s] != s]
    print(f"resolve: {len(cache)} cached, {len(todo)} new, {len(retry)} alias retries", flush=True)
    for i, sym in enumerate(todo + retry, 1):
        alias = aliases.get(sym)
        rec = {"symbol": sym, "curie": None, "matched_label": None, "n_gene_hits": 0,
               "resolved_via": None, "alias_used": None, "alias_tried": False}
        try:
            if sym not in cache:
                rec["curie"], rec["matched_label"], rec["n_gene_hits"] = _lookup(m, sym)
                if rec["curie"]:
                    rec["resolved_via"] = "symbol"
            if not rec["curie"] and alias and alias != sym:
                rec["alias_tried"] = True
                rec["alias_used"] = alias
                curie, labl, n = _lookup(m, alias)
                if curie:
                    rec.update(curie=curie, matched_label=labl, resolved_via="phase4_alias")
                rec["n_gene_hits"] = max(rec["n_gene_hits"], n)
        except Exception as exc:  # network/5xx after the client's own retries
            rec["error"] = f"{type(exc).__name__}: {exc}"[:200]
        _append(cachefile, rec)
        cache[sym] = rec
        if i % 200 == 0:
            print(f"  resolved {i}/{len(todo) + len(retry)}", flush=True)
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
    ident = pd.read_csv(build / "phase4-identifiers.csv")
    aliases = {r.gene_symbol: r.resolved_symbol for r in ident.itertuples()
               if isinstance(getattr(r, "resolved_symbol", None), str)}

    m = Monarch()
    version = m.version()
    print("Monarch", version, flush=True)

    res = resolve_symbols(m, symbols, aliases, build / "phase5-gene-curies.jsonl", args.pause)
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
               "n_resolved_via_phase4_alias": sum(1 for r in res.values()
                                                  if r.get("resolved_via") == "phase4_alias"),
               "n_association_rows": len(assoc_df),
               "n_genes_with_disease_edge": int(assoc_df.query("edge=='gene_to_disease'").gene_symbol.nunique()),
               "n_genes_with_phenotype_edge": int(assoc_df.query("edge=='gene_to_phenotype'").gene_symbol.nunique()),
               "errors": {s: r["error"] for s, r in {**res, **assoc}.items() if r.get("error")}},
              open(build / "phase5-monarch-summary.json", "w"), indent=2)
    print("association rows:", len(assoc_df), flush=True)


if __name__ == "__main__":
    main()
