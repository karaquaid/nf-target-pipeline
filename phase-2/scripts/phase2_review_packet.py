#!/usr/bin/env python3
"""Phase 2 pre-flight: review packet for the Phase 1a datasets that need a human pass.

Scope: datasets with a comparative study design (the ones Phase 2 would ingest) whose Phase 1a
classification confidence came out medium or low. 18 of the 49 comparative datasets, 14 of them in
the human-only first-pass set.

Provenance note: the Phase 1a pass stored a confidence value but not the reasoning behind it, so the
"why it is not a clean call" text in phase2-review-diagnosis.json is a fresh audit of each GEO record
(LLM pass over the record text plus the stored labels), not a recovered value. The adjudication block
in that file is the agent's own check of each claim the audit made against a stored field.

Outputs (phase-2/data, phase-2/docs):
    phase2-classification-review.csv   one row per dataset, machine-readable
    phase2-classification-review.md    the readable packet, launch-set datasets first

Usage
-----
    python phase-2/scripts/phase2_review_packet.py
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
from pathlib import Path

HUMAN_ORGANISMS = {"human", "human+mouse"}
VERDICT_LABEL = {
    "likely_defect": "likely defect in the stored label",
    "needs_human_check": "needs a human check",
    "explained_by_column_definition": "checked, consistent with the column definition",
}


def read_csv(path: Path) -> list[dict]:
    with path.open() as fh:
        return list(csv.DictReader(fh))


def truthy(v: str) -> bool:
    return str(v).strip().lower() == "true"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase1a", default="phase-1a/data")
    ap.add_argument("--diagnosis", default="phase-2/data/phase2-review-diagnosis.json")
    ap.add_argument("--outdata", default="phase-2/data")
    ap.add_argument("--outdocs", default="phase-2/docs")
    args = ap.parse_args()
    p1a = Path(args.phase1a)

    datasets = read_csv(p1a / "phase1a-datasets.csv")
    samples = read_csv(p1a / "phase1a-samples.csv")
    payload = json.loads(Path(args.diagnosis).read_text())
    diagnosis, adjudication = payload["diagnosis"], payload["adjudication"]
    decisions = payload.get("decisions", {})

    review = [d for d in datasets
              if truthy(d["counted_in_coverage"]) and truthy(d["comparative_design"])
              and d["confidence"] in ("medium", "low")]
    accs = {d["accession"] for d in review}
    labels = collections.defaultdict(collections.Counter)
    for s in samples:
        if s["series"] in accs:
            labels[s["series"]][s["label"]] += 1

    rows = []
    for d in review:
        acc = d["accession"]
        dia = diagnosis.get(acc, {})
        adj = adjudication.get(acc, {})
        dec = decisions.get(acc, {})
        rows.append({
            "accession": acc,
            "confidence": d["confidence"],
            "in_launch_set": d["organism"] in HUMAN_ORGANISMS,
            "organism": d["organism"],
            "title": d["title"],
            "disease": d["disease"],
            "manifestations": d["manifestations"],
            "nf_association": d["nf_association"],
            "germline_basis": d["germline_basis"],
            "study_design": d["study_design"],
            "assay_class": d["assay_class"],
            "co_assays": d["co_assays"],
            "is_superseries": bool(d["superseries_of"]),
            "n_samples": d["n_samples"],
            "n_samples_in_scope": d["n_samples_in_scope"],
            "n_nf_case_samples": d["n_nf_case_samples"],
            "n_control_samples": d["n_control_samples"],
            "control_types": d["control_types"],
            "sample_labels": "; ".join(f"{k}={v}" for k, v in labels[acc].most_common()),
            "phase1a_evidence": d["evidence"],
            "phase1a_notes": d["notes"],
            "audit_ambiguity": dia.get("ambiguity", ""),
            "audit_secondary": dia.get("secondary", ""),
            "audit_what_would_settle_it": dia.get("what_would_settle_it", ""),
            "audit_flags_stored_label": dia.get("label_looks_wrong", ""),
            "audit_label_comment": dia.get("label_comment", ""),
            "decision": dec.get("decision", ""),
            "decision_contrast": dec.get("contrast", ""),
            "decision_by": dec.get("by", ""),
            "adjudication": adj.get("verdict", ""),
            "adjudication_comment": adj.get("comment", ""),
            "url": d["url"],
        })
    rows.sort(key=lambda r: (not r["in_launch_set"], r["confidence"] != "low", r["accession"]))

    csv_path = Path(args.outdata) / "phase2-classification-review.csv"
    with csv_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"[write] {csv_path} {len(rows)} rows")

    n_launch = sum(1 for r in rows if r["in_launch_set"])
    n_flagged = sum(1 for r in rows if r["adjudication"])
    n_decided = sum(1 for r in rows if r["decision"])
    md = [
        "# Phase 2 pre-flight: classification review packet",
        "",
        f"**{len(rows)} datasets** - every comparative-design dataset whose Phase 1a confidence came out "
        f"medium or low. {n_launch} are in the human-only first-pass set; the rest are mouse-model "
        "datasets, deferred with the rest of the mouse track but listed so the review is complete.",
        "",
        "These are the datasets Phase 2 would ingest, so the labels that matter here are the ones that "
        "decide a differential-expression contrast: which samples are NF cases, which are controls, and "
        "whether the germline call holds.",
        "",
        "**How to read the audit lines.** Phase 1a stored a confidence value but not the reasoning "
        "behind it. The *why it is not a clean call* text below is a fresh audit of each GEO record "
        "(record text plus the stored labels), so it is a hypothesis about where the uncertainty sits, "
        f"not a recovered value. Where that audit claimed a stored field looks wrong ({n_flagged} "
        "datasets), the claim was checked and carries an adjudication line.",
        "",
        (f"**{n_decided} of {len(rows)} reviewed so far.** Datasets you have ruled on carry a "
         "**Decision** line naming the contrast they enter Phase 2 with."
         if n_decided else "No datasets have been ruled on yet."),
        "",
        "| verdict | meaning |",
        "|---|---|",
        "| likely defect in the stored label | the stored value is probably wrong and should be corrected |",
        "| needs a human check | the record cannot settle it; a paper or supplementary table can |",
        "| checked, consistent with the column definition | the audit's claim does not hold |",
        "",
    ]
    for group, title in ((True, "Human-only first-pass set"), (False, "Mouse-model datasets (deferred)")):
        group_rows = [r for r in rows if r["in_launch_set"] is group]
        if not group_rows:
            continue
        md += [f"## {title}", ""]
        for r in group_rows:
            md += [
                f"### [{r['accession']}]({r['url']}) - {r['confidence']} confidence",
                "",
                f"*{r['title']}*",
                "",
                f"- **Labels:** {r['disease']} / {r['manifestations']} | {r['nf_association']} "
                f"(basis: {r['germline_basis']}) | {r['study_design']} | {r['assay_class']}"
                + (f" | co-assays: {r['co_assays']}" if r["co_assays"] != "none" else "")
                + (" | **superseries**" if r["is_superseries"] else ""),
                f"- **Samples:** {r['n_samples']} in the series, {r['n_samples_in_scope']} in scope, "
                f"{r['n_nf_case_samples']} NF cases, {r['n_control_samples']} controls"
                + (f" ({r['control_types']})" if r["control_types"] != "none" else ""),
                f"- **Sample labels:** {r['sample_labels'] or '(none labelled)'}",
                f"- **Evidence recorded in Phase 1a:** {r['phase1a_evidence'] or '(none)'}",
            ]
            if r["phase1a_notes"]:
                md += [f"- **Phase 1a notes:** {r['phase1a_notes']}"]
            md += [f"- **Why it is not a clean call:** {r['audit_ambiguity'] or '(not diagnosed)'}"]
            if r["audit_secondary"]:
                md += [f"- **Also:** {r['audit_secondary']}"]
            if r["audit_what_would_settle_it"]:
                md += [f"- **What would settle it:** {r['audit_what_would_settle_it']}"]
            if r["decision"]:
                md += [f"- **Decision ({r['decision_by'] or 'reviewer'}): {r['decision']}** - "
                       f"contrast: {r['decision_contrast']}"]
                impl = decisions.get(r["accession"], {}).get("implementation", "")
                if impl:
                    md += [f"  - {impl}"]
            if r["adjudication"]:
                md += [f"- **Flagged stored field** - {VERDICT_LABEL.get(r['adjudication'], r['adjudication'])}: "
                       f"{r['adjudication_comment']}"]
            md += [""]
    md_path = Path(args.outdocs) / "phase2-classification-review.md"
    md_path.write_text("\n".join(md))
    print(f"[write] {md_path} {len(md)} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
