#!/usr/bin/env python3
"""Phase 1: scope/label classification of the GEO sweep output.

Two things live here:

1. The rubric itself - SYSTEM_PROMPT (series level), SAMPLE_LABEL_SPEC (sample level)
   and build_digest() - which is what an LLM pass is given for each GEO series. The
   2026-09-24 run executed this fan-out inside Claude Science (host.llm, Sonnet-class
   model, one call per series and one per series' sample block). LLM output is not
   deterministic, so the committed tables in phase-1a/data are the record of that run, not
   something a re-run reproduces exactly.

2. `--restore-from-tables`, which rebuilds the intermediate cache
   (classified.json, samples_labelled.json) from those committed tables, so
   phase-1a/scripts/phase1a_build_tables.py can be re-run without repeating the LLM pass.

Usage
-----
    python phase-1a/scripts/phase1a_classify.py --builddir build/phase1a --restore-from-tables phase-1a/data
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

MANIFESTATIONS = [
    "Bone defects", "Cardiovascular issues", "Cognition / Behavioral / Learning", "Sleep",
    "Cutaneous neurofibroma", "Ependymoma", "Gastrointestinal stromal tumor (GIST)",
    "Hematologic malignancies", "High grade glioma",
    "Malignant peripheral nerve sheath tumor (MPNST)", "Meningioma", "Optic pathway glioma",
    "Non-optic LGG", "Pain", "Plexiform neurofibroma", "ANNUBP / atypical neurofibroma",
    "Pulmonary disease", "Non-vestibular schwannoma", "Vestibular schwannoma", "Other",
]

SYSTEM_PROMPT = """You curate public expression datasets for a neurofibromatosis drug-target pipeline.
Judge ONLY from the GEO record text given. Never infer from your own knowledge of what a tumour type
usually involves, and never treat the fact that a search matched the record as evidence.

SCOPE RULE (strict): the project studies germline / NF-associated disease only.
In scope: samples from patients with neurofibromatosis type 1, NF2-related schwannomatosis, or
schwannomatosis (SMARCB1/LZTR1); engineered Nf1/Nf2/Smarcb1/Lztr1-deficient animals or isogenic cells;
cell lines the record identifies as derived from an NF patient's tumour (e.g. ST88-14, sNF96.2, S462,
T265, 90-8TL for NF1; HEI-193, Ben-Men-1 for NF2).
Out of scope: sporadic tumours carrying somatic NF1/NF2 loss (most meningioma, much vestibular
schwannoma and glioma work), cancers where NF1 appears only as one mutated gene among many, and records
where "NF1"/"NF2" refers to nuclear factor 1 or another unrelated entity.
If the record gives no positive indication of germline NF status or an engineered NF genotype, the
dataset is NOT in scope; say so rather than guessing.

Return ONLY a JSON object, no prose, with exactly these keys:
{"nf_association": one of "germline_nf_patient" | "engineered_nf_model" | "nf_derived_cell_line" | "mixed_nf_and_sporadic" | "sporadic_somatic_only" | "not_nf_related",
 "germline_basis": one of "stated_nf_cohort" | "per_sample_nf_status" | "engineered_genotype" | "cell_line_provenance" | "inferred" | "none",
 "in_scope": true|false,
 "exclusion_reason": "" or a short phrase,
 "disease": "NF1" | "NF2-SWN" | "SWN" | "Not specified",
 "manifestations": [one or more of the fixed list below, applied verbatim],
 "organism_class": "human" | "mouse" | "rat" | "zebrafish" | "other" | "mixed",
 "material": "patient_tissue" | "patient_derived_primary_culture" | "immortalized_cell_line" | "mouse_tissue" | "mouse_derived_culture" | "pdx_or_xenograft" | "ipsc_or_engineered" | "other",
 "study_design": "tumor_vs_normal" | "subtype_or_grade_comparison" | "in_vitro_perturbation" | "xenograft_or_in_vivo_treatment" | "single_arm_profiling" | "other",
 "single_cell": true|false,
 "control_types": [any of "matched_adjacent_normal","unaffected_donor_normal","isogenic_or_engineered_control","non_nf_tumor_comparator","none"],
 "n_nf_samples_est": integer or null,
 "n_control_samples_est": integer or null,
 "confidence": "high" | "medium" | "low",
 "evidence": "<=200 chars quoted or paraphrased from the record that justifies in_scope and disease",
 "notes": "<=200 chars"}

Fixed manifestation list (use these strings exactly, no paraphrase):
""" + "; ".join(MANIFESTATIONS) + """
Use "Other" only when the record is in scope but fits none of the listed manifestations (e.g. whole-blood
or fibroblast profiling of NF1 patients). For an out-of-scope record still give your best disease and
manifestation reading, so the exclusions table is informative."""

SAMPLE_LABEL_SPEC = """
SAMPLE LABEL VOCABULARY (use exactly one `label` per sample):
  nf_case_tumor                 - tumour tissue/cells from an NF patient or an NF-genotype animal/cell line
  nf_case_nontumor              - non-tumour material from an NF case (Nf1-/- nerve pre-tumour, patient blood, patient fibroblast)
  control_matched_adjacent_normal - normal tissue from the same patient/animal as a tumour sample in the series
  control_unaffected_donor_normal - normal tissue or primary cells from an unaffected donor
  control_isogenic_engineered   - wild-type littermate, parental/isogenic line, NF1/NF2-restored or re-expressed line, scramble / non-targeting control
  comparator_sporadic_same_tumor - same tumour type but sporadic (no germline NF)
  comparator_non_nf_tumor       - a different tumour type used for comparison
  treated_or_perturbed          - an NF sample under drug or genetic perturbation (an experimental arm, NOT a control)
  other_or_unclear              - anything else, or the record does not say

Also give per sample: `sporadic`: true|false|unknown, and `in_scope_sample`: true|false
(false for sporadic samples and non-NF comparators; the project excludes sporadic tumours).
Judge only from the sample title/source/characteristics plus the series context given. Do not guess from
tumour type alone. Every sample in the input must appear exactly once in the output.
"""


def build_digest(series_rec: dict, sample_rows: list[dict], max_samples_shown: int = 30) -> str:
    """The exact per-series text handed to the classifier."""
    lines = []
    for s in sample_rows[:max_samples_shown]:
        t = f"{s['title']} :: {s['source']} :: {s['characteristics']}"
        lines.append(re.sub(r"\s+", " ", t)[:220])
    extra = (f"\n(+{len(sample_rows) - max_samples_shown} more samples not shown)"
             if len(sample_rows) > max_samples_shown else "")
    r = series_rec
    return (f"ACCESSION: {r['accession']}\nTITLE: {r['title']}\nORGANISM(S): {r['taxon']}\n"
            f"ASSAY TYPE: {r['gds_type']}\nN_SAMPLES: {r['n_samples']}\nRELEASE: {r['pdat']}\n"
            f"PLATFORMS: {r['platforms']}\nSERIES RELATIONS: {r['relations'] or 'none'}\n"
            f"SUMMARY: {re.sub(chr(10), ' ', r['summary'])[:1500]}\n"
            f"OVERALL DESIGN: {r['overall_design'][:900]}\n"
            f"SUPPLEMENTARY FILES: {r['supplementary_files'][:300] or 'none'}\n"
            f"SAMPLE RECORDS ({len(sample_rows)} fetched):\n" + "\n".join(lines) + extra)


def restore_from_tables(datadir: Path, builddir: Path) -> tuple[int, int]:
    """Rebuild classified.json / samples_labelled.json from the committed CSVs."""
    classified: dict[str, dict] = {}
    with (datadir / "phase1a-datasets.csv").open() as fh:
        for row in csv.DictReader(fh):
            if row.get("source") not in (None, "", "GEO"):
                continue
            classified[row["accession"]] = {
                "in_scope": True,
                "nf_association": row["nf_association"],
                "germline_basis": row["germline_basis"],
                "exclusion_reason": "",
                "disease": row["disease"],
                "manifestations": [m for m in row["manifestations"].split(";") if m],
                "organism_class": row["organism"],
                "material": row["material"],
                "study_design": row["study_design"],
                "single_cell": row["single_cell"] == "True",
                "control_types": [c for c in row["control_types"].split(";") if c and c != "none"],
                "confidence": row["confidence"],
                "evidence": row["evidence"],
                "notes": row["notes"],
            }
    with (datadir / "phase1a-excluded.csv").open() as fh:
        for row in csv.DictReader(fh):
            classified[row["accession"]] = {
                "in_scope": False,
                "nf_association": row["nf_association"],
                "germline_basis": "none",
                "exclusion_reason": row["exclusion_reason"],
                "disease": row["disease_reading"],
                "manifestations": [m for m in row["manifestation_reading"].split(";") if m],
                "organism_class": row["organism"],
                "material": "", "study_design": "", "single_cell": False,
                "control_types": [], "confidence": row["confidence"],
                "evidence": "", "notes": "",
            }
    labels = []
    with (datadir / "phase1a-samples.csv").open() as fh:
        for row in csv.DictReader(fh):
            labels.append({"series": row["series"], "gsm": row["gsm"], "label": row["label"],
                           "sporadic": {"True": True, "False": False}.get(row["sporadic"], "unknown"),
                           "in_scope_sample": row["in_scope_sample"] == "True"})
    manual_path = datadir / "phase1a-manual-classifications.json"
    if manual_path.exists():
        manual = json.loads(manual_path.read_text())
        classified.update(manual.get("series", {}))
        seen = {(r["series"], r["gsm"]) for r in labels}
        labels.extend(r for r in manual.get("samples", [])
                      if (r["series"], r["gsm"]) not in seen)
    builddir.mkdir(parents=True, exist_ok=True)
    (builddir / "classified.json").write_text(json.dumps(classified, indent=1))
    (builddir / "samples_labelled.json").write_text(json.dumps(labels))
    return len(classified), len(labels)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--builddir", default="build/phase1a")
    ap.add_argument("--restore-from-tables", metavar="DATADIR",
                    help="rebuild the classification cache from the committed phase-1a/data tables")
    args = ap.parse_args()
    if not args.restore_from_tables:
        print(__doc__)
        return 0
    n_series, n_samples = restore_from_tables(Path(args.restore_from_tables), Path(args.builddir))
    print(f"[restore] {n_series} series classifications, {n_samples} sample labels")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
