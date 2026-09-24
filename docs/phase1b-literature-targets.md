# Phase 1b — Literature-derived candidate targets

A PubMed sweep of 32 disease- and manifestation-directed queries returned 492 articles, of which 303 named at least one molecular target presented as a driver, modifier, or therapeutic target in neurofibromatosis. Extraction and normalisation produced **547 distinct gene × disease × manifestation rows covering 272 genes/targets**. Eighty-one of those rows are anchored in at least one paper whose full text was retrieved and read; the remaining 466 rest on abstracts alone and are labelled as such. The full list is `data/phase1b-literature-targets.csv`; the paper-level record, including per-paper access, is `data/phase1b-references.csv`.

This list is deliberately independent of the expression pipeline. It is held for the Phase 7 comparison, where overlaps and one-sided findings between the two derivations get examined.

## NF1

The MEK1/2 axis dominates the NF1 literature and is the only NF-relevant target in this sweep with regulatory-grade human evidence. Selumetinib produced durable volumetric responses in inoperable plexiform neurofibroma, first in the phase 1 dose-finding cohort ([Dombi 2016](https://doi.org/10.1056/NEJMoa1605943)) and then in the phase 2 SPRINT trial that supported approval ([Gross 2020](https://doi.org/10.1056/NEJMoa1912735)), with longer-term safety and efficacy data accumulating since ([Kim 2024](https://doi.org/10.1093/neuonc/noae121)). The same node carries into NF1-associated glioma: selumetinib showed activity in paediatric low-grade glioma including the NF1-associated stratum ([Fangusaro 2019](https://doi.org/10.1016/S1470-2045%2819%2930277-3)), and trametinib has been reported in progressive paediatric LGG ([Selt 2020](https://doi.org/10.1007/s11060-020-03640-3)). Upstream of MEK, the neurofibromin–RAS relationship is well characterised but remains hard to drug directly, and the literature increasingly frames neurofibromin as more than a RasGAP ([Anastasaki 2022](https://doi.org/10.1242/dmm.049362)).

Malignant progression is the second well-supported NF1 axis, and it is a loss-of-function story rather than a druggable-kinase one. *CDKN2A* deletion marks the transition from plexiform neurofibroma to atypical neurofibroma/ANNUBP ([Chaney 2020](https://doi.org/10.1158/0008-5472.CAN-19-1429)), and PRC2 component loss (*EED*, *SUZ12*) separates MPNST from its benign precursors and correlates with genomic evolution patterns ([Cortes-Ciriano 2023](https://doi.org/10.1158/2159-8290.CD-22-0786); [Ma 2018](https://doi.org/10.1002/glia.23500)). Both are tumour-suppressor losses: they are strong stratification markers and poor direct drug targets, which is exactly the direction-of-effect distinction the Phase 6 rubric will need to encode.

NF1 pain has a small but mechanistically coherent target set built around the neurofibromin–CRMP2 interface and downstream N-type calcium channel (*CACNA1B*) regulation ([Moutal 2017](https://doi.org/10.1097/j.pain.0000000000001026); [Moutal 2018](https://doi.org/10.1016/j.neuroscience.2018.04.002)), extended to a porcine model with quality-of-life measures ([Khanna 2019](https://doi.org/10.1097/j.pain.0000000000001648)). This is the clearest example in the sweep of a non-tumour manifestation with a nameable target.

## NF2-SWN

Merlin loss converges on the Hippo pathway and on PAK/PI3K signalling, and the therapeutic literature is preclinical or early-phase rather than approved. Everolimus reached a phase 0 trial in vestibular schwannoma and meningioma ([Karajannis 2021](https://doi.org/10.1158/1535-7163.MCT-21-0143)), and mTOR inhibition has been paired with dasatinib in preclinical schwannoma models ([Sagers 2020](https://doi.org/10.1038/s41598-020-60156-6)). Combined PI3K and PAK inhibition is the most developed combination claim in NF2-related schwannomatosis ([Nagel 2024](https://doi.org/10.1038/s41388-024-02958-w)), and PAK inhibition has also been combined with Hippo-pathway blockade in NF2-deficient Schwann cells ([Benton 2024](https://doi.org/10.1371/journal.pone.0305121)). Direct TEAD inhibition appears in the sweep only as a preprint ([Laws 2025](https://doi.org/10.1101/2025.11.15.688608)) and is flagged accordingly; the PI3K/PAK combination likewise first appeared as a preprint ([Fernandez-Valle 2023](https://doi.org/10.21203/rs.3.rs-3405297/v1)) before peer-reviewed publication.

VEGFA is the one NF2 target with real-world clinical use: bevacizumab for NF2-associated vestibular schwannoma, with response and hearing outcomes reported in patient series ([Fujii 2020](https://doi.org/10.2176/nmc.oa.2019-0194)). Recent spatial profiling of the NF2-related vestibular schwannoma immune environment ([Jones 2025](https://doi.org/10.1038/s41467-025-57586-z)) points at a tumour-microenvironment target layer that this sweep only touches. In meningioma, mTORC1 dependence is subtype-linked ([von Spreckelsen 2020](https://doi.org/10.1186/s40478-020-00912-x)) and dual MAPK/PI3K-AKT-mTOR blockade has preclinical support ([Mondielli 2022](https://doi.org/10.3390/cancers14184448)), while merlin-deficient tumours have been targeted through NEDD8/selumetinib combination ([Lyons Rimmer 2020](https://doi.org/10.3390/cancers12071744)). NF2 also emerges as the recurrent driver in spinal ependymoma ([Neyazi 2024](https://doi.org/10.1007/s00401-023-02668-9)).

## SWN (schwannomatosis)

Schwannomatosis is the thinnest of the three by a wide margin — 19 of 547 rows — and its targets are the predisposition genes themselves. Germline *LZTR1* loss-of-function predisposes to schwannomatosis ([Piotrowski 2013](https://doi.org/10.1038/ng.2855)), and the mechanism resolves to LZTR1 acting in a CUL3 complex that ubiquitinates RAS ([Steklov 2018](https://doi.org/10.1126/science.aap7607); [Zhang 2021](https://doi.org/10.3892/ol.2021.12825)), which places SWN back on the RAS axis shared with NF1 and makes it the most interesting cross-disease mechanistic link to carry into Phase 5. *SMARCB1*-driven disease and the clinical management of both subtypes are covered by the GENTURIS guideline ([Evans 2022](https://doi.org/10.1038/s41431-022-01086-x)); phenotypic expansion of *LZTR1*-related disease continues to be reported ([Horn 2024](https://doi.org/10.3389/fneur.2024.1391425)). Pain, the dominant clinical problem in schwannomatosis, produced six rows and no target with a mechanism beyond the predisposition genes — a genuine gap, not a search artefact.

## Coverage by disease and manifestation

Distinct gene × manifestation rows. "Not specified" is the disease column for papers on sporadic tumours with somatic *NF1*/*NF2* loss that do not distinguish germline disease.

| Manifestation | NF1 | NF2-SWN | SWN | Not specified | Total |
|---|---|---|---|---|---|
| Bone defects | 5 | 0 | 0 | 4 | 9 |
| Cardiovascular issues | 6 | 1 | 0 | 5 | 12 |
| Cognition / Behavioral / Learning | 7 | 0 | 0 | 0 | 7 |
| Sleep | 4 | 0 | 0 | 2 | 6 |
| Cutaneous neurofibroma | 21 | 0 | 1 | 2 | 24 |
| Ependymoma | 0 | 6 | 0 | 3 | 9 |
| Gastrointestinal stromal tumor (GIST) | 9 | 0 | 0 | 6 | 15 |
| Hematologic malignancies | 3 | 0 | 0 | 11 | 14 |
| High grade glioma | 11 | 0 | 0 | 36 | 47 |
| Malignant peripheral nerve sheath tumor (MPNST) | 70 | 1 | 2 | 5 | 78 |
| Meningioma | 0 | 32 | 0 | 39 | 71 |
| Optic pathway glioma | 15 | 0 | 0 | 2 | 17 |
| Non-optic LGG | 5 | 0 | 0 | 10 | 15 |
| Pain | 13 | 0 | 6 | 2 | 21 |
| Plexiform neurofibroma | 42 | 0 | 0 | 3 | 45 |
| ANNUBP / atypical neurofibroma | 8 | 0 | 0 | 0 | 8 |
| Pulmonary disease | 5 | 1 | 0 | 0 | 6 |
| Non-vestibular schwannoma | 0 | 17 | 5 | 4 | 26 |
| Vestibular schwannoma | 1 | 47 | 2 | 5 | 55 |
| Other | 23 | 2 | 3 | 34 | 62 |

Four manifestations — Sleep, Pulmonary disease, Cognition/Behavioral/Learning, Bone defects — return single-digit row counts and no full-text-verified target. Cardiovascular issues is comparably thin. These are the combinations Phase 3b will have to decide about explicitly, and the decision should not be read off expression coverage alone, because for several of them the literature is equally empty.

## Access and verification

The plan requires that every literature claim declare full-text versus abstract-only provenance, and the numbers here are worse than the raw PMC statistics suggest. Of 303 contributing papers, 210 have a PMC identifier, but full text was actually retrieved for only 77: the remaining PMC records returned empty bodies (not open access), and one is a licence-blocked preprint. Every row in `data/phase1b-literature-targets.csv` carries `paper_access` per PMID and an `evidence_tier`:

| Evidence tier | Rows |
|---|---|
| full text – supported | 60 |
| full text – partial | 19 |
| full text – not supported | 2 |
| abstract only | 466 |

Verification was attempted on the 103 rows with two or more supporting papers, producing 257 row–paper judgements, of which 136 were assessable against retrieved text and 121 were `not_assessed` for want of full text. Twenty-two of those 103 rows have no full-text-accessible paper at all.

Two rows failed verification outright and should be treated as extraction artefacts rather than findings: MTOR / Not specified / Other and YAP1-TEAD / NF2-SWN / Other. A further 30 rows carry a `manifestation_in_fulltext_differs` value, meaning the full text studies a different manifestation than the abstract-level label implied; those labels should be corrected from the full-text column before Phase 7 matching, not silently trusted.

**Provenance caveat on the verification itself.** Of the 136 assessable judgements, 77 were made by a model pass over the whole retrieved article body. The remaining 59 were judged from gene-focused excerpts of the same retrieved bodies (two to three windows of roughly 300 characters, widened by gene alias and phenotype terms) after the verification run exhausted its token budget. Those 59 rest on targeted passages rather than complete articles and are provisional relative to the other 77. The tier counts above do not distinguish the two; if Phase 7 weights full-text confirmation heavily, re-running the excerpt-based subset over complete bodies is the cheapest way to firm it up.

## Limitations

Extraction is model-based over abstracts, so the list carries recall and precision error that has not been quantified against a gold standard. Twenty-nine of the 78 retried abstracts legitimately named no molecular target; no attempt was made to measure how many targets were missed in the other direction.

Gene symbols were normalised with an alias map (MEK1/2 → MAP2K1/2, merlin → NF2, FAK → PTK2, and similar), which collapses some family-level mentions onto a single label; `gene_target` values such as "PI3K (family)", "PRC2 (EED/SUZ12/EZH2)", and "RAS (pan)" are deliberately not HGNC symbols and will need expansion before target-level database queries in Phase 4.

The 173 rows labelled "Not specified" for disease are concentrated in Meningioma and High grade glioma, where most published work concerns sporadic tumours carrying somatic *NF2* or *NF1* loss rather than germline disease. The project's labelling standard has no rule for this case. Until one exists, those rows are neither safely counted as NF disease evidence nor safely discarded.

Queries were capped at 18 results each and date-filtered from 2005, so highly cited older primary work is under-represented. Citation-graph expansion (backward and forward from the best hits) was not performed.

## Method

Thirty-two PubMed queries spanning NF1, NF2-SWN, and SWN crossed with the plan's fixed manifestation vocabulary, run through the PubMed connector (`search_articles`, relevance-sorted, 18 results per query, `date_from=2005`), returned 492 unique PMIDs; metadata and abstracts were retrieved for 482. Each abstract was passed to a model extraction step returning gene, disease, manifestation(s) from the fixed list, role, mechanism, and study system, with instructions not to extract cohort-defining gene mentions or assay reagents. Seventy-eight calls failed transiently and were re-run, yielding 108 further rows. Gene strings were normalised, manifestations validated against the fixed vocabulary verbatim, and disease coerced to NF1 / NF2-SWN / SWN / Not specified. Rows with two or more supporting papers went to full-text verification via PubMed Central.

## Files

- `data/phase1b-literature-targets.csv` — 547 rows, one per gene × disease × manifestation, with mechanism, supporting PMIDs, per-paper access, and evidence tier
- `data/phase1b-references.csv` — 303 contributing papers with DOI, PMC id, whether full text was read, and rows contributed
- `data/phase1b-coverage.csv` — the coverage matrix above in machine-readable form
