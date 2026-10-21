"""Check that the Phase 2 launch set's raw files actually resolve, before ingestion.

For each launch-set dataset this lists the archive's supplementary directory and asks the
server for the size of every file, so a dataset whose raw data is missing, renamed or
sample-level-only is found now rather than mid-pipeline. Nothing is downloaded.

GEO series files:      https://ftp.ncbi.nlm.nih.gov/geo/series/GSE<prefix>nnn/<acc>/suppl/
GEO per-sample files:  .../samples/GSM<prefix>nnn/<gsm>/suppl/      (checked when a series
                       carries no series-level files, as single-cell submissions often do)
ArrayExpress:          https://www.ebi.ac.uk/biostudies/api/v1/studies/<acc>

Writes phase-2/data/phase2-raw-file-check.csv. Run from the repo root:
    python phase-2/scripts/phase2_raw_file_check.py [--limit-samples 6]
"""

from __future__ import annotations

import argparse
import re
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
READINESS = ROOT / "phase-2" / "data" / "phase2-launchset-readiness.csv"
OVERRIDES = ROOT / "phase-2" / "data" / "phase2-sample-overrides.csv"
SAMPLES = ROOT / "phase-1a" / "data" / "phase1a-samples.csv"
OUT = ROOT / "phase-2" / "data" / "phase2-raw-file-check.csv"

GEO_FTP = "https://ftp.ncbi.nlm.nih.gov/geo"
BIOSTUDIES = "https://www.ebi.ac.uk/biostudies/api/v1/studies"
HREF = re.compile(r'<a href="([^"/][^"]*)">')  # relative names only
SKIP = ("://",)  # the index page footers link out to hhs.gov; those are not files
SESSION = requests.Session()
PAUSE = 0.34  # NCBI: 3 requests/second without an API key


def get(url: str, method: str = "GET", tries: int = 3):
    for attempt in range(tries):
        time.sleep(PAUSE)
        try:
            r = SESSION.request(method, url, timeout=120, allow_redirects=True)
            if r.status_code < 500:
                return r
        except requests.RequestException:
            if attempt == tries - 1:
                raise
        time.sleep(2 ** attempt)
    return r


def stem(accession: str) -> str:
    """GEO's bucket directory: GSE163071 -> GSE163nnn, GSM4971650 -> GSM4971nnn."""
    prefix = re.match(r"([A-Z]+)(\d+)", accession)
    kind, digits = prefix.group(1), prefix.group(2)
    return f"{kind}{digits[:-3]}nnn" if len(digits) > 3 else f"{kind}nnn"


def listing(url: str) -> tuple[int, list[str]]:
    r = get(url)
    if r.status_code != 200:
        return r.status_code, []
    return 200, [h for h in HREF.findall(r.text)
                 if not h.endswith("/") and not any(s in h for s in SKIP)]


def classify(names: list[str], availability: str) -> str:
    """Does what the archive actually holds match what Phase 1a recorded?"""
    low = " ".join(names).lower()
    has_raw_tar = any(n.lower().endswith("_raw.tar") for n in names)
    # ArrayExpress ships two-colour and Affymetrix raw data as -raw-data-*.txt, not a tar.
    if "-raw-data-" in low:
        return "matches: raw array files present (ArrayExpress -raw-data- files)"
    has_cel = ".cel" in low
    has_counts = "count" in low or "tpm" in low or "fpkm" in low
    if availability == "raw_array_files":
        if has_raw_tar or has_cel:
            return "matches: raw array files present"
        return "MISMATCH: recorded raw_array_files, but no _RAW.tar or CEL at this level"
    if availability == "raw_counts":
        return ("matches: count matrix present" if has_counts
                else "MISMATCH: recorded raw_counts, but no count-like file name")
    if availability == "processed_matrix_only":
        return ("matches: processed files only, no _RAW.tar" if not has_raw_tar
                else "richer than recorded: a _RAW.tar is present")
    return "no expectation recorded"


def sizes(base: str, names: list[str]) -> tuple[int, str, int]:
    """Total bytes, largest file, and how many files reported no size."""
    total, largest, unknown = 0, ("", 0), 0
    for name in names:
        r = get(base + name, method="HEAD")
        n = int(r.headers.get("Content-Length", 0) or 0)
        if not n:
            unknown += 1
        total += n
        if n > largest[1]:
            largest = (name, n)
    return total, f"{largest[0]} ({largest[1] / 1e6:.1f} MB)" if largest[0] else "", unknown


def check_geo(acc: str, gsms: list[str], limit_samples: int) -> dict:
    base = f"{GEO_FTP}/series/{stem(acc)}/{acc}/suppl/"
    status, names = listing(base)
    level, note = "series", ""
    if status == 200 and names:
        total, largest, unknown = sizes(base, names)
        n_files = len(names)
    else:
        # No series-level files: sample-level submission, sample a few GSMs and extrapolate.
        level = "sample"
        checked, total, n_files, largest, unknown = 0, 0, 0, ("", 0), 0
        for gsm in gsms[:limit_samples]:
            sbase = f"{GEO_FTP}/samples/{stem(gsm)}/{gsm}/suppl/"
            s_status, s_names = listing(sbase)
            if s_status != 200 or not s_names:
                continue
            s_total, s_largest, s_unknown = sizes(sbase, s_names)
            checked += 1
            total += s_total
            n_files += len(s_names)
            unknown += s_unknown
            if s_largest:
                largest = (s_largest, 0) if not largest[0] else largest
        if checked:
            note = (f"series directory empty or absent (HTTP {status}); {checked} of {len(gsms)} samples "
                    f"checked, {total / 1e6:.1f} MB for those, so roughly "
                    f"{total / checked * len(gsms) / 1e9:.2f} GB for the series")
            status = 200
        else:
            note = f"no files at series level (HTTP {status}) and none on the first {limit_samples} samples"
            status = 404
        largest = largest[0] if isinstance(largest, tuple) else largest
    return {"level": level, "http_status": status, "n_files": n_files, "total_bytes": total,
            "largest_file": largest if isinstance(largest, str) else "", "n_files_without_size": unknown,
            "url_checked": base, "note": note, "files": "; ".join(names[:8])}


def check_arrayexpress(acc: str) -> dict:
    """BioStudies keeps the file table on its own endpoint, not inside the study record."""
    url = f"{BIOSTUDIES}/{acc}/files"
    r = get(url)
    if r.status_code != 200:
        return {"level": "study", "http_status": r.status_code, "n_files": 0, "total_bytes": 0,
                "largest_file": "", "n_files_without_size": 0, "url_checked": url,
                "note": "BioStudies file listing did not resolve"}
    files = [f for f in r.json().get("items", []) if f.get("file_type") == "file"]
    total = sum(int(f.get("Size", 0) or 0) for f in files)
    raw = [f for f in files
           if "raw" in str(f.get("Description", "")).lower()
           or f.get("path", "").lower().endswith((".cel", ".cel.gz", ".gpr"))]
    biggest = max(files, key=lambda f: int(f.get("Size", 0) or 0), default=None)
    return {"level": "study", "http_status": 200, "n_files": len(files), "total_bytes": total,
            "largest_file": (f"{biggest['path']} ({int(biggest.get('Size', 0)) / 1e6:.1f} MB)"
                             if biggest else ""),
            "n_files_without_size": sum(1 for f in files if not f.get("Size")),
            "url_checked": url,
            "note": f"{len(raw)} of {len(files)} files are described as raw data",
            "files": "; ".join(f.get("path", "") for f in files[:8])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-samples", type=int, default=6,
                    help="GSMs to size when a series has no series-level files")
    args = ap.parse_args()

    readiness = pd.read_csv(READINESS)
    overrides = pd.read_csv(OVERRIDES, keep_default_na=False)
    samples = pd.read_csv(SAMPLES)
    kept = overrides[overrides.use_in_phase2.astype(str) == "True"]

    rows = []
    for _, d in readiness.iterrows():
        acc = d.accession
        gsms = (kept.loc[kept.series == acc, "sample_id"].tolist()
                or samples.loc[(samples.series == acc) &
                               (samples.in_scope_sample.astype(str) == "True"), "gsm"].tolist())
        res = check_arrayexpress(acc) if d.source == "ArrayExpress" else check_geo(acc, gsms, args.limit_samples)
        rows.append({"accession": acc, "source": d.source, "assay_class": d.assay_class,
                     "data_availability": d.data_availability, "n_samples_expected": len(gsms),
                     "files_found_at": res["level"], **{k: res[k] for k in
                     ("http_status", "n_files", "total_bytes", "largest_file", "n_files_without_size",
                      "url_checked", "note", "files")},
                     "expectation_check": classify(res["files"].split("; "), d.data_availability),
                     "resolves": res["http_status"] == 200 and res["n_files"] > 0,
                     "checked_date": time.strftime("%Y-%m-%d")})
        print(f"  {acc}: {'ok' if rows[-1]['resolves'] else 'PROBLEM'} "
              f"{res['n_files']} files, {res['total_bytes'] / 1e6:.1f} MB at {res['level']} level")

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    print(f"[write] {OUT.relative_to(ROOT)}: {int(out.resolves.sum())} of {len(out)} resolve, "
          f"{out.total_bytes.sum() / 1e9:.2f} GB sized so far")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
