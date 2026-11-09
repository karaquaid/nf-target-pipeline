# Phase 5: Cross-Disease Mechanistic Validation

Generated from Phase 4 dossier commit `f552f88f`. Monarch KG 2026-10-07 (API 1.31.1); DisMech release v0.1.46.

## What this phase does and does not establish

It asks two questions of every candidate target: does the Monarch knowledge graph independently associate this gene with the stratum's disease or its manifestation, and does DisMech name this gene in the disease's curated mechanism. Neither is a scoring step; the composite confidence signal is Phase 6's rubric. Absence of an edge is recorded as absence of evidence, never as evidence against a target.

## Access per source

| Source | Access | Version | Auth |
|---|---|---|---|
| Monarch KG | full records over REST, no field withheld | KG 2026-10-07, API 1.31.1 | none |
| DisMech | full YAML knowledge base from pinned release assets; **no API exists** | v0.1.46 (2026-10-29) | none |

## Inputs and identifier resolution

- 3,752 dossier rows over 9 disease x manifestation strata, 1,930 distinct gene symbols
- 1,902 symbols resolved to HGNC CURIEs; 28 did not resolve and are tiered `unassessed`
- 43 of those resolved only on the second attempt, using `phase4-identifiers.csv`'s `resolved_symbol`. A first pass that tried the literal label alone left 71 unresolved, and most were real genes under withdrawn or alias symbols that Monarch does not index under the old name - GBA (GBA1), SEPT9 (SEPTIN9), MLLT4 (AFDN), KIAA0101 (PCLAF), FOXO1A, DARC, IL1RL1, HIST1H2BD and the C#orf/KIAA/FLJ placeholders. Calling that set junk locus IDs would have hidden a real coverage gap; `resolved_via` records which spelling worked for each gene.
- Two labels resolved only because Phase 4 had already diagnosed them: `March 1` is spreadsheet date corruption of MARCH1, now MARCHF1, and the composite `TPSAB1/B2` maps to TPSAB1 alone, so TPSB2 is not assessed under that row.
- The 28 still unresolved are 25 clone-based locus identifiers (AC/AL/AP/RP11/LOC-style), the legacy placeholders FLJ41484 and MGC24103, and `Oligodendrocyte differentiation (clemastine target)` - a Phase 1b literature label that names a process rather than a gene product, already flagged `not_a_gene_symbol` in Phase 4. None was dropped from the tables.
- 25,733 association rows retrieved; 630 genes carry a causal gene-disease edge and 635 a gene-phenotype edge. 0 request errors.

## A correction worth recording

The phenotype-support flag was first defined as any shared HPO term between a candidate gene and the stratum disease's full phenotype profile. That flagged 981 of 3,752 rows, and the matches were dominated by pleiotropic terms - Seizure (245 rows), Global developmental delay (217), Intellectual disability (215), Hypertelorism (214) - which hundreds of Mendelian genes carry. Such a match says nothing about a gene as an NF target. The flag is now scoped to manifestation-specific HPO terms (`phase5-manifestation-hpo-map.csv`), and terms carried by more than 50 candidate genes are excluded from the tier while still being reported. Scoliosis, at 120 candidate genes, is the one such term. The broad-profile overlap is kept as `n_disease_profile_hpo_matches` and still covers 996 rows - it should not be read as support.

## Support tiers

- `A_mechanism` - named in a DisMech mechanism node or genetic section for the stratum, or carrying a Monarch causal edge to the stratum's disease
- `B_phenotype` - gene-to-HPO edge to a manifestation-specific HPO term
- `C_other_only` - resolved, has Monarch edges, none matching this stratum
- `D_no_edges` - resolved, no causal-disease or phenotype edges in the KG
- `unassessed` - symbol did not resolve to an HGNC CURIE; not looked up, not a negative

| Disease | Manifestation | A | B | C | D | unassessed | DisMech nodes | DisMech coverage |
|---|---|---|---|---|---|---|---|---|
| NF1 | ANNUBP / atypical neurofibroma | 2 | 1 | 29 | 31 | 0 | 19 | `disease+shared_unsubtyped` |
| NF1 | Bone defects | 0 | 1 | 36 | 56 | 0 | 12 | `disease` |
| NF1 | Cutaneous neurofibroma | 0 | 1 | 163 | 261 | 0 | 19 | `disease+shared_unsubtyped` |
| NF1 | Malignant peripheral nerve sheath tumor (MPNST) | 6 | 3 | 330 | 519 | 0 | 22 | `disease+manifestation` |
| NF1 | Optic pathway glioma | 2 | 0 | 115 | 292 | 15 | 16 | `approximate+disease` |
| NF1 | Plexiform neurofibroma | 2 | 2 | 318 | 486 | 0 | 19 | `disease+shared_unsubtyped` |
| NF2-SWN | Non-vestibular schwannoma | 0 | 1 | 69 | 142 | 9 | 6 | `manifestation` |
| NF2-SWN | Pain | 0 | 0 | 53 | 130 | 9 | 6 | `cross_disease_borrow` |
| NF2-SWN | Vestibular schwannoma | 0 | 1 | 206 | 448 | 13 | 7 | `manifestation` |

### Every tier A and tier B candidate

| Gene | Disease | Manifestation | Tier | DisMech entry | Manifestation HPO |
|---|---|---|---|---|---|
| CDKN2A | NF1 | ANNUBP / atypical neurofibroma | A_mechanism | Neurofibroma | - |
| SUZ12 | NF1 | ANNUBP / atypical neurofibroma | A_mechanism | Neurofibroma | - |
| KIT | NF1 | ANNUBP / atypical neurofibroma | B_phenotype | - | HP:0001067 |
| PTPN11 | NF1 | Bone defects | B_phenotype | - | HP:0006487 |
| KIT | NF1 | Cutaneous neurofibroma | B_phenotype | - | HP:0001067 |
| PTEN | NF1 | Malignant peripheral nerve sheath tumor (MPNST) | A_mechanism | Neurofibromatosis_Type_1 | - |
| CDKN2A | NF1 | Malignant peripheral nerve sheath tumor (MPNST) | A_mechanism | Malignant_Peripheral_Nerve_Sheath_Tumor | - |
| CDKN2B | NF1 | Malignant peripheral nerve sheath tumor (MPNST) | A_mechanism | Malignant_Peripheral_Nerve_Sheath_Tumor | - |
| EED | NF1 | Malignant peripheral nerve sheath tumor (MPNST) | A_mechanism | Malignant_Peripheral_Nerve_Sheath_Tumor | - |
| SUZ12 | NF1 | Malignant peripheral nerve sheath tumor (MPNST) | A_mechanism | Malignant_Peripheral_Nerve_Sheath_Tumor | - |
| TP53 | NF1 | Malignant peripheral nerve sheath tumor (MPNST) | A_mechanism | Malignant_Peripheral_Nerve_Sheath_Tumor | - |
| BRAF | NF1 | Malignant peripheral nerve sheath tumor (MPNST) | B_phenotype | - | HP:0100697 |
| MAP2K1 | NF1 | Malignant peripheral nerve sheath tumor (MPNST) | B_phenotype | - | HP:0100697 |
| PTPN11 | NF1 | Malignant peripheral nerve sheath tumor (MPNST) | B_phenotype | - | HP:0100697 |
| BRAF | NF1 | Optic pathway glioma | A_mechanism | Pilocytic_Astrocytoma | - |
| RAF1 | NF1 | Optic pathway glioma | A_mechanism | Pilocytic_Astrocytoma | - |
| PTEN | NF1 | Plexiform neurofibroma | A_mechanism | Neurofibromatosis_Type_1 | - |
| CDKN2A | NF1 | Plexiform neurofibroma | A_mechanism | Neurofibroma | - |
| KIT | NF1 | Plexiform neurofibroma | B_phenotype | - | HP:0001067 |
| SPRED1 | NF1 | Plexiform neurofibroma | B_phenotype | - | HP:0001067 |
| MBD4 | NF2-SWN | Non-vestibular schwannoma | B_phenotype | - | HP:0100008 |
| MBD4 | NF2-SWN | Vestibular schwannoma | B_phenotype | - | HP:0100008 |

## DisMech mechanism context

52 pathophysiology nodes across 7 entries, each with its GO biological processes, direction modifier, downstream links and quoted evidence with a PMID. Gene-level overlap with the candidate list is 12 rows, which is expected: DisMech annotates driver genes, roughly one per disorder, so it supplies mechanism context for a stratum rather than per-candidate evidence. The per-candidate evidence in this phase comes from Monarch.

Coverage is uneven by manifestation and the `coverage_dismech` column records which case each stratum is:

- `manifestation` - the manifestation has its own entry
- `shared_unsubtyped` - cutaneous neurofibroma, plexiform neurofibroma and ANNUBP all map to the single un-subtyped `Neurofibroma` entry, so their DisMech support is not independent
- `approximate` - optic pathway glioma maps to `Pilocytic_Astrocytoma`, not an OPG-specific entry
- `disease` - mechanism taken from the NF1 disease entry, used for non-tumour manifestations
- `cross_disease_borrow` - NF2-SWN Pain has no NF2-SWN entry; the relevant Chronic Neuropathic Pain node sits in `Schwannomatosis`, a different disease. Flagged, never counted as direct support.

## Cross-disease mechanism screen

Indexing all 3,777 disorder entries in the release gives 2,950 distinct GO process terms. Matching the NF mechanism nodes against them yields 10,905 node-to-disorder rows, of which 527 share two GO terms and the rest share one. This is a screen, not a verdict: sharing a GO process term is a reason to read two mechanism descriptions side by side, not a finding that two diseases share a mechanism. No mechanism-sharing claim is made here.

Most frequently co-occurring disorders at two shared terms:

| Other disorder | Node pairings |
|---|---|
| estrogen-receptor positive breast cancer | 18 |
| juvenile polyposis syndrome | 18 |
| classic familial adenomatous polyposis | 18 |
| Cowden disease | 18 |
| breast carcinoma | 18 |
| PTEN hamartoma tumor syndrome | 18 |
| non-small cell lung carcinoma | 12 |
| familial nonmedullary thyroid carcinoma | 12 |
| thyroid gland follicular carcinoma | 12 |
| neurofibromatosis | 8 |

## Carried into Phase 6

- Rank within the disease x manifestation stratum; coverage differs by disease and again by manifestation, so composites are not comparable across strata
- `unassessed` must not score as a zero: 108 rows had no HGNC resolution and were never looked up
- Three strata share one DisMech entry and one is approximate; their DisMech support is correlated, not independent
- NF2-SWN Pain support would be a cross-disease borrow and is excluded from direct support
- Tier A and B together cover 22 of 3,752 rows. Phase 5 confirms a small number of candidates against curated knowledge; it does not rank the bulk of the list.

## Files

- `phase5-cross-disease-mechanisms.csv.gz`
- `phase5-dismech-gene-overlap.csv`
- `phase5-dismech-genetic.csv`
- `phase5-dismech-mechanisms.csv`
- `phase5-manifestation-hpo-map.csv`
- `phase5-monarch-associations.csv.gz`
- `phase5-provenance.json`
- `phase5-support-by-stratum.csv`
- `phase5-target-support.csv`
