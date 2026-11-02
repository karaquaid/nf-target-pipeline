"""Build the pinned Ensembl identifier map the pipeline maps everything onto.

Ratified call 3 fixes HGNC symbols through a pinned Ensembl release, with the original id
kept alongside. This script downloads one release's GTF and writes the transcript and gene
tables that phase2_ingest.py joins onto each dataset's ranked list, plus a RefSeq table
built from the same release's cross-references. The RefSeq table exists because the custom
REFSEQ CDFs two series ship (GPL7869 for GSE14038, GPL10371 for GSE41747) name their
probesets by RefSeq accession, and those platforms' GEO tables carry no symbol column.

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
REFSEQ_URL = ("https://ftp.ensembl.org/pub/release-{release}/tsv/homo_sapiens/"
              "Homo_sapiens.GRCh38.{release}.refseq.tsv.gz")
ATTR = re.compile(r'(\S+) "([^"]*)"')


def fetch(release: str, url_template: str = GTF_URL, suffix: str = "gtf.gz") -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    dest = CACHE / f"Homo_sapiens.GRCh38.{release}.{suffix}"
    if not dest.exists():
        url = url_template.format(release=release)
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
    # RefSeq mRNA accessions, taken from the same release so the symbol a probeset maps to is
    # the symbol the rest of the pipeline uses. Only the mRNA cross-references are kept; the
    # peptide ones name the same gene and would double the table for nothing.
    refseq = {}
    with gzip.open(fetch(args.release, REFSEQ_URL, "refseq.tsv.gz"), "rt") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        gene_col, xref_col, db_col = (header.index(c) for c in ("gene_stable_id", "xref", "db_name"))
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if parts[db_col] != "RefSeq_mRNA":
                continue
            symbol = genes.get(parts[gene_col], "")
            if symbol:
                refseq.setdefault(parts[xref_col], symbol)
    refseq_path = OUT_DIR / f"ensembl-{args.release}-refseq2symbol.tsv.gz"
    with gzip.open(refseq_path, "wt") as fh:
        fh.write("refseq_id\tgene_symbol\n")
        for accession, symbol in sorted(refseq.items()):
            fh.write(f"{accession}\t{symbol}\n")
    print(f"[write] {refseq_path.relative_to(ROOT)}: {len(refseq)} RefSeq mRNA accessions "
          f"with a gene symbol")
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
