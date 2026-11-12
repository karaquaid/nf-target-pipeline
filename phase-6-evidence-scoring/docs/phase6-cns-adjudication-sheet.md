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

**Proposed drug verdict: `demonstrated`** — 4 primary human claim(s), all demonstrated. Decisive claim(s): CNS-001, CNS-005, CNS-006, CNS-008.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-001** · [PMID 40086436](https://pubmed.ncbi.nlm.nih.gov/40086436/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12121847/) · `full_text` · `supporting` · number
  - > Case 2 demonstrated an increase in the CSF/plasma ratio during the course of treatment, with tumor tissue reaching a concentration of 4μM avapritinib following six months of treatment ().
  - *Effective targeting of PDGFRA-altered high-grade glioma with avapritinib.* — Cancer Cell 2025
  - **proposed: `demonstrated`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF concentration / CSF:plasma ratio / tumor tissue concentration = CSF levels of avapritinib (15-46nM); tumor tissue concentration 4μM after six months; increase in CSF/plasma ratio over treatment course · confidence high
  - rationale: Primary human CSF and tumor tissue concentrations measured directly in patients on treatment; CSF/plasma ratio rose and CSF levels were quantified (15-46nM), plus tumor tissue reached 4μM, directly demonstrating CNS exposure.
  - span relied on: “Case 2 demonstrated an increase in the CSF/plasma ratio during the course of treatment, with tumor tissue reaching a concentration of 4μM avapritinib following six months of treatment ( Figure S7C ). CSF levels of avapritinib (15 −46nM) in both cases were substantially higher compared to dasatinib levels in Case 2 (~2nM)”
  - read from: pmc_body / Avapritinib shows radiographic response in a subset of pediatric and young adult HGG patients with PDGFRA alterations · **your verdict:** _______
- **CNS-002** · [PMID 38167404](https://pubmed.ncbi.nlm.nih.gov/38167404/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761696/) · `full_text` · `supporting` · no number
  - > These effects most likely result from avapritinib’s ability to penetrate the blood-brain barrier (BBB) and interact with unidentified targets in the brain.
  - *Avapritinib-based SAR studies unveil a binding pocket in KIT and PDGFRA.* — Nat Commun 2024
  - **proposed: `demonstrated`** · basis `clinical_cns_response` · restated · human · arm `not_applicable` · clinical CNS adverse effect (cognitive side effects) = cognitive side effects are a concern in a subset of patients · confidence medium · **flagged for human check**
  - rationale: No measured brain/CSF concentration or Kp,uu given; claim is an inferential restatement explaining clinical cognitive AEs. Clinical CNS activity (cognitive toxicity in patients) supports demonstrated per rubric, but no direct exposure data provided.
  - span relied on: “cognitive side effects are a concern in a subset of patients, particularly when risk-mitigation strategies, such as early treatment interruptions, are not followed. These effects most likely result from avapritinib’s ability to penetrate the blood-brain barrier (BBB) and interact with unidentified targets in the brain”
  - read from: pmc_body / Introduction · **your verdict:** _______
- **CNS-003** · [PMID 40086436](https://pubmed.ncbi.nlm.nih.gov/40086436/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12121847/) · `full_text` · `supporting` · no number
  - > Avapritinib treatment results in efficient brain penetrance and prolonged survival in-altered DMG models We next asked whether avapritinib crosses the blood-brain barrier and impacts tumor growth in-altered glioma animal models.
  - *Effective targeting of PDGFRA-altered high-grade glioma with avapritinib.* — Cancer Cell 2025
  - **proposed: `demonstrated`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain tissue concentration = brain tissue concentrations reaching their maximum at 10μM two hours post-ingestion; steady state brain concentrations of 1μM exceeding in vitro IC50 by 2-12 fold · confidence high
  - rationale: Primary PK data in normal (non-knockout, non-BBB-modified) mice show measured brain tissue concentrations of avapritinib exceeding in vitro IC50, directly demonstrating CNS exposure.
  - span relied on: “Pharmacokinetic analysis of avapritinib in non-tumor-bearing CD-1 mice showed a peak concentration of 10 μg/mL (20.08 μM) occurring at two hours following one oral dose, with brain tissue concentrations reaching their maximum at 10μM two hours post-ingestion ( Figure 3A ). ... Following eight days of daily avapritinib dosing to achieve steady state levels, brain tissues exhibited avapritinib concentrations of 1μM, exceeding IC 50 values observed in vitro by 2-12 fold ( Figure S6B ).”
  - read from: pmc_body / Avapritinib treatment results in efficient brain penetrance and prolonged survival in PDGFRA -altered DMG models in vivo · **your verdict:** _______
- **CNS-004** · [PMID 40086436](https://pubmed.ncbi.nlm.nih.gov/40086436/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12121847/) · `full_text` · `supporting` · no number
  - > In summary, we show that avapritinib efficiently crosses the blood brain barrier to achieve supratherapeutic concentrations in target brain tissue.
  - *Effective targeting of PDGFRA-altered high-grade glioma with avapritinib.* — Cancer Cell 2025
  - **proposed: `demonstrated`** · basis `preclinical_cns_efficacy` · primary · mouse · arm `normal` · brain tissue concentration = supratherapeutic concentrations in target brain tissue · confidence high
  - rationale: Section title and summary sentence report measured brain tissue drug concentration exceeding therapeutic threshold in an in vivo PDGFRA-altered glioma model, a primary CNS exposure finding, not an unsupported assertion.
  - span relied on: “avapritinib efficiently crosses the blood brain barrier to achieve supratherapeutic concentrations in target brain tissue”
  - read from: pmc_body / Avapritinib treatment results in efficient brain penetrance and prolonged survival in PDGFRA -altered DMG models in vivo · **your verdict:** _______
- **CNS-005** · [PMID 41961082](https://pubmed.ncbi.nlm.nih.gov/41961082/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13068680/) · `full_text` · `limiting` · no number
  - > Although data on CNS penetration of avapritinib in AML are limited, and CSF levels of avapritinib were not available in this case, preclinical studies and early clinical data in-mutated gliomas suggest that the drug can effectively cross the blood–brain barrier and exert antitumor activity within the CNS [].
  - *Avapritinib for targeting KIT D816V-mutated acute myeloid leukemia relapsed after allogeneic hematopoietic stem cell transplant with extramedullary and central nervous system involvement.* — Ann Hematol 2026
  - **proposed: `demonstrated`** · basis `clinical_cns_response` · primary · human · arm `not_applicable` · none (clinical CNS response, no exposure quantity) = nan · confidence medium · **flagged for human check**
  - rationale: No CSF/brain concentration measured ("CSF levels... were not available"), and the crossing-BBB claim is a restated assertion citing other studies. But this case report documents an actual clinical CNS response (molecular remission of CNS-involved AML, sustained >1 year, rechallenge response) to avapritinib in this patient.
  - span relied on: “achieved molecular remission with avapritinib alone... the effective management of extramedullary disease involving the CNS... highlights the potential of this agent... the observed CNS response is particularly significant”
  - read from: pmc_body / Case report · **your verdict:** _______
- **CNS-006** · [PMID 40086436](https://pubmed.ncbi.nlm.nih.gov/40086436/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12121847/) · `abstract_only` · `supporting` · number
  - > We reveal that the PDGFRA/KIT inhibitor avapritinib shows (1) selectivity for PDGFRA inhibition, (2) distinct patterns of subcellular effects, (3) in vitro and in vivo activity in patient-derived HGG models, and (4) effective blood-brain barrier penetration in mice and humans.
  - *Effective targeting of PDGFRA-altered high-grade glioma with avapritinib.* — Cancer Cell 2025
  - **proposed: `demonstrated`** · basis `clinical_cns_response` · primary · human · arm `normal` · none (qualitative BBB penetration + radiographic response in CNS tumor) = nan · confidence medium · **flagged for human check**
  - rationale: Abstract states effective BBB penetration in mice and humans plus radiographic response in recurrent PDGFRA-altered HGG patients, i.e., clinical activity against a CNS tumor site, supporting demonstrated despite no numeric exposure value given.
  - span relied on: “effective blood-brain barrier penetration in mice and humans ... results in radiographic response in 3/7 cases”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-007** · [PMID 38167404](https://pubmed.ncbi.nlm.nih.gov/38167404/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761696/) · `abstract_only` · `supporting` · no number
  - > We utilize this information to design, synthesize and characterize avapritinib derivatives for the determination of key pharmacophoric features to overcome drug resistance and limit potential blood-brain barrier penetration.
  - *Avapritinib-based SAR studies unveil a binding pocket in KIT and PDGFRA.* — Nat Commun 2024
  - **proposed: `unknown`** · basis `design_or_prediction` · primary · na · arm `not_applicable` · none = nan · confidence medium
  - rationale: No measured brain/CSF exposure for avapritinib is reported; text is a design goal (limiting future derivatives' BBB penetration) and mention of neuro-cognitive side effects, not a PK measurement.
  - span relied on: “patients eventually progress, mostly due to acquired resistance mutations or following discontinuation due to neuro-cognitive side effects”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-008** · [PMID 41961082](https://pubmed.ncbi.nlm.nih.gov/41961082/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13068680/) · `abstract_only` · `supporting` · no number
  - > Remarkably, rechallenge with single‑agent avapritinib again induced molecular remission in both peripheral blood and cerebrospinal fluid, along with near‑complete metabolic response across all previously involved sites.
  - *Avapritinib for targeting KIT D816V-mutated acute myeloid leukemia relapsed after allogeneic hematopoietic stem cell transplant with extramedullary and central nervous system involvement.* — Ann Hematol 2026
  - **proposed: `demonstrated`** · basis `clinical_cns_response` · primary · human · arm `normal` · clinical CNS response (molecular remission in CSF) = molecular remission in both peripheral blood and cerebrospinal fluid · confidence high
  - rationale: Single-agent avapritinib produced molecular remission in CSF and clinical/neurological improvement, indicating direct clinical activity against CNS leukemic involvement in a human patient, no BBB-opening co-intervention used.
  - span relied on: “rechallenge with single‑agent avapritinib again induced molecular remission in both peripheral blood and cerebrospinal fluid, along with near‑complete metabolic response across all previously involved sites”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### BINIMETINIB

2 attributed of 14 retrieved sentences · 1 full text, 1 abstract-only · ChEMBL calculated flag: `predicted_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 8 drug rows

**Proposed drug verdict: `unknown`** — No primary, normal-arm claim carries a measured or clinical finding. Decisive claim(s): nan.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-009** · [PMID 41369830](https://pubmed.ncbi.nlm.nih.gov/41369830/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12799883/) · `full_text` · `supporting` · number
  - > These results highlight the potential of encorafenib plus binimetinib to provide meaningful intracranial tumor shrinkage and improved complete responses in patients with BRAF V600-mutant melanoma with brain metastases, although the considerable heterogeneity across included studies suggests that these findings should be interpreted with caution.
  - *The safety and efficacy of encorafenib plus binimetinib for brain metastases: a systematic review and meta-analysis.* — Discov Oncol 2025
  - **proposed: `demonstrated`** · basis `clinical_cns_response` · restated · human · arm `not_applicable` · intracranial CR/ORR/PR (clinical response in brain metastases) = intracranial CR rate higher than prior studies; intracranial ORR and PR generally comparable · confidence medium · **flagged for human check**
  - rationale: Meta-analysis reports clinical intracranial response (CR/ORR/PR) for the encorafenib+binimetinib combination in brain metastases, indicating CNS activity, though it is a combination therapy and a review restatement of pooled trial data.
  - span relied on: “The intracranial CR rate observed with encorafenib plus binimetinib was higher than that reported in prior dual, triplet, or monotherapy studies, while intracranial ORR and PR were generally comparable”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-010** · [PMID 28921565](https://pubmed.ncbi.nlm.nih.gov/28921565/) · `abstract_only` · `supporting` · number
  - > PD0325901 displayed more promising characteristics than trametinib (GSK1120212), binimetinib (MEK162), selumetinib (AZD6244), and pimasertib (AS703026): PD0325901 was the weakest substrate of P-gp and BCRP in vitro, its brain penetration was only marginally higher in Abcb1a/b;Abcg2mice, and efficient target inhibition in the brain could be achieved at clinically relevant plasma levels.
  - *The impact of P-glycoprotein and breast cancer resistance protein on the brain pharmacokinetics and pharmacodynamics of a panel of MEK inhibitors.* — Int J Cancer 2017
  - **proposed: `unknown`** · basis `design_or_prediction` · primary · mouse · arm `not_applicable` · none = nan · confidence low · **flagged for human check**
  - rationale: Abstract compares PD0325901 favorably to binimetinib without giving binimetinib's own brain penetration, Kp,uu, or CSF/brain-plasma ratio values; no exposure quantity for binimetinib specifically is stated.
  - span relied on: “PD0325901 displayed more promising characteristics than trametinib (GSK1120212), binimetinib (MEK162), selumetinib (AZD6244), and pimasertib (AS703026)”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### COBIMETINIB

3 attributed of 19 retrieved sentences · 0 full text, 3 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 12 drug rows

**Proposed drug verdict: `contradicted`** — 2 primary mouse claim(s), all contradicted. Decisive claim(s): CNS-011, CNS-012.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-011** · [PMID 25243894](https://pubmed.ncbi.nlm.nih.gov/25243894/) · `abstract_only` · `supporting` · number
  - > The objectives of this study were to determine in vitro and in vivo if cobimetinib is a substrate of P-glycoprotein (P-gp) and/or breast cancer resistance protein (Bcrp1) and to assess the implications of efflux on cobimetinib pharmacokinetics (PK), brain penetration, and target modulation.
  - *Role of P-glycoprotein on the brain penetration and brain pharmacodynamic activity of the MEK inhibitor cobimetinib.* — Mol Pharm 2014
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma Kp = mean total brain to plasma ratio (Kp) at 6 h postdose was 0.3 and 0.2 in WT and Bcrp1(-/-) mice · confidence high
  - rationale: WT mouse Kp of 0.3 is low, indicating brain exclusion under normal P-gp function; KO/elacridar arms (Kp 11, 6, 7) reflect transporter removal, not native patient exposure.
  - span relied on: “After an oral 10 mg/kg dose of cobimetinib, the mean total brain to plasma ratio (Kp) at 6 h postdose was 0.3 and 0.2 in WT and Bcrp1(-/-) mice, respectively.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-012** · [PMID 25243894](https://pubmed.ncbi.nlm.nih.gov/25243894/) · `abstract_only` · `supporting` · number
  - > After an oral 10 mg/kg dose of cobimetinib, the mean total brain to plasma ratio (Kp) at 6 h postdose was 0.3 and 0.2 in WT and Bcrp1(-/-) mice, respectively.
  - *Role of P-glycoprotein on the brain penetration and brain pharmacodynamic activity of the MEK inhibitor cobimetinib.* — Mol Pharm 2014
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma Kp = 0.3 (WT), 0.2 (Bcrp1-/-) · confidence high
  - rationale: WT mouse Kp of 0.3 is a low brain:plasma ratio indicating exclusion from CNS; Bcrp1-/- arm is also low (0.2). Only elacridar/Mdr1a/b-/- arms showed high Kp, reflecting transporter removal, not normal exposure.
  - span relied on: “the mean total brain to plasma ratio (Kp) at 6 h postdose was 0.3 and 0.2 in WT and Bcrp1(-/-) mice, respectively”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-013** · [PMID 40975475](https://pubmed.ncbi.nlm.nih.gov/40975475/) · `abstract_only` · `supporting` · number
  - > Of these, we selected only the 11 which can cross the blood-brain barrier: cobimetinib, panobinostat, melphalan, rucaparib, alectinib, ponatinib, danazol, carboplatin, vandetanib, erlotinib, and gefitinib.
  - *Transcriptomic profiling unveils novel therapeutic options for drug-resistant temporal lobe epilepsy.* — Eur J Pharmacol 2025
  - **proposed: `unknown`** · basis `design_or_prediction` · restated · na · arm `not_applicable` · none = nan · confidence high
  - rationale: This is a curation-criterion assertion from a drug-repurposing screen, not a measured CSF/brain concentration or ratio for cobimetinib; no exposure data or clinical CNS activity reported for this drug.
  - span relied on: “we selected only the 11 which can cross the blood-brain barrier: cobimetinib, panobinostat, melphalan, rucaparib, alectinib, ponatinib, danazol, carboplatin, vandetanib, erlotinib, and gefitinib”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### DABRAFENIB

2 attributed of 14 retrieved sentences · 2 full text, 0 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 10 drug rows

**Proposed drug verdict: `demonstrated`** — 1 primary human claim(s), all demonstrated. Decisive claim(s): CNS-014.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-014** · [PMID 32817058](https://pubmed.ncbi.nlm.nih.gov/32817058/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7437885/) · `full_text` · `supporting` · no number
  - > In line with other clinical responses,the initial response of the brain lesion to dabrafenib suggested that the drug did cross the blood-brain barrier, and our data suggest that resistance was not mediated by cell-intrinsic events, so we examined if resistance was mediated by factors in the brain microenvironment.
  - *Brain microenvironment-driven resistance to immune and targeted therapies in acral melanoma.* — ESMO Open 2020
  - **proposed: `demonstrated`** · basis `clinical_cns_response` · primary · human · arm `not_applicable` · none - clinical response of brain lesion = nan · confidence medium · **flagged for human check**
  - rationale: Reports a clinical brain lesion response to dabrafenib in a patient, i.e. clinical activity at a CNS disease site, not merely a prediction or in-vitro assay.
  - span relied on: “the initial response of the brain lesion to dabrafenib suggested that the drug did cross the blood-brain barrier”
  - read from: pmc_body / Resistance to targeted therapy in the brain · **your verdict:** _______
- **CNS-015** · [PMID 38291372](https://pubmed.ncbi.nlm.nih.gov/38291372/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10826080/) · `full_text` · `supporting` · no number
  - > Finally, tovorafenib had greater CNS penetration compared with the type I RAF inhibitor dabrafenib [].
  - *LOGGIC/FIREFLY-2: a phase 3, randomized trial of tovorafenib vs. chemotherapy in pediatric and young adult patients with newly diagnosed low-grade glioma harboring an activating RAF alteration.* — BMC Cancer 2024
  - **proposed: `unknown`** · basis `review_restatement` · restated · na · arm `not_applicable` · none = nan · confidence high
  - rationale: Background-section comparative assertion citing another reference, no exposure numbers (CSF/brain conc, Kp,uu, B:P) for dabrafenib given in text; restatement, not a measurement.
  - span relied on: “tovorafenib had greater CNS penetration compared with the type I RAF inhibitor dabrafenib”
  - read from: pmc_body / Background · **your verdict:** _______

### DASATINIB

9 attributed of 74 retrieved sentences · 1 full text, 8 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_record` · CNS-manifestation trial evidence on 0 drug rows

**Proposed drug verdict: left blank** — Primary human claims disagree (contradicted, demonstrated); left for the reviewer rather than resolved by majority.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-016** · [PMID 32493453](https://pubmed.ncbi.nlm.nih.gov/32493453/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7268320/) · `full_text` · `supporting` · number
  - > Supplementary information Supplementary information on clinical parameters and sample collection.Sequential therapies of the investigated drugs in the study cohort.Depiction of the used HPLC gradient for sample analysis.Overview of the used mass spectrometer parameters.Normalized chromatogram of a standard solution of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat obtained with the developed HPLC-QqQ MS method.Overview of the corresponding method performance parameters.Depiction of measured CCS values of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat.Depiction of the quantitation results for imatinib CSF samples
  - *Cerebrospinal fluid penetration of targeted therapeutics in pediatric brain tumor patients.* — Acta Neuropathol Commun 2020
  - **proposed: `demonstrated`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF concentration = moderate (1-10 nM) · confidence high
  - rationale: Primary CSF concentration measured directly from pediatric brain tumor patients via Ommaya reservoirs; dasatinib detected at moderate (1-10 nM) penetrance, a measured CNS exposure, not merely a prediction.
  - span relied on: “regorafenib and dasatinib moderate (1-10 nM) penetrance”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-017** · [PMID 19491323](https://pubmed.ncbi.nlm.nih.gov/19491323/) · `abstract_only` · `limiting` · number
  - > In vivo brain distribution studies showed that the CNS distribution of dasatinib is limited, with the brain-to-plasma concentration ratios less than 0.12 in wild-type mice, which increased approximately 8-fold in Mdr1a/b(-/-) Bcrp1(-/-) mice.
  - *P-glycoprotein and breast cancer resistance protein influence brain distribution of dasatinib.* — J Pharmacol Exp Ther 2009
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma concentration ratio = less than 0.12 in wild-type mice · confidence high
  - rationale: Primary measured PK in wild-type (normal) mice shows a low brain:plasma ratio (<0.12), indicating exclusion from CNS; knockout/inhibitor increases describe transporter role, not patient exposure.
  - span relied on: “the CNS distribution of dasatinib is limited, with the brain-to-plasma concentration ratios less than 0.12 in wild-type mice”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-018** · [PMID 24790822](https://pubmed.ncbi.nlm.nih.gov/24790822/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4000600/) · `abstract_only` · `supporting` · number
  - > With 40 mg dasatinib administered once daily, its trough level and cerebrospinal fluid (CSF) concentration were 32 ng/mL and below the sensitivity threshold of 1 ng/mL, respectively.
  - *Philadelphia chromosome-positive acute lymphoblastic leukemia with extramedullary and meningeal relapse after allogeneic hematopoietic stem cell transplantation that was successfully treated with dasatinib.* — Springerplus 2014
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF concentration and plasma trough level = trough level 32 ng/mL; CSF concentration below sensitivity threshold of 1 ng/mL · confidence high
  - rationale: Directly measured human plasma and CSF concentrations at 40 mg dose show dasatinib essentially undetectable in CSF despite measurable plasma trough, indicating CNS exclusion at this dose.
  - span relied on: “The trough level and CSF concentration of dasatinib administered at a daily dose of 40 mg were 32 ng/mL and below the sensitivity threshold of 1 ng/mL, respectively.”
  - read from: pmc_body / Case description · **your verdict:** _______
- **CNS-019** · [PMID 35098970](https://pubmed.ncbi.nlm.nih.gov/35098970/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8612719/) · `abstract_only` · `supporting` · number
  - > The primary objective is to evaluate the central nervous system penetration of dasatinib and quercetin through analysis of cerebrospinal fluid collected at baseline and after 12 weeks of treatment.
  - *Senolytic Therapy to Modulate the Progression of Alzheimer's Disease (SToMP-AD): A Pilot Clinical Trial.* — J Prev Alzheimers Dis 2022
  - **proposed: `unknown`** · basis `design_or_prediction` · primary · human · arm `not_applicable` · none = nan · confidence high
  - rationale: This describes the trial's planned objective/method to measure CSF penetration, not a reported result. No CSF concentration, ratio, or outcome value for dasatinib is given in the text.
  - span relied on: “The primary objective is to evaluate the central nervous system penetration of dasatinib and quercetin through analysis of cerebrospinal fluid collected at baseline and after 12 weeks of treatment.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-020** · [PMID 42578491](https://pubmed.ncbi.nlm.nih.gov/42578491/) · `abstract_only` · `supporting` · number
  - > In CSF, the mean dasatinib concentration was 0.5 ± 0.2 ng/mL at 2 h.
  - *Low Dasatinib Penetration of the Blood-Brain Barrier in Children With Philadelphia Chromosome-Positive Acute Lymphoblastic Leukemia: Evidence From LC-MS/MS Analysis.* — Pediatr Blood Cancer 2026
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF concentration and plasma:CSF ratio = CSF 0.5 ± 0.2 ng/mL at 2h; plasma/CSF ratio 225:1 (98:1-406:1) · confidence high
  - rationale: Primary human PK measurement in paired plasma/CSF samples shows very low CSF concentration and plasma:CSF ratio of 225:1, indicating poor BBB penetration despite therapeutic plasma levels - a clear contradicted finding.
  - span relied on: “In CSF, the mean dasatinib concentration was 0.5 ± 0.2 ng/mL at 2 h. The median paired plasma/CSF concentration ratio was 225:1 (98:1-406:1). In conclusion, despite therapeutic systemic levels, dasatinib penetrates poorly into CSF in children with Ph + ALL.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-021** · [PMID 19491323](https://pubmed.ncbi.nlm.nih.gov/19491323/) · `abstract_only` · `supporting` · no number
  - > The objective of this study was to investigate the role of P-glycoprotein (P-gp) and breast cancer resistance protein (BCRP) in modulating the CNS penetration of dasatinib.
  - *P-glycoprotein and breast cancer resistance protein influence brain distribution of dasatinib.* — J Pharmacol Exp Ther 2009
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma concentration ratio = brain-to-plasma concentration ratios less than 0.12 in wild-type mice · confidence high
  - rationale: Wild-type mouse brain-to-plasma ratio <0.12 is a low absolute exposure, showing exclusion from CNS; knockout/inhibitor arms describe transporter role, not patient-relevant exposure.
  - span relied on: “In vivo brain distribution studies showed that the CNS distribution of dasatinib is limited, with the brain-to-plasma concentration ratios less than 0.12 in wild-type mice, which increased approximately 8-fold in Mdr1a/b(-/-) Bcrp1(-/-) mice.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-022** · [PMID 42578491](https://pubmed.ncbi.nlm.nih.gov/42578491/) · `abstract_only` · `limiting` · no number
  - > In conclusion, despite therapeutic systemic levels, dasatinib penetrates poorly into CSF in children with PhALL.
  - *Low Dasatinib Penetration of the Blood-Brain Barrier in Children With Philadelphia Chromosome-Positive Acute Lymphoblastic Leukemia: Evidence From LC-MS/MS Analysis.* — Pediatr Blood Cancer 2026
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF:plasma concentration ratio = median paired plasma/CSF concentration ratio was 225:1 (98:1-406:1); CSF mean 0.5 ± 0.2 ng/mL vs plasma 101.6 ± 42.1 ng/mL at 2h · confidence high
  - rationale: Primary human PK measurement in normal (non-transporter-modified) patients shows CSF concentration ~225-fold lower than plasma, directly demonstrating poor BBB penetration - a contradicted finding.
  - span relied on: “The median paired plasma/CSF concentration ratio was 225:1 (98:1-406:1). In conclusion, despite therapeutic systemic levels, dasatinib penetrates poorly into CSF in children with Ph + ALL.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-023** · [PMID 42578491](https://pubmed.ncbi.nlm.nih.gov/42578491/) · `abstract_only` · `supporting` · no number
  - > We measured dasatinib concentrations in paired plasma and cerebrospinal fluid (CSF) samples from children with Philadelphia chromosome-positive acute lymphoblastic leukemia (Ph+ ALL).
  - *Low Dasatinib Penetration of the Blood-Brain Barrier in Children With Philadelphia Chromosome-Positive Acute Lymphoblastic Leukemia: Evidence From LC-MS/MS Analysis.* — Pediatr Blood Cancer 2026
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · plasma-to-CSF concentration ratio / CSF concentration = CSF 0.5 ± 0.2 ng/mL at 2h; plasma 101.6 ± 42.1 ng/mL at 2h; median plasma/CSF ratio 225:1 (98:1-406:1) · confidence high
  - rationale: Primary human PK data in normal (non-transporter-modified) children show CSF concentrations far below plasma (ratio ~225:1), directly demonstrating poor CNS penetration - a contradicted finding.
  - span relied on: “In CSF, the mean dasatinib concentration was 0.5 ± 0.2 ng/mL at 2 h. The median paired plasma/CSF concentration ratio was 225:1 (98:1-406:1). In conclusion, despite therapeutic systemic levels, dasatinib penetrates poorly into CSF in children with Ph + ALL.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-024** · [PMID 42578491](https://pubmed.ncbi.nlm.nih.gov/42578491/) · `abstract_only` · `supporting` · no number
  - > After validating a liquid chromatography-tandem mass spectrometry (LC-MS/MS) assay for dasatinib in both matrices, we quantified drug concentrations in plasma and CSF and expressed blood-brain barrier penetration as the plasma-to-CSF concentration ratio.
  - *Low Dasatinib Penetration of the Blood-Brain Barrier in Children With Philadelphia Chromosome-Positive Acute Lymphoblastic Leukemia: Evidence From LC-MS/MS Analysis.* — Pediatr Blood Cancer 2026
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · plasma:CSF concentration ratio (and CSF concentration) = Mean CSF concentration 0.5 ± 0.2 ng/mL at 2h; median plasma/CSF ratio 225:1 (98:1-406:1) · confidence high
  - rationale: Primary human PK in paired plasma/CSF samples from children on oral dasatinib shows very low CSF concentration and high plasma:CSF ratio (225:1), indicating poor BBB penetration - a measured contradicted finding.
  - span relied on: “In CSF, the mean dasatinib concentration was 0.5 ± 0.2 ng/mL at 2 h. The median paired plasma/CSF concentration ratio was 225:1 (98:1-406:1). In conclusion, despite therapeutic systemic levels, dasatinib penetrates poorly into CSF in children with Ph + ALL.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### ENCORAFENIB

3 attributed of 9 retrieved sentences · 1 full text, 2 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 7 drug rows

**Proposed drug verdict: `contradicted`** — 2 primary mouse claim(s), all contradicted. Decisive claim(s): CNS-026, CNS-027.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-025** · [PMID 41369830](https://pubmed.ncbi.nlm.nih.gov/41369830/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12799883/) · `full_text` · `supporting` · number
  - > These results highlight the potential of encorafenib plus binimetinib to provide meaningful intracranial tumor shrinkage and improved complete responses in patients with BRAF V600-mutant melanoma with brain metastases, although the considerable heterogeneity across included studies suggests that these findings should be interpreted with caution.
  - *The safety and efficacy of encorafenib plus binimetinib for brain metastases: a systematic review and meta-analysis.* — Discov Oncol 2025
  - **proposed: `demonstrated`** · basis `clinical_cns_response` · restated · human · arm `not_applicable` · intracranial response rate (CR/ORR/PR) in brain metastases = intracranial CR rate higher than prior studies; ORR and PR generally comparable · confidence medium · **flagged for human check**
  - rationale: This is a meta-analysis reporting clinical intracranial response data (CR/ORR/PR) for encorafenib+binimetinib in brain metastases, i.e. clinical activity against a CNS tumor site, meeting the demonstrated criterion despite being a review synthesizing other trials.
  - span relied on: “The intracranial CR rate observed with encorafenib plus binimetinib was higher than that reported in prior dual, triplet, or monotherapy studies, while intracranial ORR and PR were generally comparable, and SD fell within previously reported ranges.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-026** · [PMID 29155017](https://pubmed.ncbi.nlm.nih.gov/29155017/) · `abstract_only` · `limiting` · no number
  - > However, absolute brain concentrations and brain-to-plasma ratios remained very low in all strains, indicating intrinsically poor brain penetration of encorafenib.
  - *P-glycoprotein (MDR1/ABCB1) and Breast Cancer Resistance Protein (BCRP/ABCG2) affect brain accumulation and intestinal disposition of encorafenib in mice.* — Pharmacol Res 2017
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain concentration and brain-to-plasma ratio = very low in all strains · confidence high · **flagged for human check**
  - rationale: Measured brain-to-plasma ratios were low even in wild-type mice (the normal, non-knockout arm), directly demonstrating poor CNS exposure; knockout-only increases do not change this wild-type finding.
  - span relied on: “absolute brain concentrations and brain-to-plasma ratios remained very low in all strains, indicating intrinsically poor brain penetration of encorafenib”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-027** · [PMID 29155017](https://pubmed.ncbi.nlm.nih.gov/29155017/) · `abstract_only` · `limiting` · no number
  - > The low brain penetration of encorafenib might limit its efficacy against malignancies positioned behind a functional blood-brain barrier, but its oral bioavailability and distribution to other tested organs (liver, kidney, spleen, testis) was high.
  - *P-glycoprotein (MDR1/ABCB1) and Breast Cancer Resistance Protein (BCRP/ABCG2) affect brain accumulation and intestinal disposition of encorafenib in mice.* — Pharmacol Res 2017
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio / brain concentration = absolute brain concentrations and brain-to-plasma ratios remained very low in all strains · confidence high · **flagged for human check**
  - rationale: Wild-type mice (normal arm) show very low absolute brain concentration and brain-to-plasma ratio; knockout arms show increased but still low levels, confirming intrinsically poor CNS penetration.
  - span relied on: “However, absolute brain concentrations and brain-to-plasma ratios remained very low in all strains, indicating intrinsically poor brain penetration of encorafenib.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### IMATINIB

21 attributed of 90 retrieved sentences · 13 full text, 8 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_record` · CNS-manifestation trial evidence on 0 drug rows

**Proposed drug verdict: `demonstrated`** — 2 primary human claim(s), all demonstrated. Decisive claim(s): CNS-035, CNS-036.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-028** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `limiting` · number
  - > Subsequently, it was demonstrated that thedistribution of imatinib is limited by ABCB1-mediated efflux, resulting in limited brain penetration [].
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `review_restatement` · restated · mouse · arm `unclear` · none = nan · confidence medium · **flagged for human check**
  - rationale: Background section restates a cited prior study's finding with no actual exposure numbers given in this text; the later knockout-comparison sentence also lacks reported values/arm-specific ratios here.
  - span relied on: “it was demonstrated that the in vivo distribution of imatinib is limited by ABCB1-mediated efflux, resulting in limited brain penetration [ 5 ]”
  - read from: pmc_body / Background · **your verdict:** _______
- **CNS-029** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > However, ABCB1 is not the sole transporter expressed in the blood-brain barrier that may limit the brain distribution of imatinib.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `review_restatement` · restated · other_animal · arm `transporter_knockout_or_inhibitor` · brain:plasma (referenced, not given numerically) = nan · confidence medium · **flagged for human check**
  - rationale: Background section restates prior studies' findings (citations 5,6,9) of limited brain penetration without giving primary numeric exposure values here; it is a secondary restatement, not this paper's own measurement.
  - span relied on: “it was demonstrated that the in vivo distribution of imatinib is limited by ABCB1-mediated efflux, resulting in limited brain penetration [5]. More recently, positron emission topography studies with [N-11C-methyl]-imatinib have confirmed limited brain penetration in primates [6].”
  - read from: pmc_body / Background · **your verdict:** _______
- **CNS-030** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > The brain-to-plasma ratio of imatinib 2 hours after administration did not differ significantly between the two groups (P = 0.83), and similar brain-to-plasma AUCratios were observed for each group (0.070 for imatinib plus vehicle0.078 for imatinib plus tariquidar).
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma AUC ratio = 0.070 for imatinib plus vehicle, 0.078 for imatinib plus tariquidar · confidence high
  - rationale: Vehicle (normal/wild-type) arm shows brain-to-plasma AUC ratio of only 0.070, a low absolute ratio indicating exclusion from brain; tariquidar co-administration (efflux inhibitor) did not meaningfully change this ratio (0.078).
  - span relied on: “similar brain-to-plasma AUCratios were observed for each group (0.070 for imatinib plus vehicle0.078 for imatinib plus tariquidar)”
  - read from: pmc_body / Results · **your verdict:** _______
- **CNS-031** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > Table 1 Pharmacokinetics of imatinib in Balb/C mice in the presence and absence of tariquidar Imatinib alone Imatinib + Tariquidar Plasma Mean SD Mean SD Fold Change P-value C(ng/mL) 5,710.5 1,472.3 6,813.2 1,547.9 1.19 - T(hr) 0.17 - 0.17 - - - AUC(hr*ng/mL) 12,167.5 - 26,724.6 - 2.20 0.001 Liver Mean SD Mean SD Fold Change P-value C(ng/g) 26,279.7 4,560.2 46,139.1 11,000.6 1.76 - T(hr) 0.25 - 0.17 - - - AUC(hr*ng/g) 68,330.8 - 153,209.2 - 2.24 < 0.00001 Brain Mean SD Mean SD Fold Change P-value C(ng/g) 194.7 27.2 417.0 116.6 2.14 - T(hr) 2 - 2 - - - AUC(hr*ng/g) 574.23 - 1,277.7 - 2.23 0.00001 Discussio
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain concentration vs plasma concentration (brain:plasma ratio) = Brain Cmax 194.7 ng/g vs Plasma Cmax 5,710.5 ng/mL (imatinib alone arm) · confidence high
  - rationale: In the imatinib-alone (normal, no tariquidar) arm, brain Cmax (194.7 ng/g) is ~29-fold lower than plasma Cmax (5,710.5 ng/mL), demonstrating low brain exposure relative to plasma - a contradicted finding for unmodified exposure.
  - span relied on: “Plasma Mean SD Mean SD Fold Change P-value C(ng/mL) 5,710.5 ... Brain Mean SD Mean SD Fold Change P-value C(ng/g) 194.7 27.2 417.0 116.6 2.14”
  - read from: pmc_body / TABLE · **your verdict:** _______
- **CNS-032** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > The brain-to-plasma concentration ratio of imatinib 2 hours after administration was not significantly affected by tariquidar.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma concentration ratio / AUC ratio = not significantly affected by tariquidar; AUC 0-4 brain-to-plasma ratio similar with or without tariquidar · confidence medium · **flagged for human check**
  - rationale: A brain:plasma ratio is reported but no absolute value is given, only that it is unchanged by tariquidar in wild-type mice; cannot judge whether it is high or low in absolute terms.
  - span relied on: “The brain-to-plasma concentration ratio of imatinib 2 hours after administration was not significantly affected by tariquidar. In addition, the AUC 0–4 ratio for brain-to-plasma was similar in the presence or absence of tariquidar.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-033** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > Specifically, elacridar has been shown to result in a 9.3-fold increase in the brain-to-plasma concentration ratio, as compared to administration of imatinib alone [].
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `review_restatement` · restated · mouse · arm `transporter_knockout_or_inhibitor` · brain-to-plasma concentration ratio = 9.3-fold increase with elacridar vs imatinib alone · confidence medium
  - rationale: This is a Discussion-section restatement of another paper's finding (ref 14), citing a brain-to-plasma ratio increase produced only under elacridar efflux-inhibitor co-administration, not imatinib alone exposure in a normal arm.
  - span relied on: “elacridar has been shown to result in a 9.3-fold increase in the brain-to-plasma concentration ratio, as compared to administration of imatinib alone [ 14 ]”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-034** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > Though the increase in brain exposure to imatinib was reported to be higher with oral administration, as compared to i.v., this was only measured at 4 hours post-imatinib, and the analysis was based only on measurement of total radioactivity.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `review_restatement` · restated · mouse · arm `unclear` · brain exposure (total radioactivity) = nan · confidence medium
  - rationale: This Discussion paragraph restates and critiques a prior study's (Breedveld et al.) finding, explicitly noting it is unreliable (radioactivity-only, single timepoint, unclear parent vs metabolite); not a primary measurement in this paper.
  - span relied on: “Though the increase in brain exposure to imatinib was reported to be higher with oral administration, as compared to i.v., this was only measured at 4 hours post-imatinib, and the analysis was based only on measurement of total radioactivity.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-035** · [PMID 32493453](https://pubmed.ncbi.nlm.nih.gov/32493453/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7268320/) · `full_text` · `supporting` · number
  - > Consequently, we tested whether CSF protein levels routinely measured at the same time point as drug penetration analyzes correlated to imatinib concentrations and could indeed detect a positive correlation (Additional file: Figure S6).
  - *Cerebrospinal fluid penetration of targeted therapeutics in pediatric brain tumor patients.* — Acta Neuropathol Commun 2020
  - **proposed: `demonstrated`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF concentration = mean 77.7 nM, range 5.7–288.5 nM; detected in 75% (9/12) samples · confidence high
  - rationale: Primary CSF concentration data from pediatric patients receiving imatinib, measured directly in CSF samples, demonstrating actual CNS exposure in humans under normal (non-BBB-modifying) conditions.
  - span relied on: “imatinib (mean 77.7 nM, range 5.7–288.5 nM) ... Imatinib and dasatinib were detected in 75% (9/12) and 66% (2/3) respectively.”
  - read from: pmc_body / Quantitation of pharmaceuticals including free drug levels and metabolites · **your verdict:** _______
- **CNS-036** · [PMID 32493453](https://pubmed.ncbi.nlm.nih.gov/32493453/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7268320/) · `full_text` · `supporting` · number
  - > Supplementary information Supplementary information on clinical parameters and sample collection.Sequential therapies of the investigated drugs in the study cohort.Depiction of the used HPLC gradient for sample analysis.Overview of the used mass spectrometer parameters.Normalized chromatogram of a standard solution of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat obtained with the developed HPLC-QqQ MS method.Overview of the corresponding method performance parameters.Depiction of measured CCS values of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat.Depiction of the quantitation results for imatinib CSF samples
  - *Cerebrospinal fluid penetration of targeted therapeutics in pediatric brain tumor patients.* — Acta Neuropathol Commun 2020
  - **proposed: `demonstrated`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF concentration = &gt; 10 nM · confidence high
  - rationale: Primary measured CSF concentration of imatinib in pediatric brain tumor patients via Ommaya reservoir sampling, reported as high penetrance (>10 nM), with active metabolites also detected.
  - span relied on: “ribociclib, vorinostat and imatinib showed high (> 10 nM)... penetrance”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-037** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `limiting` · no number
  - > More recently, positron emission topography studies with [-C-methyl]-imatinib have confirmed limited brain penetration in primates [].
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `contradicted`** · basis `review_restatement` · restated · other_animal · arm `normal` · brain penetration (PET imaging) = limited brain penetration in primates · confidence low · **flagged for human check**
  - rationale: Background section restates a PET imaging finding from another paper (ref 6) showing limited brain penetration of imatinib in primates under normal (non-transporter-modified) conditions - a low CNS exposure finding, but it is a citation of external work, not this paper's own measurement.
  - span relied on: “positron emission topography studies with [ N - 11 C-methyl]-imatinib have confirmed limited brain penetration in primates”
  - read from: pmc_body / Background · **your verdict:** _______
- **CNS-038** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `limiting` · no number
  - > Here, we evaluated the effect of tariquidar on the disposition of imatinib in mice, in order to provide a pharmacokinetic rationale for attempts to improve the agent's low brain penetration.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `design_or_prediction` · restated · mouse · arm `not_applicable` · none = nan · confidence medium
  - rationale: Background sentence is a restated assertion motivating the study, not a measurement. No brain/CSF concentration, ratio, or Kp,uu value given for imatinib in this text.
  - span relied on: “to provide a pharmacokinetic rationale for attempts to improve the agent's low brain penetration”
  - read from: pmc_body / Background · **your verdict:** _______
- **CNS-039** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · no number
  - > Hence, it is possible that the higher imatinib dose utilized in the current study results in higher plasma concentrations of drug and, therefore, saturation of drug efflux at the blood-brain barrier.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `design_or_prediction` · restated · mouse · arm `normal` · brain-to-plasma ratio (discussed, not measured for imatinib alone in this study) = nan · confidence medium · **flagged for human check**
  - rationale: Matched sentence is speculative discussion. Surrounding text cites a different paper's elacridar co-administration result (9.3-fold brain:plasma increase), not a measurement of imatinib alone in this paper.
  - span relied on: “it is possible that the higher imatinib dose utilized in the current study results in higher plasma concentrations of drug and, therefore, saturation of drug efflux at the blood-brain barrier”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-040** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · no number
  - > Based on our findings, simply doubling the dose of imatinib without addition of an inhibitor would likely result in a similar increase in overall brain exposure, due to increased plasma concentrations of drug.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `design_or_prediction` · primary · mouse · arm `unclear` · none = nan · confidence medium
  - rationale: This is a predictive/interpretive statement in the Conclusion ("would likely result"), not a reported measurement. No concentration, ratio, or Kp,uu value is given here to support a direction.
  - span relied on: “simply doubling the dose of imatinib without addition of an inhibitor would likely result in a similar increase in overall brain exposure”
  - read from: pmc_body / Conclusion · **your verdict:** _______
- **CNS-041** · [PMID 12604685](https://pubmed.ncbi.nlm.nih.gov/12604685/) · `abstract_only` · `supporting` · number
  - > In the wild-type mice, the brain-to-plasma STI-571 concentration ratio at all time points was low (1-3%);
  - *Distribution of STI-571 to the brain is limited by P-glycoprotein-mediated efflux.* — J Pharmacol Exp Ther 2003
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio = 1-3% · confidence high
  - rationale: Primary measured brain-to-plasma ratio in wild-type (normal, non-knockout) mice is low (1-3%), directly demonstrating CNS exclusion of imatinib via P-glycoprotein efflux.
  - span relied on: “In the wild-type mice, the brain-to-plasma STI-571 concentration ratio at all time points was low (1-3%)”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-042** · [PMID 12604685](https://pubmed.ncbi.nlm.nih.gov/12604685/) · `abstract_only` · `supporting` · number
  - > When 12.5 mg/kg STI-571 was given intravenously, the brain-to-plasma ratio of STI-571 in the mdr1a/b (-/-) mice was approximately 7-fold greater than that of wild-type mice up to 120 min postdose.
  - *Distribution of STI-571 to the brain is limited by P-glycoprotein-mediated efflux.* — J Pharmacol Exp Ther 2003
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio = low (1-3%) · confidence high
  - rationale: Matched sentence reports knockout-arm ratio, which describes transporter effect, not patient exposure. Surrounding text gives wild-type brain-to-plasma ratio of 1-3%, a low absolute value demonstrating CNS exclusion.
  - span relied on: “In the wild-type mice, the brain-to-plasma STI-571 concentration ratio at all time points was low (1-3%)”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-043** · [PMID 25539457](https://pubmed.ncbi.nlm.nih.gov/25539457/) · `abstract_only` · `supporting` · number
  - > Brain exposure increased substantially in Mdr1a(-/-) rats for loperamide and in Mdr1a(-/-)/Abcg2(-/-) rats for imatinib and compound Y, but minimally to modestly in Abcg2(-/-) rats for dantrolene and compound X.
  - *Differential role of P-glycoprotein and breast cancer resistance protein in drug distribution into brain, CSF and peripheral nerve tissues in rats.* — Xenobiotica 2014
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · rat · arm `transporter_knockout_or_inhibitor` · brain exposure increase (knockout vs WT) and CSF:unbound brain concentration ratio = Brain exposure increased substantially only in Mdr1a(-/-)/Abcg2(-/-) rats; CSF to unbound brain concentration ratio reduced to 1 in Mdr1a(-/-)/Abcg2(-/-) rats for imatinib · confidence high · **flagged for human check**
  - rationale: Increased brain exposure only occurs in double-knockout rats, describing transporter effect not normal exposure. In wild-type rats imatinib is a dual Pgp/Bcrp substrate with restricted brain penetration, indicating exclusion from CNS under normal conditions.
  - span relied on: “Brain exposure increased substantially in Mdr1a(-/-) rats for loperamide and in Mdr1a(-/-)/Abcg2(-/-) rats for imatinib and compound Y... While CSF to unbound brain concentration ratio remained ≥3 in the KO animals for dantrolene, compounds X and Y, it was reduced to 1 in the Mdr1a(-/-)/Abcg2(-/-) rats for imatinib.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-044** · [PMID 25539457](https://pubmed.ncbi.nlm.nih.gov/25539457/) · `abstract_only` · `supporting` · number
  - > While CSF to unbound brain concentration ratio remained ≥3 in the KO animals for dantrolene, compounds X and Y, it was reduced to 1 in the Mdr1a(-/-)/Abcg2(-/-) rats for imatinib.
  - *Differential role of P-glycoprotein and breast cancer resistance protein in drug distribution into brain, CSF and peripheral nerve tissues in rats.* — Xenobiotica 2014
  - **proposed: `unknown`** · basis `measured_pk_animal` · primary · rat · arm `transporter_knockout_or_inhibitor` · CSF to unbound brain concentration ratio; brain exposure (Mdr1a-/-/Abcg2-/- rats) = CSF:unbound brain ratio reduced to 1 in Mdr1a(-/-)/Abcg2(-/-) rats; brain exposure increased substantially in Mdr1a(-/-)/Abcg2(-/-) rats · confidence medium · **flagged for human check**
  - rationale: All measured exposure/ratio data for imatinib are from double-knockout (Mdr1a-/-/Abcg2-/-) rats, describing transporter effect, not wild-type patient-relevant exposure; no wild-type brain/CSF exposure value is given.
  - span relied on: “Brain exposure increased substantially in Mdr1a(-/-) rats for loperamide and in Mdr1a(-/-)/Abcg2(-/-) rats for imatinib and compound Y... it was reduced to 1 in the Mdr1a(-/-)/Abcg2(-/-) rats for imatinib.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-045** · [PMID 15073132](https://pubmed.ncbi.nlm.nih.gov/15073132/) · `abstract_only` · `limiting` · no number
  - > There is limited penetration of imatinib into the CSF of nonhuman primates after i.v.
  - *Plasma and cerebrospinal fluid pharmacokinetics of imatinib after administration to nonhuman primates.* — Clin Cancer Res 2004
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF:plasma AUC ratio = 5% +/-2% · confidence high
  - rationale: Primary measured PK in normal (non-transporter-manipulated) nonhuman primates shows low CSF:plasma AUC ratio (5%), directly supporting the conclusion of limited CNS penetration.
  - span relied on: “The mean CSF:plasma area under the plasma concentration versus time curve ratio for all of the animals was 5% +/-2%.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-046** · [PMID 15073132](https://pubmed.ncbi.nlm.nih.gov/15073132/) · `abstract_only` · `supporting` · no number
  - > We used a nonhuman primate model that is highly predictive of the cerebrospinal fluid penetration of drugs in humans to study the pharmacokinetics of imatinib in plasma and cerebrospinal fluid (CSF) after i.v.
  - *Plasma and cerebrospinal fluid pharmacokinetics of imatinib after administration to nonhuman primates.* — Clin Cancer Res 2004
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF:plasma AUC ratio = CSF:plasma AUC ratio 5% +/-2%; mean peak CSF concentration 0.25 +/-0.07 microM (i.v.) and 0.07 +/-0.04 microM (p.o.) · confidence high
  - rationale: Primary nonhuman primate PK study measured low CSF:plasma AUC ratio (~5%) and low absolute CSF concentrations in normal (non-transporter-modified) animals, directly demonstrating exclusion of imatinib from CNS compartment.
  - span relied on: “The mean CSF:plasma area under the plasma concentration versus time curve ratio for all of the animals was 5% +/-2%. CONCLUSIONS: There is limited penetration of imatinib into the CSF of nonhuman primates after i.v. and p.o. administration.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-047** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `abstract_only` · `supporting` · no number
  - > Though tariquidar increased the absolute exposure of imatinib, the brain-to-plasma ratio of imatinib was unaffected.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma AUC ratio = 0.070 for imatinib plus vehicle versus 0.078 for imatinib plus tariquidar · confidence high
  - rationale: Vehicle-arm (normal) brain:plasma AUC ratio of 0.070 is low in absolute terms, indicating imatinib is largely excluded from brain even without an efflux inhibitor; tariquidar (inhibitor arm) did not change this, confirming exclusion is not solely efflux-transporter driven at baseline.
  - span relied on: “similar brain-to-plasma AUC 0–4 ratios were observed for each group (0.070 for imatinib plus vehicle versus 0.078 for imatinib plus tariquidar)”
  - read from: pmc_body / Results · **your verdict:** _______
- **CNS-048** · [PMID 34896751](https://pubmed.ncbi.nlm.nih.gov/34896751/) · `abstract_only` · `supporting` · no number
  - > The contribution of BCRP to the brain and CSF distribution of the dual P-glycoprotein/BCRP substrates, imatinib and prazosin, was similar to that of BCRP-specific substrates.
  - *Investigation of the role and quantitative impact of breast cancer resistance protein on drug distribution into brain and CSF in rats.* — Drug Metab Pharmacokinet 2021
  - **proposed: `unknown`** · basis `measured_pk_animal` · primary · rat · arm `transporter_knockout_or_inhibitor` · Kp,uu,brain / Kp,uu,CSF (BCRP contribution comparison) = nan · confidence low · **flagged for human check**
  - rationale: No actual Kp,uu value for imatinib is given in the abstract; only a qualitative comparison of BCRP's contribution (a transporter-inhibitor-based study) to other substrates, not an absolute exposure number for imatinib itself.
  - span relied on: “The contribution of BCRP to the brain and CSF distribution of the dual P-glycoprotein/BCRP substrates, imatinib and prazosin, was similar to that of BCRP-specific substrates.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### PAZOPANIB

12 attributed of 22 retrieved sentences · 9 full text, 3 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 7 drug rows

**Proposed drug verdict: left blank** — Primary mouse claims disagree (contradicted, demonstrated); left for the reviewer rather than resolved by majority.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-049** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `full_text` · `supporting` · number
  - > We further demonstrated that simultaneous inhibition of P-gp and Bcrp1 mediated active efflux at the mouse BBB could significantly improve the brain penetration of pazopanib.
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain penetration/brain:plasma (wild-type baseline vs inhibitor-modulated) = not numerically stated; "significantly improve the brain penetration of pazopanib" upon P-gp/Bcrp1 inhibition · confidence high · **flagged for human check**
  - rationale: Wild-type mouse brain penetration of pazopanib was low and only improved by pharmacologic efflux inhibition (canertinib/erlotinib), i.e. a BBB-modifying co-intervention; baseline (normal) exposure is excluded, consistent with contradicted.
  - span relied on: “We investigated the role of P-gp and BCRP in brain disposition of pazopanib in FVB wild type mice. We further demonstrated that simultaneous inhibition of P-gp and Bcrp1 mediated active efflux at the mouse BBB could significantly improve the brain penetration of pazopanib.”
  - read from: pmc_body / 4. Discussion · **your verdict:** _______
- **CNS-050** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `full_text` · `supporting` · number
  - > In contrast to the in vitro findings, initial in vivo experiments showed selective inhibition of P-gp or Ko143 did not have any significant influence on brain penetration of pazopanib ().
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma concentration ratio (Cb/Cp) = severely limited brain/plasma ratio in wild-type mice; selective P-gp or Bcrp1 (Ko143) inhibition alone had no significant effect · confidence high
  - rationale: Primary measurement in wild-type FVB mice (normal arm, no BBB-opening co-intervention) shows brain penetration severely limited by active efflux; single-transporter inhibition didn't rescue it. Only elacridar dual-inhibition (transporter-inhibitor arm) raised exposure, which is separately flagged.
  - span relied on: “Distribution of pazopanib to the brain was severely limited due to active efflux. In contrast to the in vitro findings, initial in vivo experiments showed selective inhibition of P-gp or Ko143 did not have any significant influence on brain penetration of pazopanib”
  - read from: pmc_body / 4. Discussion · **your verdict:** _______
- **CNS-051** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `full_text` · `supporting` · number
  - > These results suggest that even if pazopanib is a moderate substrate of P-gp in vitro, in vivo at the mouse BBB, both P-gp and Bcrp1 act in concert to limit brain penetration of pazopanib.
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain/plasma concentration ratio (Cb/Cp) = severely limited brain distribution; elacridar increased Cb/Cp ~5-fold vs wild type, indicating low baseline ratio · confidence high
  - rationale: In wild-type FVB mice (normal arm), pazopanib brain penetration was severely limited by P-gp/Bcrp1 efflux; only inhibitor (elacridar) co-dosing raised Cb/Cp, confirming low baseline CNS exposure.
  - span relied on: “Distribution of pazopanib to the brain was severely limited due to active efflux.”
  - read from: pmc_body / 4. Discussion · **your verdict:** _______
- **CNS-052** · [PMID 28869476](https://pubmed.ncbi.nlm.nih.gov/28869476/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5757517/) · `full_text` · `supporting` · number
  - > We found that pazopanib crosses the blood-brain barrier (BBB) with no detectable peripheral off-side effects, and reduces p-tau in TauP301L mice.
  - *Pazopanib Reduces Phosphorylated Tau Levels and Alters Astrocytes in a Mouse Model of Tauopathy.* — J Alzheimers Dis 2017
  - **proposed: `unknown`** · basis `mechanistic_assertion` · unclear · mouse · arm `normal` · none = nan · confidence medium
  - rationale: Sentence is an Introduction-section summary assertion with no reported CSF/brain concentration, Kp,uu, or brain:plasma ratio value; no exposure quantity is given in the surrounding text either.
  - span relied on: “We found that pazopanib crosses the blood-brain barrier (BBB) with no detectable peripheral off-side effects, and reduces p-tau in TauP301L mice.”
  - read from: pmc_body / Introduction · **your verdict:** _______
- **CNS-053** · [PMID 28869476](https://pubmed.ncbi.nlm.nih.gov/28869476/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5757517/) · `full_text` · `supporting` · number
  - > Results Pazopanib penetrates the blood-brain barrier Following a single intraperitoneal (IP) injection of pazopanib of 0, 5, or 10mg/kg in dimethyl sulfoxide (DMSO) in C57BL/6 mice, we found that the drug penetrates the BBB and peaks at approximately 4 hours (T) ().
  - *Pazopanib Reduces Phosphorylated Tau Levels and Alters Astrocytes in a Mouse Model of Tauopathy.* — J Alzheimers Dis 2017
  - **proposed: `demonstrated`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain concentration = 450 ng/mL (5 mg/kg) and 583.33 ng/mL (10 mg/kg) at Tmax, ~1 µM and 1.3 µM · confidence high
  - rationale: Primary measured brain tissue concentration in normal wild-type mice after IP dosing, not a transporter knockout or BBB-opening co-intervention; directly quantifies CNS exposure.
  - span relied on: “The peak concentration (C max ) in the brain at the 4-hour point was 450ng/mL for the 5mg/kg dose and 583.33 ng/mL for the 10 mg/kg dose, corresponding to approximately 1μM and 1.3μM”
  - read from: pmc_body / Pazopanib penetrates the blood-brain barrier · **your verdict:** _______
- **CNS-054** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `full_text` · `supporting` · no number
  - > The fact that both these test compounds in our study are also known to modulate P-gp and BCRP functional activity (;), we selected erlotinib and canertinib as clinically relevant inhibitors for improving pazopanib brain penetration.
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - **proposed: `unknown`** · basis `design_or_prediction` · primary · mouse · arm `not_applicable` · none = nan · confidence high · **flagged for human check**
  - rationale: Discussion section explains rationale for choosing inhibitors; surrounding text describes in vitro P-gp/BCRP inhibitory potency of erlotinib/canertinib, not actual pazopanib brain exposure measurement. No CNS concentration/ratio for pazopanib given here.
  - span relied on: “we selected erlotinib and canertinib as clinically relevant inhibitors for improving pazopanib brain penetration”
  - read from: pmc_body / 4. Discussion · **your verdict:** _______
- **CNS-055** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `full_text` · `supporting` · no number
  - > In addition, from the clinical perspective, we show that canertinib or erlotinib, although not as potent as elacridar could be indicated as clinically relevant efflux modulators in combination therapy to enhance brain penetration of pazopanib for the treatment of recurrent brain tumors.
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain accumulation/partitioning (brain:plasma, implied low in wild-type) = ABC efflux transporters P-gp and BCRP restrict brain partitioning of pazopanib in mice · confidence medium · **flagged for human check**
  - rationale: Primary finding: pazopanib brain partitioning is restricted by efflux transporters in normal (wild-type) mice, and only improved by elacridar co-administration - an efflux-inhibitor arm, not baseline exposure. Matched sentence itself is a design/clinical-suggestion statement.
  - span relied on: “ABC efflux transporters P-gp and BCRP restrict brain partitioning of pazopanib in mice. Further, we demonstrated that simultaneous inhibition of these efflux transporters at BBB by elacridar could significantly improve pazopanib brain accumulation.”
  - read from: pmc_body / 4. Discussion · **your verdict:** _______
- **CNS-056** · [PMID 22749591](https://pubmed.ncbi.nlm.nih.gov/22749591/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3396766/) · `full_text` · `limiting` · no number
  - > We have shown in our laboratory (manuscript under revision with) that one probable reason for limited brain penetration of pazopanib is due to ATP binding cassette efflux proteins;
  - *Determination of pazopanib (GW-786034) in mouse plasma and brain tissue by liquid chromatography-tandem mass spectrometry (LC/MS-MS).* — J Chromatogr B Analyt Technol Biomed Life Sci 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma AUC ratio = AUC ratio of 0.015 (1.5% of plasma concentration reaching brain) · confidence high
  - rationale: Primary measured brain:plasma AUC ratio of 0.015 in wild-type FVB mice after i.v. pazopanib shows severely restricted, low brain exposure - a contradicted finding, not merely an assertion.
  - span relied on: “Plasma area under the curve from time zero to the last time point (AUC t ) was 1.35 ± 0.04 min*mg/mL, as compared to 0.020 ± 0.001 min*mg/mL in the brain, giving a ratio of 0.015. This suggested that only 1.5% of the concentration in plasma was able to reach the brain.”
  - read from: pmc_body / 3.6 Method application · **your verdict:** _______
- **CNS-057** · [PMID 22749591](https://pubmed.ncbi.nlm.nih.gov/22749591/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3396766/) · `full_text` · `supporting` · no number
  - > However, the tight endothelial junctions located in brain capillaries which are further fortified by the presence of ABC efflux transporters (blood–– brain barrier, BBB) can restrict the brain penetration of pazopanib and may lead to its therapeutic inefficacy when used as an anti-tumor agent for recurrent brain tumors.
  - *Determination of pazopanib (GW-786034) in mouse plasma and brain tissue by liquid chromatography-tandem mass spectrometry (LC/MS-MS).* — J Chromatogr B Analyt Technol Biomed Life Sci 2012
  - **proposed: `unknown`** · basis `mechanistic_assertion` · restated · na · arm `not_applicable` · none = nan · confidence high
  - rationale: This is an Introduction-section mechanistic assertion about BBB/efflux transporters predicting restricted brain penetration, with no measured exposure quantity (CSF, brain concentration, Kp,uu) given for pazopanib anywhere in the supplied text.
  - span relied on: “the tight endothelial junctions located in brain capillaries which are further fortified by the presence of ABC efflux transporters (blood–– brain barrier, BBB) can restrict the brain penetration of pazopanib and may lead to its therapeutic inefficacy”
  - read from: pmc_body / 1. INTRODUCTION · **your verdict:** _______
- **CNS-058** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `abstract_only` · `supporting` · number
  - > However, dual P-gp/Bcrp1 inhibition by elacridar (GF120918), significantly enhanced pazopanib brain penetration by ~5-fold without altering its plasma concentrations.
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `transporter_knockout_or_inhibitor` · brain accumulation / brain penetration (fold-change with and without efflux inhibitor) = ~5-fold increase with elacridar (dual P-gp/Bcrp1 inhibitor); baseline (wild-type, no inhibitor) brain accumulation substantially lower, limited by P-gp and Bcrp1 · confidence high
  - rationale: The ~5-fold enhancement occurred only under dual efflux-inhibitor co-administration (elacridar), describing the transporter effect, not native exposure. The normal (wild-type, uninhibited) arm shows pazopanib brain accumulation is limited by P-gp/Bcrp1 - a contradicted finding for the drug alone.
  - span relied on: “dual P-gp/Bcrp1 inhibition by elacridar (GF120918), significantly enhanced pazopanib brain penetration by ~5-fold without altering its plasma concentrations... both P-gp and Bcrp1 act in concert to limit brain accumulation of pazopanib”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-059** · [PMID 22749591](https://pubmed.ncbi.nlm.nih.gov/22749591/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3396766/) · `abstract_only` · `supporting` · number
  - > This method was applied to determine brain to plasma concentration ratio and relevant pharmacokinetic parameters of pazopanib after a single intravenous dose of 5 mg/kg in FVB wild type mice.
  - *Determination of pazopanib (GW-786034) in mouse plasma and brain tissue by liquid chromatography-tandem mass spectrometry (LC/MS-MS).* — J Chromatogr B Analyt Technol Biomed Life Sci 2012
  - **proposed: `unknown`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma = nan · confidence low · **flagged for human check**
  - rationale: A brain:plasma ratio was measured in wild-type mice (method paper), but the actual numeric value/direction of the ratio is not reported in the supplied text, so direction cannot be judged.
  - span relied on: “This method was applied to determine brain to plasma concentration ratio and relevant pharmacokinetic parameters of pazopanib after a single intravenous dose of 5 mg/kg in FVB wild type mice.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-060** · [PMID 28869476](https://pubmed.ncbi.nlm.nih.gov/28869476/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5757517/) · `abstract_only` · `supporting` · number
  - > Pazopanib crosses the blood-brain barrier with no detectable peripheral off-side effects, and decreases p-tau in TauP301L mice.
  - *Pazopanib Reduces Phosphorylated Tau Levels and Alters Astrocytes in a Mouse Model of Tauopathy.* — J Alzheimers Dis 2017
  - **proposed: `unknown`** · basis `design_or_prediction` · unclear · mouse · arm `normal` · none = nan · confidence medium · **flagged for human check**
  - rationale: Sentence asserts BBB crossing and a behavioral/biochemical CNS effect (reduced p-tau) but no actual exposure quantity (CSF/brain concentration, Kp,uu, B:P ratio) is reported in abstract text.
  - span relied on: “pazopanib crosses the blood-brain barrier (BBB) with no detectable peripheral off-side effects, and reduces p-tau in TauP301L mice”
  - read from: pmc_body / Introduction · **your verdict:** _______

### REGORAFENIB

4 attributed of 51 retrieved sentences · 2 full text, 2 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 0 drug rows

**Proposed drug verdict: `demonstrated`** — 1 primary human claim(s), all demonstrated. Decisive claim(s): CNS-061.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-061** · [PMID 32493453](https://pubmed.ncbi.nlm.nih.gov/32493453/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7268320/) · `full_text` · `supporting` · number
  - > Supplementary information Supplementary information on clinical parameters and sample collection.Sequential therapies of the investigated drugs in the study cohort.Depiction of the used HPLC gradient for sample analysis.Overview of the used mass spectrometer parameters.Normalized chromatogram of a standard solution of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat obtained with the developed HPLC-QqQ MS method.Overview of the corresponding method performance parameters.Depiction of measured CCS values of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat.Depiction of the quantitation results for imatinib CSF samples
  - *Cerebrospinal fluid penetration of targeted therapeutics in pediatric brain tumor patients.* — Acta Neuropathol Commun 2020
  - **proposed: `demonstrated`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF concentration = moderate (1-10 nM) · confidence high
  - rationale: Primary measured CSF concentration in pediatric brain tumor patients via Ommaya reservoirs; regorafenib detected at 1-10 nM, a direct CNS exposure measurement in humans.
  - span relied on: “regorafenib and dasatinib moderate (1-10 nM) penetrance”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-062** · [PMID 42573440](https://pubmed.ncbi.nlm.nih.gov/42573440/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13471100/) · `full_text` · `supporting` · no number
  - > Although regorafenib is capable of reaching intracranial tumors, CNS exposure is limited by high plasma protein binding and active efflux transporters such as P-glycoprotein and breast cancer resistance protein at the blood–brain barrier.
  - *Pathway dysregulation and therapeutic resistance in glioblastoma: molecular mechanisms and emerging therapeutic targets.* — Future Sci OA 2026
  - **proposed: `unknown`** · basis `review_restatement` · restated · human · arm `not_applicable` · none = nan · confidence medium
  - rationale: This is a Review article paragraph citing another source [63] with a qualitative assertion about CNS exposure and efflux; no measured CSF/brain concentration, Kp,uu, or B:P ratio is reported for regorafenib in this text.
  - span relied on: “Although regorafenib is capable of reaching intracranial tumors, CNS exposure is limited by high plasma protein binding and active efflux transporters such as P-glycoprotein and breast cancer resistance protein at the blood–brain barrier.”
  - read from: pmc_body / Molecular signaling pathways and emerging therapeutic targets in GBM · **your verdict:** _______
- **CNS-063** · [PMID 39637954](https://pubmed.ncbi.nlm.nih.gov/39637954/) · `abstract_only` · `supporting` · no number
  - > Despite these overall negative findings, some data indicate improved clinical outcomes in a subset of GBM patients treated with certain PKIs (i.e., regorafenib) and encourage further research to identify PKIs with better blood-brain barrier penetration and lower risk for resistance development.
  - *Protein kinase inhibitors as targeted therapy for glioblastoma: a meta-analysis of randomized controlled clinical trials.* — Pharmacol Res 2025
  - **proposed: `unknown`** · basis `clinical_cns_response` · restated · human · arm `not_applicable` · none = nan · confidence high
  - rationale: Meta-analysis abstract notes improved outcomes in a GBM subset on PKIs including regorafenib, but calls for better BBB penetration - no exposure measurement; clinical benefit claim is vague/subset-level, not approval or definitive CNS activity.
  - span relied on: “encourage further research to identify PKIs with better blood-brain barrier penetration”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-064** · [PMID 39941744](https://pubmed.ncbi.nlm.nih.gov/39941744/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11816343/) · `abstract_only` · `supporting` · no number
  - > Additionally, the suboptimal dosing of regorafenib, due to its poor penetration of the blood-brain barrier, may reduce the likelihood of effectively targeting certain PKs.
  - *Multikinase Treatment of Glioblastoma: Evaluating the Rationale for Regorafenib.* — Cancers (Basel) 2025
  - **proposed: `unknown`** · basis `design_or_prediction` · restated · human · arm `not_applicable` · none = nan · confidence high
  - rationale: This is an unsupported assertion/discussion statement in an abstract, with no CSF, brain tissue, or Kp,uu measurement reported. No exposure quantity is given anywhere in the supplied text.
  - span relied on: “the suboptimal dosing of regorafenib, due to its poor penetration of the blood-brain barrier, may reduce the likelihood of effectively targeting certain PKs”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### RIPRETINIB

2 attributed of 5 retrieved sentences · 1 full text, 1 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_record` · CNS-manifestation trial evidence on 0 drug rows

**Proposed drug verdict: `unknown`** — No primary, normal-arm claim carries a measured or clinical finding. Decisive claim(s): nan.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-065** · [PMID 40656249](https://pubmed.ncbi.nlm.nih.gov/40656249/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12255365/) · `full_text` · `limiting` · no number
  - > Interestingly, ripretinib, a fourth-line TKI approved for advanced GIST, also has limited CNS penetration, underscoring an ongoing lack of therapeutic options for CNS metastases [].
  - *Cerebral Metastasis of a Gastrointestinal Stromal Tumor: A Case Report and Literature Review.* — Cureus 2025
  - **proposed: `unknown`** · basis `review_restatement` · restated · na · arm `not_applicable` · none = nan · confidence high
  - rationale: Discussion-section assertion citing an external reference [6], no exposure measurement (CSF/brain concentration, Kp,uu, or ratio) given for ripretinib in this case report; a restated claim, not primary data.
  - span relied on: “ripretinib, a fourth-line TKI approved for advanced GIST, also has limited CNS penetration”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-066** · [PMID 40656249](https://pubmed.ncbi.nlm.nih.gov/40656249/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12255365/) · `abstract_only` · `supporting` · no number
  - > This case underscores the absence of effective systemic treatments for CNS disease, as most TKIs, including imatinib and ripretinib, have poor CNS penetration.
  - *Cerebral Metastasis of a Gastrointestinal Stromal Tumor: A Case Report and Literature Review.* — Cureus 2025
  - **proposed: `unknown`** · basis `mechanistic_assertion` · restated · human · arm `not_applicable` · none = nan · confidence high
  - rationale: General assertion in a case report discussion, no measured exposure (CSF/brain concentration, Kp,uu, B:P ratio) for ripretinib given anywhere in the text; patient never even received the drug.
  - span relied on: “most TKIs, including imatinib and ripretinib, have poor CNS penetration”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### SELUMETINIB

2 attributed of 9 retrieved sentences · 0 full text, 2 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 12 drug rows

**Proposed drug verdict: `contradicted`** — 1 primary mouse claim(s), all contradicted. Decisive claim(s): CNS-067.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-067** · [PMID 28921565](https://pubmed.ncbi.nlm.nih.gov/28921565/) · `abstract_only` · `supporting` · number
  - > PD0325901 displayed more promising characteristics than trametinib (GSK1120212), binimetinib (MEK162), selumetinib (AZD6244), and pimasertib (AS703026): PD0325901 was the weakest substrate of P-gp and BCRP in vitro, its brain penetration was only marginally higher in Abcb1a/b;Abcg2mice, and efficient target inhibition in the brain could be achieved at clinically relevant plasma levels.
  - *The impact of P-glycoprotein and breast cancer resistance protein on the brain pharmacokinetics and pharmacodynamics of a panel of MEK inhibitors.* — Int J Cancer 2017
  - **proposed: `contradicted`** · basis `clinical_cns_response` · primary · mouse · arm `normal` · target inhibition in brain relative to plasma levels achievable in patients = target inhibition only at plasma levels far above levels in patients receiving the maximum tolerated dose · confidence high · **flagged for human check**
  - rationale: Surrounding text shows selumetinib requires supratherapeutic plasma levels (not achievable clinically) for brain target engagement, indicating effective CNS exposure/efficacy is excluded at clinically relevant doses - a contradicted finding, not merely an assertion.
  - span relied on: “Notably, target inhibition could also be demonstrated for selumetinib, but only at plasma levels far above levels in patients receiving the maximum tolerated dose.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-068** · [PMID 32939452](https://pubmed.ncbi.nlm.nih.gov/32939452/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7486535/) · `abstract_only` · `supporting` · no number
  - > We qualitatively assessed the effect of selumetinib on SNF-related spinal canal distortion, cerebrospinal fluid distribution, and spinal cord deformity on MRI.
  - *The MEK inhibitor selumetinib reduces spinal neurofibroma burden in patients with NF1 and plexiform neurofibromas.* — Neurooncol Adv 2020
  - **proposed: `unknown`** · basis `clinical_cns_response` · primary · human · arm `not_applicable` · none = nan · confidence medium · **flagged for human check**
  - rationale: Spinal neurofibromas are peripheral nerve tumors causing spinal canal/cord compression, not a CNS parenchymal tumor; no CSF/brain drug concentration or CNS tissue exposure measurement is reported, only qualitative MRI imaging of mass effect.
  - span relied on: “Eighteen patients showed subtle to a marked improvement in SNF burden, 5 remained stable, and no worsening was observed during treatment.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### SORAFENIB

13 attributed of 44 retrieved sentences · 6 full text, 7 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 17 drug rows

**Proposed drug verdict: `contradicted`** — 2 primary mouse claim(s), all contradicted. Decisive claim(s): CNS-075, CNS-076.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-069** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `full_text` · `supporting` · number
  - > The CSF penetration of sorafenib was only 0.02% relative to total (free and protein bound) plasma drug exposure.
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF:plasma penetration ratio = 0.02% (3.4% after protein binding correction) · confidence high
  - rationale: Primary measured CSF:plasma ratio in non-human primates (normal, untreated animals) is extremely low (0.02%, 3.4% free-drug corrected), indicating exclusion from CNS, not a transporter-modified or BBB-opened arm.
  - span relied on: “The CSF penetration of sorafenib was only 0.02% relative to total (free and protein bound) plasma drug exposure. ... correcting for protein binding only minimally increased the CSF penetration to 3.4%.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-070** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `full_text` · `limiting` · no number
  - > Based on our findings of limited CSF penetration, sorafenib may act in limiting metastatic spread by controlling the primary disease [].
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF:plasma / CSF penetration = limited CSF penetration · confidence high · **flagged for human check**
  - rationale: This is the paper's own primary non-human-primate CSF PK finding (title, Discussion restating their Results) showing limited CSF penetration of sorafenib, i.e., CNS exclusion, not a co-intervention or knockout arm.
  - span relied on: “Based on our findings of limited CSF penetration, sorafenib may act in limiting metastatic spread by controlling the primary disease”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-071** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `full_text` · `supporting` · no number
  - > Sorafenib is highly protein bound, and thus CSF penetration was calculated using an estimated free drug exposure.
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF:plasma penetration ratio = 0.02% (3.4% after protein-binding correction) · confidence high
  - rationale: Primary measured CSF:plasma penetration in non-human primates (normal, non-transporter-modified arm) is very low (0.02%, only 3.4% free-drug corrected), indicating CNS exclusion.
  - span relied on: “The CSF penetration of sorafenib was only 0.02% relative to total (free and protein bound) plasma drug exposure. ... correcting for protein binding only minimally increased the CSF penetration to 3.4%.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-072** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `full_text` · `supporting` · no number
  - > The drug exposure of sorafenib in the CSF relative to total and free drug plasma exposure in NHP is limited.
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF:plasma (total and free drug) = limited · confidence high · **flagged for human check**
  - rationale: Primary NHP PK study directly measured CSF relative to plasma (total and free) sorafenib exposure and found it limited - a low CSF:plasma ratio in a normal (non-transporter-modified) animal model, i.e., exclusion from CNS.
  - span relied on: “The drug exposure of sorafenib in the CSF relative to total and free drug plasma exposure in NHP is limited.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-073** · [PMID 22335402](https://pubmed.ncbi.nlm.nih.gov/22335402/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3296237/) · `full_text` · `supporting` · no number
  - > Sorafenib was chosen as the model substrate since we have previously shown that its brain penetration is restricted by BCRP and possibly by P-gp.
  - *Insight into the cooperation of P-glycoprotein (ABCB1) and breast cancer resistance protein (ABCG2) at the blood-brain barrier: a case study examining sorafenib efflux clearance.* — Mol Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · restated · mouse · arm `transporter_knockout_or_inhibitor` · brain efflux clearance / brain penetration restricted by BCRP and P-gp = sorafenib clearance out of the brain decreases when BCRP is absent at the BBB; absence of P-gp alone does not alter the efflux clearance · confidence medium · **flagged for human check**
  - rationale: Matched sentence is a restated assertion citing prior work, but surrounding Results-derived text in same Discussion gives primary BEI data in wild-type/knockout mice showing BCRP-mediated efflux restricts sorafenib brain penetration, i.e. exclusion from CNS.
  - span relied on: “This study shows that sorafenib clearance out of the brain decreases when BCRP is absent at the BBB. Interestingly, absence of P-gp alone does not alter the efflux clearance of sorafenib.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-074** · [PMID 32776310](https://pubmed.ncbi.nlm.nih.gov/32776310/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7677279/) · `full_text` · `supporting` · no number
  - > Future studies in younger rats are warranted to verify the influence of age on the brain penetration of sorafenib and its N-oxide.
  - *The Influence of Paracetamol on the Penetration of Sorafenib and Sorafenib N-Oxide Through the Blood-Brain Barrier in Rats.* — Eur J Drug Metab Pharmacokinet 2020
  - **proposed: `unknown`** · basis `design_or_prediction` · unclear · rat · arm `not_applicable` · none = nan · confidence high
  - rationale: Matched sentence is a forward-looking design suggestion, not a measurement. Surrounding text discusses study limitations (animal numbers, age, sampling) but reports no brain/plasma or CSF concentration values for sorafenib.
  - span relied on: “Future studies in younger rats are warranted to verify the influence of age on the brain penetration of sorafenib and its N-oxide.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-075** · [PMID 20952483](https://pubmed.ncbi.nlm.nih.gov/20952483/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3014301/) · `abstract_only` · `supporting` · number
  - > Steady-state brain-to-plasma concentration ratio of sorafenib was approximately 0.36 ± 0.056 in the Bcrp1(-/-) mice, 0.11 ± 0.021 in the Mdr1a/b(-/-) mice, and 0.91 ± 0.29 in the Mdr1a/b(-/-)Bcrp1(-/-) mice compared with 0.094 ± 0.007 in the wild-type mice.
  - *The role of the breast cancer resistance protein (ABCG2) in the distribution of sorafenib to the brain.* — J Pharmacol Exp Ther 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma concentration ratio = 0.094 ± 0.007 in the wild-type mice (brain-to-plasma equilibrium-distribution coefficient 0.06 in wild-type mice) · confidence high
  - rationale: Wild-type (normal transporter) mice show low brain-to-plasma ratio (~0.09) and distribution coefficient 0.06, indicating sorafenib is excluded from CNS under native BBB efflux; knockout/inhibitor arms don't reflect normal exposure.
  - span relied on: “compared with 0.094 ± 0.007 in the wild-type mice. ... The brain-to-plasma equilibrium-distribution coefficient ... was 0.06 in wild-type mice.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-076** · [PMID 20952483](https://pubmed.ncbi.nlm.nih.gov/20952483/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3014301/) · `abstract_only` · `supporting` · number
  - > Sorafenib brain-to-plasma ratios increased on coadministration of the dual P-gp/BCRP inhibitor elacridar such that the ratio in wild-type mice (0.76 ± 0.24), Bcrp1(-/-) mice (1.03 ± 0.33), Mdr1a/b(-/-) mice (1.3 ± 0.29), and Mdr1a/b(-/-)Bcrp1(-/-) mice (0.73 ± 0.35) were not significantly different.
  - *The role of the breast cancer resistance protein (ABCG2) in the distribution of sorafenib to the brain.* — J Pharmacol Exp Ther 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio / AUC brain:plasma coefficient = 0.06 (AUC coefficient) and 0.094 ± 0.007 (steady-state brain-to-plasma ratio) in wild-type mice · confidence high
  - rationale: Wild-type (normal, no transporter knockout/inhibitor) mice show brain:plasma ratios of 0.06-0.094, a low absolute ratio indicating exclusion from CNS; the matched sentence's elevated ratios only occur with elacridar co-administration (transporter inhibitor arm), not normal exposure.
  - span relied on: “The brain-to-plasma equilibrium-distribution coefficient (area under the concentration-time profiles for plasma/area under the concentration-time profiles for brain) was 0.06 in wild-type mice. Steady-state brain-to-plasma concentration ratio of sorafenib was approximately ... 0.094 ± 0.007 in the wild-type mice.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-077** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `abstract_only` · `supporting` · number
  - > The mean CSF penetration of sorafenib was 0.02% and 3.4% after correcting for plasma protein binding.
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF:plasma AUC ratio (CSF penetration) = 0.02% (unadjusted), 3.4% (protein-binding corrected) · confidence high
  - rationale: Primary measured CSF:plasma AUC ratio in non-human primates (normal, non-transporter-modified) is low in absolute terms (0.02-3.4%), indicating exclusion from CSF compartment.
  - span relied on: “The mean CSF penetration of sorafenib was 0.02% and 3.4% after correcting for plasma protein binding.”
  - read from: pmc_body / Results · **your verdict:** _______
- **CNS-078** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `abstract_only` · `supporting` · no number
  - > The CSF penetration of sorafenib is limited relative to total and free drug exposure in plasma.
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF:plasma penetration (%) = 0.02% relative to total plasma exposure; 3.4% after correcting for protein binding · confidence high
  - rationale: Primary measured PK in non-human primates (normal, untreated) shows CSF penetration of 0.02%/3.4%, a low ratio indicating exclusion from CSF compartment - a contradicted finding, not merely an assertion.
  - span relied on: “The CSF penetration of sorafenib was only 0.02% relative to total (free and protein bound) plasma drug exposure. ... correcting for protein binding only minimally increased the CSF penetration to 3.4%.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-079** · [PMID 22335402](https://pubmed.ncbi.nlm.nih.gov/22335402/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3296237/) · `abstract_only` · `supporting` · no number
  - > The present study uses the brain penetration of sorafenib to investigate these findings and attempts to explain the mechanistic basis of this cooperation with a simple theory based on affinity and capacity dependent carrier-mediated transport.
  - *Insight into the cooperation of P-glycoprotein (ABCB1) and breast cancer resistance protein (ABCG2) at the blood-brain barrier: a case study examining sorafenib efflux clearance.* — Mol Pharm 2012
  - **proposed: `unknown`** · basis `measured_pk_animal` · primary · mouse · arm `transporter_knockout_or_inhibitor` · brain efflux clearance (not a brain:plasma or CSF:plasma exposure ratio) = Sorafenib clearance out of the brain decreased 2-fold in the Bcrp1(-/-) mice and 2.5-fold in the Mdr1a/1b(-/-)Bcrp1(-/-) mice. Clearance out of brain when P-gp was absent did not change significantly compared to wild-type. · confidence medium · **flagged for human check**
  - rationale: Only efflux clearance in knockout mice is reported, not a brain:plasma/CSF exposure ratio or wild-type concentration measurement; no wild-type exposure value given to judge direction, so unknown per rubric trap 1.
  - span relied on: “Sorafenib clearance out of the brain decreased 2-fold in the Bcrp1(-/-) mice and 2.5-fold in the Mdr1a/1b(-/-)Bcrp1(-/-) mice. Clearance out of brain when P-gp was absent did not change significantly compared to wild-type.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-080** · [PMID 32776310](https://pubmed.ncbi.nlm.nih.gov/32776310/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7677279/) · `abstract_only` · `supporting` · no number
  - > Pharmacokinetic analysis revealed increased brain exposure to sorafenib and sorafenib N-oxide after co-administration of paracetamol.
  - *The Influence of Paracetamol on the Penetration of Sorafenib and Sorafenib N-Oxide Through the Blood-Brain Barrier in Rats.* — Eur J Drug Metab Pharmacokinet 2020
  - **proposed: `demonstrated`** · basis `measured_pk_animal` · primary · rat · arm `bbb_modifying_cointervention` · brain tissue concentration/exposure = increased brain exposure to sorafenib after co-administration of paracetamol · confidence medium · **flagged for human check**
  - rationale: Primary rat PK measurement shows sorafenib reaches brain tissue (detectable exposure), but the increase is attributed to paracetamol co-administration, a BBB-modifying cointervention, not baseline sorafenib penetration alone.
  - span relied on: “A single administration of paracetamol increases exposure to sorafenib and sorafenib N-oxide in the brain tissue.”
  - read from: pmc_body / Key Points · **your verdict:** _______
- **CNS-081** · [PMID 36768736](https://pubmed.ncbi.nlm.nih.gov/36768736/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9917080/) · `abstract_only` · `supporting` · no number
  - > Among these problems, the presence of the blood-brain barrier of the brain and the need to use high doses of sorafenib, the existence of mechanisms for the redistribution of sorafenib and its release in the brain tissue, as well as the high resistance of gliomas and glioblastomas to therapy should be considered the main ones.
  - *Ca-Dependent Effects of the Selenium-Sorafenib Nanocomplex on Glioblastoma Cells and Astrocytes of the Cerebral Cortex: Anticancer Agent and Cytoprotector.* — Int J Mol Sci 2023
  - **proposed: `unknown`** · basis `design_or_prediction` · restated · na · arm `not_applicable` · none = nan · confidence high
  - rationale: Background framing asserting BBB limits sorafenib delivery and motivating a new nanocomplex; no measured CSF/brain concentration, Kp,uu, or B:P ratio given for sorafenib itself.
  - span relied on: “the presence of the blood-brain barrier of the brain and the need to use high doses of sorafenib, the existence of mechanisms for the redistribution of sorafenib and its release in the brain tissue”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### SUNITINIB

11 attributed of 25 retrieved sentences · 3 full text, 8 abstract-only · ChEMBL calculated flag: `predicted_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 5 drug rows

**Proposed drug verdict: `contradicted`** — 1 primary mouse claim(s), all contradicted. Decisive claim(s): CNS-090.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-082** · [PMID 37997517](https://pubmed.ncbi.nlm.nih.gov/37997517/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10726873/) · `full_text` · `supporting` · number
  - > One potential reason for this could be due to its limited penetration through an intact BBB.A study by Sobanska and colleagues used a rabbit model to show that the exposure of sunitinib in plasma, aqueous humor, and CSF was different depending on the time of day of drug administration (8 am dose area under the curve [AUC], CSF: 55.5 ng*h/mL vs.
  - *Chemotherapy in pediatric brain tumor and the challenge of the blood-brain barrier.* — Cancer Med 2023
  - **proposed: `contradicted`** · basis `measured_pk_animal` · restated · other_animal · arm `normal` · CSF AUC / BBB penetration percentage = sunitinib penetration through the BBB was reported to be very low (<5%) and comparable in both dosing groups; CSF AUC 55.5 ng*h/mL (8am) vs 66.3 ng*h/mL (9pm) · confidence high
  - rationale: Rabbit PK study (normal, non-transporter-modified) reports measured CSF exposure and explicitly states BBB penetration was very low (<5%), a contradicted finding despite CSF being detectable.
  - span relied on: “sunitinib penetration through the BBB was reported to be very low (<5%) and comparable in both dosing groups”
  - read from: pmc_body / Sunitinib · **your verdict:** _______
- **CNS-083** · [PMID 37997517](https://pubmed.ncbi.nlm.nih.gov/37997517/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10726873/) · `full_text` · `supporting` · number
  - > 9 pm dose AUC, CSF: 66.3 ng*h/mL, respectively).However, sunitinib penetration through the BBB was reported to be very low (<5%) and comparable in both dosing groups.
  - *Chemotherapy in pediatric brain tumor and the challenge of the blood-brain barrier.* — Cancer Med 2023
  - **proposed: `contradicted`** · basis `measured_pk_animal` · restated · other_animal · arm `normal` · CSF:plasma penetration ratio (BBB penetration %) = &lt;5% · confidence medium
  - rationale: Rabbit PK study (cited ref 108) reports measured CSF AUC values and BBB penetration <5%, a low absolute exposure ratio in a normal (non-transporter-modified) animal model - meets contradicted criteria.
  - span relied on: “sunitinib penetration through the BBB was reported to be very low (<5%) and comparable in both dosing groups”
  - read from: pmc_body / Sunitinib · **your verdict:** _______
- **CNS-084** · [PMID 37997517](https://pubmed.ncbi.nlm.nih.gov/37997517/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10726873/) · `full_text` · `supporting` · number
  - > To overcome the limitations of the BBB, a study by Szalek and colleagues evaluated the antibiotic ciprofloxacin to modulate the BBB and enhance penetration of sunitinib.They found that rabbits treated with sunitinib + ciprofloxacin had higher 24‐h CSF exposures (AUCand C) compared to those that only received sunitinib (50.4 vs.
  - *Chemotherapy in pediatric brain tumor and the challenge of the blood-brain barrier.* — Cancer Med 2023
  - **proposed: `unknown`** · basis `measured_pk_animal` · restated · other_animal · arm `bbb_modifying_cointervention` · CSF AUC0-24 and Cmax = 50.4 vs. 155 ng*h/mL and 4.2 vs. 18 ng/mL (sunitinib alone vs. sunitinib + ciprofloxacin) · confidence medium · **flagged for human check**
  - rationale: This is a restatement (Review article, citing ref 109) of a rabbit PK study where ciprofloxacin co-administration was used to modulate BBB and boost sunitinib CSF exposure - a BBB-modifying co-intervention, not sunitinib's own CNS penetration; also secondary restatement.
  - span relied on: “rabbits treated with sunitinib + ciprofloxacin had higher 24‐h CSF exposures (AUC 0–24 and C max ) compared to those that only received sunitinib (50.4 vs. 155 ng*h/mL and 4.2 vs. 18 ng/mL)”
  - read from: pmc_body / Sunitinib · **your verdict:** _______
- **CNS-085** · [PMID 22166826](https://pubmed.ncbi.nlm.nih.gov/22166826/) · `abstract_only` · `supporting` · number
  - > The chemotherapy (gemcitabine and cisplatin) and the molecular target therapy (sunitinib) were administerd but the primary lesion and metastases was progressive and serum G-CSF concentration was elevated to 229 pg/ml.
  - *[Granulocyte-colony-stimulating factor (G-CSF)-producing carcinoma of collecting ducts of Bellini: a case report].* — Hinyokika Kiyo 2011
  - **proposed: `unknown`** · basis `clinical_cns_response` · primary · human · arm `not_applicable` · none = nan · confidence high
  - rationale: No CNS tumor/disease site, no CSF or brain concentration, no brain:plasma ratio. This is a renal collecting-duct carcinoma with systemic metastases progressing on sunitinib plus chemo; no CNS exposure data given.
  - span relied on: “nan”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-086** · [PMID 26813470](https://pubmed.ncbi.nlm.nih.gov/26813470/) · `abstract_only` · `supporting` · number
  - > The concentrations of sunitinib and its active metabolite (SU12662) in the plasma, CSF, AH were measured with the validated HPLC-UV method.
  - *The influence of the time-of-day administration of sunitinib on the penetration through the blood-brain and blood-aqueous humour barriers in rabbits.* — Eur Rev Med Pharmacol Sci 2016
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF concentration (AUC0-t) and CSF:plasma penetration ratio = CSF AUC0-t 55.5 and 66.3 ng×h/mL vs plasma AUC0-t 2051.8 and 3069.3 ng×h/mL; penetration through BBB <5% · confidence high
  - rationale: Primary measured CSF and plasma AUCs in normal (non-transporter-modified) rabbits show CSF exposure <5% of plasma, an explicit low penetration ratio - direct contradicted finding, not merely an assertion.
  - span relied on: “the degree of sunitinib penetration through the BAB and BBB was very low (< 5%) and comparable in both groups”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-087** · [PMID 26813470](https://pubmed.ncbi.nlm.nih.gov/26813470/) · `abstract_only` · `supporting` · number
  - > After the evening administration (8 p.m.) the exposure to sunitinib in the rabbits' plasma, AH and CSF was higher than after the morning administration (8 a.m.), but the degree of sunitinib penetration through the BAB and BBB was very low (< 5%) and comparable in both groups.
  - *The influence of the time-of-day administration of sunitinib on the penetration through the blood-brain and blood-aqueous humour barriers in rabbits.* — Eur Rev Med Pharmacol Sci 2016
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF:plasma penetration ratio (AUC-based, % penetration through BBB) = degree of sunitinib penetration through the BAB and BBB was very low (< 5%) · confidence high
  - rationale: Primary measured PK in normal rabbits (CSF/plasma AUC) shows BBB penetration <5%, a low absolute ratio indicating CNS exclusion, not a transporter-knockout or BBB-opening co-intervention study.
  - span relied on: “the degree of sunitinib penetration through the BAB and BBB was very low (< 5%) and comparable in both groups”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-088** · [PMID 20524040](https://pubmed.ncbi.nlm.nih.gov/20524040/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2997175/) · `abstract_only` · `supporting` · no number
  - > These results indicate that sunitinib may be an important pharmacologic agent for the treatment of invasive medulloblastoma, particularly given evidence of its ability to cross the blood-brain barrier to target tumor cells, and thus warrants further in vivo testing for confirmation of efficacy.
  - *Sunitinib induces PTEN expression and inhibits PDGFR signaling and migration of medulloblastoma cells.* — J Neurooncol 2010
  - **proposed: `unknown`** · basis `mechanistic_assertion` · restated · in_vitro · arm `not_applicable` · none = nan · confidence high
  - rationale: All experiments in this abstract are in vitro cell migration/signaling assays; the BBB-crossing claim is an unsupported assertion citing external evidence, not a measured exposure in this text.
  - span relied on: “particularly given evidence of its ability to cross the blood-brain barrier to target tumor cells”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-089** · [PMID 22238213](https://pubmed.ncbi.nlm.nih.gov/22238213/) · `abstract_only` · `supporting` · no number
  - > Combined elacridar plus N-desethyl sunitinib treatment increased N-desethyl sunitinib plasma and brain exposures, but not brain-to-plasma ratios in wild-type mice.
  - *P-glycoprotein (ABCB1) and breast cancer resistance protein (ABCG2) restrict brain accumulation of the active sunitinib metabolite N-desethyl sunitinib.* — J Pharmacol Exp Ther 2012
  - **proposed: `unknown`** · basis `measured_pk_animal` · primary · mouse · arm `transporter_knockout_or_inhibitor` · brain-to-plasma ratio / brain concentration (of N-desethyl sunitinib metabolite) = 13.7-fold increased brain accumulation of N-desethyl sunitinib in Abcb1a/1b(-/-)/Abcg2(-/-) mice; elacridar increased plasma/brain exposure but not brain-to-plasma ratio in wild-type mice · confidence high · **flagged for human check**
  - rationale: All measured exposure data in this text concern the metabolite N-desethyl sunitinib, not sunitinib itself. Sunitinib parent drug brain exposure is not reported here, so no direct verdict on sunitinib can be made.
  - span relied on: “brain accumulation of N-desethyl sunitinib was markedly increased (13.7-fold) in Abcb1a/1b(-/-)/Abcg2(-/-) mice, but not in Abcb1a/1b(-/-) or Abcg2(-/-) mice. In the absence of the ABCB1 and ABCG2 inhibitor elacridar, brain concentrations of N-desethyl sunitinib were detectable only in Abcb1a/1b(-/-)/Abcg2(-/-) mice after sunitinib administration.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-090** · [PMID 24113148](https://pubmed.ncbi.nlm.nih.gov/24113148/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3836310/) · `abstract_only` · `supporting` · no number
  - > Overall, these findings indicate that there is a cooperation at the blood-brain barrier (BBB) in restricting the brain penetration of sunitinib, and brain delivery can be enhanced by administration of a dual inhibitor.
  - *Pharmacokinetic assessment of efflux transport in sunitinib distribution to the brain.* — J Pharmacol Exp Ther 2013
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma AUC ratio = wild-type baseline brain-to-plasma ratio (implied low; elacridar-coadministered WT ratio ≈12 vs Mdr1a/b(-/-)Bcrp1(-/-) ≈17.3) · confidence medium · **flagged for human check**
  - rationale: Primary mouse PK shows efflux transporters (P-gp, Bcrp) in intact wild-type BBB restrict sunitinib brain penetration; baseline (normal) distribution is limited, only enhanced by inhibitor/knockout, consistent with CNS exclusion in normal animals.
  - span relied on: “The brain-to-plasma ratio after coadministration of elacridar in wild-type mice was ≈ 12 compared with ≈ 17.3 in Mdr1a/b(-/-)Bcrp1(-/-) mice.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-091** · [PMID 26813470](https://pubmed.ncbi.nlm.nih.gov/26813470/) · `abstract_only` · `supporting` · no number
  - > Therefore, the penetration of sunitinib through the blood-brain barrier (BBB) and blood-aqueous humour barrier (BAB) is an issue of growing interest.
  - *The influence of the time-of-day administration of sunitinib on the penetration through the blood-brain and blood-aqueous humour barriers in rabbits.* — Eur Rev Med Pharmacol Sci 2016
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF AUC and CSF:plasma penetration ratio = CSF AUC0-t 55.5 and 66.3 ng×h/mL vs plasma AUC0-t 2051.8 and 3069.3 ng×h/mL; penetration through BBB <5% · confidence high
  - rationale: Primary measured CSF/plasma exposure in normal rabbits shows BBB penetration <5%, a low absolute ratio, directly contradicting CNS exposure despite being in abstract-only text.
  - span relied on: “the degree of sunitinib penetration through the BAB and BBB was very low (< 5%) and comparable in both groups”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-092** · [PMID 26813470](https://pubmed.ncbi.nlm.nih.gov/26813470/) · `abstract_only` · `supporting` · no number
  - > The aim of the study was to investigate the influence of the time-of-day administration on the penetration of sunitinib into the cerebrospinal fluid (CSF) and aqueous humour (AH).
  - *The influence of the time-of-day administration of sunitinib on the penetration through the blood-brain and blood-aqueous humour barriers in rabbits.* — Eur Rev Med Pharmacol Sci 2016
  - **proposed: `demonstrated`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF AUC0-t (cerebrospinal fluid concentration) = Cerebrospinal AUC0-t for sunitinib in groups I and II were 55.5 and 66.3 ng x h/mL, respectively · confidence medium · **flagged for human check**
  - rationale: Rabbits (normal, non-transporter-modified) show detectable, measured sunitinib CSF concentrations, i.e. actual CNS exposure, even though penetration ratio vs plasma is low (<5%), which the paper itself still reports as measurable, non-zero CSF exposure.
  - span relied on: “The cerebrospinal AUC0-t for sunitinib in groups I and II were 55.5 and 66.3 ng × h/mL, respectively.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### TIVOZANIB

1 attributed of 2 retrieved sentences · 0 full text, 1 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_record` · CNS-manifestation trial evidence on 0 drug rows

**Proposed drug verdict: `contradicted`** — 1 primary mouse claim(s), all contradicted. Decisive claim(s): CNS-093.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-093** · [PMID 32234426](https://pubmed.ncbi.nlm.nih.gov/32234426/) · `abstract_only` · `limiting` · no number
  - > The modest effect of ABC transporters on tivozanib brain accumulation, if also true in humans, might mean that this drug is not strongly limited in its therapeutic efficacy against malignant lesions situated partly or completely behind the blood-brain barrier.
  - *Brain accumulation of tivozanib is restricted by ABCB1 (P-glycoprotein) and ABCG2 (breast cancer resistance protein) in mice.* — Int J Pharm 2020
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio = increased 2.2-fold in Abcb1a/1b -/- and 2.6-fold in Abcb1a/1b;Abcg2 -/- vs wild-type · confidence high · **flagged for human check**
  - rationale: Wild-type brain-to-plasma ratio is markedly lower than knockout ratios, indicating transporter-mediated exclusion in the normal (wild-type) arm; knockout fold-increases describe the transporters, not patient exposure. Matched sentence itself is a prediction/discussion statement.
  - span relied on: “The brain-to-plasma ratios were significantly increased in Abcb1a/1b -/- (2.2-fold) and Abcb1a/1b;Abcg2 -/- (2.6-fold) mice compared to wild-type mice, indicating a modest protective role of these transporters in the blood-brain barrier.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### TOVORAFENIB

3 attributed of 4 retrieved sentences · 1 full text, 2 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 7 drug rows

**Proposed drug verdict: `contradicted`** — 1 primary mouse claim(s), all contradicted. Decisive claim(s): CNS-095.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-094** · [PMID 38291372](https://pubmed.ncbi.nlm.nih.gov/38291372/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10826080/) · `full_text` · `supporting` · no number
  - > Finally, tovorafenib had greater CNS penetration compared with the type I RAF inhibitor dabrafenib [].
  - *LOGGIC/FIREFLY-2: a phase 3, randomized trial of tovorafenib vs. chemotherapy in pediatric and young adult patients with newly diagnosed low-grade glioma harboring an activating RAF alteration.* — BMC Cancer 2024
  - **proposed: `unknown`** · basis `review_restatement` · restated · na · arm `not_applicable` · none = nan · confidence high
  - rationale: Background section assertion citing another reference [32], no measured exposure value (CSF/brain concentration, Kp,uu, or ratio) given in matched sentence or surrounding text; this is a restated comparative claim, not primary PK data.
  - span relied on: “tovorafenib had greater CNS penetration compared with the type I RAF inhibitor dabrafenib”
  - read from: pmc_body / Background · **your verdict:** _______
- **CNS-095** · [PMID 30622172](https://pubmed.ncbi.nlm.nih.gov/30622172/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6374543/) · `abstract_only` · `supporting` · number
  - > The purpose of this study was to perform a quantitative assessment and evaluation of the influence of efflux mechanisms at the blood-brain barrier (BBB), in particular, Abcb1/P-glycoprotein (P-gp) and Abcg2/breast cancer resistance protein (Bcrp), on the brain distribution of three panRAF inhibitors: CCT196969 [1-(3-(-butyl)-1-phenyl-1-pyrazol-5-yl)-3-(2-fluoro-4-((3-oxo-3,4-dihydropyrido[2,3-b]pyrazin-8-yl)oxy)phenyl)urea], LY3009120 1-(3,3-Dimethylbutyl)-3-(2-fluoro-4-methyl-5-(7-methyl-2-(methylamino)pyrido(2,3-d)pyrimidin-6-yl)phenyl)urea, and MLN2480 [4-pyrimidinecarboxamide, 6-amino-5-chloro--[(1)-1-[5-[[[5-chloro-4-(trifluoromethyl)-2-pyridinyl]amino]carbonyl]-2-thiazolyl]ethyl]-].
  - *Brain Distribution and Active Efflux of Three panRAF Inhibitors: Considerations in the Treatment of Melanoma Brain Metastases.* — J Pharmacol Exp Ther 2019
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain distribution (brain:plasma, wild-type mice) = brain distribution of ... MLN2480 is limited, and is enhanced in transgenic mice lacking P-gp and Bcrp · confidence high
  - rationale: MLN2480 is tovorafenib. Wild-type mouse brain distribution is reported as limited; enhancement only occurs in P-gp/Bcrp knockout mice, consistent with efflux-restricted normal-arm exposure.
  - span relied on: “In vivo studies in mice show that the brain distribution of CCT196969, LY3009120, and MLN2480 is limited, and is enhanced in transgenic mice lacking P-gp and Bcrp.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-096** · [PMID 38884947](https://pubmed.ncbi.nlm.nih.gov/38884947/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11404696/) · `abstract_only` · `supporting` · no number
  - > The advent of pan-RAF inhibitors, notably Tovorafenib, offers a promising advance, demonstrating enhanced efficacy and better penetration of the blood-brain barrier, without the issue of paradoxical activation.
  - *A critical review of RAF inhibitors in BRAF-mutated glioma treatment.* — Pharmacogenomics 2024
  - **proposed: `unknown`** · basis `review_restatement` · restated · na · arm `not_applicable` · none = nan · confidence high
  - rationale: This is a Review abstract asserting BBB penetration with no exposure measurement (no CSF/brain concentration, Kp,uu, or ratio) reported anywhere in the supplied text; a qualitative restatement only.
  - span relied on: “demonstrating enhanced efficacy and better penetration of the blood-brain barrier”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### TRAMETINIB

2 attributed of 13 retrieved sentences · 0 full text, 2 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 2 drug rows

**Proposed drug verdict: `contradicted`** — 1 primary mouse claim(s), all contradicted. Decisive claim(s): CNS-097.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-097** · [PMID 24875464](https://pubmed.ncbi.nlm.nih.gov/24875464/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4109207/) · `abstract_only` · `supporting` · no number
  - > In vitro studies indicated that trametinib is a substrate for both P-glycoprotein (P-gp) and Bcrp, efflux transporters found at the blood-brain barrier.
  - *Factors influencing the CNS distribution of a novel MEK-1/2 inhibitor: implications for combination therapy for melanoma brain metastases.* — Drug Metab Dispos 2014
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma partition coefficient (AUCbrain/AUCplasma) = ~5-fold higher in Mdr1a/b(-/-) and triple knockout mice vs wild-type and Bcrp1(-/-) mice; similar between wild-type and Bcrp knockout mice · confidence high
  - rationale: Matched sentence is an in-vitro substrate assertion (trap 3/unknown alone), but surrounding text reports wild-type mouse AUCbrain/AUCplasma is markedly lower than knockout, indicating restricted CNS exposure in the normal (non-knockout) arm.
  - span relied on: “The brain-to-plasma partition coefficient (AUCbrain/AUCplasma) was approximately 5-fold higher in Mdr1a/b((-/-)) (P-gp knockout) and Mdr1a/b((-/-))Bcrp1((-/-)) (triple knockout) mice when compared with wild-type and Bcrp1((-/-)) (Bcrp knockout) mice.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-098** · [PMID 31063549](https://pubmed.ncbi.nlm.nih.gov/31063549/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7571492/) · `abstract_only` · `supporting` · no number
  - > In vivo, PK analysis revealed enhanced blood-brain barrier penetration of trametinib after oHSV treatment.
  - *Oncolytic HSV therapy increases trametinib access to brain tumors and sensitizes them in vivo.* — Neuro Oncol 2019
  - **proposed: `unknown`** · basis `preclinical_cns_efficacy` · primary · mouse · arm `bbb_modifying_cointervention` · brain:plasma (qualitative, "enhanced blood-brain barrier penetration") = enhanced blood-brain barrier penetration of trametinib after oHSV treatment (no numeric value given) · confidence medium · **flagged for human check**
  - rationale: The increase in brain exposure is attributed to oHSV co-treatment (a BBB-modifying cointervention), not trametinib's intrinsic CNS penetration; no baseline/absolute PK values given for trametinib alone.
  - span relied on: “In vivo, PK analysis revealed enhanced blood-brain barrier penetration of trametinib after oHSV treatment.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### VEMURAFENIB

26 attributed of 42 retrieved sentences · 14 full text, 12 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 0 drug rows

**Proposed drug verdict: `contradicted`** — 4 primary human claim(s), all contradicted. Decisive claim(s): CNS-117, CNS-118, CNS-123, CNS-124.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-099** · [PMID 26579371](https://pubmed.ncbi.nlm.nih.gov/26579371/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4590304/) · `full_text` · `supporting` · number
  - > Furthermore, in their knockout mouse model, the brain-to-plasma ratios of vemurafenib were increased significantly when Abc1a/1b and Abcg2 were both absent.
  - *The pharmacological impact of ATP-binding cassette drug transporters on vemurafenib-based therapy.* — Acta Pharm Sin B 2014
  - **proposed: `unknown`** · basis `review_restatement` · restated · mouse · arm `transporter_knockout_or_inhibitor` · brain-to-plasma ratio = increased significantly when Abc1a/1b and Abcg2 were both absent (vs WT, not quantified) · confidence medium
  - rationale: This is a review restating another paper's knockout-mouse PK finding describing transporter exclusion, not exposure a normal patient receives; no WT ratio value given to judge direction for normal arm.
  - span relied on: “the brain-to-plasma ratios of vemurafenib were increased significantly when Abc1a/1b and Abcg2 were both absent”
  - read from: pmc_body / The pharmacological impact of ABC drug transporters on the bioavailability and distribution of vemurafenib · **your verdict:** _______
- **CNS-100** · [PMID 26579371](https://pubmed.ncbi.nlm.nih.gov/26579371/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4590304/) · `full_text` · `supporting` · number
  - > Durmus et al.reported that inhibition of both ABCB1 and ABCG2 could significantly improve the bioavailability (A) and brain penetration (B) of vemurafenib.
  - *The pharmacological impact of ATP-binding cassette drug transporters on vemurafenib-based therapy.* — Acta Pharm Sin B 2014
  - **proposed: `unknown`** · basis `review_restatement` · restated · mouse · arm `transporter_knockout_or_inhibitor` · brain-to-plasma ratio / brain accumulation (elacridar/knockout vs WT) = elacridar significantly elevated the plasma levels of vemurafenib and brain accumulation in WT mice to the same levels as in Abc1a/1b−/−;Abcg2−/− mice · confidence medium · **flagged for human check**
  - rationale: This is a review restating Durmus et al.'s findings from an efflux-inhibitor/knockout study, not normal physiological exposure. Describes transporter effect, not exposure achieved without inhibition, so does not demonstrate CNS delivery in patients.
  - span relied on: “In vivo, the dual Abcb1a/1b and Abcg2 inhibitor elacridar significantly elevated the plasma levels of vemurafenib and brain accumulation in WT mice to the same levels as in Abc1a/1b−/−;Abcg2−/− mice.”
  - read from: pmc_body / The pharmacological impact of ABC drug transporters on the bioavailability and distribution of vemurafenib · **your verdict:** _______
- **CNS-101** · [PMID 26579371](https://pubmed.ncbi.nlm.nih.gov/26579371/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4590304/) · `full_text` · `supporting` · number
  - > The clinical application of a dual ABCB1 and ABCG2 inhibitor such as elacridar could possibly provide a solution to increase the oral bioavailability and enhance brain penetration of vemurafenib in patients with brain metastatic melanoma.
  - *The pharmacological impact of ATP-binding cassette drug transporters on vemurafenib-based therapy.* — Acta Pharm Sin B 2014
  - **proposed: `unknown`** · basis `review_restatement` · restated · na · arm `not_applicable` · none = nan · confidence high
  - rationale: This Conclusions-section review paragraph asserts limited brain penetration and proposes elacridar as a future solution, but cites no measured brain/CSF/plasma exposure values; it is a restatement/design proposal, not a primary PK measurement.
  - span relied on: “the actions of ABCB1 and ABCG2 in the GI tract and at the BBB contribute significantly to reduced oral bioavailability and limit the penetration of the brain by vemurafenib”
  - read from: pmc_body / Conclusions · **your verdict:** _______
- **CNS-102** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > These observations seem to be corroborated by a clinical study showing that the concentration of vemurafenib in cerebrospinal fluid (CSF) was < 1% of the plasma concentration [].
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `contradicted`** · basis `review_restatement` · restated · human · arm `normal` · CSF:plasma concentration ratio = < 1% of the plasma concentration · confidence medium · **flagged for human check**
  - rationale: This is a restatement (citation [22]) of a clinical CSF:plasma measurement in humans showing very low vemurafenib CNS exposure - a clear exclusion finding, though the primary data are not reproduced here.
  - span relied on: “the concentration of vemurafenib in cerebrospinal fluid (CSF) was < 1% of the plasma concentration”
  - read from: pmc_body / (untitled section) · **your verdict:** _______
- **CNS-103** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > Vemurafenib has intrinsic antitumor potential against intracranial A375 tumors The brain penetration of vemurafenib was previously reported to be significantly higher (between approximately 20‐ and 80‐fold) incompared with WT mice [,].
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `unknown`** · basis `review_restatement` · restated · mouse · arm `transporter_knockout_or_inhibitor` · brain:plasma (restated from prior reports) = 20- to 80-fold higher in Abcb1a/b;Abcg2-/- vs WT mice · confidence high
  - rationale: This is a restatement of prior literature (citations 18,19), not a primary measurement in this paper, and the comparison is knockout vs WT, describing transporter effect rather than normal-patient CNS exposure.
  - span relied on: “The brain penetration of vemurafenib was previously reported to be significantly higher (between approximately 20‐ and 80‐fold) in Abcb1a/b;Abcg2 −/− compared with WT mice [ 18 , 19 ].”
  - read from: pmc_body / Vemurafenib has intrinsic antitumor potential against intracranial A375 tumors · **your verdict:** _______
- **CNS-104** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > Vemurafenib penetration into subcutaneous tumors is similar in WT andmice and as we found that vemurafenib was equally effective (Fig.) and did not result in body weight loss (Fig.), we selected these dose regimens for the efficacy study against intracranial A375 tumors.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `unknown`** · basis `measured_pk_animal` · primary · mouse · arm `transporter_knockout_or_inhibitor` · subcutaneous tumor penetration (not CNS compartment) = Vemurafenib penetration into subcutaneous tumors is similar in WT and Abcb1a/b;Abcg2 −/− mice · confidence high · **flagged for human check**
  - rationale: This measurement is about subcutaneous (non-CNS) tumor exposure used to dose-level between strains before the intracranial efficacy study; it is not a CSF, brain, or Kp,uu measurement, so it does not speak to CNS penetration.
  - span relied on: “Vemurafenib penetration into subcutaneous tumors is similar in WT and Abcb1a/b;Abcg2 −/− mice”
  - read from: pmc_body / Dose adaptions between WT and Abcb1a/b;Abcg2 −/− mice are needed to level the systemic exposure of vemurafenib between strains · **your verdict:** _______
- **CNS-105** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > These drug distribution data are in line with the observed intracranial antitumor efficacy (Fig.), as vemurafenib tumor concentrations were similar between WT mice receiving 25 mg·kgand WT mice receiving 10 mg·kgof vemurafenib with concomitant elacridar, but lower than inmice receiving 10 or 25 mg·kgvemurafenib.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio / tissue concentration in normal brain and tumor core = tissue-plasma ratios very close to total blood volume (~2%); negligible penetration in normal brain of WT mice; tumor core levels ~half of those in knockout mice · confidence high
  - rationale: WT (normal, non-transporter-modified) mice show negligible brain penetration, ratio ~blood volume only; elacridar partially rescues but WT alone is excluded, consistent with contradicted in the normal arm.
  - span relied on: “the vemurafenib penetration in normal brain regions of WT mice was negligible. The tissue–plasma ratios were very close to the total blood volume of the murine brain (approximately 2%)”
  - read from: pmc_body / P‐gp and BCRP reduce vemurafenib penetration in MBMs · **your verdict:** _______
- **CNS-106** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > Intracranial A375 tumors develop therapy resistance despite sufficient vemurafenib tumor penetration and target inhibition As mentioned above, the A375 MBM model is responsive to vemurafenib, but developed therapy resistance after just a few days of treatment inmice receiving 10 mg·kgvemurafenib (Fig.).
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `demonstrated`** · basis `measured_pk_animal` · primary · mouse · arm `transporter_knockout_or_inhibitor` · brain concentration / tissue-plasma ratio = vemurafenib concentrations in various brain regions not different between Abcb1a/b;Abcg2-/- and WT+elacridar mice; tissue-plasma ratios unchanged over time · confidence medium · **flagged for human check**
  - rationale: Primary measured brain/tumor concentrations exist, but reported mainly in transporter-knockout/elacridar arms; WT brain exposure data are implied but not given as an absolute number in text, so arm is flagged.
  - span relied on: “the vemurafenib concentrations in various brain regions in tumor‐bearing mice treated for a short (5 days) or long (10 days) period were not different in Abcb1a/b;Abcg2 −/− mice and WT mice also receiving elacridar (Fig. 4A–D )”
  - read from: pmc_body / Intracranial A375 tumors develop therapy resistance despite sufficient vemurafenib tumor penetration and target inhibition · **your verdict:** _______
- **CNS-107** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > Since the vemurafenib concentration in responsive short‐term (5 days) treated tumors and resistant long‐term (10 days) treated tumors was similar, we explored alternative ways by which intracranial A375 tumor may acquire resistance in a small pilot cohort we had available for immunohistochemical analysis (= 2 per group).
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `demonstrated`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain tumor tissue concentration = vemurafenib concentration in responsive short-term (5 days) and resistant long-term (10 days) treated tumors was similar · confidence high
  - rationale: Section title states "sufficient vemurafenib tumor penetration"; matched sentence references measured intracranial tumor drug concentration in a normal (non-transporter-modified) mouse xenograft model, demonstrating CNS tumor exposure.
  - span relied on: “Since the vemurafenib concentration in responsive short‐term (5 days) treated tumors and resistant long‐term (10 days) treated tumors was similar”
  - read from: pmc_body / Intracranial A375 tumors develop therapy resistance despite sufficient vemurafenib tumor penetration and target inhibition · **your verdict:** _______
- **CNS-108** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > 4 Vemurafenib concentrations in short‐term and long‐term treated intracranial A375 tumors.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio (tissue-plasma ratio) in normal brain and tumor core = tissue-plasma ratios were very close to the total blood volume of the murine brain (approximately 2%); tumor core levels in WT ~half of Abcb1a/b;Abcg2-/- mice · confidence high
  - rationale: WT (normal, non-transporter-modified) mice show negligible brain penetration, ratio near blood-volume background; tumor core also only half of knockout levels. This is a primary measured PK finding showing CNS exclusion in the normal arm.
  - span relied on: “In line with previous reports, the vemurafenib penetration in normal brain regions of WT mice was negligible. The tissue–plasma ratios were very close to the total blood volume of the murine brain (approximately 2%).”
  - read from: pmc_body / P‐gp and BCRP reduce vemurafenib penetration in MBMs · **your verdict:** _______
- **CNS-109** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · no number
  - > Several preclinical studies have demonstrated that vemurafenib [,], dabrafenib [], and encorafenib [] exhibit very poor brain penetration in mice as a result of efficient efflux by P‐glycoprotein (P‐gp;
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `contradicted`** · basis `measured_pk_human` · restated · human · arm `normal` · CSF:plasma concentration ratio = < 1% · confidence high
  - rationale: Surrounding text cites a clinical study measuring vemurafenib CSF:plasma ratio <1%, a clearly low exposure ratio, indicating CNS exclusion despite being a restatement of another paper's finding.
  - span relied on: “the concentration of vemurafenib in cerebrospinal fluid (CSF) was < 1% of the plasma concentration [ 22 ]”
  - read from: pmc_body / (untitled section) · **your verdict:** _______
- **CNS-110** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · no number
  - > Therefore, P‐gp/BCRP inhibitors might help to improve the clinical response of MBMs to vemurafenib by increasing its brain penetration, but pinpointing the mechanism behind the brain‐specific acquired resistance will likely be necessary to produce durable responses.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `unknown`** · basis `design_or_prediction` · primary · mouse · arm `unclear` · none = nan · confidence medium · **flagged for human check**
  - rationale: Matched sentence is a forward-looking clinical prediction. Surrounding text reports tumor response (efficacy), not a measured brain/CSF concentration, Kp,uu, or brain:plasma ratio for vemurafenib - so no exposure quantity is available to call demonstrated/contradicted.
  - span relied on: “vemurafenib achieved greater antitumor responses in Abcb1a/b;Abcg2 −/− mice, indicating that P‐gp and BCRP still play a protective role at the compromised BBB of MBMs”
  - read from: pmc_body / (untitled section) · **your verdict:** _______
- **CNS-111** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · no number
  - > Dose adaptions between WT andmice are needed to level the systemic exposure of vemurafenib between strains The aim of this study was to assess the impact of P‐gp and BCRP at the BBB on the intracranial efficacy of vemurafenib against MBMs by comparing WT andmice.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `unknown`** · basis `design_or_prediction` · primary · mouse · arm `transporter_knockout_or_inhibitor` · plasma AUC (systemic exposure, not CNS compartment) = nan · confidence high
  - rationale: Matched sentence and surrounding text describe study design and plasma (systemic) exposure differences across genotypes/elacridar arms, not brain/CSF concentration, Kp,uu, or brain:plasma ratio. No CNS exposure measurement is reported here.
  - span relied on: “the plasma area under the curve (AUC) was significantly higher in Abcb1a/b;Abcg2 −/− mice compared with WT mice receiving the same dose”
  - read from: pmc_body / Dose adaptions between WT and Abcb1a/b;Abcg2 −/− mice are needed to level the systemic exposure of vemurafenib between strains · **your verdict:** _______
- **CNS-112** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · no number
  - > P‐gp and BCRP reduce vemurafenib penetration in MBMs P‐gp and BCRP limit the brain penetration of vemurafenib by virtue of their efflux function at the BBB [,].
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `unknown`** · basis `mechanistic_assertion` · restated · mouse · arm `transporter_knockout_or_inhibitor` · none = nan · confidence medium · **flagged for human check**
  - rationale: Matched sentence is a cited background assertion citing other papers. Surrounding text describes a plasma-concentration discrepancy experiment, not a brain/CSF concentration, Kp,uu, or brain:plasma ratio for vemurafenib itself.
  - span relied on: “The vemurafenib plasma concentration in WT mice receiving 25 mg·kg−1 was around one‐fourth of the concentration observed in our previous pharmacokinetic experiment”
  - read from: pmc_body / P‐gp and BCRP reduce vemurafenib penetration in MBMs · **your verdict:** _______
- **CNS-113** · [PMID 22454535](https://pubmed.ncbi.nlm.nih.gov/22454535/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3383040/) · `abstract_only` · `supporting` · number
  - > The steady-state brain-to-plasma ratio of vemurafenib was 0.035 ± 0.009 in Mdr1a/b(-/-) mice, 0.009 ± 0.006 in Bcrp1(-/-) mice, and 1.00 ± 0.19 in Mdr1a/b(-/-)Bcrp1(-/-) mice compared with 0.012 ± 0.004 in wild-type mice.
  - *Impact of P-glycoprotein (ABCB1) and breast cancer resistance protein (ABCG2) on the brain distribution of a novel BRAF inhibitor: vemurafenib (PLX4032).* — J Pharmacol Exp Ther 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio (steady-state) and AUC brain/plasma distribution coefficient = 0.012 ± 0.004 in wild-type mice (AUC ratio 0.004 in wild-type mice) · confidence high
  - rationale: Wild-type mouse brain-to-plasma ratio (0.012, AUC ratio 0.004) is low, showing restricted CNS penetration in normal (non-knockout) animals; knockout values describe transporter contribution, not patient-relevant exposure.
  - span relied on: “0.012 ± 0.004 in wild-type mice”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-114** · [PMID 23020847](https://pubmed.ncbi.nlm.nih.gov/23020847/) · `abstract_only` · `supporting` · number
  - > We aimed to establish whether oral availability and brain penetration of vemurafenib could be restricted by the multidrug efflux transporters P-glycoprotein (P-gp/ABCB1) and breast cancer resistance protein (BCRP/ABCG2), as these might limit therapeutic efficacy, especially against brain metastases.
  - *Oral availability and brain penetration of the B-RAFV600E inhibitor vemurafenib can be enhanced by the P-GLYCOprotein (ABCB1) and breast cancer resistance protein (ABCG2) inhibitor elacridar.* — Mol Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio = Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice · confidence high
  - rationale: The wild-type arm brain-to-plasma ratio is the baseline comparator; the huge fold-increase only in double-knockout mice shows WT brain accumulation is low, i.e., efflux transporters exclude vemurafenib from brain in normal (WT) mice.
  - span relied on: “Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice, indicating pronounced overlapping functions of these transporters in reducing vemurafenib brain accumulation.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-115** · [PMID 23020847](https://pubmed.ncbi.nlm.nih.gov/23020847/) · `abstract_only` · `supporting` · number
  - > Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice, indicating pronounced overlapping functions of these transporters in reducing vemurafenib brain accumulation.
  - *Oral availability and brain penetration of the B-RAFV600E inhibitor vemurafenib can be enhanced by the P-GLYCOprotein (ABCB1) and breast cancer resistance protein (ABCG2) inhibitor elacridar.* — Mol Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio = not increased in Abcg2(-/-); 1.7-fold in Abcb1a/1b(-/-); 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice (implying low ratio in WT) · confidence high · **flagged for human check**
  - rationale: WT mice brain-to-plasma ratio is low (baseline from which 21.4-fold increase occurs only in double KO); large fold-increases needed in KO arms to restore brain exposure show normal (WT) CNS exposure is markedly restricted/excluded.
  - span relied on: “Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice, indicating pronounced overlapping functions of these transporters in reducing vemurafenib brain accumulation.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-116** · [PMID 23020847](https://pubmed.ncbi.nlm.nih.gov/23020847/) · `abstract_only` · `supporting` · number
  - > As predicted by previously described pharmacokinetic modeling, halving the amount of active efflux transport at the WT blood-brain barrier by testing heterozygous Abcb1a/1b(+/-);Abcg2(+/-) mice had little impact on vemurafenib brain accumulation.
  - *Oral availability and brain penetration of the B-RAFV600E inhibitor vemurafenib can be enhanced by the P-GLYCOprotein (ABCB1) and breast cancer resistance protein (ABCG2) inhibitor elacridar.* — Mol Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio = Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice · confidence high
  - rationale: The matched sentence (heterozygous mice, little impact) is a knockout-adjacent detail; but surrounding text gives the primary WT-vs-knockout brain:plasma ratios showing low brain penetration restricted by efflux transporters in the normal (WT) condition, i.e., exclusion from CNS at baseline.
  - span relied on: “Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice, indicating pronounced overlapping functions of these transporters in reducing vemurafenib brain accumulation.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-117** · [PMID 25933211](https://pubmed.ncbi.nlm.nih.gov/25933211/) · `abstract_only` · `limiting` · number
  - > In conclusion, our preliminary results highlight for the first time a low CSF vemurafenib penetration rate associated with a large interindividual variability in patients treated for metastatic BRAF-V600 mutated melanoma and brain metastases.
  - *Cerebrospinal fluid concentrations of vemurafenib in patients treated for brain metastatic BRAF-V600 mutated melanoma.* — Melanoma Res 2015
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF:plasma ratio = mean ratio of the CSF:plasma concentration was 0.98±0.84% · confidence high
  - rationale: Primary human PK measurement in patients on standard vemurafenib dosing shows CSF:plasma ratio ~1%, explicitly described as low penetration, directly measured, not transporter-modified or co-intervention arm.
  - span relied on: “The mean ratio of the CSF : plasma concentration was 0.98±0.84%.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-118** · [PMID 25933211](https://pubmed.ncbi.nlm.nih.gov/25933211/) · `abstract_only` · `supporting` · number
  - > The mean plasma and CSF concentrations of vemurafenib were 53.4±26.2 and 0.47±0.37 mg/l, respectively.
  - *Cerebrospinal fluid concentrations of vemurafenib in patients treated for brain metastatic BRAF-V600 mutated melanoma.* — Melanoma Res 2015
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF:plasma concentration ratio = CSF:plasma ratio 0.98±0.84%; CSF 0.47±0.37 mg/l vs plasma 53.4±26.2 mg/l · confidence high
  - rationale: Direct human PK measurement in patients shows CSF:plasma ratio ~1%, explicitly described as low penetration, indicating exclusion from CNS compartment under normal dosing.
  - span relied on: “The mean plasma and CSF concentrations of vemurafenib were 53.4±26.2 and 0.47±0.37 mg/l, respectively. The mean ratio of the CSF : plasma concentration was 0.98±0.84%... a low CSF vemurafenib penetration rate associated with a large interindividual variability”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-119** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `abstract_only` · `supporting` · number
  - > We intracranially implanted A375 melanoma cells in wild-type (WT) and Abcb1a/b;Abcg2mice, characterized the tumor BBB, analyzed drug levels in plasma and brain lesions after oral vemurafenib administration, and determined the efficacy against brain metastases and subcutaneous lesions.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain lesion drug concentration vs plasma (vemurafenib penetration into MBM) = vemurafenib achieved greater antitumor efficacy against MBMs in Abcb1a/b;Abcg2 -/- mice compared with WT mice; expression of these transporters limited vemurafenib penetration into A375 MBMs · confidence medium · **flagged for human check**
  - rationale: WT-arm drug-level/efficacy data show P-gp/BCRP at BBB restrict vemurafenib penetration into brain metastases relative to KO mice; this is the normal (non-knockout) patient-relevant exposure limitation, i.e. CNS exclusion.
  - span relied on: “P-gp and BCRP are expressed in MBM-associated brain endothelium both in patients and in A375 xenografts and expression of these transporters limited vemurafenib penetration into A375 MBMs”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-120** · [PMID 41097037](https://pubmed.ncbi.nlm.nih.gov/41097037/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12524707/) · `abstract_only` · `supporting` · number
  - > Further ranking according to their blood-brain barrier permeability, as well as structural and transcriptomic similarities to known anti-GBM drugs, revealed SP600125, vemurafenib, FG-7142, dibenzoylmethane, and phensuximide as the most promising for GMT inhibition.
  - *Transcriptomic-Driven Drug Repurposing Reveals SP600125 as a Promising Drug Candidate for the Treatment of Glial-Mesenchymal Transition in Glioblastoma.* — Int J Mol Sci 2025
  - **proposed: `unknown`** · basis `design_or_prediction` · primary · na · arm `not_applicable` · none = nan · confidence high
  - rationale: This is an in-silico ranking by predicted BBB permeability and transcriptomic similarity, not a measured exposure value. No CSF/brain concentration, Kp,uu, or clinical CNS activity data for vemurafenib is reported anywhere in the text.
  - span relied on: “Further ranking according to their blood-brain barrier permeability, as well as structural and transcriptomic similarities to known anti-GBM drugs, revealed SP600125, vemurafenib, FG-7142, dibenzoylmethane, and phensuximide as the most promising for GMT inhibition.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-121** · [PMID 22454535](https://pubmed.ncbi.nlm.nih.gov/22454535/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3383040/) · `abstract_only` · `limiting` · no number
  - > These data indicate that the brain distribution of vemurafenib is severely restricted at the blood-brain barrier because of active efflux by both P-gp and BCRP.
  - *Impact of P-glycoprotein (ABCB1) and breast cancer resistance protein (ABCG2) on the brain distribution of a novel BRAF inhibitor: vemurafenib (PLX4032).* — J Pharmacol Exp Ther 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma ratio (AUC brain/AUC plasma; steady-state brain-to-plasma ratio) = 0.004 (AUC ratio, wild-type); steady-state brain-to-plasma ratio 0.012 ± 0.004 in wild-type mice · confidence high
  - rationale: Wild-type mouse brain:plasma ratios (0.004 and 0.012) are very low, indicating restricted CNS exposure. Knockout/inhibitor arms (Mdr1a/b-/-, Bcrp1-/-, double KO reaching 1.00) describe transporter contribution, not patient-relevant exposure.
  - span relied on: “The in vivo studies revealed that the brain distribution coefficient (area under the concentration time profile of brain/area under the concentration time profile of plasma) of vemurafenib was 0.004 in wild-type mice... compared with 0.012 ± 0.004 in wild-type mice.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-122** · [PMID 23020847](https://pubmed.ncbi.nlm.nih.gov/23020847/) · `abstract_only` · `supporting` · no number
  - > Our data suggest that elacridar coadministration may be considered to improve the therapeutic efficacy of vemurafenib, especially for brain metastases located behind a functional blood-brain barrier.
  - *Oral availability and brain penetration of the B-RAFV600E inhibitor vemurafenib can be enhanced by the P-GLYCOprotein (ABCB1) and breast cancer resistance protein (ABCG2) inhibitor elacridar.* — Mol Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio = Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice · confidence high
  - rationale: In wild-type mice (the clinically relevant arm), brain accumulation is low/restricted; high ratio only emerges in double-knockout mice, which describes transporter effect, not patient-relevant CNS exposure. Matched sentence is a design-goal assertion.
  - span relied on: “Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice, indicating pronounced overlapping functions of these transporters in reducing vemurafenib brain accumulation.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-123** · [PMID 25933211](https://pubmed.ncbi.nlm.nih.gov/25933211/) · `abstract_only` · `supporting` · no number
  - > The concentrations of vemurafenib in the CSF and the plasma were measured by high-performance liquid chromatography.
  - *Cerebrospinal fluid concentrations of vemurafenib in patients treated for brain metastatic BRAF-V600 mutated melanoma.* — Melanoma Res 2015
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF:plasma concentration ratio = mean ratio of CSF:plasma concentration was 0.98±0.84% · confidence high
  - rationale: Primary human PK data in patients show CSF:plasma ratio ~1%, explicitly described as low penetration - a direct measured exclusion from CNS compartment.
  - span relied on: “The mean ratio of the CSF : plasma concentration was 0.98±0.84%. ... a low CSF vemurafenib penetration rate associated with a large interindividual variability”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-124** · [PMID 25933211](https://pubmed.ncbi.nlm.nih.gov/25933211/) · `abstract_only` · `supporting` · no number
  - > Further investigations with larger cohorts are required to study the relationship between CSF vemurafenib concentrations and cerebral response.
  - *Cerebrospinal fluid concentrations of vemurafenib in patients treated for brain metastatic BRAF-V600 mutated melanoma.* — Melanoma Res 2015
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF:plasma concentration ratio = mean CSF:plasma ratio 0.98±0.84%; CSF conc 0.47±0.37 mg/l vs plasma 53.4±26.2 mg/l · confidence high
  - rationale: Primary human PK data in six patients show CSF:plasma ratio ~1%, explicitly described as low penetration - direct measured exclusion from CSF compartment under normal dosing.
  - span relied on: “The mean ratio of the CSF : plasma concentration was 0.98±0.84%... highlight for the first time a low CSF vemurafenib penetration rate”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
