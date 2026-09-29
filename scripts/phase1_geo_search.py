#!/usr/bin/env python3
"""Phase 1: public expression-dataset sweep for NF1 / NF2-SWN / schwannomatosis.

Searches NCBI GEO (db=gds, series only, expression assay types only) with one
query per manifestation in the project labeling standard, then pulls the SOFT
header for every hit (series-level fields plus per-sample characteristics).

Design notes
------------
* Queries, the search date and the raw E-utilities responses are all recorded,
  so the sweep is re-runnable and diffable. Nothing here decides scope: disease,
  manifestation, germline-vs-sporadic and study-design labels are assigned in a
  separate classification step that reads this script's output.
* Every accession reported downstream came back from esearch/esummary, so it
  exists by construction.
* Mouse and human are both collected; organism is a column, not a filter.

Usage
-----
    python scripts/phase1_geo_search.py --outdir build/phase1 [--email you@example.org]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

import requests

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
ACC_CGI = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"

# Expression assays only: unfiltered keyword hits also return ChIP-seq, ATAC,
# methylation and miRNA series, which are not Phase 2/3 inputs.
EXPR = (
    '("expression profiling by high throughput sequencing"[DataSet Type]'
    ' OR "expression profiling by array"[DataSet Type]'
    ' OR "expression profiling by genome tiling array"[DataSet Type])'
)
SERIES = "gse[ETYP]"

# One query per manifestation in the labeling standard, plus disease-level
# catch-alls. The manifestation named here is a search-provenance hint only;
# the authoritative label is assigned in the classification step.
QUERIES: list[tuple[str, str, str]] = [
    ("cutaneous_neurofibroma", "Cutaneous neurofibroma",
     '"cutaneous neurofibroma"[All Fields] OR "dermal neurofibroma"[All Fields]'),
    ("plexiform_neurofibroma", "Plexiform neurofibroma",
     '"plexiform neurofibroma"[All Fields]'),
    ("annubp", "ANNUBP / atypical neurofibroma",
     '"atypical neurofibroma"[All Fields] OR "ANNUBP"[All Fields]'
     ' OR "atypical neurofibromatous neoplasm"[All Fields]'),
    ("neurofibroma_any", "Cutaneous neurofibroma",
     '"neurofibroma"[All Fields]'),
    ("mpnst", "Malignant peripheral nerve sheath tumor (MPNST)",
     '"MPNST"[All Fields] OR "malignant peripheral nerve sheath"[All Fields]'
     ' OR "neurofibrosarcoma"[All Fields]'),
    ("vestibular_schwannoma", "Vestibular schwannoma",
     '"vestibular schwannoma"[All Fields] OR "acoustic neuroma"[All Fields]'
     ' OR "acoustic schwannoma"[All Fields]'),
    ("nonvestibular_schwannoma", "Non-vestibular schwannoma",
     '"spinal schwannoma"[All Fields] OR "peripheral schwannoma"[All Fields]'
     ' OR ("schwannoma"[All Fields] AND ("spinal"[All Fields] OR "peripheral nerve"[All Fields]))'),
    ("schwannoma_any", "Vestibular schwannoma",
     '"schwannoma"[All Fields] OR "schwannomas"[All Fields]'),
    ("schwannomatosis", "Non-vestibular schwannoma",
     '"schwannomatosis"[All Fields] OR "LZTR1"[All Fields]'
     ' OR ("SMARCB1"[All Fields] AND ("schwannoma"[All Fields] OR "nerve sheath"[All Fields]))'),
    ("meningioma", "Meningioma",
     '"meningioma"[All Fields] AND ("NF2"[All Fields] OR "neurofibromatosis"[All Fields]'
     ' OR "merlin"[All Fields] OR "schwannomatosis"[All Fields])'),
    ("ependymoma", "Ependymoma",
     '"ependymoma"[All Fields] AND ("NF2"[All Fields] OR "neurofibromatosis"[All Fields]'
     ' OR "merlin"[All Fields])'),
    ("optic_pathway_glioma", "Optic pathway glioma",
     '"optic pathway glioma"[All Fields] OR "optic glioma"[All Fields]'
     ' OR "optic nerve glioma"[All Fields]'),
    ("non_optic_lgg", "Non-optic LGG",
     '("pilocytic astrocytoma"[All Fields] OR "low grade glioma"[All Fields]'
     ' OR "low-grade glioma"[All Fields])'
     ' AND ("NF1"[All Fields] OR "neurofibromatosis"[All Fields])'),
    ("high_grade_glioma", "High grade glioma",
     '("glioblastoma"[All Fields] OR "high grade glioma"[All Fields]'
     ' OR "anaplastic astrocytoma"[All Fields])'
     ' AND ("neurofibromatosis"[All Fields] OR "NF1 syndrome"[All Fields])'),
    ("gist", "Gastrointestinal stromal tumor (GIST)",
     '"gastrointestinal stromal"[All Fields]'
     ' AND ("NF1"[All Fields] OR "neurofibromatosis"[All Fields])'),
    ("heme", "Hematologic malignancies",
     '("juvenile myelomonocytic leukemia"[All Fields] OR "JMML"[All Fields]'
     ' OR "myeloid leukemia"[All Fields])'
     ' AND ("NF1"[All Fields] OR "neurofibromatosis"[All Fields])'),
    ("bone", "Bone defects",
     '("tibial pseudarthrosis"[All Fields] OR "pseudarthrosis"[All Fields]'
     ' OR "bone"[All Fields] OR "osteoblast"[All Fields] OR "skeletal"[All Fields])'
     ' AND ("NF1"[All Fields] OR "neurofibromatosis"[All Fields])'),
    ("cognition", "Cognition / Behavioral / Learning",
     '("learning"[All Fields] OR "cognitive"[All Fields] OR "hippocampus"[All Fields]'
     ' OR "behavior"[All Fields] OR "autism"[All Fields])'
     ' AND ("NF1"[All Fields] OR "neurofibromatosis"[All Fields])'),
    ("pain", "Pain",
     '("pain"[All Fields] OR "dorsal root ganglion"[All Fields] OR "nociception"[All Fields])'
     ' AND ("NF1"[All Fields] OR "neurofibromatosis"[All Fields])'),
    ("sleep", "Sleep",
     '("sleep"[All Fields] OR "circadian"[All Fields])'
     ' AND ("NF1"[All Fields] OR "neurofibromatosis"[All Fields])'),
    ("pulmonary", "Pulmonary disease",
     '("lung"[All Fields] OR "pulmonary"[All Fields])'
     ' AND ("neurofibromatosis"[All Fields] OR "NF1 syndrome"[All Fields])'),
    ("cardiovascular", "Cardiovascular issues",
     '("cardiac"[All Fields] OR "heart"[All Fields] OR "vascular"[All Fields]'
     ' OR "vasculopathy"[All Fields])'
     ' AND ("neurofibromatosis"[All Fields] OR "NF1 syndrome"[All Fields])'),
    ("nf1_disease", "Other",
     '"neurofibromatosis type 1"[All Fields] OR "neurofibromatosis 1"[All Fields]'
     ' OR "von Recklinghausen"[All Fields]'),
    ("nf2_disease", "Other",
     '"neurofibromatosis type 2"[All Fields] OR "neurofibromatosis 2"[All Fields]'
     ' OR "merlin"[All Fields]'),
    ("nf_generic", "Other",
     '"neurofibromatosis"[All Fields]'),
    ("nf1_gene_model", "Other",
     '("Nf1"[All Fields] AND ("knockout"[All Fields] OR "conditional"[All Fields]'
     ' OR "mutant"[All Fields] OR "haploinsufficient"[All Fields] OR "null"[All Fields]))'),
    ("nf2_gene_model", "Other",
     '("Nf2"[All Fields] AND ("knockout"[All Fields] OR "conditional"[All Fields]'
     ' OR "mutant"[All Fields] OR "null"[All Fields]))'),
]


class NCBI:
    """Rate-limited NCBI client (3 req/s without an API key, 10 with)."""

    def __init__(self, email: str | None = None, api_key: str | None = None):
        self.params = {"tool": "nf-target-pipeline"}
        if email:
            self.params["email"] = email
        if api_key:
            self.params["api_key"] = api_key
        self.delay = 0.11 if api_key else 0.35
        self.session = requests.Session()
        self._last = 0.0

    def _wait(self):
        gap = time.time() - self._last
        if gap < self.delay:
            time.sleep(self.delay - gap)
        self._last = time.time()

    def get(self, url: str, params: dict, tries: int = 4) -> requests.Response:
        for attempt in range(tries):
            self._wait()
            try:
                r = self.session.get(url, params={**self.params, **params}, timeout=90)
                if r.status_code == 200:
                    return r
                if r.status_code in (429, 500, 502, 503, 504):
                    time.sleep(2 ** attempt)
                    continue
                r.raise_for_status()
            except requests.RequestException:
                if attempt == tries - 1:
                    raise
                time.sleep(2 ** attempt)
        raise RuntimeError(f"giving up on {url} {params}")

    def esearch(self, term: str, retmax: int = 500) -> tuple[list[str], int]:
        uids: list[str] = []
        retstart = 0
        while True:
            r = self.get(f"{EUTILS}/esearch.fcgi", {
                "db": "gds", "term": term, "retmode": "json",
                "retmax": retmax, "retstart": retstart})
            res = r.json()["esearchresult"]
            batch = res.get("idlist", [])
            uids.extend(batch)
            total = int(res.get("count", 0))
            retstart += retmax
            if retstart >= total or not batch:
                return uids, total

    def esummary(self, uids: list[str]) -> list[dict]:
        out = []
        for i in range(0, len(uids), 200):
            chunk = uids[i:i + 200]
            r = self.get(f"{EUTILS}/esummary.fcgi", {
                "db": "gds", "id": ",".join(chunk), "retmode": "json"})
            res = r.json().get("result", {})
            out.extend(res[u] for u in res.get("uids", []) if u in res)
        return out

    def soft(self, accession: str, targ: str) -> str:
        r = self.get(ACC_CGI, {"acc": accession, "targ": targ,
                               "form": "text", "view": "brief"})
        return r.text


def parse_soft(text: str) -> list[dict]:
    """Parse a brief SOFT text stream into a list of entity dicts."""
    entities: list[dict] = []
    cur: dict | None = None
    for line in text.splitlines():
        if line.startswith("^"):
            if cur:
                entities.append(cur)
            key, _, val = line[1:].partition("=")
            cur = {"_entity": key.strip(), "_id": val.strip()}
        elif line.startswith("!") and cur is not None:
            key, _, val = line[1:].partition("=")
            cur.setdefault(key.strip(), []).append(val.strip())
    if cur:
        entities.append(cur)
    return entities


def series_record(summ: dict, soft_self: list[dict]) -> dict:
    s = soft_self[0] if soft_self else {}
    g = lambda k: s.get(k, [])  # noqa: E731
    return {
        "accession": summ.get("accession"),
        "title": summ.get("title", ""),
        "summary": summ.get("summary", ""),
        "overall_design": " ".join(g("Series_overall_design")),
        "gds_type": summ.get("gdstype", ""),
        "taxon": summ.get("taxon", ""),
        "n_samples": summ.get("n_samples"),
        "pdat": summ.get("pdat", ""),
        "platforms": ";".join(sorted(set(g("Series_platform_id")))),
        "pubmed_ids": ";".join(str(x) for x in (summ.get("pubmedids") or [])),
        "relations": ";".join(g("Series_relation")),
        "supplementary_files": ";".join(
            os.path.basename(u) for u in g("Series_supplementary_file")),
        "ftp_link": summ.get("ftplink", ""),
        "url": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={summ.get('accession')}",
    }


def sample_records(accession: str, soft_gsm: list[dict]) -> list[dict]:
    rows = []
    for e in soft_gsm:
        if e.get("_entity") != "SAMPLE":
            continue
        chars = (e.get("Sample_characteristics_ch1", [])
                 + e.get("Sample_characteristics_ch2", []))
        rows.append({
            "series": accession,
            "gsm": e.get("_id", ""),
            "title": " ".join(e.get("Sample_title", [])),
            "source": " ".join(e.get("Sample_source_name_ch1", [])),
            "organism": " ".join(e.get("Sample_organism_ch1", [])),
            "characteristics": " | ".join(chars),
            "library_strategy": " ".join(e.get("Sample_library_strategy", [])),
            "platform": " ".join(e.get("Sample_platform_id", [])),
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="build/phase1")
    ap.add_argument("--email", default=os.environ.get("NCBI_EMAIL"))
    ap.add_argument("--api-key", default=os.environ.get("NCBI_API_KEY"))
    ap.add_argument("--max-samples-fetch", type=int, default=400,
                    help="skip per-sample SOFT fetch above this series size")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    (outdir / "soft").mkdir(parents=True, exist_ok=True)
    ncbi = NCBI(args.email, args.api_key)
    run_date = dt.date.today().isoformat()

    hits: dict[str, set[str]] = {}
    query_log = []
    for qid, manifestation_hint, core in QUERIES:
        term = f"({core}) AND {SERIES} AND {EXPR}"
        uids, total = ncbi.esearch(term)
        summaries = ncbi.esummary(uids) if uids else []
        accs = [s.get("accession") for s in summaries
                if str(s.get("accession", "")).startswith("GSE")]
        for a in accs:
            hits.setdefault(a, set()).add(qid)
        query_log.append({"query_id": qid, "manifestation_hint": manifestation_hint,
                          "term": term, "n_hits": total, "accessions": sorted(accs)})
        print(f"[query] {qid:26s} {total:4d} hits", flush=True)
        for s in summaries:
            acc = str(s.get("accession", ""))
            if acc.startswith("GSE"):
                (outdir / "soft" / f"{acc}.summary.json").write_text(json.dumps(s))

    (outdir / "queries.json").write_text(json.dumps(
        {"run_date": run_date, "series_filter": SERIES, "assay_filter": EXPR,
         "queries": query_log}, indent=2))
    print(f"[sweep] {len(hits)} unique series across {len(QUERIES)} queries", flush=True)

    series_rows, sample_rows, skipped = [], [], []
    for i, acc in enumerate(sorted(hits), 1):
        summ = json.loads((outdir / "soft" / f"{acc}.summary.json").read_text())
        self_txt = ncbi.soft(acc, "self")
        (outdir / "soft" / f"{acc}.self.soft").write_text(self_txt)
        rec = series_record(summ, parse_soft(self_txt))
        rec["query_ids"] = ";".join(sorted(hits[acc]))
        n = int(rec["n_samples"] or 0)
        if n and n <= args.max_samples_fetch:
            gsm_txt = ncbi.soft(acc, "gsm")
            (outdir / "soft" / f"{acc}.gsm.soft").write_text(gsm_txt)
            sample_rows.extend(sample_records(acc, parse_soft(gsm_txt)))
            rec["sample_metadata"] = "fetched"
        else:
            rec["sample_metadata"] = "skipped_too_large"
            skipped.append(acc)
        series_rows.append(rec)
        if i % 25 == 0:
            print(f"[detail] {i}/{len(hits)}", flush=True)

    (outdir / "series.json").write_text(json.dumps(series_rows, indent=2))
    (outdir / "samples.json").write_text(json.dumps(sample_rows))
    print(f"[done] {len(series_rows)} series, {len(sample_rows)} samples, "
          f"{len(skipped)} series too large for per-sample fetch", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
