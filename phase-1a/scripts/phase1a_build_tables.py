#!/usr/bin/env python3
"""Phase 1: turn the GEO sweep + classification output into the deliverable tables.

Inputs (from phase-1a/scripts/phase1a_geo_search.py and the classification step):
    <builddir>/series.json      series-level GEO metadata for every hit
    <builddir>/samples.json     per-sample SOFT records
    <builddir>/queries.json     query strings, hit counts, search date
    <builddir>/classified.json  accession -> series-level classification
    <builddir>/samples_labelled.json  [{series, gsm, label, sporadic, in_scope_sample}]

Outputs (in phase-1a/data):
    phase1a-datasets.csv         one row per in-scope dataset
    phase1a-dataset-labels.csv   long dataset x disease x manifestation
    phase1a-samples.csv          per-sample manifest for in-scope datasets (Phase 2 input list)
    phase1a-excluded.csv         everything the sweep returned and the reason it was dropped
    phase1a-coverage.csv         disease x manifestation x organism counts, zeros included
    phase1a-queries.csv          search provenance
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

MANIFESTATIONS = [
    "Bone defects", "Cardiovascular issues", "Cognition / Behavioral / Learning", "Sleep",
    "Cutaneous neurofibroma", "Ependymoma", "Gastrointestinal stromal tumor (GIST)",
    "Hematologic malignancies", "High grade glioma",
    "Malignant peripheral nerve sheath tumor (MPNST)", "Meningioma", "Optic pathway glioma",
    "Non-optic LGG", "Pain", "Plexiform neurofibroma", "ANNUBP / atypical neurofibroma",
    "Pulmonary disease", "Non-vestibular schwannoma", "Vestibular schwannoma", "Other",
]
DISEASES = ["NF1", "NF2-SWN", "SWN"]
CONTROL_LABELS = {"control_matched_adjacent_normal", "control_unaffected_donor_normal",
                  "control_isogenic_engineered"}
CASE_LABELS = {"nf_case_tumor", "nf_case_nontumor"}
COMPARATIVE_DESIGNS = {"tumor_vs_normal", "subtype_or_grade_comparison"}


def data_availability(supp: str, gds_type: str, relations: str) -> str:
    s = supp.lower()
    if not s:
        return "none_listed"
    if re.search(r"\.cel|_raw\.tar|\.idat", s):
        return "raw_array_files"
    if re.search(r"count|htseq|featurecount|rsem\.genes|\.bam", s):
        return "raw_counts"
    if re.search(r"fpkm|tpm|rpkm|normali[sz]ed|expression|matrix|deseq|edger|\.mtx|barcodes", s):
        return "processed_matrix_only"
    return "other_supplementary"


def parse_relations(rel: str) -> tuple[list[str], list[str], bool]:
    sup, sub = [], []
    sra = "sra?term=" in rel.lower() or "/sra" in rel.lower()
    for part in rel.split(";"):
        m = re.search(r"(SuperSeries of|SubSeries of):\s*(GSE\d+)", part, re.I)
        if m:
            (sup if m.group(1).lower().startswith("superseries") else sub).append(m.group(2))
    return sup, sub, sra


def organism_class(taxon: str, classified_org: str) -> str:
    t = taxon.lower()
    human, mouse = "homo sapiens" in t, "mus musculus" in t
    if human and mouse:
        return "human+mouse"
    if human:
        return "human"
    if mouse:
        return "mouse"
    return classified_org or "other"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--builddir", default="build/phase1a")
    ap.add_argument("--datadir", default="phase-1a/data")
    ap.add_argument("--additions", default="phase-1a/data/phase1a-arrayexpress-additions.json",
                    help="hand-curated non-GEO records to merge (dataset counts only)")
    args = ap.parse_args()
    B, D = Path(args.builddir), Path(args.datadir)
    D.mkdir(parents=True, exist_ok=True)

    series = {r["accession"]: r for r in json.loads((B / "series.json").read_text())}
    classified = json.loads((B / "classified.json").read_text())
    queries = json.loads((B / "queries.json").read_text())
    samples = json.loads((B / "samples.json").read_text())
    labels = {(r["series"], r["gsm"]): r
              for r in json.loads((B / "samples_labelled.json").read_text())}

    samples_by_series = defaultdict(list)
    for s in samples:
        samples_by_series[s["series"]].append(s)

    # ---- dedup: a SubSeries whose SuperSeries is also in the sweep is not counted separately
    dup_of = {}
    for acc, rec in series.items():
        _sup, sub, _sra = parse_relations(rec.get("relations", ""))
        for parent in sub:
            if parent in series:
                dup_of[acc] = parent

    dataset_rows, label_rows, sample_rows, excluded_rows = [], [], [], []
    for acc in sorted(series):
        rec = series[acc]
        cls = classified.get(acc)
        sup, sub, sra = parse_relations(rec.get("relations", ""))
        org = organism_class(rec.get("taxon", ""), (cls or {}).get("organism_class", ""))
        if cls is None or not cls.get("in_scope"):
            excluded_rows.append({
                "accession": acc, "title": rec["title"], "organism": org,
                "n_samples": rec["n_samples"],
                "nf_association": (cls or {}).get("nf_association", "unclassified"),
                "exclusion_reason": (cls or {}).get("exclusion_reason", "classification failed"),
                "disease_reading": (cls or {}).get("disease", ""),
                "manifestation_reading": ";".join((cls or {}).get("manifestations", []) or []),
                "confidence": (cls or {}).get("confidence", ""),
                "url": rec["url"],
            })
            continue

        smp = samples_by_series.get(acc, [])
        lab = [labels.get((acc, s["gsm"]), {}) for s in smp]
        n_case = sum(1 for x in lab if x.get("label") in CASE_LABELS)
        n_ctrl = sum(1 for x in lab if x.get("label") in CONTROL_LABELS)
        n_inscope = sum(1 for x in lab if x.get("in_scope_sample") is True)
        n_sporadic = sum(1 for x in lab if x.get("sporadic") is True)
        ctypes = sorted({x["label"] for x in lab if x.get("label") in CONTROL_LABELS})
        manifs = [m for m in (cls.get("manifestations") or []) if m in MANIFESTATIONS] or ["Other"]
        disease = cls.get("disease") if cls.get("disease") in DISEASES else "Not specified"

        dataset_rows.append({
            "accession": acc, "source": "GEO", "sample_level_labelled": True,
            "title": rec["title"], "disease": disease,
            "manifestations": ";".join(manifs), "organism": org,
            "material": cls.get("material", ""), "study_design": cls.get("study_design", ""),
            "comparative_design": cls.get("study_design") in COMPARATIVE_DESIGNS,
            "single_cell": bool(cls.get("single_cell")),
            "nf_association": cls.get("nf_association", ""),
            "germline_basis": cls.get("germline_basis", ""),
            "n_samples": rec["n_samples"],
            "n_samples_metadata_fetched": len(smp),
            "n_samples_in_scope": n_inscope,
            "n_nf_case_samples": n_case, "n_control_samples": n_ctrl,
            "n_sporadic_samples_excluded": n_sporadic,
            "control_types": ";".join(ctypes) if ctypes else "none",
            "data_availability": data_availability(rec.get("supplementary_files", ""),
                                                   rec.get("gds_type", ""),
                                                   rec.get("relations", "")),
            "sra_raw_reads": sra,
            "assay_type": rec.get("gds_type", ""), "platforms": rec.get("platforms", ""),
            "release_date": rec.get("pdat", ""), "pubmed_ids": rec.get("pubmed_ids", ""),
            "superseries_of": ";".join(sup), "subseries_of": ";".join(sub),
            "counted_in_coverage": acc not in dup_of,
            "duplicate_of": dup_of.get(acc, ""),
            "confidence": cls.get("confidence", ""), "evidence": cls.get("evidence", ""),
            "notes": cls.get("notes", ""), "query_ids": rec.get("query_ids", ""),
            "url": rec["url"],
        })
        for m in manifs:
            label_rows.append({"accession": acc, "disease": disease, "manifestation": m,
                               "organism": org, "study_design": cls.get("study_design", ""),
                               "n_samples_in_scope": n_inscope,
                               "counted_in_coverage": acc not in dup_of})
        for s in smp:
            x = labels.get((acc, s["gsm"]), {})
            sample_rows.append({**{k: s[k] for k in
                                   ("series", "gsm", "title", "source", "organism",
                                    "characteristics", "library_strategy", "platform")},
                                "label": x.get("label", "unlabelled"),
                                "sporadic": x.get("sporadic", "unknown"),
                                "in_scope_sample": x.get("in_scope_sample", "")})

    # ---- hand-curated ArrayExpress records that are not mirrored from GEO
    add_path = Path(args.additions)
    if add_path.exists() and dataset_rows:
        template = {k: "" for k in dataset_rows[0]}
        for a in json.loads(add_path.read_text())["records"]:
            manifs = [m for m in a["manifestations"].split(";") if m in MANIFESTATIONS]
            row = {**template, **a, "source": "ArrayExpress", "sample_level_labelled": False,
                   "manifestations": ";".join(manifs),
                   "n_samples_metadata_fetched": 0, "n_samples_in_scope": 0,
                   "n_nf_case_samples": 0, "n_control_samples": 0,
                   "n_sporadic_samples_excluded": 0, "sra_raw_reads": False,
                   "counted_in_coverage": True, "duplicate_of": "",
                   "url": f"https://www.ebi.ac.uk/biostudies/arrayexpress/studies/{a['accession']}"}
            row = {k: row[k] for k in template}
            dataset_rows.append(row)
            for m in manifs:
                label_rows.append({"accession": a["accession"], "disease": a["disease"],
                                   "manifestation": m, "organism": a["organism"],
                                   "study_design": a["study_design"],
                                   "n_samples_in_scope": 0, "counted_in_coverage": True})
        ds_extra = {a["accession"]: a for a in json.loads(add_path.read_text())["records"]}
        print(f"[merge] {len(ds_extra)} ArrayExpress records added "
              f"(dataset counts only; samples not labelled)")

    # ---- coverage: every disease x manifestation x organism cell, zeros included
    cov = defaultdict(lambda: {"n_datasets": 0, "n_samples_in_scope": 0,
                               "n_comparative_design": 0, "n_with_controls": 0})
    ds_by_acc = {d["accession"]: d for d in dataset_rows}
    for r in label_rows:
        if not r["counted_in_coverage"]:
            continue
        d = ds_by_acc[r["accession"]]
        org = "human" if "human" in r["organism"] else ("mouse" if "mouse" in r["organism"] else "other")
        c = cov[(r["disease"], r["manifestation"], org)]
        c["n_datasets"] += 1
        c["n_samples_in_scope"] += r["n_samples_in_scope"]
        c["n_comparative_design"] += int(bool(d["comparative_design"]))
        c["n_with_controls"] += int(d["n_control_samples"] > 0)
    cov_rows = []
    for disease in DISEASES + ["Not specified"]:
        for m in MANIFESTATIONS:
            for org in ("human", "mouse", "other"):
                c = cov.get((disease, m, org), {"n_datasets": 0, "n_samples_in_scope": 0,
                                                "n_comparative_design": 0, "n_with_controls": 0})
                cov_rows.append({"disease": disease, "manifestation": m, "organism": org, **c})

    q_rows = [{"query_id": q["query_id"], "manifestation_hint": q["manifestation_hint"],
               "term": q["term"], "n_hits": q["n_hits"], "run_date": queries["run_date"]}
              for q in queries["queries"]]

    def write(name, rows):
        path = D / name
        if not rows:
            path.write_text("")
            return path, 0
        with path.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        return path, len(rows)

    for name, rows in [("phase1a-datasets.csv", dataset_rows),
                       ("phase1a-dataset-labels.csv", label_rows),
                       ("phase1a-samples.csv", sample_rows),
                       ("phase1a-excluded.csv", excluded_rows),
                       ("phase1a-coverage.csv", cov_rows),
                       ("phase1a-queries.csv", q_rows)]:
        path, n = write(name, rows)
        print(f"[write] {path} {n} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
