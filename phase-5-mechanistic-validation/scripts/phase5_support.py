#!/usr/bin/env python3
"""Phase 5, synthesis: join Monarch and DisMech evidence onto the Phase 4
dossier rows, record what each source could have said, and order candidates
within their disease x manifestation stratum.

This phase does NOT produce the composite confidence score - that is Phase 6's
rubric. What it produces is a mechanistic-support tier from Phase 5 evidence
alone, plus a coverage field, so Phase 6 can combine it with the Phase 4
dossier without having to re-derive what was or was not checkable.

Tiers, per candidate row:
  A_mechanism   gene named in a DisMech mechanism node or genetic section for
                this stratum, or a Monarch causal edge to the stratum's disease.
                The Monarch half never fires - see DISEASE_TERMS below - so in
                practice this tier is DisMech mechanism-node membership
  B_phenotype   gene-to-HPO edge to a MANIFESTATION-specific HPO term (see
                phase5_hpo_map.py). Terms tagged non_specific in that map, such
                as Scoliosis at 119 candidate genes, are excluded: matching a
                pleiotropic term is not evidence about an NF target
  C_other_only  gene resolved and has Monarch edges, none matching this stratum
  D_no_edges    gene resolved, no causal-disease or phenotype edges at all
  unassessed    symbol did not resolve to an HGNC CURIE - absence of evidence
                here is absence of a lookup, not a negative finding

Usage:
  python phase5_support.py --builddir build/phase5 --datadir <phase>/data
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

# Specificity tags from the HPO map that are allowed to carry B_phenotype.
TIERED_SPECIFICITY = {"specific", "moderate"}
# Monarch disease terms that count as "this stratum's disease" for tier A.
#
# STRUCTURALLY VACUOUS, and kept deliberately. Monarch's
# CausalGeneToDiseaseAssociation edges are Mendelian gene-disease assertions, so
# for an NF disease term the only subjects are the causative germline genes -
# NF1, NF2, SMARCB1, LZTR1, SPRED1 - which are exactly the genes the Phase 1b
# driver rule removes from the candidate list. Verified against the live API:
# each NF Mondo term has 2 causal edges naming 1 gene, the broader
# GeneToDiseaseAssociation category is unpopulated, and the overlap with the
# candidate set is 0. So monarch_disease_terms is empty for all 3,752 rows and
# tier A is in practice DisMech mechanism-node membership alone.
#
# The clause stays because it costs nothing and will start firing if Monarch
# ever ingests non-causal gene-disease associations. The count is written to
# provenance so a future run notices when it stops being zero. What it must NOT
# do is let a reader infer that Monarch looked for disease-level support and
# found none: Monarch cannot express that support for a non-driver gene at all.
DISEASE_TERMS = {
    "NF1": {"MONDO:0018975", "MONDO:0021061", "MONDO:0008078", "MONDO:0011035"},
    "NF2-SWN": {"MONDO:0007039", "MONDO:0859764", "MONDO:1030016"},
    "SWN": {"MONDO:0008075", "MONDO:0024517", "MONDO:0014299", "MONDO:1030016", "MONDO:0859765"},
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--builddir", default="build/phase5")
    ap.add_argument("--datadir", default="phase-5-mechanistic-validation/data")
    args = ap.parse_args()
    build, data = Path(args.builddir), Path(args.datadir)

    dossier = pd.read_csv(build / "phase4-target-dossier.csv")
    assoc = pd.read_csv(data / "phase5-monarch-associations.csv.gz")
    overlap = pd.read_csv(data / "phase5-dismech-gene-overlap.csv")
    mech = pd.read_csv(data / "phase5-dismech-mechanisms.csv")
    profiles = json.load(open(build / "phase5-disease-profiles.json"))
    hpo_map = pd.read_csv(data / "phase5-manifestation-hpo-map.csv")
    tiered = hpo_map[hpo_map.specificity.isin(TIERED_SPECIFICITY)]
    man_hpo = tiered.groupby("manifestation").hpo_id.apply(set).to_dict()
    man_hpo_all = hpo_map.groupby("manifestation").hpo_id.apply(set).to_dict()
    curies = {}
    for line in (build / "phase5-gene-curies.jsonl").open():
        rec = json.loads(line)
        curies[rec["symbol"]] = rec.get("curie")

    dis_edges = assoc[assoc.edge == "gene_to_disease"]
    phe_edges = assoc[assoc.edge == "gene_to_phenotype"]
    genes_with_dis = set(dis_edges.gene_symbol)
    genes_with_phe = set(phe_edges.gene_symbol)
    dis_by_gene = dis_edges.groupby("gene_symbol")["object_curie"].apply(set).to_dict()
    phe_by_gene = phe_edges.groupby("gene_symbol")["object_curie"].apply(set).to_dict()

    # Which sources could have spoken for a given stratum.
    roles = mech.groupby(["disease", "manifestation"])["entry_role"].apply(set).to_dict()

    rows = []
    for _, r in dossier.iterrows():
        sym, dis, man = r["gene_symbol"], r["disease"], r["manifestation"]
        curie = curies.get(sym)
        stratum_roles = roles.get((dis, man), set())
        dismech_direct = stratum_roles - {"cross_disease_borrow"}
        hit = overlap[(overlap.gene_symbol == sym) & (overlap.disease == dis)
                      & (overlap.manifestation == man)]
        dismech_entries = sorted(set(hit.entry))
        monarch_disease_hit = sorted(dis_by_gene.get(sym, set()) & DISEASE_TERMS.get(dis, set()))
        prof = set(profiles.get(dis, {}).get("hpo", []))
        gene_phe = phe_by_gene.get(sym, set())
        monarch_pheno_hit = sorted(gene_phe & man_hpo.get(man, set()))
        # reported, never tiered: the broad disease-profile overlap, which is
        # dominated by pleiotropic terms and overstates support if believed
        profile_hit = sorted(gene_phe & prof)
        nonspecific_hit = sorted(gene_phe & (man_hpo_all.get(man, set()) - man_hpo.get(man, set())))

        if not curie:
            tier = "unassessed"
        elif dismech_entries or monarch_disease_hit:
            tier = "A_mechanism"
        elif monarch_pheno_hit:
            tier = "B_phenotype"
        elif sym in genes_with_dis or sym in genes_with_phe:
            tier = "C_other_only"
        else:
            tier = "D_no_edges"

        rows.append({
            "gene_symbol": sym, "disease": dis, "manifestation": man,
            "gene_curie": curie,
            "phase5_support_tier": tier,
            "dismech_entries": "|".join(dismech_entries),
            "monarch_disease_terms": "|".join(monarch_disease_hit),
            "n_manifestation_hpo_matches": len(monarch_pheno_hit),
            "manifestation_hpo_terms": "|".join(monarch_pheno_hit),
            "n_nonspecific_manifestation_hpo_matches": len(nonspecific_hit),
            "n_disease_profile_hpo_matches": len(profile_hit),
            "n_monarch_disease_edges": len(dis_by_gene.get(sym, set())),
            "n_monarch_phenotype_edges": len(phe_by_gene.get(sym, set())),
            # coverage: what COULD have spoken here, independent of what did
            "coverage_monarch": "yes" if curie else "symbol_unresolved",
            # every entry role serving this stratum, so a reader can see when a
            # manifestation is covered only by a shared, approximate or
            # borrowed entry rather than one of its own
            "coverage_dismech": "+".join(sorted(stratum_roles)) or "none",
            "dismech_direct_entry": bool(dismech_direct),
            "expr_best_rank_in_stratum": r.get("expr_best_rank_in_stratum"),
            "in_expression": r.get("in_expression"), "in_literature": r.get("in_literature"),
        })

    sup = pd.DataFrame(rows)
    order = {"A_mechanism": 0, "B_phenotype": 1, "C_other_only": 2, "D_no_edges": 3, "unassessed": 4}
    sup["_t"] = sup.phase5_support_tier.map(order)
    sup["_e"] = pd.to_numeric(sup.expr_best_rank_in_stratum, errors="coerce").fillna(10**6)
    sup = sup.sort_values(["disease", "manifestation", "_t", "_e", "gene_symbol"])
    sup["phase5_rank_in_stratum"] = sup.groupby(["disease", "manifestation"]).cumcount() + 1
    sup = sup.drop(columns=["_t", "_e"])
    sup.to_csv(data / "phase5-target-support.csv", index=False)

    tiers = sup.groupby(["disease", "manifestation"]).phase5_support_tier.value_counts().unstack(fill_value=0)
    tiers.to_csv(data / "phase5-support-by-stratum.csv")
    json.dump({"rows": len(sup),
               # these columns hold "" (not NaN) in memory, so count non-empty
               "rows_with_monarch_disease_term": int((sup.monarch_disease_terms.fillna("") != "").sum()),
               "rows_with_dismech_entry": int((sup.dismech_entries.fillna("") != "").sum()),
               "rows_with_manifestation_hpo_term": int((sup.manifestation_hpo_terms.fillna("") != "").sum()),
               "note": "rows_with_monarch_disease_term is expected to be 0: Monarch's causal "
                       "gene-disease edges name only the germline NF genes, which the Phase 1b "
                       "driver rule excludes. If it is ever non-zero, Monarch has gained "
                       "non-causal gene-disease edges and tier A should be revisited."},
              open(data / "phase5-support-column-coverage.json", "w"), indent=2)
    print(tiers.to_string())
    print("\nrows:", len(sup), "| tier totals:", sup.phase5_support_tier.value_counts().to_dict())


if __name__ == "__main__":
    main()
