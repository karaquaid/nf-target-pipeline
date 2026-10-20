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
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
