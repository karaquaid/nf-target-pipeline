"""Build the pinned Ensembl identifier map the pipeline maps everything onto.

Ratified call 3 fixes HGNC symbols through a pinned Ensembl release, with the original id
kept alongside. This script downloads one release's GTF and writes the transcript and gene
tables that phase2_ingest.py joins onto each dataset's ranked list.

The release is part of the filename and is recorded in the ingestion manifest, so a remap
is a visible change rather than a silent drift.

Usage, from the repo root:
    python phase-2/scripts/phase2_build_idmap.py --release 113
"""

from __future__ import annotations

import argparse
import gzip
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "phase-2" / "data"
CACHE = ROOT / "build" / "phase2" / "_ensembl"
GTF_URL = ("https://ftp.ensembl.org/pub/release-{release}/gtf/homo_sapiens/"
           "Homo_sapiens.GRCh38.{release}.gtf.gz")
ATTR = re.compile(r'(\S+) "([^"]*)"')


def fetch(release: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    dest = CACHE / f"Homo_sapiens.GRCh38.{release}.gtf.gz"
    if not dest.exists():
        url = GTF_URL.format(release=release)
        print(f"[fetch] {url}")
        urllib.request.urlretrieve(url, dest)
    print(f"[fetch] {dest.relative_to(ROOT)} {dest.stat().st_size / 1e6:.1f} MB")
    return dest


def parse(gtf: Path) -> tuple[list[tuple[str, str, str]], dict[str, str]]:
    """Transcript rows (transcript, gene, symbol) and the gene-to-symbol map."""
    transcripts: list[tuple[str, str, str]] = []
    genes: dict[str, str] = {}
    with gzip.open(gtf, "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            fields = line.split("\t")
            if len(fields) < 9 or fields[2] not in ("gene", "transcript"):
                continue
            attrs = dict(ATTR.findall(fields[8]))
            gene_id = attrs.get("gene_id", "")
            symbol = attrs.get("gene_name", "")
            if fields[2] == "gene":
                genes[gene_id] = symbol
            else:
                transcripts.append((attrs.get("transcript_id", ""), gene_id, symbol))
    return transcripts, genes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", default="113", help="Ensembl release to pin")
    args = ap.parse_args()

    transcripts, genes = parse(fetch(args.release))
    tx_path = OUT_DIR / f"ensembl-{args.release}-tx2gene.tsv.gz"
    with gzip.open(tx_path, "wt") as fh:
        fh.write("transcript_id\tgene_id\tgene_symbol\n")
        for tx, gene, symbol in transcripts:
            fh.write(f"{tx}\t{gene}\t{symbol}\n")
    gene_path = OUT_DIR / f"ensembl-{args.release}-gene2symbol.tsv.gz"
    with gzip.open(gene_path, "wt") as fh:
        fh.write("gene_id\tgene_symbol\n")
        for gene, symbol in sorted(genes.items()):
            fh.write(f"{gene}\t{symbol}\n")

    named = sum(1 for _, _, s in transcripts if s)
    print(f"[write] {tx_path.relative_to(ROOT)}: {len(transcripts)} transcripts, "
          f"{named} with a gene symbol ({named / max(len(transcripts), 1):.1%})")
    print(f"[write] {gene_path.relative_to(ROOT)}: {len(genes)} genes, "
          f"{sum(1 for s in genes.values() if s)} with a symbol")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
