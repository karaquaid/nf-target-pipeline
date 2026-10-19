"""Per-dataset ingest readiness for the Phase 2 launch set.

Derives the 22-dataset launch set from the committed Phase 1a tables and the
Phase 2 pre-flight records, and reports what each dataset still needs before it
can enter a differential-expression contrast.

Launch set = comparative-design datasets containing human material, counted in
coverage (so superseries/subseries duplicates are already collapsed), minus the
seven the pre-flight review took out.

Sample counts come from the frozen Phase 1a labels; where a dataset has rows in
phase2-sample-overrides.csv those rows supersede them, which is why both are
reported side by side rather than merged.

Run from the repo root:
    python phase-2/scripts/phase2_launchset_readiness.py
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATASETS = ROOT / "phase-1a" / "data" / "phase1a-datasets.csv"
SAMPLES = ROOT / "phase-1a" / "data" / "phase1a-samples.csv"
OVERRIDES = ROOT / "phase-2" / "data" / "phase2-sample-overrides.csv"
NON_GEO = ROOT / "phase-2" / "data" / "phase2-non-geo-samples.csv"
DIAGNOSIS = ROOT / "phase-2" / "data" / "phase2-review-diagnosis.json"
OUT = ROOT / "phase-2" / "data" / "phase2-launchset-readiness.csv"

# Taken out by the pre-flight review; rationale per accession is in the
# decisions block of phase2-review-diagnosis.json.
EXCLUDED = [
    "GSE120687",
    "GSE172221",
    "GSE2841",
    "GSE325204",
    "GSE56598",
    "GSE5675",
    "GSE77205",
]

HUMAN = "Homo sapiens"
MOUSE = "Mus musculus"


def truthy(series):
    return series.astype(str).str.lower().eq("true")


def launch_set(datasets):
    comparative = datasets[truthy(datasets.comparative_design)]
    human = comparative[comparative.organism.astype(str).str.contains("human", case=False)]
    counted = human[truthy(human.counted_in_coverage)]
    return counted[~counted.accession.isin(EXCLUDED)].copy()


def blockers(row):
    found = []
    if row["source"] == "ArrayExpress" and row["non_geo_label_rows"] == 0:
        found.append("no sample-level labels (ArrayExpress)")
        if str(row["control_types"]) not in ("none", "nan"):
            found.append("control arm unconfirmed")
    human_total = row["human_cases"] + row["human_controls"] + row["human_other"]
    if row["source"] == "GEO" and human_total == 0 and row["override_cases_kept"] == 0:
        found.append("no human in-scope samples labelled")
    if human_total == 1:
        found.append("single human sample, no contrast")
    if (
        row["human_controls"] == 0
        and row["distinct_labels_in_scope"] <= 1
        and not row["stated_contrast"]
    ):
        found.append("no contrast derivable from labels")
    if row["stated_contrast"] and row["override_arm_rows"] == 0 and row["non_geo_label_rows"] == 0:
        found.append("stated contrast has no per-sample arm assignment")
    if row["mouse_in_scope"]:
        found.append(f"{row['mouse_in_scope']} mouse samples need a deferral tag")
    if row["data_availability"] == "processed_matrix_only":
        found.append("processed matrix only")
    return "; ".join(found) or "ready"


def main():
    datasets = pd.read_csv(DATASETS)
    samples = pd.read_csv(SAMPLES)
    overrides = pd.read_csv(OVERRIDES)
    non_geo = pd.read_csv(NON_GEO)
    decisions = json.loads(DIAGNOSIS.read_text())["decisions"]

    launch = launch_set(datasets)
    in_scope = samples[truthy(samples.in_scope_sample)]
    kept = overrides[truthy(overrides.use_in_phase2)]

    rows = []
    for accession in sorted(launch.accession):
        dataset = launch[launch.accession == accession].iloc[0]
        mine = in_scope[in_scope.series == accession]
        human = mine[mine.organism == HUMAN]
        arm = human.label.astype(str).str.split("_").str[0]
        kept_here = kept[kept.series == accession]
        decision = decisions.get(accession, {})
        rows.append(
            {
                "accession": accession,
                "source": dataset.source,
                "assay_class": dataset.assay_class,
                "data_availability": dataset.data_availability,
                "control_types": dataset.control_types,
                "platforms": dataset.platforms if pd.notna(dataset.platforms) else "",
                "human_cases": int((arm == "nf").sum()),
                "human_controls": int((arm == "control").sum()),
                "human_other": int((~arm.isin(["nf", "control"])).sum()),
                "mouse_in_scope": int((mine.organism == MOUSE).sum()),
                "distinct_labels_in_scope": int(mine.label.nunique()),
                "override_rows": int((overrides.series == accession).sum()),
                "override_cases_kept": int((kept_here.de_role == "case").sum()),
                "override_controls_kept": int((kept_here.de_role == "control").sum()),
                "override_arm_rows": int(kept_here["de_arm"].notna().sum())
                if "de_arm" in overrides.columns
                else 0,
                "non_geo_label_rows": int((non_geo.series == accession).sum()),
                "preflight_decision": decision.get("decision", ""),
                "stated_contrast": decision.get("contrast", ""),
            }
        )

    readiness = pd.DataFrame(rows)
    readiness["blocker"] = readiness.apply(blockers, axis=1)
    readiness.to_csv(OUT, index=False)

    ready = int((readiness.blocker == "ready").sum())
    print(f"{len(readiness)} datasets in the launch set, {ready} ready as labelled")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
