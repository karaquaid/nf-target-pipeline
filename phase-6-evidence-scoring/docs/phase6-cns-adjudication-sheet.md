# Phase 6 review sheet: adjudicating the CNS delivery claims

The Phase 5 literature pass retrieved 452 CNS-relevant sentences for the 20 active moieties behind the shortlist drug labels, of which **124 actually name the drug they were retrieved for**. Those 124 are below, grouped by moiety. The other 328 mention a different drug than the one the paper was retrieved for and are not evidence about that drug.

## What to decide

Phase 6 scores CNS delivery three-state (project plan, Phase 6, settled 2026-11-10). Fill `verdict` per claim against those definitions:

| verdict | what qualifies |
| --- | --- |
| `demonstrated` | measured exposure in the CNS compartment (CSF, brain tissue, Kp,uu, brain:plasma above a trivial ratio), or approval/trial activity in a CNS indication for the relevant manifestation |
| `contradicted` | measured pharmacokinetics showing CNS exclusion - the state the pipeline currently has no source for, which is why this read exists |
| `unknown` | everything else, including assertions without exposure data, review restatements and predictions. Scored as unassessed, never as a negative |

`keyword_direction` is the Phase 5 regex label and is **a sorting aid, not a verdict** - it was wrong on trametinib's brain-to-plasma paper, calling an efflux-limited finding `supporting`. Read the sentence, not the label.

Controlled vocabularies for the remaining columns:

- `evidence_basis`: `measured_pk_human`, `measured_pk_animal`, `clinical_cns_response`, `preclinical_cns_efficacy`, `mechanistic_assertion`, `review_restatement`, `design_or_prediction`
- `primary_or_restated`: `primary`, `restated`, `unclear`
- `species`: `human`, `mouse`, `rat`, `other_animal`, `in_vitro`, `na`
- `metric` / `value`: the quantity as the sentence states it (`Kp,uu`, `brain:plasma`, `CSF:plasma`, `CSF concentration`, `none`), copied verbatim

A claim read from an abstract can still be decisive when the abstract states the measurement itself - record it and leave `access` as the provenance, as Phase 1b does. The drug-level verdict goes in `data/phase6-cns-adjudication-rollup.csv`; a drug needs one `demonstrated` or `contradicted` claim it rests on, named in `decisive_claim_ids`.

## Where each drug stands before the read

| moiety | attributed claims | full text | with a number | claim ids | ChEMBL calculated flag | openFDA label | rows w/ CNS trial evidence | max NF trials |
| --- | ---: | ---: | ---: | --- | --- | --- | ---: | ---: |
| VEMURAFENIB | 26 | 14 | 18 | CNS-099-CNS-124 | predicted_non_permeant | no_statement | 0 | 0 |
| IMATINIB | 21 | 13 | 13 | CNS-028-CNS-048 | predicted_non_permeant | no_record | 0 | 6 |
| SORAFENIB | 13 | 6 | 4 | CNS-069-CNS-081 | predicted_non_permeant | no_label_found;no_statement | 17 | 1 |
| PAZOPANIB | 12 | 9 | 8 | CNS-049-CNS-060 | predicted_non_permeant | no_statement | 7 | 4 |
| SUNITINIB | 11 | 3 | 6 | CNS-082-CNS-092 | predicted_permeant | no_label_found;no_statement | 5 | 1 |
| DASATINIB | 9 | 1 | 5 | CNS-016-CNS-024 | predicted_non_permeant | no_record | 0 | 0 |
| AVAPRITINIB | 8 | 5 | 2 | CNS-001-CNS-008 | predicted_non_permeant | no_record | 0 | 0 |
| REGORAFENIB | 4 | 2 | 1 | CNS-061-CNS-064 | predicted_non_permeant | no_statement | 0 | 0 |
| ENCORAFENIB | 3 | 1 | 1 | CNS-025-CNS-027 | predicted_non_permeant | no_statement | 7 | 1 |
| TOVORAFENIB | 3 | 1 | 1 | CNS-094-CNS-096 | predicted_non_permeant | no_statement | 7 | 1 |
| COBIMETINIB | 3 | 0 | 3 | CNS-011-CNS-013 | predicted_non_permeant | no_label_found;no_statement | 12 | 1 |
| DABRAFENIB | 2 | 2 | 0 | CNS-014-CNS-015 | predicted_non_permeant | no_label_found;no_statement | 10 | 3 |
| BINIMETINIB | 2 | 1 | 2 | CNS-009-CNS-010 | predicted_permeant | no_statement | 8 | 2 |
| RIPRETINIB | 2 | 1 | 0 | CNS-065-CNS-066 | predicted_non_permeant | no_record | 0 | 0 |
| SELUMETINIB | 2 | 0 | 1 | CNS-067-CNS-068 | predicted_non_permeant | no_label_found;no_statement | 12 | 18 |
| TRAMETINIB | 2 | 0 | 0 | CNS-097-CNS-098 | predicted_non_permeant | no_label_found;no_statement | 2 | 9 |
| TIVOZANIB | 1 | 0 | 0 | CNS-093-CNS-093 | predicted_non_permeant | no_record | 0 | 0 |
| MIDOSTAURIN | 0 | 0 | 0 | - | predicted_non_permeant | no_label_found | 0 | 0 |
| PEXIDARTINIB | 0 | 0 | 0 | - | predicted_non_permeant | no_label_found;no_statement | 0 | 0 |
| QUIZARTINIB | 0 | 0 | 0 | - | predicted_non_permeant | no_statement | 0 | 0 |

3 moieties carry no attributed claim and so cannot move off `unknown` on literature evidence: MIDOSTAURIN, PEXIDARTINIB, QUIZARTINIB. They are listed in the rollup so the absence is recorded rather than silent.

## The claims

### AVAPRITINIB

8 attributed of 13 retrieved sentences · 5 full text, 3 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_record` · CNS-manifestation trial evidence on 0 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-001** · [PMID 40086436](https://pubmed.ncbi.nlm.nih.gov/40086436/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12121847/) · `full_text` · `supporting` · number
  - > Case 2 demonstrated an increase in the CSF/plasma ratio during the course of treatment, with tumor tissue reaching a concentration of 4μM avapritinib following six months of treatment ().
  - *Effective targeting of PDGFRA-altered high-grade glioma with avapritinib.* — Cancer Cell 2025
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-002** · [PMID 38167404](https://pubmed.ncbi.nlm.nih.gov/38167404/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761696/) · `full_text` · `supporting` · no number
  - > These effects most likely result from avapritinib’s ability to penetrate the blood-brain barrier (BBB) and interact with unidentified targets in the brain.
  - *Avapritinib-based SAR studies unveil a binding pocket in KIT and PDGFRA.* — Nat Commun 2024
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-003** · [PMID 40086436](https://pubmed.ncbi.nlm.nih.gov/40086436/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12121847/) · `full_text` · `supporting` · no number
  - > Avapritinib treatment results in efficient brain penetrance and prolonged survival in-altered DMG models We next asked whether avapritinib crosses the blood-brain barrier and impacts tumor growth in-altered glioma animal models.
  - *Effective targeting of PDGFRA-altered high-grade glioma with avapritinib.* — Cancer Cell 2025
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-004** · [PMID 40086436](https://pubmed.ncbi.nlm.nih.gov/40086436/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12121847/) · `full_text` · `supporting` · no number
  - > In summary, we show that avapritinib efficiently crosses the blood brain barrier to achieve supratherapeutic concentrations in target brain tissue.
  - *Effective targeting of PDGFRA-altered high-grade glioma with avapritinib.* — Cancer Cell 2025
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-005** · [PMID 41961082](https://pubmed.ncbi.nlm.nih.gov/41961082/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13068680/) · `full_text` · `limiting` · no number
  - > Although data on CNS penetration of avapritinib in AML are limited, and CSF levels of avapritinib were not available in this case, preclinical studies and early clinical data in-mutated gliomas suggest that the drug can effectively cross the blood–brain barrier and exert antitumor activity within the CNS [].
  - *Avapritinib for targeting KIT D816V-mutated acute myeloid leukemia relapsed after allogeneic hematopoietic stem cell transplant with extramedullary and central nervous system involvement.* — Ann Hematol 2026
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-006** · [PMID 40086436](https://pubmed.ncbi.nlm.nih.gov/40086436/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12121847/) · `abstract_only` · `supporting` · number
  - > We reveal that the PDGFRA/KIT inhibitor avapritinib shows (1) selectivity for PDGFRA inhibition, (2) distinct patterns of subcellular effects, (3) in vitro and in vivo activity in patient-derived HGG models, and (4) effective blood-brain barrier penetration in mice and humans.
  - *Effective targeting of PDGFRA-altered high-grade glioma with avapritinib.* — Cancer Cell 2025
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-007** · [PMID 38167404](https://pubmed.ncbi.nlm.nih.gov/38167404/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761696/) · `abstract_only` · `supporting` · no number
  - > We utilize this information to design, synthesize and characterize avapritinib derivatives for the determination of key pharmacophoric features to overcome drug resistance and limit potential blood-brain barrier penetration.
  - *Avapritinib-based SAR studies unveil a binding pocket in KIT and PDGFRA.* — Nat Commun 2024
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-008** · [PMID 41961082](https://pubmed.ncbi.nlm.nih.gov/41961082/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13068680/) · `abstract_only` · `supporting` · no number
  - > Remarkably, rechallenge with single‑agent avapritinib again induced molecular remission in both peripheral blood and cerebrospinal fluid, along with near‑complete metabolic response across all previously involved sites.
  - *Avapritinib for targeting KIT D816V-mutated acute myeloid leukemia relapsed after allogeneic hematopoietic stem cell transplant with extramedullary and central nervous system involvement.* — Ann Hematol 2026
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### BINIMETINIB

2 attributed of 14 retrieved sentences · 1 full text, 1 abstract-only · ChEMBL calculated flag: `predicted_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 8 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-009** · [PMID 41369830](https://pubmed.ncbi.nlm.nih.gov/41369830/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12799883/) · `full_text` · `supporting` · number
  - > These results highlight the potential of encorafenib plus binimetinib to provide meaningful intracranial tumor shrinkage and improved complete responses in patients with BRAF V600-mutant melanoma with brain metastases, although the considerable heterogeneity across included studies suggests that these findings should be interpreted with caution.
  - *The safety and efficacy of encorafenib plus binimetinib for brain metastases: a systematic review and meta-analysis.* — Discov Oncol 2025
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-010** · [PMID 28921565](https://pubmed.ncbi.nlm.nih.gov/28921565/) · `abstract_only` · `supporting` · number
  - > PD0325901 displayed more promising characteristics than trametinib (GSK1120212), binimetinib (MEK162), selumetinib (AZD6244), and pimasertib (AS703026): PD0325901 was the weakest substrate of P-gp and BCRP in vitro, its brain penetration was only marginally higher in Abcb1a/b;Abcg2mice, and efficient target inhibition in the brain could be achieved at clinically relevant plasma levels.
  - *The impact of P-glycoprotein and breast cancer resistance protein on the brain pharmacokinetics and pharmacodynamics of a panel of MEK inhibitors.* — Int J Cancer 2017
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### COBIMETINIB

3 attributed of 19 retrieved sentences · 0 full text, 3 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 12 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-011** · [PMID 25243894](https://pubmed.ncbi.nlm.nih.gov/25243894/) · `abstract_only` · `supporting` · number
  - > The objectives of this study were to determine in vitro and in vivo if cobimetinib is a substrate of P-glycoprotein (P-gp) and/or breast cancer resistance protein (Bcrp1) and to assess the implications of efflux on cobimetinib pharmacokinetics (PK), brain penetration, and target modulation.
  - *Role of P-glycoprotein on the brain penetration and brain pharmacodynamic activity of the MEK inhibitor cobimetinib.* — Mol Pharm 2014
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-012** · [PMID 25243894](https://pubmed.ncbi.nlm.nih.gov/25243894/) · `abstract_only` · `supporting` · number
  - > After an oral 10 mg/kg dose of cobimetinib, the mean total brain to plasma ratio (Kp) at 6 h postdose was 0.3 and 0.2 in WT and Bcrp1(-/-) mice, respectively.
  - *Role of P-glycoprotein on the brain penetration and brain pharmacodynamic activity of the MEK inhibitor cobimetinib.* — Mol Pharm 2014
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-013** · [PMID 40975475](https://pubmed.ncbi.nlm.nih.gov/40975475/) · `abstract_only` · `supporting` · number
  - > Of these, we selected only the 11 which can cross the blood-brain barrier: cobimetinib, panobinostat, melphalan, rucaparib, alectinib, ponatinib, danazol, carboplatin, vandetanib, erlotinib, and gefitinib.
  - *Transcriptomic profiling unveils novel therapeutic options for drug-resistant temporal lobe epilepsy.* — Eur J Pharmacol 2025
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### DABRAFENIB

2 attributed of 14 retrieved sentences · 2 full text, 0 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 10 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-014** · [PMID 32817058](https://pubmed.ncbi.nlm.nih.gov/32817058/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7437885/) · `full_text` · `supporting` · no number
  - > In line with other clinical responses,the initial response of the brain lesion to dabrafenib suggested that the drug did cross the blood-brain barrier, and our data suggest that resistance was not mediated by cell-intrinsic events, so we examined if resistance was mediated by factors in the brain microenvironment.
  - *Brain microenvironment-driven resistance to immune and targeted therapies in acral melanoma.* — ESMO Open 2020
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-015** · [PMID 38291372](https://pubmed.ncbi.nlm.nih.gov/38291372/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10826080/) · `full_text` · `supporting` · no number
  - > Finally, tovorafenib had greater CNS penetration compared with the type I RAF inhibitor dabrafenib [].
  - *LOGGIC/FIREFLY-2: a phase 3, randomized trial of tovorafenib vs. chemotherapy in pediatric and young adult patients with newly diagnosed low-grade glioma harboring an activating RAF alteration.* — BMC Cancer 2024
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### DASATINIB

9 attributed of 74 retrieved sentences · 1 full text, 8 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_record` · CNS-manifestation trial evidence on 0 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-016** · [PMID 32493453](https://pubmed.ncbi.nlm.nih.gov/32493453/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7268320/) · `full_text` · `supporting` · number
  - > Supplementary information Supplementary information on clinical parameters and sample collection.Sequential therapies of the investigated drugs in the study cohort.Depiction of the used HPLC gradient for sample analysis.Overview of the used mass spectrometer parameters.Normalized chromatogram of a standard solution of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat obtained with the developed HPLC-QqQ MS method.Overview of the corresponding method performance parameters.Depiction of measured CCS values of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat.Depiction of the quantitation results for imatinib CSF samples
  - *Cerebrospinal fluid penetration of targeted therapeutics in pediatric brain tumor patients.* — Acta Neuropathol Commun 2020
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-017** · [PMID 19491323](https://pubmed.ncbi.nlm.nih.gov/19491323/) · `abstract_only` · `limiting` · number
  - > In vivo brain distribution studies showed that the CNS distribution of dasatinib is limited, with the brain-to-plasma concentration ratios less than 0.12 in wild-type mice, which increased approximately 8-fold in Mdr1a/b(-/-) Bcrp1(-/-) mice.
  - *P-glycoprotein and breast cancer resistance protein influence brain distribution of dasatinib.* — J Pharmacol Exp Ther 2009
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-018** · [PMID 24790822](https://pubmed.ncbi.nlm.nih.gov/24790822/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4000600/) · `abstract_only` · `supporting` · number
  - > With 40 mg dasatinib administered once daily, its trough level and cerebrospinal fluid (CSF) concentration were 32 ng/mL and below the sensitivity threshold of 1 ng/mL, respectively.
  - *Philadelphia chromosome-positive acute lymphoblastic leukemia with extramedullary and meningeal relapse after allogeneic hematopoietic stem cell transplantation that was successfully treated with dasatinib.* — Springerplus 2014
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-019** · [PMID 35098970](https://pubmed.ncbi.nlm.nih.gov/35098970/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8612719/) · `abstract_only` · `supporting` · number
  - > The primary objective is to evaluate the central nervous system penetration of dasatinib and quercetin through analysis of cerebrospinal fluid collected at baseline and after 12 weeks of treatment.
  - *Senolytic Therapy to Modulate the Progression of Alzheimer's Disease (SToMP-AD): A Pilot Clinical Trial.* — J Prev Alzheimers Dis 2022
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-020** · [PMID 42578491](https://pubmed.ncbi.nlm.nih.gov/42578491/) · `abstract_only` · `supporting` · number
  - > In CSF, the mean dasatinib concentration was 0.5 ± 0.2 ng/mL at 2 h.
  - *Low Dasatinib Penetration of the Blood-Brain Barrier in Children With Philadelphia Chromosome-Positive Acute Lymphoblastic Leukemia: Evidence From LC-MS/MS Analysis.* — Pediatr Blood Cancer 2026
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-021** · [PMID 19491323](https://pubmed.ncbi.nlm.nih.gov/19491323/) · `abstract_only` · `supporting` · no number
  - > The objective of this study was to investigate the role of P-glycoprotein (P-gp) and breast cancer resistance protein (BCRP) in modulating the CNS penetration of dasatinib.
  - *P-glycoprotein and breast cancer resistance protein influence brain distribution of dasatinib.* — J Pharmacol Exp Ther 2009
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-022** · [PMID 42578491](https://pubmed.ncbi.nlm.nih.gov/42578491/) · `abstract_only` · `limiting` · no number
  - > In conclusion, despite therapeutic systemic levels, dasatinib penetrates poorly into CSF in children with PhALL.
  - *Low Dasatinib Penetration of the Blood-Brain Barrier in Children With Philadelphia Chromosome-Positive Acute Lymphoblastic Leukemia: Evidence From LC-MS/MS Analysis.* — Pediatr Blood Cancer 2026
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-023** · [PMID 42578491](https://pubmed.ncbi.nlm.nih.gov/42578491/) · `abstract_only` · `supporting` · no number
  - > We measured dasatinib concentrations in paired plasma and cerebrospinal fluid (CSF) samples from children with Philadelphia chromosome-positive acute lymphoblastic leukemia (Ph+ ALL).
  - *Low Dasatinib Penetration of the Blood-Brain Barrier in Children With Philadelphia Chromosome-Positive Acute Lymphoblastic Leukemia: Evidence From LC-MS/MS Analysis.* — Pediatr Blood Cancer 2026
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-024** · [PMID 42578491](https://pubmed.ncbi.nlm.nih.gov/42578491/) · `abstract_only` · `supporting` · no number
  - > After validating a liquid chromatography-tandem mass spectrometry (LC-MS/MS) assay for dasatinib in both matrices, we quantified drug concentrations in plasma and CSF and expressed blood-brain barrier penetration as the plasma-to-CSF concentration ratio.
  - *Low Dasatinib Penetration of the Blood-Brain Barrier in Children With Philadelphia Chromosome-Positive Acute Lymphoblastic Leukemia: Evidence From LC-MS/MS Analysis.* — Pediatr Blood Cancer 2026
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### ENCORAFENIB

3 attributed of 9 retrieved sentences · 1 full text, 2 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 7 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-025** · [PMID 41369830](https://pubmed.ncbi.nlm.nih.gov/41369830/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12799883/) · `full_text` · `supporting` · number
  - > These results highlight the potential of encorafenib plus binimetinib to provide meaningful intracranial tumor shrinkage and improved complete responses in patients with BRAF V600-mutant melanoma with brain metastases, although the considerable heterogeneity across included studies suggests that these findings should be interpreted with caution.
  - *The safety and efficacy of encorafenib plus binimetinib for brain metastases: a systematic review and meta-analysis.* — Discov Oncol 2025
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-026** · [PMID 29155017](https://pubmed.ncbi.nlm.nih.gov/29155017/) · `abstract_only` · `limiting` · no number
  - > However, absolute brain concentrations and brain-to-plasma ratios remained very low in all strains, indicating intrinsically poor brain penetration of encorafenib.
  - *P-glycoprotein (MDR1/ABCB1) and Breast Cancer Resistance Protein (BCRP/ABCG2) affect brain accumulation and intestinal disposition of encorafenib in mice.* — Pharmacol Res 2017
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-027** · [PMID 29155017](https://pubmed.ncbi.nlm.nih.gov/29155017/) · `abstract_only` · `limiting` · no number
  - > The low brain penetration of encorafenib might limit its efficacy against malignancies positioned behind a functional blood-brain barrier, but its oral bioavailability and distribution to other tested organs (liver, kidney, spleen, testis) was high.
  - *P-glycoprotein (MDR1/ABCB1) and Breast Cancer Resistance Protein (BCRP/ABCG2) affect brain accumulation and intestinal disposition of encorafenib in mice.* — Pharmacol Res 2017
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### IMATINIB

21 attributed of 90 retrieved sentences · 13 full text, 8 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_record` · CNS-manifestation trial evidence on 0 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-028** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `limiting` · number
  - > Subsequently, it was demonstrated that thedistribution of imatinib is limited by ABCB1-mediated efflux, resulting in limited brain penetration [].
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-029** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > However, ABCB1 is not the sole transporter expressed in the blood-brain barrier that may limit the brain distribution of imatinib.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-030** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > The brain-to-plasma ratio of imatinib 2 hours after administration did not differ significantly between the two groups (P = 0.83), and similar brain-to-plasma AUCratios were observed for each group (0.070 for imatinib plus vehicle0.078 for imatinib plus tariquidar).
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-031** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > Table 1 Pharmacokinetics of imatinib in Balb/C mice in the presence and absence of tariquidar Imatinib alone Imatinib + Tariquidar Plasma Mean SD Mean SD Fold Change P-value C(ng/mL) 5,710.5 1,472.3 6,813.2 1,547.9 1.19 - T(hr) 0.17 - 0.17 - - - AUC(hr*ng/mL) 12,167.5 - 26,724.6 - 2.20 0.001 Liver Mean SD Mean SD Fold Change P-value C(ng/g) 26,279.7 4,560.2 46,139.1 11,000.6 1.76 - T(hr) 0.25 - 0.17 - - - AUC(hr*ng/g) 68,330.8 - 153,209.2 - 2.24 < 0.00001 Brain Mean SD Mean SD Fold Change P-value C(ng/g) 194.7 27.2 417.0 116.6 2.14 - T(hr) 2 - 2 - - - AUC(hr*ng/g) 574.23 - 1,277.7 - 2.23 0.00001 Discussio
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-032** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > The brain-to-plasma concentration ratio of imatinib 2 hours after administration was not significantly affected by tariquidar.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-033** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > Specifically, elacridar has been shown to result in a 9.3-fold increase in the brain-to-plasma concentration ratio, as compared to administration of imatinib alone [].
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-034** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > Though the increase in brain exposure to imatinib was reported to be higher with oral administration, as compared to i.v., this was only measured at 4 hours post-imatinib, and the analysis was based only on measurement of total radioactivity.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-035** · [PMID 32493453](https://pubmed.ncbi.nlm.nih.gov/32493453/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7268320/) · `full_text` · `supporting` · number
  - > Consequently, we tested whether CSF protein levels routinely measured at the same time point as drug penetration analyzes correlated to imatinib concentrations and could indeed detect a positive correlation (Additional file: Figure S6).
  - *Cerebrospinal fluid penetration of targeted therapeutics in pediatric brain tumor patients.* — Acta Neuropathol Commun 2020
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-036** · [PMID 32493453](https://pubmed.ncbi.nlm.nih.gov/32493453/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7268320/) · `full_text` · `supporting` · number
  - > Supplementary information Supplementary information on clinical parameters and sample collection.Sequential therapies of the investigated drugs in the study cohort.Depiction of the used HPLC gradient for sample analysis.Overview of the used mass spectrometer parameters.Normalized chromatogram of a standard solution of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat obtained with the developed HPLC-QqQ MS method.Overview of the corresponding method performance parameters.Depiction of measured CCS values of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat.Depiction of the quantitation results for imatinib CSF samples
  - *Cerebrospinal fluid penetration of targeted therapeutics in pediatric brain tumor patients.* — Acta Neuropathol Commun 2020
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-037** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `limiting` · no number
  - > More recently, positron emission topography studies with [-C-methyl]-imatinib have confirmed limited brain penetration in primates [].
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-038** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `limiting` · no number
  - > Here, we evaluated the effect of tariquidar on the disposition of imatinib in mice, in order to provide a pharmacokinetic rationale for attempts to improve the agent's low brain penetration.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-039** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · no number
  - > Hence, it is possible that the higher imatinib dose utilized in the current study results in higher plasma concentrations of drug and, therefore, saturation of drug efflux at the blood-brain barrier.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-040** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · no number
  - > Based on our findings, simply doubling the dose of imatinib without addition of an inhibitor would likely result in a similar increase in overall brain exposure, due to increased plasma concentrations of drug.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-041** · [PMID 12604685](https://pubmed.ncbi.nlm.nih.gov/12604685/) · `abstract_only` · `supporting` · number
  - > In the wild-type mice, the brain-to-plasma STI-571 concentration ratio at all time points was low (1-3%);
  - *Distribution of STI-571 to the brain is limited by P-glycoprotein-mediated efflux.* — J Pharmacol Exp Ther 2003
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-042** · [PMID 12604685](https://pubmed.ncbi.nlm.nih.gov/12604685/) · `abstract_only` · `supporting` · number
  - > When 12.5 mg/kg STI-571 was given intravenously, the brain-to-plasma ratio of STI-571 in the mdr1a/b (-/-) mice was approximately 7-fold greater than that of wild-type mice up to 120 min postdose.
  - *Distribution of STI-571 to the brain is limited by P-glycoprotein-mediated efflux.* — J Pharmacol Exp Ther 2003
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-043** · [PMID 25539457](https://pubmed.ncbi.nlm.nih.gov/25539457/) · `abstract_only` · `supporting` · number
  - > Brain exposure increased substantially in Mdr1a(-/-) rats for loperamide and in Mdr1a(-/-)/Abcg2(-/-) rats for imatinib and compound Y, but minimally to modestly in Abcg2(-/-) rats for dantrolene and compound X.
  - *Differential role of P-glycoprotein and breast cancer resistance protein in drug distribution into brain, CSF and peripheral nerve tissues in rats.* — Xenobiotica 2014
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-044** · [PMID 25539457](https://pubmed.ncbi.nlm.nih.gov/25539457/) · `abstract_only` · `supporting` · number
  - > While CSF to unbound brain concentration ratio remained ≥3 in the KO animals for dantrolene, compounds X and Y, it was reduced to 1 in the Mdr1a(-/-)/Abcg2(-/-) rats for imatinib.
  - *Differential role of P-glycoprotein and breast cancer resistance protein in drug distribution into brain, CSF and peripheral nerve tissues in rats.* — Xenobiotica 2014
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-045** · [PMID 15073132](https://pubmed.ncbi.nlm.nih.gov/15073132/) · `abstract_only` · `limiting` · no number
  - > There is limited penetration of imatinib into the CSF of nonhuman primates after i.v.
  - *Plasma and cerebrospinal fluid pharmacokinetics of imatinib after administration to nonhuman primates.* — Clin Cancer Res 2004
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-046** · [PMID 15073132](https://pubmed.ncbi.nlm.nih.gov/15073132/) · `abstract_only` · `supporting` · no number
  - > We used a nonhuman primate model that is highly predictive of the cerebrospinal fluid penetration of drugs in humans to study the pharmacokinetics of imatinib in plasma and cerebrospinal fluid (CSF) after i.v.
  - *Plasma and cerebrospinal fluid pharmacokinetics of imatinib after administration to nonhuman primates.* — Clin Cancer Res 2004
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-047** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `abstract_only` · `supporting` · no number
  - > Though tariquidar increased the absolute exposure of imatinib, the brain-to-plasma ratio of imatinib was unaffected.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-048** · [PMID 34896751](https://pubmed.ncbi.nlm.nih.gov/34896751/) · `abstract_only` · `supporting` · no number
  - > The contribution of BCRP to the brain and CSF distribution of the dual P-glycoprotein/BCRP substrates, imatinib and prazosin, was similar to that of BCRP-specific substrates.
  - *Investigation of the role and quantitative impact of breast cancer resistance protein on drug distribution into brain and CSF in rats.* — Drug Metab Pharmacokinet 2021
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### PAZOPANIB

12 attributed of 22 retrieved sentences · 9 full text, 3 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 7 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-049** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `full_text` · `supporting` · number
  - > We further demonstrated that simultaneous inhibition of P-gp and Bcrp1 mediated active efflux at the mouse BBB could significantly improve the brain penetration of pazopanib.
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-050** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `full_text` · `supporting` · number
  - > In contrast to the in vitro findings, initial in vivo experiments showed selective inhibition of P-gp or Ko143 did not have any significant influence on brain penetration of pazopanib ().
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-051** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `full_text` · `supporting` · number
  - > These results suggest that even if pazopanib is a moderate substrate of P-gp in vitro, in vivo at the mouse BBB, both P-gp and Bcrp1 act in concert to limit brain penetration of pazopanib.
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-052** · [PMID 28869476](https://pubmed.ncbi.nlm.nih.gov/28869476/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5757517/) · `full_text` · `supporting` · number
  - > We found that pazopanib crosses the blood-brain barrier (BBB) with no detectable peripheral off-side effects, and reduces p-tau in TauP301L mice.
  - *Pazopanib Reduces Phosphorylated Tau Levels and Alters Astrocytes in a Mouse Model of Tauopathy.* — J Alzheimers Dis 2017
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-053** · [PMID 28869476](https://pubmed.ncbi.nlm.nih.gov/28869476/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5757517/) · `full_text` · `supporting` · number
  - > Results Pazopanib penetrates the blood-brain barrier Following a single intraperitoneal (IP) injection of pazopanib of 0, 5, or 10mg/kg in dimethyl sulfoxide (DMSO) in C57BL/6 mice, we found that the drug penetrates the BBB and peaks at approximately 4 hours (T) ().
  - *Pazopanib Reduces Phosphorylated Tau Levels and Alters Astrocytes in a Mouse Model of Tauopathy.* — J Alzheimers Dis 2017
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-054** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `full_text` · `supporting` · no number
  - > The fact that both these test compounds in our study are also known to modulate P-gp and BCRP functional activity (;), we selected erlotinib and canertinib as clinically relevant inhibitors for improving pazopanib brain penetration.
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-055** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `full_text` · `supporting` · no number
  - > In addition, from the clinical perspective, we show that canertinib or erlotinib, although not as potent as elacridar could be indicated as clinically relevant efflux modulators in combination therapy to enhance brain penetration of pazopanib for the treatment of recurrent brain tumors.
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-056** · [PMID 22749591](https://pubmed.ncbi.nlm.nih.gov/22749591/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3396766/) · `full_text` · `limiting` · no number
  - > We have shown in our laboratory (manuscript under revision with) that one probable reason for limited brain penetration of pazopanib is due to ATP binding cassette efflux proteins;
  - *Determination of pazopanib (GW-786034) in mouse plasma and brain tissue by liquid chromatography-tandem mass spectrometry (LC/MS-MS).* — J Chromatogr B Analyt Technol Biomed Life Sci 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-057** · [PMID 22749591](https://pubmed.ncbi.nlm.nih.gov/22749591/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3396766/) · `full_text` · `supporting` · no number
  - > However, the tight endothelial junctions located in brain capillaries which are further fortified by the presence of ABC efflux transporters (blood–– brain barrier, BBB) can restrict the brain penetration of pazopanib and may lead to its therapeutic inefficacy when used as an anti-tumor agent for recurrent brain tumors.
  - *Determination of pazopanib (GW-786034) in mouse plasma and brain tissue by liquid chromatography-tandem mass spectrometry (LC/MS-MS).* — J Chromatogr B Analyt Technol Biomed Life Sci 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-058** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `abstract_only` · `supporting` · number
  - > However, dual P-gp/Bcrp1 inhibition by elacridar (GF120918), significantly enhanced pazopanib brain penetration by ~5-fold without altering its plasma concentrations.
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-059** · [PMID 22749591](https://pubmed.ncbi.nlm.nih.gov/22749591/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3396766/) · `abstract_only` · `supporting` · number
  - > This method was applied to determine brain to plasma concentration ratio and relevant pharmacokinetic parameters of pazopanib after a single intravenous dose of 5 mg/kg in FVB wild type mice.
  - *Determination of pazopanib (GW-786034) in mouse plasma and brain tissue by liquid chromatography-tandem mass spectrometry (LC/MS-MS).* — J Chromatogr B Analyt Technol Biomed Life Sci 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-060** · [PMID 28869476](https://pubmed.ncbi.nlm.nih.gov/28869476/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5757517/) · `abstract_only` · `supporting` · number
  - > Pazopanib crosses the blood-brain barrier with no detectable peripheral off-side effects, and decreases p-tau in TauP301L mice.
  - *Pazopanib Reduces Phosphorylated Tau Levels and Alters Astrocytes in a Mouse Model of Tauopathy.* — J Alzheimers Dis 2017
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### REGORAFENIB

4 attributed of 51 retrieved sentences · 2 full text, 2 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 0 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-061** · [PMID 32493453](https://pubmed.ncbi.nlm.nih.gov/32493453/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7268320/) · `full_text` · `supporting` · number
  - > Supplementary information Supplementary information on clinical parameters and sample collection.Sequential therapies of the investigated drugs in the study cohort.Depiction of the used HPLC gradient for sample analysis.Overview of the used mass spectrometer parameters.Normalized chromatogram of a standard solution of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat obtained with the developed HPLC-QqQ MS method.Overview of the corresponding method performance parameters.Depiction of measured CCS values of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat.Depiction of the quantitation results for imatinib CSF samples
  - *Cerebrospinal fluid penetration of targeted therapeutics in pediatric brain tumor patients.* — Acta Neuropathol Commun 2020
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-062** · [PMID 42573440](https://pubmed.ncbi.nlm.nih.gov/42573440/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13471100/) · `full_text` · `supporting` · no number
  - > Although regorafenib is capable of reaching intracranial tumors, CNS exposure is limited by high plasma protein binding and active efflux transporters such as P-glycoprotein and breast cancer resistance protein at the blood–brain barrier.
  - *Pathway dysregulation and therapeutic resistance in glioblastoma: molecular mechanisms and emerging therapeutic targets.* — Future Sci OA 2026
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-063** · [PMID 39637954](https://pubmed.ncbi.nlm.nih.gov/39637954/) · `abstract_only` · `supporting` · no number
  - > Despite these overall negative findings, some data indicate improved clinical outcomes in a subset of GBM patients treated with certain PKIs (i.e., regorafenib) and encourage further research to identify PKIs with better blood-brain barrier penetration and lower risk for resistance development.
  - *Protein kinase inhibitors as targeted therapy for glioblastoma: a meta-analysis of randomized controlled clinical trials.* — Pharmacol Res 2025
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-064** · [PMID 39941744](https://pubmed.ncbi.nlm.nih.gov/39941744/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11816343/) · `abstract_only` · `supporting` · no number
  - > Additionally, the suboptimal dosing of regorafenib, due to its poor penetration of the blood-brain barrier, may reduce the likelihood of effectively targeting certain PKs.
  - *Multikinase Treatment of Glioblastoma: Evaluating the Rationale for Regorafenib.* — Cancers (Basel) 2025
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### RIPRETINIB

2 attributed of 5 retrieved sentences · 1 full text, 1 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_record` · CNS-manifestation trial evidence on 0 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-065** · [PMID 40656249](https://pubmed.ncbi.nlm.nih.gov/40656249/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12255365/) · `full_text` · `limiting` · no number
  - > Interestingly, ripretinib, a fourth-line TKI approved for advanced GIST, also has limited CNS penetration, underscoring an ongoing lack of therapeutic options for CNS metastases [].
  - *Cerebral Metastasis of a Gastrointestinal Stromal Tumor: A Case Report and Literature Review.* — Cureus 2025
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-066** · [PMID 40656249](https://pubmed.ncbi.nlm.nih.gov/40656249/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12255365/) · `abstract_only` · `supporting` · no number
  - > This case underscores the absence of effective systemic treatments for CNS disease, as most TKIs, including imatinib and ripretinib, have poor CNS penetration.
  - *Cerebral Metastasis of a Gastrointestinal Stromal Tumor: A Case Report and Literature Review.* — Cureus 2025
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### SELUMETINIB

2 attributed of 9 retrieved sentences · 0 full text, 2 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 12 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-067** · [PMID 28921565](https://pubmed.ncbi.nlm.nih.gov/28921565/) · `abstract_only` · `supporting` · number
  - > PD0325901 displayed more promising characteristics than trametinib (GSK1120212), binimetinib (MEK162), selumetinib (AZD6244), and pimasertib (AS703026): PD0325901 was the weakest substrate of P-gp and BCRP in vitro, its brain penetration was only marginally higher in Abcb1a/b;Abcg2mice, and efficient target inhibition in the brain could be achieved at clinically relevant plasma levels.
  - *The impact of P-glycoprotein and breast cancer resistance protein on the brain pharmacokinetics and pharmacodynamics of a panel of MEK inhibitors.* — Int J Cancer 2017
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-068** · [PMID 32939452](https://pubmed.ncbi.nlm.nih.gov/32939452/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7486535/) · `abstract_only` · `supporting` · no number
  - > We qualitatively assessed the effect of selumetinib on SNF-related spinal canal distortion, cerebrospinal fluid distribution, and spinal cord deformity on MRI.
  - *The MEK inhibitor selumetinib reduces spinal neurofibroma burden in patients with NF1 and plexiform neurofibromas.* — Neurooncol Adv 2020
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### SORAFENIB

13 attributed of 44 retrieved sentences · 6 full text, 7 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 17 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-069** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `full_text` · `supporting` · number
  - > The CSF penetration of sorafenib was only 0.02% relative to total (free and protein bound) plasma drug exposure.
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-070** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `full_text` · `limiting` · no number
  - > Based on our findings of limited CSF penetration, sorafenib may act in limiting metastatic spread by controlling the primary disease [].
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-071** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `full_text` · `supporting` · no number
  - > Sorafenib is highly protein bound, and thus CSF penetration was calculated using an estimated free drug exposure.
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-072** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `full_text` · `supporting` · no number
  - > The drug exposure of sorafenib in the CSF relative to total and free drug plasma exposure in NHP is limited.
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-073** · [PMID 22335402](https://pubmed.ncbi.nlm.nih.gov/22335402/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3296237/) · `full_text` · `supporting` · no number
  - > Sorafenib was chosen as the model substrate since we have previously shown that its brain penetration is restricted by BCRP and possibly by P-gp.
  - *Insight into the cooperation of P-glycoprotein (ABCB1) and breast cancer resistance protein (ABCG2) at the blood-brain barrier: a case study examining sorafenib efflux clearance.* — Mol Pharm 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-074** · [PMID 32776310](https://pubmed.ncbi.nlm.nih.gov/32776310/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7677279/) · `full_text` · `supporting` · no number
  - > Future studies in younger rats are warranted to verify the influence of age on the brain penetration of sorafenib and its N-oxide.
  - *The Influence of Paracetamol on the Penetration of Sorafenib and Sorafenib N-Oxide Through the Blood-Brain Barrier in Rats.* — Eur J Drug Metab Pharmacokinet 2020
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-075** · [PMID 20952483](https://pubmed.ncbi.nlm.nih.gov/20952483/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3014301/) · `abstract_only` · `supporting` · number
  - > Steady-state brain-to-plasma concentration ratio of sorafenib was approximately 0.36 ± 0.056 in the Bcrp1(-/-) mice, 0.11 ± 0.021 in the Mdr1a/b(-/-) mice, and 0.91 ± 0.29 in the Mdr1a/b(-/-)Bcrp1(-/-) mice compared with 0.094 ± 0.007 in the wild-type mice.
  - *The role of the breast cancer resistance protein (ABCG2) in the distribution of sorafenib to the brain.* — J Pharmacol Exp Ther 2010
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-076** · [PMID 20952483](https://pubmed.ncbi.nlm.nih.gov/20952483/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3014301/) · `abstract_only` · `supporting` · number
  - > Sorafenib brain-to-plasma ratios increased on coadministration of the dual P-gp/BCRP inhibitor elacridar such that the ratio in wild-type mice (0.76 ± 0.24), Bcrp1(-/-) mice (1.03 ± 0.33), Mdr1a/b(-/-) mice (1.3 ± 0.29), and Mdr1a/b(-/-)Bcrp1(-/-) mice (0.73 ± 0.35) were not significantly different.
  - *The role of the breast cancer resistance protein (ABCG2) in the distribution of sorafenib to the brain.* — J Pharmacol Exp Ther 2010
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-077** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `abstract_only` · `supporting` · number
  - > The mean CSF penetration of sorafenib was 0.02% and 3.4% after correcting for plasma protein binding.
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-078** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `abstract_only` · `supporting` · no number
  - > The CSF penetration of sorafenib is limited relative to total and free drug exposure in plasma.
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-079** · [PMID 22335402](https://pubmed.ncbi.nlm.nih.gov/22335402/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3296237/) · `abstract_only` · `supporting` · no number
  - > The present study uses the brain penetration of sorafenib to investigate these findings and attempts to explain the mechanistic basis of this cooperation with a simple theory based on affinity and capacity dependent carrier-mediated transport.
  - *Insight into the cooperation of P-glycoprotein (ABCB1) and breast cancer resistance protein (ABCG2) at the blood-brain barrier: a case study examining sorafenib efflux clearance.* — Mol Pharm 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-080** · [PMID 32776310](https://pubmed.ncbi.nlm.nih.gov/32776310/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7677279/) · `abstract_only` · `supporting` · no number
  - > Pharmacokinetic analysis revealed increased brain exposure to sorafenib and sorafenib N-oxide after co-administration of paracetamol.
  - *The Influence of Paracetamol on the Penetration of Sorafenib and Sorafenib N-Oxide Through the Blood-Brain Barrier in Rats.* — Eur J Drug Metab Pharmacokinet 2020
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-081** · [PMID 36768736](https://pubmed.ncbi.nlm.nih.gov/36768736/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9917080/) · `abstract_only` · `supporting` · no number
  - > Among these problems, the presence of the blood-brain barrier of the brain and the need to use high doses of sorafenib, the existence of mechanisms for the redistribution of sorafenib and its release in the brain tissue, as well as the high resistance of gliomas and glioblastomas to therapy should be considered the main ones.
  - *Ca-Dependent Effects of the Selenium-Sorafenib Nanocomplex on Glioblastoma Cells and Astrocytes of the Cerebral Cortex: Anticancer Agent and Cytoprotector.* — Int J Mol Sci 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### SUNITINIB

11 attributed of 25 retrieved sentences · 3 full text, 8 abstract-only · ChEMBL calculated flag: `predicted_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 5 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-082** · [PMID 37997517](https://pubmed.ncbi.nlm.nih.gov/37997517/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10726873/) · `full_text` · `supporting` · number
  - > One potential reason for this could be due to its limited penetration through an intact BBB.A study by Sobanska and colleagues used a rabbit model to show that the exposure of sunitinib in plasma, aqueous humor, and CSF was different depending on the time of day of drug administration (8 am dose area under the curve [AUC], CSF: 55.5 ng*h/mL vs.
  - *Chemotherapy in pediatric brain tumor and the challenge of the blood-brain barrier.* — Cancer Med 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-083** · [PMID 37997517](https://pubmed.ncbi.nlm.nih.gov/37997517/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10726873/) · `full_text` · `supporting` · number
  - > 9 pm dose AUC, CSF: 66.3 ng*h/mL, respectively).However, sunitinib penetration through the BBB was reported to be very low (<5%) and comparable in both dosing groups.
  - *Chemotherapy in pediatric brain tumor and the challenge of the blood-brain barrier.* — Cancer Med 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-084** · [PMID 37997517](https://pubmed.ncbi.nlm.nih.gov/37997517/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10726873/) · `full_text` · `supporting` · number
  - > To overcome the limitations of the BBB, a study by Szalek and colleagues evaluated the antibiotic ciprofloxacin to modulate the BBB and enhance penetration of sunitinib.They found that rabbits treated with sunitinib + ciprofloxacin had higher 24‐h CSF exposures (AUCand C) compared to those that only received sunitinib (50.4 vs.
  - *Chemotherapy in pediatric brain tumor and the challenge of the blood-brain barrier.* — Cancer Med 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-085** · [PMID 22166826](https://pubmed.ncbi.nlm.nih.gov/22166826/) · `abstract_only` · `supporting` · number
  - > The chemotherapy (gemcitabine and cisplatin) and the molecular target therapy (sunitinib) were administerd but the primary lesion and metastases was progressive and serum G-CSF concentration was elevated to 229 pg/ml.
  - *[Granulocyte-colony-stimulating factor (G-CSF)-producing carcinoma of collecting ducts of Bellini: a case report].* — Hinyokika Kiyo 2011
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-086** · [PMID 26813470](https://pubmed.ncbi.nlm.nih.gov/26813470/) · `abstract_only` · `supporting` · number
  - > The concentrations of sunitinib and its active metabolite (SU12662) in the plasma, CSF, AH were measured with the validated HPLC-UV method.
  - *The influence of the time-of-day administration of sunitinib on the penetration through the blood-brain and blood-aqueous humour barriers in rabbits.* — Eur Rev Med Pharmacol Sci 2016
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-087** · [PMID 26813470](https://pubmed.ncbi.nlm.nih.gov/26813470/) · `abstract_only` · `supporting` · number
  - > After the evening administration (8 p.m.) the exposure to sunitinib in the rabbits' plasma, AH and CSF was higher than after the morning administration (8 a.m.), but the degree of sunitinib penetration through the BAB and BBB was very low (< 5%) and comparable in both groups.
  - *The influence of the time-of-day administration of sunitinib on the penetration through the blood-brain and blood-aqueous humour barriers in rabbits.* — Eur Rev Med Pharmacol Sci 2016
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-088** · [PMID 20524040](https://pubmed.ncbi.nlm.nih.gov/20524040/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2997175/) · `abstract_only` · `supporting` · no number
  - > These results indicate that sunitinib may be an important pharmacologic agent for the treatment of invasive medulloblastoma, particularly given evidence of its ability to cross the blood-brain barrier to target tumor cells, and thus warrants further in vivo testing for confirmation of efficacy.
  - *Sunitinib induces PTEN expression and inhibits PDGFR signaling and migration of medulloblastoma cells.* — J Neurooncol 2010
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-089** · [PMID 22238213](https://pubmed.ncbi.nlm.nih.gov/22238213/) · `abstract_only` · `supporting` · no number
  - > Combined elacridar plus N-desethyl sunitinib treatment increased N-desethyl sunitinib plasma and brain exposures, but not brain-to-plasma ratios in wild-type mice.
  - *P-glycoprotein (ABCB1) and breast cancer resistance protein (ABCG2) restrict brain accumulation of the active sunitinib metabolite N-desethyl sunitinib.* — J Pharmacol Exp Ther 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-090** · [PMID 24113148](https://pubmed.ncbi.nlm.nih.gov/24113148/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3836310/) · `abstract_only` · `supporting` · no number
  - > Overall, these findings indicate that there is a cooperation at the blood-brain barrier (BBB) in restricting the brain penetration of sunitinib, and brain delivery can be enhanced by administration of a dual inhibitor.
  - *Pharmacokinetic assessment of efflux transport in sunitinib distribution to the brain.* — J Pharmacol Exp Ther 2013
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-091** · [PMID 26813470](https://pubmed.ncbi.nlm.nih.gov/26813470/) · `abstract_only` · `supporting` · no number
  - > Therefore, the penetration of sunitinib through the blood-brain barrier (BBB) and blood-aqueous humour barrier (BAB) is an issue of growing interest.
  - *The influence of the time-of-day administration of sunitinib on the penetration through the blood-brain and blood-aqueous humour barriers in rabbits.* — Eur Rev Med Pharmacol Sci 2016
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-092** · [PMID 26813470](https://pubmed.ncbi.nlm.nih.gov/26813470/) · `abstract_only` · `supporting` · no number
  - > The aim of the study was to investigate the influence of the time-of-day administration on the penetration of sunitinib into the cerebrospinal fluid (CSF) and aqueous humour (AH).
  - *The influence of the time-of-day administration of sunitinib on the penetration through the blood-brain and blood-aqueous humour barriers in rabbits.* — Eur Rev Med Pharmacol Sci 2016
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### TIVOZANIB

1 attributed of 2 retrieved sentences · 0 full text, 1 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_record` · CNS-manifestation trial evidence on 0 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-093** · [PMID 32234426](https://pubmed.ncbi.nlm.nih.gov/32234426/) · `abstract_only` · `limiting` · no number
  - > The modest effect of ABC transporters on tivozanib brain accumulation, if also true in humans, might mean that this drug is not strongly limited in its therapeutic efficacy against malignant lesions situated partly or completely behind the blood-brain barrier.
  - *Brain accumulation of tivozanib is restricted by ABCB1 (P-glycoprotein) and ABCG2 (breast cancer resistance protein) in mice.* — Int J Pharm 2020
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### TOVORAFENIB

3 attributed of 4 retrieved sentences · 1 full text, 2 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 7 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-094** · [PMID 38291372](https://pubmed.ncbi.nlm.nih.gov/38291372/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10826080/) · `full_text` · `supporting` · no number
  - > Finally, tovorafenib had greater CNS penetration compared with the type I RAF inhibitor dabrafenib [].
  - *LOGGIC/FIREFLY-2: a phase 3, randomized trial of tovorafenib vs. chemotherapy in pediatric and young adult patients with newly diagnosed low-grade glioma harboring an activating RAF alteration.* — BMC Cancer 2024
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-095** · [PMID 30622172](https://pubmed.ncbi.nlm.nih.gov/30622172/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6374543/) · `abstract_only` · `supporting` · number
  - > The purpose of this study was to perform a quantitative assessment and evaluation of the influence of efflux mechanisms at the blood-brain barrier (BBB), in particular, Abcb1/P-glycoprotein (P-gp) and Abcg2/breast cancer resistance protein (Bcrp), on the brain distribution of three panRAF inhibitors: CCT196969 [1-(3-(-butyl)-1-phenyl-1-pyrazol-5-yl)-3-(2-fluoro-4-((3-oxo-3,4-dihydropyrido[2,3-b]pyrazin-8-yl)oxy)phenyl)urea], LY3009120 1-(3,3-Dimethylbutyl)-3-(2-fluoro-4-methyl-5-(7-methyl-2-(methylamino)pyrido(2,3-d)pyrimidin-6-yl)phenyl)urea, and MLN2480 [4-pyrimidinecarboxamide, 6-amino-5-chloro--[(1)-1-[5-[[[5-chloro-4-(trifluoromethyl)-2-pyridinyl]amino]carbonyl]-2-thiazolyl]ethyl]-].
  - *Brain Distribution and Active Efflux of Three panRAF Inhibitors: Considerations in the Treatment of Melanoma Brain Metastases.* — J Pharmacol Exp Ther 2019
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-096** · [PMID 38884947](https://pubmed.ncbi.nlm.nih.gov/38884947/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11404696/) · `abstract_only` · `supporting` · no number
  - > The advent of pan-RAF inhibitors, notably Tovorafenib, offers a promising advance, demonstrating enhanced efficacy and better penetration of the blood-brain barrier, without the issue of paradoxical activation.
  - *A critical review of RAF inhibitors in BRAF-mutated glioma treatment.* — Pharmacogenomics 2024
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### TRAMETINIB

2 attributed of 13 retrieved sentences · 0 full text, 2 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 2 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-097** · [PMID 24875464](https://pubmed.ncbi.nlm.nih.gov/24875464/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4109207/) · `abstract_only` · `supporting` · no number
  - > In vitro studies indicated that trametinib is a substrate for both P-glycoprotein (P-gp) and Bcrp, efflux transporters found at the blood-brain barrier.
  - *Factors influencing the CNS distribution of a novel MEK-1/2 inhibitor: implications for combination therapy for melanoma brain metastases.* — Drug Metab Dispos 2014
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-098** · [PMID 31063549](https://pubmed.ncbi.nlm.nih.gov/31063549/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7571492/) · `abstract_only` · `supporting` · no number
  - > In vivo, PK analysis revealed enhanced blood-brain barrier penetration of trametinib after oHSV treatment.
  - *Oncolytic HSV therapy increases trametinib access to brain tumors and sensitizes them in vivo.* — Neuro Oncol 2019
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______

### VEMURAFENIB

26 attributed of 42 retrieved sentences · 14 full text, 12 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 0 drug rows

**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-099** · [PMID 26579371](https://pubmed.ncbi.nlm.nih.gov/26579371/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4590304/) · `full_text` · `supporting` · number
  - > Furthermore, in their knockout mouse model, the brain-to-plasma ratios of vemurafenib were increased significantly when Abc1a/1b and Abcg2 were both absent.
  - *The pharmacological impact of ATP-binding cassette drug transporters on vemurafenib-based therapy.* — Acta Pharm Sin B 2014
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-100** · [PMID 26579371](https://pubmed.ncbi.nlm.nih.gov/26579371/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4590304/) · `full_text` · `supporting` · number
  - > Durmus et al.reported that inhibition of both ABCB1 and ABCG2 could significantly improve the bioavailability (A) and brain penetration (B) of vemurafenib.
  - *The pharmacological impact of ATP-binding cassette drug transporters on vemurafenib-based therapy.* — Acta Pharm Sin B 2014
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-101** · [PMID 26579371](https://pubmed.ncbi.nlm.nih.gov/26579371/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4590304/) · `full_text` · `supporting` · number
  - > The clinical application of a dual ABCB1 and ABCG2 inhibitor such as elacridar could possibly provide a solution to increase the oral bioavailability and enhance brain penetration of vemurafenib in patients with brain metastatic melanoma.
  - *The pharmacological impact of ATP-binding cassette drug transporters on vemurafenib-based therapy.* — Acta Pharm Sin B 2014
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-102** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > These observations seem to be corroborated by a clinical study showing that the concentration of vemurafenib in cerebrospinal fluid (CSF) was < 1% of the plasma concentration [].
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-103** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > Vemurafenib has intrinsic antitumor potential against intracranial A375 tumors The brain penetration of vemurafenib was previously reported to be significantly higher (between approximately 20‐ and 80‐fold) incompared with WT mice [,].
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-104** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > Vemurafenib penetration into subcutaneous tumors is similar in WT andmice and as we found that vemurafenib was equally effective (Fig.) and did not result in body weight loss (Fig.), we selected these dose regimens for the efficacy study against intracranial A375 tumors.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-105** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > These drug distribution data are in line with the observed intracranial antitumor efficacy (Fig.), as vemurafenib tumor concentrations were similar between WT mice receiving 25 mg·kgand WT mice receiving 10 mg·kgof vemurafenib with concomitant elacridar, but lower than inmice receiving 10 or 25 mg·kgvemurafenib.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-106** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > Intracranial A375 tumors develop therapy resistance despite sufficient vemurafenib tumor penetration and target inhibition As mentioned above, the A375 MBM model is responsive to vemurafenib, but developed therapy resistance after just a few days of treatment inmice receiving 10 mg·kgvemurafenib (Fig.).
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-107** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > Since the vemurafenib concentration in responsive short‐term (5 days) treated tumors and resistant long‐term (10 days) treated tumors was similar, we explored alternative ways by which intracranial A375 tumor may acquire resistance in a small pilot cohort we had available for immunohistochemical analysis (= 2 per group).
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-108** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > 4 Vemurafenib concentrations in short‐term and long‐term treated intracranial A375 tumors.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-109** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · no number
  - > Several preclinical studies have demonstrated that vemurafenib [,], dabrafenib [], and encorafenib [] exhibit very poor brain penetration in mice as a result of efficient efflux by P‐glycoprotein (P‐gp;
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-110** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · no number
  - > Therefore, P‐gp/BCRP inhibitors might help to improve the clinical response of MBMs to vemurafenib by increasing its brain penetration, but pinpointing the mechanism behind the brain‐specific acquired resistance will likely be necessary to produce durable responses.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-111** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · no number
  - > Dose adaptions between WT andmice are needed to level the systemic exposure of vemurafenib between strains The aim of this study was to assess the impact of P‐gp and BCRP at the BBB on the intracranial efficacy of vemurafenib against MBMs by comparing WT andmice.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-112** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · no number
  - > P‐gp and BCRP reduce vemurafenib penetration in MBMs P‐gp and BCRP limit the brain penetration of vemurafenib by virtue of their efflux function at the BBB [,].
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-113** · [PMID 22454535](https://pubmed.ncbi.nlm.nih.gov/22454535/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3383040/) · `abstract_only` · `supporting` · number
  - > The steady-state brain-to-plasma ratio of vemurafenib was 0.035 ± 0.009 in Mdr1a/b(-/-) mice, 0.009 ± 0.006 in Bcrp1(-/-) mice, and 1.00 ± 0.19 in Mdr1a/b(-/-)Bcrp1(-/-) mice compared with 0.012 ± 0.004 in wild-type mice.
  - *Impact of P-glycoprotein (ABCB1) and breast cancer resistance protein (ABCG2) on the brain distribution of a novel BRAF inhibitor: vemurafenib (PLX4032).* — J Pharmacol Exp Ther 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-114** · [PMID 23020847](https://pubmed.ncbi.nlm.nih.gov/23020847/) · `abstract_only` · `supporting` · number
  - > We aimed to establish whether oral availability and brain penetration of vemurafenib could be restricted by the multidrug efflux transporters P-glycoprotein (P-gp/ABCB1) and breast cancer resistance protein (BCRP/ABCG2), as these might limit therapeutic efficacy, especially against brain metastases.
  - *Oral availability and brain penetration of the B-RAFV600E inhibitor vemurafenib can be enhanced by the P-GLYCOprotein (ABCB1) and breast cancer resistance protein (ABCG2) inhibitor elacridar.* — Mol Pharm 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-115** · [PMID 23020847](https://pubmed.ncbi.nlm.nih.gov/23020847/) · `abstract_only` · `supporting` · number
  - > Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice, indicating pronounced overlapping functions of these transporters in reducing vemurafenib brain accumulation.
  - *Oral availability and brain penetration of the B-RAFV600E inhibitor vemurafenib can be enhanced by the P-GLYCOprotein (ABCB1) and breast cancer resistance protein (ABCG2) inhibitor elacridar.* — Mol Pharm 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-116** · [PMID 23020847](https://pubmed.ncbi.nlm.nih.gov/23020847/) · `abstract_only` · `supporting` · number
  - > As predicted by previously described pharmacokinetic modeling, halving the amount of active efflux transport at the WT blood-brain barrier by testing heterozygous Abcb1a/1b(+/-);Abcg2(+/-) mice had little impact on vemurafenib brain accumulation.
  - *Oral availability and brain penetration of the B-RAFV600E inhibitor vemurafenib can be enhanced by the P-GLYCOprotein (ABCB1) and breast cancer resistance protein (ABCG2) inhibitor elacridar.* — Mol Pharm 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-117** · [PMID 25933211](https://pubmed.ncbi.nlm.nih.gov/25933211/) · `abstract_only` · `limiting` · number
  - > In conclusion, our preliminary results highlight for the first time a low CSF vemurafenib penetration rate associated with a large interindividual variability in patients treated for metastatic BRAF-V600 mutated melanoma and brain metastases.
  - *Cerebrospinal fluid concentrations of vemurafenib in patients treated for brain metastatic BRAF-V600 mutated melanoma.* — Melanoma Res 2015
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-118** · [PMID 25933211](https://pubmed.ncbi.nlm.nih.gov/25933211/) · `abstract_only` · `supporting` · number
  - > The mean plasma and CSF concentrations of vemurafenib were 53.4±26.2 and 0.47±0.37 mg/l, respectively.
  - *Cerebrospinal fluid concentrations of vemurafenib in patients treated for brain metastatic BRAF-V600 mutated melanoma.* — Melanoma Res 2015
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-119** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `abstract_only` · `supporting` · number
  - > We intracranially implanted A375 melanoma cells in wild-type (WT) and Abcb1a/b;Abcg2mice, characterized the tumor BBB, analyzed drug levels in plasma and brain lesions after oral vemurafenib administration, and determined the efficacy against brain metastases and subcutaneous lesions.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-120** · [PMID 41097037](https://pubmed.ncbi.nlm.nih.gov/41097037/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12524707/) · `abstract_only` · `supporting` · number
  - > Further ranking according to their blood-brain barrier permeability, as well as structural and transcriptomic similarities to known anti-GBM drugs, revealed SP600125, vemurafenib, FG-7142, dibenzoylmethane, and phensuximide as the most promising for GMT inhibition.
  - *Transcriptomic-Driven Drug Repurposing Reveals SP600125 as a Promising Drug Candidate for the Treatment of Glial-Mesenchymal Transition in Glioblastoma.* — Int J Mol Sci 2025
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-121** · [PMID 22454535](https://pubmed.ncbi.nlm.nih.gov/22454535/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3383040/) · `abstract_only` · `limiting` · no number
  - > These data indicate that the brain distribution of vemurafenib is severely restricted at the blood-brain barrier because of active efflux by both P-gp and BCRP.
  - *Impact of P-glycoprotein (ABCB1) and breast cancer resistance protein (ABCG2) on the brain distribution of a novel BRAF inhibitor: vemurafenib (PLX4032).* — J Pharmacol Exp Ther 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-122** · [PMID 23020847](https://pubmed.ncbi.nlm.nih.gov/23020847/) · `abstract_only` · `supporting` · no number
  - > Our data suggest that elacridar coadministration may be considered to improve the therapeutic efficacy of vemurafenib, especially for brain metastases located behind a functional blood-brain barrier.
  - *Oral availability and brain penetration of the B-RAFV600E inhibitor vemurafenib can be enhanced by the P-GLYCOprotein (ABCB1) and breast cancer resistance protein (ABCG2) inhibitor elacridar.* — Mol Pharm 2012
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-123** · [PMID 25933211](https://pubmed.ncbi.nlm.nih.gov/25933211/) · `abstract_only` · `supporting` · no number
  - > The concentrations of vemurafenib in the CSF and the plasma were measured by high-performance liquid chromatography.
  - *Cerebrospinal fluid concentrations of vemurafenib in patients treated for brain metastatic BRAF-V600 mutated melanoma.* — Melanoma Res 2015
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
- **CNS-124** · [PMID 25933211](https://pubmed.ncbi.nlm.nih.gov/25933211/) · `abstract_only` · `supporting` · no number
  - > Further investigations with larger cohorts are required to study the relationship between CSF vemurafenib concentrations and cerebral response.
  - *Cerebrospinal fluid concentrations of vemurafenib in patients treated for brain metastatic BRAF-V600 mutated melanoma.* — Melanoma Res 2015
  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______
