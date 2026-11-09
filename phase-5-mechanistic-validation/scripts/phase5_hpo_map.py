#!/usr/bin/env python3
"""Phase 5: map each manifestation label to manifestation-specific HPO terms.

Why this exists. The first cut of the phenotype-support flag asked whether a
candidate gene shared ANY HPO term with the stratum disease's full phenotype
profile. That flagged 981 of 3,752 rows, and the matches were dominated by
pleiotropic terms - Seizure (245 rows), Global developmental delay (217),
Intellectual disability (215), Hypertelorism (214). Hundreds of Mendelian genes
carry those, so the match says nothing about the gene as an NF target. The flag
is therefore scoped to HPO terms that name the manifestation itself.

Term selection: each manifestation's candidate terms come from Monarch
/search with category=biolink:PhenotypicFeature, filtered to HP: CURIEs whose
label contains the query string, then hand-curated to drop body-site variants
that are not the manifestation (eyelid/jaw/forefoot pain) and, for
non-vestibular schwannoma, to drop the vestibular terms. The curated lists are
the CURATED constant below - they are a judgement call, recorded here so the
judgement is reviewable rather than buried in a notebook.

Each term carries the number of candidate genes in the Phase 5 association set
that are annotated to it, so a reader can see a term's breadth. Terms tagged
`non_specific` (>50 candidate genes, e.g. Scoliosis at 119) are kept in the map
for transparency but excluded from the support tier by phase5_support.py.

Usage:
  python phase5_hpo_map.py --builddir build/phase5 --datadir <phase>/data
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from monarch_client import Monarch  # noqa: E402

# manifestation -> search strings used against Monarch
QUERIES = {
    "Malignant peripheral nerve sheath tumor (MPNST)": ["malignant peripheral nerve sheath tumor"],
    "Plexiform neurofibroma": ["plexiform neurofibroma"],
    "Cutaneous neurofibroma": ["cutaneous neurofibroma", "subcutaneous neurofibroma", "neurofibroma"],
    "ANNUBP / atypical neurofibroma": ["atypical neurofibroma", "neurofibroma"],
    "Optic pathway glioma": ["optic nerve glioma", "optic pathway glioma"],
    "Bone defects": ["tibial pseudarthrosis", "sphenoid wing dysplasia",
                     "bowing of the long bones", "scoliosis"],
    "Vestibular schwannoma": ["vestibular schwannoma"],
    "Non-vestibular schwannoma": ["schwannoma", "peripheral schwannoma"],
    "Pain": ["neuropathic pain", "chronic pain", "pain"],
}

# Hand-curated keep-lists, resolved from the searches above.
CURATED = {
    "Malignant peripheral nerve sheath tumor (MPNST)": ["HP:0100697"],
    "Plexiform neurofibroma": ["HP:0009732"],
    "Cutaneous neurofibroma": ["HP:0100698", "HP:0001067"],
    "ANNUBP / atypical neurofibroma": ["HP:0007524", "HP:0001067"],
    "Optic pathway glioma": ["HP:0009734"],
    "Bone defects": ["HP:0009736", "HP:6001124", "HP:0006487", "HP:0002650"],
    "Vestibular schwannoma": ["HP:0009588", "HP:0009589", "HP:0009590"],
    # vestibular terms deliberately excluded here
    "Non-vestibular schwannoma": ["HP:0100008", "HP:0009593", "HP:0025604", "HP:0100011"],
    # body-site-specific pains deliberately excluded
    "Pain": ["HP:0012531", "HP:0012532", "HP:6000040"],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--builddir", default="build/phase5")
    ap.add_argument("--datadir", default="phase-5-mechanistic-validation/data")
    args = ap.parse_args()
    build, data = Path(args.builddir), Path(args.datadir)

    m = Monarch()
    labels: dict[str, str] = {}
    for man, qs in QUERIES.items():
        for q in qs:
            for h in m.search(q, "biolink:PhenotypicFeature", limit=10):
                if h["id"].startswith("HP:") and q.lower() in h["name"].lower():
                    labels[h["id"]] = h["name"]

    assoc = pd.read_csv(data / "phase5-monarch-associations.csv.gz")
    phe = assoc[assoc.edge == "gene_to_phenotype"]
    breadth = phe.groupby("object_curie").gene_symbol.nunique().to_dict()
    fallback = dict(zip(assoc.object_curie, assoc.object_label))

    rows = []
    for man, terms in CURATED.items():
        for t in terms:
            rows.append({"manifestation": man, "hpo_id": t,
                         "hpo_label": labels.get(t) or fallback.get(t),
                         "n_candidate_genes_with_term": breadth.get(t, 0)})
    df = pd.DataFrame(rows)
    df["specificity"] = pd.cut(df.n_candidate_genes_with_term, [-1, 0, 10, 50, 10 ** 9],
                               labels=["absent_from_candidates", "specific", "moderate", "non_specific"])
    df.to_csv(data / "phase5-manifestation-hpo-map.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
