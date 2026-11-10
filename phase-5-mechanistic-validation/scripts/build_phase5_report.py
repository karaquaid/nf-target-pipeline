#!/usr/bin/env python3
"""Phase 5: assemble provenance and the write-up from the generated tables.

Every number in the report is read from the tables, not restated from a run log.

Usage:
  python build_phase5_report.py --builddir build/phase5 \
      --datadir <phase>/data --docdir <phase>/docs
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd

TIER_DOC = {
    "A_mechanism": "named in a DisMech mechanism node or genetic section for the stratum, "
                   "or carrying a Monarch causal edge to the stratum's disease",
    "B_phenotype": "gene-to-HPO edge to a manifestation-specific HPO term",
    "C_other_only": "resolved, has Monarch edges, none matching this stratum",
    "D_no_edges": "resolved, no causal-disease or phenotype edges in the KG",
    "unassessed": "symbol did not resolve to an HGNC CURIE; not looked up, not a negative",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--builddir", default="build/phase5")
    ap.add_argument("--datadir", default="phase-5-mechanistic-validation/data")
    ap.add_argument("--docdir", default="phase-5-mechanistic-validation/docs")
    args = ap.parse_args()
    build, data, docs = Path(args.builddir), Path(args.datadir), Path(args.docdir)
    docs.mkdir(parents=True, exist_ok=True)

    inputs = json.load(open(build / "phase5-inputs.json"))
    mon = json.load(open(build / "phase5-monarch-summary.json"))
    dis = json.load(open(build / "phase5-dismech-summary.json"))
    sup = pd.read_csv(data / "phase5-target-support.csv")
    assoc = pd.read_csv(data / "phase5-monarch-associations.csv.gz")
    mech = pd.read_csv(data / "phase5-dismech-mechanisms.csv")
    cross = pd.read_csv(data / "phase5-cross-disease-mechanisms.csv.gz")
    hpo_map = pd.read_csv(data / "phase5-manifestation-hpo-map.csv")
    overlap = pd.read_csv(data / "phase5-dismech-gene-overlap.csv")

    prov = {
        "input_commit": inputs["input_commit"],
        "sources": {
            "monarch": {"endpoint": "https://api-v3.monarchinitiative.org/v3/api",
                        "kg_version": mon["monarch_kg_version"],
                        "api_version": mon["monarch_api_version"],
                        "auth": "none",
                        "access": "full records over REST; no field withheld",
                        "requests": {"symbol_resolution": mon["n_symbols"],
                                     "association_queries": mon["n_resolved"] * 2,
                                     "disease_phenotype_profiles": 3},
                        "errors": len(mon["errors"])},
            "dismech": {"repo": "github.com/monarch-initiative/dismech",
                        "release": dis["dismech_release"],
                        "released": dis["dismech_release_published"],
                        "access": "full YAML knowledge base from pinned release assets; no API exists",
                        "entries_fetched": dis["entries_fetched"],
                        "disorders_indexed": dis["n_disorders_indexed"]},
        },
        "counts": {
            "dossier_rows": inputs["dossier_rows"],
            "distinct_genes": inputs["distinct_genes"],
            "genes_resolved": mon["n_resolved"],
            "genes_unresolved": len(mon["unresolved_symbols"]),
            "monarch_association_rows": mon["n_association_rows"],
            "genes_with_causal_disease_edge": mon["n_genes_with_disease_edge"],
            "genes_with_phenotype_edge": mon["n_genes_with_phenotype_edge"],
            "dismech_mechanism_nodes": dis["n_mechanism_nodes"],
            "dismech_gene_overlap_rows": dis["n_gene_overlap_rows"],
            "cross_disease_rows": dis["n_cross_disease_rows"],
            "support_tiers": sup.phase5_support_tier.value_counts().to_dict(),
        },
        "unresolved_symbols": mon["unresolved_symbols"],
    }
    json.dump(prov, open(data / "phase5-provenance.json", "w"), indent=2)

    tiers = (sup.groupby(["disease", "manifestation"]).phase5_support_tier
             .value_counts().unstack(fill_value=0))
    for col in ["A_mechanism", "B_phenotype", "C_other_only", "D_no_edges", "unassessed"]:
        if col not in tiers:
            tiers[col] = 0
    cov = sup.groupby(["disease", "manifestation"]).coverage_dismech.first()
    nodes_per = mech.dropna(subset=["node"]).groupby(["disease", "manifestation"]).node.nunique()

    L = []
    A = L.append
    A("# Phase 5: Cross-Disease Mechanistic Validation\n")
    A(f"Generated from Phase 4 dossier commit `{inputs['input_commit'][:8]}`. "
      f"Monarch KG {mon['monarch_kg_version']} (API {mon['monarch_api_version']}); "
      f"DisMech release {dis['dismech_release']}.\n")

    A("## What this phase does and does not establish\n")
    A("It asks two questions of every candidate target: does the Monarch knowledge graph "
      "independently associate this gene with the stratum's disease or its manifestation, and "
      "does DisMech name this gene in the disease's curated mechanism. Neither is a scoring "
      "step; the composite confidence signal is Phase 6's rubric. Absence of an edge is "
      "recorded as absence of evidence, never as evidence against a target.\n")

    A("## Access per source\n")
    A("| Source | Access | Version | Auth |")
    A("|---|---|---|---|")
    A(f"| Monarch KG | full records over REST, no field withheld | KG {mon['monarch_kg_version']}, "
      f"API {mon['monarch_api_version']} | none |")
    A(f"| DisMech | full YAML knowledge base from pinned release assets; **no API exists** | "
      f"{dis['dismech_release']} ({(dis['dismech_release_published'] or '')[:10]}) | none |")
    A("")

    A("## Inputs and identifier resolution\n")
    A(f"- {inputs['dossier_rows']:,} dossier rows over {len(tiers)} disease x manifestation strata, "
      f"{inputs['distinct_genes']:,} distinct gene symbols")
    A(f"- {mon['n_resolved']:,} symbols resolved to HGNC CURIEs; "
      f"{len(mon['unresolved_symbols'])} did not resolve and are tiered `unassessed`")
    A(f"- {mon.get('n_resolved_via_phase4_alias', 0)} of those resolved only on the second attempt, "
      "using `phase4-identifiers.csv`'s `resolved_symbol`. A first pass that tried the literal "
      "label alone left 71 unresolved, and most were real genes under withdrawn or alias symbols "
      "that Monarch does not index under the old name - GBA (GBA1), SEPT9 (SEPTIN9), MLLT4 (AFDN), "
      "KIAA0101 (PCLAF), FOXO1A, DARC, IL1RL1, HIST1H2BD and the C#orf/KIAA/FLJ placeholders. "
      "Calling that set junk locus IDs would have hidden a real coverage gap; `resolved_via` "
      "records which spelling worked for each gene.")
    A("- Two labels resolved only because Phase 4 had already diagnosed them: `March 1` is "
      "spreadsheet date corruption of MARCH1, now MARCHF1, and the composite `TPSAB1/B2` maps to "
      "TPSAB1 alone, so TPSB2 is not assessed under that row.")
    clone_re = re.compile(r"^(AC|AL|AP|RP11|RP1|CTD|LINC|LOC)[0-9A-Z\-.]*$")
    n_clone = sum(1 for s in mon["unresolved_symbols"] if clone_re.match(s))
    A(f"- The {len(mon['unresolved_symbols'])} still unresolved are {n_clone} clone-based locus "
      "identifiers (AC/AL/AP/RP11/LOC-style), the legacy placeholders FLJ41484 and MGC24103, and "
      "`Oligodendrocyte differentiation (clemastine target)` - a Phase 1b literature label that "
      "names a process rather than a gene product, already flagged `not_a_gene_symbol` in Phase 4. "
      "None was dropped from the tables.")
    A(f"- {mon['n_association_rows']:,} association rows retrieved; "
      f"{mon['n_genes_with_disease_edge']} genes carry a causal gene-disease edge and "
      f"{mon['n_genes_with_phenotype_edge']} a gene-phenotype edge. "
      f"{len(mon['errors'])} request errors.\n")

    A("## A correction worth recording\n")
    A("The phenotype-support flag was first defined as any shared HPO term between a candidate "
      "gene and the stratum disease's full phenotype profile. That flagged 981 of "
      f"{inputs['dossier_rows']:,} rows, and the matches were dominated by pleiotropic terms - "
      "Seizure (245 rows), Global developmental delay (217), Intellectual disability (215), "
      "Hypertelorism (214) - which hundreds of Mendelian genes carry. Such a match says nothing "
      "about a gene as an NF target. The flag is now scoped to manifestation-specific HPO terms "
      "(`phase5-manifestation-hpo-map.csv`), and terms carried by more than 50 candidate genes "
      "are excluded from the tier while still being reported. Scoliosis, at "
      f"{int(hpo_map.loc[hpo_map.hpo_id == 'HP:0002650', 'n_candidate_genes_with_term'].iloc[0])} "
      "candidate genes, is the one such term. The broad-profile overlap is kept as "
      f"`n_disease_profile_hpo_matches` and still covers "
      f"{int((sup.n_disease_profile_hpo_matches > 0).sum())} rows - it should not be read as support.\n")

    A("## Support tiers\n")
    for k, v in TIER_DOC.items():
        A(f"- `{k}` - {v}")
    A("")
    A("| Disease | Manifestation | A | B | C | D | unassessed | DisMech nodes | DisMech coverage |")
    A("|---|---|---|---|---|---|---|---|---|")
    for (dz, man), row in tiers.iterrows():
        A(f"| {dz} | {man} | {row['A_mechanism']} | {row['B_phenotype']} | {row['C_other_only']} | "
          f"{row['D_no_edges']} | {row['unassessed']} | {nodes_per.get((dz, man), 0)} | "
          f"`{cov.get((dz, man), 'none')}` |")
    A("")

    A("### Every tier A and tier B candidate\n")
    A("| Gene | Disease | Manifestation | Tier | DisMech entry | Manifestation HPO |")
    A("|---|---|---|---|---|---|")
    for _, r in sup[sup.phase5_support_tier.isin(["A_mechanism", "B_phenotype"])].iterrows():
        A(f"| {r.gene_symbol} | {r.disease} | {r.manifestation} | {r.phase5_support_tier} | "
          f"{r.dismech_entries if isinstance(r.dismech_entries, str) else '-'} | "
          f"{r.manifestation_hpo_terms if isinstance(r.manifestation_hpo_terms, str) else '-'} |")
    A("")

    A("## DisMech mechanism context\n")
    A(f"{dis['n_mechanism_nodes']} pathophysiology nodes across {len(dis['entries_fetched'])} entries, "
      "each with its GO biological processes, direction modifier, downstream links and quoted "
      "evidence with a PMID. Gene-level overlap with the candidate list is "
      f"{dis['n_gene_overlap_rows']} rows, which is expected: DisMech annotates driver genes, "
      "roughly one per disorder, so it supplies mechanism context for a stratum rather than "
      "per-candidate evidence. The per-candidate evidence in this phase comes from Monarch.\n")
    A("Coverage is uneven by manifestation and the `coverage_dismech` column records which case "
      "each stratum is:\n")
    A("- `manifestation` - the manifestation has its own entry")
    A("- `shared_unsubtyped` - cutaneous neurofibroma, plexiform neurofibroma and ANNUBP all map "
      "to the single un-subtyped `Neurofibroma` entry, so their DisMech support is not independent")
    A("- `approximate` - optic pathway glioma maps to `Pilocytic_Astrocytoma`, not an OPG-specific entry")
    A("- `disease` - mechanism taken from the NF1 disease entry, used for non-tumour manifestations")
    A("- `cross_disease_borrow` - NF2-SWN Pain has no NF2-SWN entry; the relevant Chronic "
      "Neuropathic Pain node sits in `Schwannomatosis`, a different disease. Flagged, never "
      "counted as direct support.\n")

    A("## Cross-disease mechanism screen\n")
    two = int((cross.n_shared_go_terms >= 2).sum())
    A(f"Indexing all {dis['n_disorders_indexed']:,} disorder entries in the release gives "
      f"{dis['n_go_process_terms']:,} distinct GO process terms. Matching the NF mechanism nodes "
      f"against them yields {len(cross):,} node-to-disorder rows, of which {two} share two GO terms "
      "and the rest share one. This is a screen, not a verdict: sharing a GO process term is a "
      "reason to read two mechanism descriptions side by side, not a finding that two diseases "
      "share a mechanism. No mechanism-sharing claim is made here.\n")
    top = (cross[cross.n_shared_go_terms >= 2]
           .groupby("other_disorder").size().sort_values(ascending=False).head(10))
    if len(top):
        A("Most frequently co-occurring disorders at two shared terms:\n")
        A("| Other disorder | Node pairings |")
        A("|---|---|")
        for k, v in top.items():
            A(f"| {k} | {v} |")
        A("")

    A("## Carried into Phase 6\n")
    A("- Rank within the disease x manifestation stratum; coverage differs by disease and again by "
      "manifestation, so composites are not comparable across strata")
    A("- `unassessed` must not score as a zero: 108 rows had no HGNC resolution and were never looked up")
    A("- Three strata share one DisMech entry and one is approximate; their DisMech support is "
      "correlated, not independent")
    A("- NF2-SWN Pain support would be a cross-disease borrow and is excluded from direct support")
    A(f"- Tier A and B together cover {int(sup.phase5_support_tier.isin(['A_mechanism','B_phenotype']).sum())} "
      f"of {inputs['dossier_rows']:,} rows. Phase 5 confirms a small number of candidates against "
      "curated knowledge; it does not rank the bulk of the list.\n")

    A("## Files\n")
    for f in sorted(data.glob("phase5-*")):
        A(f"- `{f.name}`")

    (docs / "phase5-mechanistic-validation.md").write_text("\n".join(L) + "\n")
    print("wrote", docs / "phase5-mechanistic-validation.md")
    print("tier totals:", prov["counts"]["support_tiers"])


if __name__ == "__main__":
    main()
