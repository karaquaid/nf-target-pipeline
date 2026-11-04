#!/usr/bin/env python3
"""Phase 3, step 1: label every Phase 2 contrast with disease, manifestation(s)
and the aggregation stratum it belongs to.

Phase 2 produced one ranked list file per dataset; a file may carry several
contrasts. Rank aggregation happens per stratum ("comparison_class"), so each
contrast needs three things recorded before any aggregation runs:

  disease            NF1 | NF2-SWN | SWN              (project labelling standard)
  manifestations     from the fixed 20-term vocabulary (project labelling standard)
  comparison_class   the stratum whose contrasts may be aggregated together

The disease and manifestation values are not re-derived here. They are taken
from the Phase 1a dataset-level label table and then narrowed to the arms that
the individual contrast actually compares, which is the only part this script
decides. Every narrowing is recorded in CONTRAST_LABELS with the arm names it
was read from, and the script fails if a narrowed manifestation is not among
the ones Phase 1a recorded for that dataset.

Inputs
  phase-2/data/phase2-ingestion-manifest.csv   effect_type, gene_space, arms
  phase-1a/data/phase1a-dataset-labels.csv     dataset-level disease/manifestation
  <ranked-lists dir>/<acc>_de.csv              the contrasts that actually exist

Output
  phase-3/data/phase3-contrast-labels.csv      one row per contrast
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd

# The fixed manifestation vocabulary from docs/project-plan.md. Applied as-is;
# no new terms, no rewording.
MANIFESTATIONS = [
    "Bone defects",
    "Cardiovascular issues",
    "Cognition / Behavioral / Learning",
    "Sleep",
    "Cutaneous neurofibroma",
    "Ependymoma",
    "Gastrointestinal stromal tumor (GIST)",
    "Hematologic malignancies",
    "High grade glioma",
    "Malignant peripheral nerve sheath tumor (MPNST)",
    "Meningioma",
    "Optic pathway glioma",
    "Non-optic LGG",
    "Pain",
    "Plexiform neurofibroma",
    "ANNUBP / atypical neurofibroma",
    "Pulmonary disease",
    "Non-vestibular schwannoma",
    "Vestibular schwannoma",
    "Other",
]
DISEASES = ["NF1", "NF2-SWN", "SWN"]

MPNST = "Malignant peripheral nerve sheath tumor (MPNST)"
PNF = "Plexiform neurofibroma"
CNF = "Cutaneous neurofibroma"
ANNUBP = "ANNUBP / atypical neurofibroma"
VS = "Vestibular schwannoma"
NVS = "Non-vestibular schwannoma"
OPG = "Optic pathway glioma"
BONE = "Bone defects"
PAIN = "Pain"

# One entry per (accession, contrast) that Phase 2 actually produced.
#   test_arm / reference_arm  the two arms, as named in the Phase 2 sample table
#   manifestations            narrowed from the Phase 1a dataset labels to the arms
#   comparison_class          the aggregation stratum
#   usable_for_candidates     False means the contrast is kept in the table for
#                             audit but contributes no candidates, with a reason
#   basis                     why this narrowing, in one line
CONTRAST_LABELS = {
    # -- NF1, malignant transformation: MPNST against a benign nerve sheath arm --
    ("E-TABM-69", "Malignant peripheral nerve sheath tumor (MPNST)_vs_Plexiform neurofibroma"): dict(
        disease="NF1", manifestations=[MPNST, PNF],
        test_arm="Malignant peripheral nerve sheath tumor (MPNST)", reference_arm="Plexiform neurofibroma",
        comparison_class="nf1_mpnst_vs_benign_pnst", usable_for_candidates=True,
        basis="Both arms are named manifestations of the dataset; the contrast compares them directly.",
    ),
    ("GSE145064", "mpnst_vs_plexiform_neurofibroma"): dict(
        disease="NF1", manifestations=[MPNST, PNF],
        test_arm="mpnst", reference_arm="plexiform_neurofibroma",
        comparison_class="nf1_mpnst_vs_benign_pnst", usable_for_candidates=True,
        basis="Both arms are named manifestations of the dataset; the contrast compares them directly.",
    ),
    ("GSE179043", "mpnst_vs_plexiform_neurofibroma"): dict(
        disease="NF1", manifestations=[MPNST, PNF],
        test_arm="mpnst", reference_arm="plexiform_neurofibroma",
        comparison_class="nf1_mpnst_vs_benign_pnst", usable_for_candidates=True,
        basis="Both arms are named manifestations of the dataset; the contrast compares them directly.",
    ),
    ("GSE318927", "mpnst_vs_plexiform_neurofibroma"): dict(
        disease="NF1", manifestations=[MPNST, PNF],
        test_arm="mpnst", reference_arm="plexiform_neurofibroma",
        comparison_class="nf1_mpnst_vs_benign_pnst", usable_for_candidates=True,
        basis="Both arms are named manifestations of the dataset; the contrast compares them directly.",
    ),
    ("GSE66743", "mpnst_vs_neurofibroma"): dict(
        disease="NF1", manifestations=[MPNST],
        test_arm="mpnst", reference_arm="neurofibroma",
        comparison_class="nf1_mpnst_vs_benign_pnst", usable_for_candidates=True,
        basis="MPNST is the only manifestation Phase 1a recorded for this dataset; the reference arm is "
              "neurofibroma of unstated subtype, so no neurofibroma manifestation is claimed.",
    ),
    ("GSE207400", "mpnst_g1_vs_benign_nf_g4"): dict(
        disease="NF1", manifestations=[MPNST],
        test_arm="mpnst_g1", reference_arm="benign_nf_g4",
        comparison_class="nf1_mpnst_vs_benign_pnst", usable_for_candidates=True,
        basis="Test arm is MPNST; the benign reference arm is neurofibroma of unstated subtype, which "
              "Phase 1a labelled Other for this dataset.",
    ),
    ("GSE207400", "mpnst_g2_vs_benign_nf_g4"): dict(
        disease="NF1", manifestations=[MPNST],
        test_arm="mpnst_g2", reference_arm="benign_nf_g4",
        comparison_class="nf1_mpnst_vs_benign_pnst", usable_for_candidates=True,
        basis="Second MPNST grade arm against the same benign reference.",
    ),
    ("GSE239561", "mpnst_high_grade_vs_pnf"): dict(
        disease="NF1", manifestations=[MPNST, PNF],
        test_arm="mpnst_high_grade", reference_arm="pnf",
        comparison_class="nf1_mpnst_vs_benign_pnst", usable_for_candidates=True,
        basis="Both arms are named manifestations of the dataset; targeted 770-gene panel space.",
    ),

    # -- NF1, premalignant: atypical neurofibroma against a benign arm --
    ("GSE207400", "premalignant_nf_g3_vs_benign_nf_g4"): dict(
        disease="NF1", manifestations=[ANNUBP],
        test_arm="premalignant_nf_g3", reference_arm="benign_nf_g4",
        comparison_class="nf1_atypical_vs_benign_pnst", usable_for_candidates=True,
        basis="The premalignant grade-3 arm is the ANNUBP / atypical neurofibroma manifestation "
              "Phase 1a recorded for this dataset.",
    ),
    ("GSE239561", "annubp_vs_pnf"): dict(
        disease="NF1", manifestations=[ANNUBP, PNF],
        test_arm="annubp", reference_arm="pnf",
        comparison_class="nf1_atypical_vs_benign_pnst", usable_for_candidates=True,
        basis="Both arms are named manifestations of the dataset; targeted 770-gene panel space.",
    ),
    ("GSE239561", "nf_with_atypia_vs_pnf"): dict(
        disease="NF1", manifestations=[ANNUBP, PNF],
        test_arm="nf_with_atypia", reference_arm="pnf",
        comparison_class="nf1_atypical_vs_benign_pnst", usable_for_candidates=True,
        basis="Neurofibroma with atypia sits in the ANNUBP / atypical neurofibroma term, which Phase 1a "
              "recorded for this dataset; targeted 770-gene panel space.",
    ),

    # -- NF1, benign subtype against plexiform neurofibroma --
    ("GSE239561", "nf_vs_pnf"): dict(
        disease="NF1", manifestations=[PNF],
        test_arm="nf", reference_arm="pnf",
        comparison_class="nf1_benign_subtype_vs_pnf", usable_for_candidates=True,
        basis="Reference arm is the plexiform neurofibroma manifestation; the test arm is neurofibroma of "
              "unstated subtype, so no second manifestation is claimed. Test arm n=2.",
    ),
    ("GSE239561", "cellular_nf_vs_pnf"): dict(
        disease="NF1", manifestations=[PNF],
        test_arm="cellular_nf", reference_arm="pnf",
        comparison_class="nf1_benign_subtype_vs_pnf", usable_for_candidates=False,
        basis="Reference arm is the plexiform neurofibroma manifestation. Test arm has a single sample, "
              "so the contrast carries no within-arm variance and is excluded from candidate generation.",
    ),

    # -- NF1, tumour against normal nerve or normal skin --
    ("GSE14038", "nf_case_vs_control"): dict(
        disease="NF1", manifestations=[PNF, CNF, MPNST],
        test_arm="nf_case", reference_arm="control",
        comparison_class="nf1_pnst_vs_normal", usable_for_candidates=True,
        basis="The case arm pools every nerve sheath lesion in the series, so all three manifestations "
              "Phase 1a recorded for this dataset apply to the contrast.",
    ),
    ("GSE41747", "mpnst_vs_normal_nerve"): dict(
        disease="NF1", manifestations=[MPNST],
        test_arm="mpnst", reference_arm="normal_nerve",
        comparison_class="nf1_pnst_vs_normal", usable_for_candidates=True,
        basis="Test arm is MPNST alone; reference arm is normal human nerve.",
    ),
    ("GSE41747", "neurofibroma_vs_normal_nerve"): dict(
        disease="NF1", manifestations=[PNF, CNF],
        test_arm="neurofibroma", reference_arm="normal_nerve",
        comparison_class="nf1_pnst_vs_normal", usable_for_candidates=True,
        basis="The neurofibroma arm covers the plexiform and cutaneous manifestations Phase 1a recorded "
              "for this dataset; reference arm is normal human nerve.",
    ),

    # -- NF2-SWN, schwannoma against normal nerve --
    ("GSE108524", "nf_case_vs_control"): dict(
        disease="NF2-SWN", manifestations=[VS],
        test_arm="nf_case", reference_arm="control",
        comparison_class="nf2swn_schwannoma_vs_normal", usable_for_candidates=True,
        basis="Vestibular schwannoma is the only manifestation Phase 1a recorded for this dataset.",
    ),
    ("GSE141801", "nf_case_vs_control"): dict(
        disease="NF2-SWN", manifestations=[VS],
        test_arm="nf_case", reference_arm="control",
        comparison_class="nf2swn_schwannoma_vs_normal", usable_for_candidates=True,
        basis="Vestibular schwannoma is the only manifestation Phase 1a recorded for this dataset.",
    ),
    ("GSE141801", "treated_vs_control"): dict(
        disease="NF2-SWN", manifestations=[VS],
        test_arm="treated", reference_arm="control",
        comparison_class="nf2swn_invitro_perturbation", usable_for_candidates=False,
        basis="This contrast compares a treated arm against the control arm, so it measures response to a "
              "perturbation rather than the disease state. Kept for audit; contributes no candidates.",
    ),

    # -- NF2-SWN, painful against non-painful schwannoma --
    ("GSE138347", "painful_vs_non_painful"): dict(
        disease="NF2-SWN", manifestations=[PAIN, VS, NVS],
        test_arm="painful", reference_arm="non_painful",
        comparison_class="nf2swn_painful_vs_non_painful_schwannoma", usable_for_candidates=True,
        basis="The contrast is on the pain state; both schwannoma site manifestations Phase 1a recorded "
              "for this dataset are present in both arms.",
    ),

    # -- NF1, glioma against non-neoplastic brain --
    ("GSE163071", "nf1_pilocytic_astrocytoma_vs_non_neoplastic_brain"): dict(
        disease="NF1", manifestations=[OPG],
        test_arm="nf1_pilocytic_astrocytoma", reference_arm="non_neoplastic_brain",
        comparison_class="nf1_glioma_vs_normal_brain", usable_for_candidates=True,
        basis="Optic pathway glioma is the only manifestation Phase 1a recorded for this dataset.",
    ),

    # -- NF1, bone --
    ("GSE232516", "nf_case_vs_control"): dict(
        disease="NF1", manifestations=[BONE],
        test_arm="nf_case", reference_arm="control",
        comparison_class="nf1_bone_vs_normal", usable_for_candidates=True,
        basis="Pseudarthrosis periosteum against iliac-crest periosteum from the same patients, so the "
              "reference arm is unaffected tissue at a different site rather than a healthy donor. Two "
              "samples per arm.",
    ),
    ("GSE234071", "nf_case_vs_control"): dict(
        disease="NF1", manifestations=[BONE],
        test_arm="nf_case", reference_arm="control",
        comparison_class="nf1_bone_vs_normal", usable_for_candidates=True,
        basis="Bone defects is the only manifestation Phase 1a recorded for this dataset. Two samples per arm.",
    ),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".", help="repo root")
    ap.add_argument("--ranked-dir", required=True, help="directory of Phase 2 <acc>_de.csv files")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    repo = Path(args.repo)
    ranked = Path(args.ranked_dir)
    out = Path(args.out) if args.out else repo / "phase-3/data/phase3-contrast-labels.csv"

    manifest = pd.read_csv(repo / "phase-2/data/phase2-ingestion-manifest.csv")
    labels1a = pd.read_csv(repo / "phase-1a/data/phase1a-dataset-labels.csv")

    # The contrasts that actually exist on disk, read from the ranked lists.
    found = set()
    for acc, de_file in manifest.loc[manifest.de_file.notna(), ["accession", "de_file"]].itertuples(index=False):
        path = ranked / de_file
        if not path.exists():
            print(f"FAIL missing ranked list: {path}", file=sys.stderr)
            return 1
        for contrast in pd.read_csv(path, usecols=["contrast"])["contrast"].unique():
            found.add((acc, contrast))

    declared = set(CONTRAST_LABELS)
    if found != declared:
        for k in sorted(found - declared):
            print(f"FAIL contrast on disk with no label entry: {k}", file=sys.stderr)
        for k in sorted(declared - found):
            print(f"FAIL label entry for a contrast not on disk: {k}", file=sys.stderr)
        return 1

    mf = manifest.set_index("accession")
    rows = []
    for (acc, contrast), spec in sorted(CONTRAST_LABELS.items()):
        if spec["disease"] not in DISEASES:
            print(f"FAIL {acc}/{contrast}: disease {spec['disease']!r} off vocabulary", file=sys.stderr)
            return 1
        allowed = set(labels1a.loc[labels1a.accession == acc, "manifestation"])
        for man in spec["manifestations"]:
            if man not in MANIFESTATIONS:
                print(f"FAIL {acc}/{contrast}: manifestation {man!r} off vocabulary", file=sys.stderr)
                return 1
            if man not in allowed:
                print(f"FAIL {acc}/{contrast}: manifestation {man!r} not recorded for this dataset in "
                      f"Phase 1a (recorded: {sorted(allowed)})", file=sys.stderr)
                return 1
        row = mf.loc[acc]
        arms = dict(part.split(":") for part in str(row.n_per_arm).split(";"))
        rows.append({
            "accession": acc,
            "contrast": contrast,
            "disease": spec["disease"],
            "manifestations": "|".join(spec["manifestations"]),
            "comparison_class": spec["comparison_class"],
            "effect_type": row.effect_type,
            "gene_space": row.gene_space,
            "test_arm": spec["test_arm"],
            "reference_arm": spec["reference_arm"],
            "n_test": int(arms.get(spec["test_arm"], 0)),
            "n_reference": int(arms.get(spec["reference_arm"], 0)),
            "assay_class": row.assay_class,
            "engine": row.engine,
            "usable_for_candidates": spec["usable_for_candidates"],
            "basis": spec["basis"],
        })

    out.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out, index=False, quoting=csv.QUOTE_MINIMAL)

    # A comparison_class must not mix effect types: the project plan forbids pooling a
    # disease-vs-normal reading with a between-state reading into one ranking.
    mixed = df.groupby("comparison_class")["effect_type"].nunique()
    if (mixed > 1).any():
        print(f"FAIL comparison_class mixes effect types: {list(mixed[mixed > 1].index)}", file=sys.stderr)
        return 1

    usable = df[df.usable_for_candidates]
    print(f"wrote {out} with {len(df)} contrasts over {df.accession.nunique()} datasets")
    print(f"  usable for candidates: {len(usable)} contrasts, {usable.accession.nunique()} datasets")
    for cls, g in usable.groupby("comparison_class"):
        print(f"  {cls:<48} {g.accession.nunique()} datasets, {len(g)} contrasts, {g.effect_type.iloc[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
