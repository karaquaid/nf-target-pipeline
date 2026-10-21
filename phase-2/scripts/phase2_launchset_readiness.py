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

# Held back after the pre-flight review, for reasons recorded in the decisions block
# of phase2-review-diagnosis.json. Deferred, not dropped: their samples keep their
# tags in phase2-sample-overrides.csv so the later pass starts from a finished manifest.
DEFERRED = {
    "GSE244433": "held for the mouse decision (Kara, 2026-10-19): once the mouse arm is "
                 "deferred the series has 1 human sample and no contrast",
}

HUMAN = "Homo sapiens"
MOUSE = "Mus musculus"


def truthy(series):
    return series.astype(str).str.lower().eq("true")


def launch_set(datasets):
    comparative = datasets[truthy(datasets.comparative_design)]
    human = comparative[comparative.organism.astype(str).str.contains("human", case=False)]
    counted = human[truthy(human.counted_in_coverage)]
    keep = counted[~counted.accession.isin(EXCLUDED + list(DEFERRED))]
    return keep.copy()


NO_RANKING = {
    "single arm, no within-dataset contrast",
    "no two arms with 2 or more samples, no differential-expression test",
    "1 donor per arm, the contrast is not replicated across individuals",
}


def pipeline_role(blocker: str) -> str:
    """Ranked datasets feed Phase 3; the rest are ingested for coverage and Phase 7."""
    if blocker == "ready":
        return "ranked"
    if all(part.strip() in NO_RANKING for part in blocker.split(";")):
        return "ingested_no_ranking"
    return "not_ready"


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
        and row["override_arms"] == 0
    ):
        found.append("no contrast derivable from labels")
    # A stated contrast needs per-sample arms, unless the frozen Phase 1a labels already
    # split the samples into two sides (case vs control), which the ingestion step reads.
    if (row["stated_contrast"] and row["override_arm_rows"] == 0 and row["non_geo_label_rows"] == 0
            and row["distinct_labels_in_scope"] <= 1):
        found.append("stated contrast has no per-sample arm assignment")
    # Arms are recorded, but one arm cannot be contrasted, and a contrast needs two
    # arms of at least two samples. A singleton arm inside a larger series (e.g. one
    # cellular neurofibroma in a progression series) drops out of the test, it does
    # not block the dataset.
    if row["override_arms"] == 1:
        found.append("single arm, no within-dataset contrast")
    elif row["override_arms"] > 1 and row["arms_with_n_ge_2"] < 2:
        found.append("no two arms with 2 or more samples, no differential-expression test")
    elif row["min_arm_donors"] == 1 and row["override_arms"] > 1:  # only set where donors are recorded
        found.append("1 donor per arm, the contrast is not replicated across individuals")
    if row["mouse_untagged"]:
        found.append(f"{row['mouse_untagged']} mouse samples need a deferral tag")
    # processed_matrix_only is no longer a blocker: the policy (accept the authors'
    # normalization, record it in the manifest, never silently rescale) was recorded on
    # 2026-10-21 and is in phase2-pipeline-spec.md.
    # A targeted panel is no longer a blocker: the normalization route and the gene-space
    # handling were ruled on 2026-10-20 and are in phase2-pipeline-spec.md. The column stays
    # so the dataset is never silently handed the genome-wide array route.
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
        # de_arm: which side of the contrast a kept sample sits on. Absent on rows
        # written before the column existed, so treat blanks as "no arm recorded".
        non_geo_here = non_geo[non_geo.series == accession]
        if len(non_geo_here) and dataset.source == "ArrayExpress":
            kept_rows = non_geo_here[truthy(non_geo_here.use_in_phase2)]
        else:
            kept_rows = kept_here
        arms = (kept_rows["de_arm"].replace("", pd.NA).dropna()
                if "de_arm" in kept_rows.columns else pd.Series(dtype=object))
        # The unit of inference is the donor where one is recorded, not the array or well:
        # E-MEXP-258 has 16 channels from 2 donors, GSE292071 104 plates from 16 patients.
        if "patient_id" in kept_rows.columns and kept_rows["patient_id"].replace("", pd.NA).notna().any():
            donors = kept_rows.assign(_arm=kept_rows["de_arm"]).groupby("_arm")["patient_id"].nunique()
        else:
            # No donor column for this dataset: the per-arm donor count is unknown, which is
            # not the same as small. The ingestion step extracts patient ids per the spec.
            donors = pd.Series(dtype=int)
        # Dataset-level assay_class can disagree with what the samples actually are:
        # GSE239561 is recorded as an expression array but every sample is a NanoString
        # panel, which needs a different normalization route and a smaller gene space.
        assay_mix = mine.sample_assay.value_counts() if "sample_assay" in samples.columns else pd.Series(dtype=int)
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
                "mouse_untagged": int(sum(1 for g in mine.loc[mine.organism == MOUSE, "gsm"]
                                          if g not in set(overrides.loc[overrides.series == accession, "sample_id"]))),
                "distinct_labels_in_scope": int(mine.label.nunique()),
                "override_rows": int((overrides.series == accession).sum()),
                "override_cases_kept": int((kept_here.de_role == "case").sum()),
                "override_controls_kept": int((kept_here.de_role == "control").sum()),
                "override_arm_rows": int(arms.notna().sum()),
                "override_arms": int(arms.nunique()),
                "min_arm_n": int(arms.value_counts().min()) if len(arms) else 0,
                "arms_with_n_ge_2": int((arms.value_counts() >= 2).sum()),
                "min_arm_donors": int(donors.min()) if len(donors) else 0,
                "non_geo_label_rows": int((non_geo.series == accession).sum()),
                "sample_assay": ";".join(f"{k}:{v}" for k, v in assay_mix.items()),
                "targeted_panel": bool(len(assay_mix) and assay_mix.idxmax() == "expression_panel_targeted"),
                "preflight_decision": decision.get("decision", ""),
                "stated_contrast": decision.get("contrast", ""),
            }
        )

    readiness = pd.DataFrame(rows)
    readiness["blocker"] = readiness.apply(blockers, axis=1)
    readiness["pipeline_role"] = readiness.blocker.map(pipeline_role)
    readiness.to_csv(OUT, index=False)

    roles = readiness.pipeline_role.value_counts()
    print(f"{len(readiness)} datasets in the launch set: {roles.get('ranked', 0)} ranked, "
          f"{roles.get('ingested_no_ranking', 0)} ingested without a ranking, "
          f"{roles.get('not_ready', 0)} not ready")
    for acc, why in sorted(DEFERRED.items()):
        print(f"  deferred: {acc} - {why}")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
