"""Check every de_arm value against the contrast recorded for that dataset.

The arms in phase2-sample-overrides.csv are derived by parsing record fields (disease state,
tumor type, sample title, or a supplementary table quoted in the row's reason). The contrast
each dataset is supposed to enter Phase 2 with is recorded separately, in the decisions block
of phase2-review-diagnosis.json. Those two can drift apart, so this script compares them:

* every arm label must be expressible in the words of the stated contrast, after punctuation
  is normalized away and compound phrases are split into tokens ("non-neoplastic brain" and
  "non_neoplastic_brain" match; "plexiform/benign neurofibroma" covers "plexiform_neurofibroma")
* where the arm label and the contrast use genuinely different vocabulary, the mapping is
  declared in ARM_SYNONYMS below rather than inferred
* where the contrast states arm sizes as "(n)", those must equal the arm sizes on disk

A second pass asks a different question: can the arm be recovered from the evidence recorded
beside it? For each dataset it looks for an annotation key, or the title, whose value decides
the arm. A dataset where nothing decides it has labels that cannot be reproduced from the row
they sit on. This is what caught GSE179043, where four samples annotated "tissue: MPNST" and
titled MPNST-2-nnn were carried in the plexiform_neurofibroma arm: the contrast check passed
because both arms belong to the stated contrast, and only the evidence check saw the clash.

Exits non-zero if any dataset fails, so it can gate a commit. Run from the repo root:
    python phase-2/scripts/phase2_verify_arms.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OVERRIDES = ROOT / "phase-2" / "data" / "phase2-sample-overrides.csv"
DIAGNOSIS = ROOT / "phase-2" / "data" / "phase2-review-diagnosis.json"

# de_arm label -> the phrase the stated contrast uses for it. Only needed where the two use
# different words; everything else matches on its own tokens.
ARM_SYNONYMS = {
    "GSE207400": {"mpnst_g1": "MPNST", "mpnst_g2": "MPNST",
                  "premalignant_nf_g3": "atypical neurofibroma", "benign_nf_g4": "neurofibroma"},
    "GSE292071": {"nf2_swn": "NF2-related schwannomatosis", "swn": "non-NF2-related schwannomatosis"},
    "GSE138347": {"painful": "painful", "non_painful": "non-painful"},
    "GSE239561": {"nf": "NF", "cellular_nf": "cellular NF", "nf_with_atypia": "NF with atypia",
                  "annubp": "ANNUBP", "pnf": "PNF", "mpnst_high_grade": "high-grade MPNST"},
    "GSE218493": {"cutaneous_neurofibroma": "cutaneous", "plexiform_neurofibroma": "plexiform neurofibroma"},
    "GSE232528": {"nf2_meningioma": "NF2-patient meningiomas"},
    "GSE344687": {"nf2_vestibular_schwannoma": "NF2-associated vestibular schwannoma"},
}


def tokens(text: str) -> set[str]:
    return set(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


def annotation_pairs(annotation: str) -> dict[str, str]:
    """Record fields as key/value, from either "key: value | key: value" or "key=value; ..."."""
    out = {}
    for part in re.split(r"\s*\|\s*|;\s*", str(annotation)):
        hit = re.match(r"\s*([^=:]+?)\s*[=:]\s*(.*)", part)
        if hit:
            out[hit.group(1).strip().lower()] = hit.group(2).strip().lower()
    return out


def determining_fields(group: pd.DataFrame) -> list[str]:
    """Which recorded fields decide the arm: a field whose value is constant within an arm,
    never shared between arms, and present on every row."""
    parsed = group.annotation.map(annotation_pairs)
    found = []
    for key in sorted(set().union(*parsed) if len(parsed) else set()):
        values = parsed.map(lambda fields: fields.get(key))
        if values.isna().any():
            continue
        pair = pd.DataFrame({"value": values.values, "arm": group.de_arm.values})
        if pair.groupby("value").arm.nunique().max() == 1 and pair.value.nunique() >= group.de_arm.nunique():
            found.append(key)
    titles = group.title.astype(str).str.lower()
    if titles.nunique() == len(group) and len(group) > 1:
        prefix = titles.str.replace(r"[^a-z]+.*$", "", regex=True)
        if prefix.nunique() > 1 and pd.crosstab(prefix, group.de_arm).gt(0).sum(axis=1).max() == 1:
            found.append("title")
    return found


def check_evidence(kept: pd.DataFrame, decisions: dict) -> None:
    print("\n[verify] can each arm be recovered from the evidence recorded beside it?")
    for accession, group in kept.groupby("series"):
        if group.de_arm.nunique() < 2:
            continue
        fields = determining_fields(group)
        if fields:
            print(f"ok   {accession}: arm follows from {', '.join(fields)}")
        elif decisions.get(accession, {}).get("label_provenance_note"):
            print(f"note {accession}: no recorded field decides the arm; the decisions block says "
                  f"where the split comes from")
        else:
            print(f"WARN {accession}: no recorded field or title decides the arm. Either the arms "
                  f"were read from something not written down, or a row contradicts its own "
                  f"annotation. Record the provenance in the decisions block or fix the row")


def main() -> int:
    overrides = pd.read_csv(OVERRIDES, keep_default_na=False)
    decisions = json.loads(DIAGNOSIS.read_text())["decisions"]
    kept = overrides[(overrides.use_in_phase2.astype(str) == "True") & (overrides.de_arm != "")]

    failures = []
    for accession, group in kept.groupby("series"):
        arms = group.de_arm.value_counts()
        decision = decisions.get(accession)
        if not decision or not decision.get("contrast"):
            failures.append(f"{accession}: arms recorded but no contrast in the decisions block")
            continue
        contrast = decision["contrast"]
        contrast_tokens = tokens(contrast) | tokens(decision.get("implementation", ""))
        problems = []
        for arm in arms.index:
            phrase = ARM_SYNONYMS.get(accession, {}).get(arm, arm.replace("_", " "))
            missing = tokens(phrase) - contrast_tokens
            if missing:
                problems.append(f"arm {arm!r} has no counterpart in the contrast (missing {sorted(missing)})")
        stated = [int(n) for n in re.findall(r"\((\d+)\)", contrast)]
        if stated and sorted(stated) != sorted(arms.tolist()):
            problems.append(f"contrast states arm sizes {sorted(stated)}, overrides give {sorted(arms.tolist())}")
        status = "ok" if not problems else "FAIL"
        print(f"{status:4} {accession}: {dict(arms)}")
        if problems:
            for p in problems:
                print(f"       {p}")
            failures.append(accession)
    print(f"[verify] {len(kept.series.unique()) - len(failures)} of {len(kept.series.unique())} "
          f"datasets with arms agree with their recorded contrast")
    check_evidence(kept, decisions)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
