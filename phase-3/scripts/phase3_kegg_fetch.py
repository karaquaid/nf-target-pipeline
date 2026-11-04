#!/usr/bin/env python3
"""Phase 3, step 4a: build a symbol-to-pathway map from the KEGG REST API.

Earlier phases mapped pathways for target names picked out by hand. Phase 3 has
to go the other way, from a whole measured transcriptome to the pathways its
candidates fall in, so what is needed is a complete human gene-to-pathway table
rather than per-name lookups. This script fetches that table once and writes a
compact committed copy, so the enrichment step is reproducible without hitting
the API again and the KEGG release behind every result is on record.

Endpoint syntax was verified against the current KEGG REST API documentation at
https://www.kegg.jp/kegg/rest/keggapi.html before this code was written, not
recalled. The four operations used, in the documented URL forms:

  /info/pathway              pathway database size and last-update date
  /list/pathway/hsa          human pathway ids and names
  /list/hsa                  human gene entries; field 4 is "SYMBOL, ALIAS, ...; description"
  /link/pathway/hsa          pathway ids linked from each human gene

KEGG asks that the REST API not be hammered, so this makes four requests total
and caches the result. Note KEGG's licence: the data is free for academic use,
and redistribution is restricted, so only the derived symbol-to-pathway mapping
needed to reproduce the enrichment is committed, not the raw dumps.

Outputs
  phase-3/data/phase3-kegg-gene-pathway.tsv.gz  gene_symbol, kegg_gene, pathway_id, pathway_name
  phase-3/data/phase3-kegg-provenance.json      release string, URLs, row counts, fetch date
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

BASE = "https://rest.kegg.jp"
ENDPOINTS = {
    "info": f"{BASE}/info/pathway",
    "pathways": f"{BASE}/list/pathway/hsa",
    "genes": f"{BASE}/list/hsa",
    "gene_pathway": f"{BASE}/link/pathway/hsa",
}


def fetch(url: str, attempts: int = 4, timeout: int = 300) -> str:
    """One KEGG REST call. The /list/hsa dump is a few megabytes and the service
    throttles repeat callers, so a read timeout is retried rather than treated as
    a failure. A non-200 status is reported, never silently replaced."""
    last = None
    for attempt in range(1, attempts + 1):
        req = urllib.request.Request(url, headers={"Accept": "text/plain"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                if r.status != 200:
                    raise RuntimeError(f"{url} returned HTTP {r.status}")
                return r.read().decode("utf-8")
        except (TimeoutError, OSError) as exc:
            last = exc
            print(f"  attempt {attempt}/{attempts} on {url} failed: {exc}", file=sys.stderr)
            time.sleep(10 * attempt)
    raise RuntimeError(f"{url} failed after {attempts} attempts: {last}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".")
    args = ap.parse_args()
    repo = Path(args.repo)

    raw = {}
    for name, url in ENDPOINTS.items():
        raw[name] = fetch(url)
        print(f"fetched {url}  {len(raw[name]):,} bytes")
        time.sleep(1)

    # /info/pathway reports the entry count and the last-update date, which is the
    # only version stamp KEGG exposes for the pathway database over REST.
    info_lines = [ln.strip() for ln in raw["info"].splitlines() if ln.strip()]
    release = " | ".join(" ".join(ln.split()) for ln in info_lines[:3])

    pathway_name = {}
    for line in raw["pathways"].strip().split("\n"):
        pid, name = line.split("\t")
        pathway_name[pid if pid.startswith("path:") else f"path:{pid}"] = name

    # Field 4 of /list/hsa is "SYMBOL, ALIAS1, ALIAS2; description" for named genes
    # and a bare description for the unnamed ones. The first comma-separated token
    # before the semicolon is KEGG's primary symbol.
    symbol = {}
    for line in raw["genes"].strip().split("\n"):
        parts = line.split("\t")
        if len(parts) < 4 or ";" not in parts[3]:
            continue
        names = parts[3].split(";")[0]
        symbol[parts[0]] = names.split(",")[0].strip()

    rows = []
    for line in raw["gene_pathway"].strip().split("\n"):
        gene, pid = line.split("\t")
        sym = symbol.get(gene)
        if sym is None:
            continue
        rows.append((sym, gene, pid, pathway_name.get(pid, "")))

    df = pd.DataFrame(rows, columns=["gene_symbol", "kegg_gene", "pathway_id", "pathway_name"])
    df = df.drop_duplicates().sort_values(["pathway_id", "gene_symbol"])
    if df.empty or df.pathway_name.eq("").any():
        print("FAIL pathway names did not resolve for every linked pathway", file=sys.stderr)
        return 1

    out = repo / "phase-3/data/phase3-kegg-gene-pathway.tsv.gz"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, sep="\t", index=False)

    prov = {
        "fetched": dt.date.today().isoformat(),
        "kegg_pathway_db_info": release,
        "endpoints": ENDPOINTS,
        "documentation_verified_against": "https://www.kegg.jp/kegg/rest/keggapi.html",
        "human_pathways": len(pathway_name),
        "human_gene_entries": len(raw["genes"].strip().split("\n")),
        "gene_entries_with_symbol": len(symbol),
        "gene_pathway_links": len(raw["gene_pathway"].strip().split("\n")),
        "rows_written": int(len(df)),
        "distinct_symbols": int(df.gene_symbol.nunique()),
        "distinct_pathways": int(df.pathway_id.nunique()),
    }
    (repo / "phase-3/data/phase3-kegg-provenance.json").write_text(json.dumps(prov, indent=2) + "\n")

    print(f"\nwrote {out}")
    print(f"  {len(df):,} links, {df.gene_symbol.nunique():,} symbols, {df.pathway_id.nunique()} pathways")
    print(f"  KEGG pathway database: {release}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
