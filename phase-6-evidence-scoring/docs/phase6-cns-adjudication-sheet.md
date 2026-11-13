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

**Evidence score: `demonstrated`** (resolved) — best supporting claim 0.9, best contradicting 0.0, direction +1.0. best claim 0.90, direction +1.00. Corroboration: 3.703 total weight across 8 claims (does not set the band). Heaviest claims: CNS-001 (0.90), CNS-003 (0.68), CNS-008 (0.65).

**Proposed drug verdict: `demonstrated`** — 4 primary human claim(s), all demonstrated. Decisive claim(s): CNS-001, CNS-005, CNS-006, CNS-008.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-001** · [PMID 40086436](https://pubmed.ncbi.nlm.nih.gov/40086436/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12121847/) · `full_text` · `supporting` · number
  - > Case 2 demonstrated an increase in the CSF/plasma ratio during the course of treatment, with tumor tissue reaching a concentration of 4μM avapritinib following six months of treatment ().
  - *Effective targeting of PDGFRA-altered high-grade glioma with avapritinib.* — Cancer Cell 2025
  - **proposed: `demonstrated`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF/plasma ratio; CSF concentration; tumor tissue concentration = CSF/plasma ratio increased over treatment; tumor tissue 4μM; CSF levels 15-46nM · confidence high · weight **0.90**
  - rationale: Primary human PK data: measured CSF concentrations, rising CSF/plasma ratio, and tumor tissue concentration of 4μM in patients on treatment, directly demonstrating CNS/tumor exposure.
  - span relied on: “Case 2 demonstrated an increase in the CSF/plasma ratio during the course of treatment, with tumor tissue reaching a concentration of 4μM avapritinib following six months of treatment ... CSF levels of avapritinib (15 −46nM) in both cases were substantially higher compared to dasatinib levels in Case 2 (~2nM)”
  - read from: pmc_body / Avapritinib shows radiographic response in a subset of pediatric and young adult HGG patients with PDGFRA alterations · **your verdict:** _______
- **CNS-002** · [PMID 38167404](https://pubmed.ncbi.nlm.nih.gov/38167404/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761696/) · `full_text` · `supporting` · no number
  - > These effects most likely result from avapritinib’s ability to penetrate the blood-brain barrier (BBB) and interact with unidentified targets in the brain.
  - *Avapritinib-based SAR studies unveil a binding pocket in KIT and PDGFRA.* — Nat Commun 2024
  - **proposed: `unknown`** · basis `mechanistic_assertion` · restated · human · arm `not_applicable` · none = nan · confidence medium · weight **0.08**
  - rationale: Introduction-section mechanistic assertion inferred from clinical cognitive side effects, citing other papers (refs 8,12); no measured CSF/brain concentration, Kp,uu, or exposure value is given in this text.
  - span relied on: “These effects most likely result from avapritinib's ability to penetrate the blood-brain barrier (BBB) and interact with unidentified targets in the brain”
  - read from: pmc_body / Introduction · **your verdict:** _______
- **CNS-003** · [PMID 40086436](https://pubmed.ncbi.nlm.nih.gov/40086436/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12121847/) · `full_text` · `supporting` · no number
  - > Avapritinib treatment results in efficient brain penetrance and prolonged survival in-altered DMG models We next asked whether avapritinib crosses the blood-brain barrier and impacts tumor growth in-altered glioma animal models.
  - *Effective targeting of PDGFRA-altered high-grade glioma with avapritinib.* — Cancer Cell 2025
  - **proposed: `demonstrated`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain tissue concentration = brain tissue concentrations reaching their maximum at 10μM two hours post-ingestion; steady state brain concentrations of 1μM exceeding IC50 by 2-12 fold · confidence high · weight **0.68**
  - rationale: Primary measured brain tissue concentrations in normal (non-tumor-bearing) wild-type mice, at pharmacologically relevant levels exceeding in vitro IC50, directly demonstrating CNS penetrance in normal brain compartment.
  - span relied on: “Pharmacokinetic analysis of avapritinib in non-tumor-bearing CD-1 mice showed a peak concentration of 10 μg/mL (20.08 μM) occurring at two hours following one oral dose, with brain tissue concentrations reaching their maximum at 10μM two hours post-ingestion... Following eight days of daily avapritinib dosing to achieve steady state levels, brain tissues exhibited avapritinib concentrations of 1μM, exceeding IC 50 values observed in vitro by 2-12 fold”
  - read from: pmc_body / Avapritinib treatment results in efficient brain penetrance and prolonged survival in PDGFRA -altered DMG models in vivo · **your verdict:** _______
- **CNS-004** · [PMID 40086436](https://pubmed.ncbi.nlm.nih.gov/40086436/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12121847/) · `full_text` · `supporting` · no number
  - > In summary, we show that avapritinib efficiently crosses the blood brain barrier to achieve supratherapeutic concentrations in target brain tissue.
  - *Effective targeting of PDGFRA-altered high-grade glioma with avapritinib.* — Cancer Cell 2025
  - **proposed: `demonstrated`** · basis `preclinical_cns_efficacy` · primary · mouse · arm `normal` · brain tissue concentration = supratherapeutic concentrations in target brain tissue · confidence medium · weight **0.38** · **flagged for human check**
  - rationale: Section title and sentence report measured brain tissue drug concentration in DMG in vivo models, summarizing primary PK data from this paper's in vivo brain penetrance study.
  - span relied on: “avapritinib efficiently crosses the blood brain barrier to achieve supratherapeutic concentrations in target brain tissue”
  - read from: pmc_body / Avapritinib treatment results in efficient brain penetrance and prolonged survival in PDGFRA -altered DMG models in vivo · **your verdict:** _______
- **CNS-005** · [PMID 41961082](https://pubmed.ncbi.nlm.nih.gov/41961082/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13068680/) · `full_text` · `limiting` · no number
  - > Although data on CNS penetration of avapritinib in AML are limited, and CSF levels of avapritinib were not available in this case, preclinical studies and early clinical data in-mutated gliomas suggest that the drug can effectively cross the blood–brain barrier and exert antitumor activity within the CNS [].
  - *Avapritinib for targeting KIT D816V-mutated acute myeloid leukemia relapsed after allogeneic hematopoietic stem cell transplant with extramedullary and central nervous system involvement.* — Ann Hematol 2026
  - **proposed: `demonstrated`** · basis `clinical_cns_response` · primary · human · arm `not_applicable` · none = nan · confidence medium · weight **0.55** · **flagged for human check**
  - rationale: No CSF/brain concentration data; CSF levels explicitly unavailable. But this is a primary clinical case report showing CNS disease response to avapritinib alone, qualifying as clinical CNS activity, not just assertion.
  - span relied on: “a patient with relapsed KIT D816V -mutated AML involving both CNS and extensive extramedullary disease, who achieved molecular remission with avapritinib alone”
  - read from: pmc_body / Case report · **your verdict:** _______
- **CNS-006** · [PMID 40086436](https://pubmed.ncbi.nlm.nih.gov/40086436/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12121847/) · `abstract_only` · `supporting` · number
  - > We reveal that the PDGFRA/KIT inhibitor avapritinib shows (1) selectivity for PDGFRA inhibition, (2) distinct patterns of subcellular effects, (3) in vitro and in vivo activity in patient-derived HGG models, and (4) effective blood-brain barrier penetration in mice and humans.
  - *Effective targeting of PDGFRA-altered high-grade glioma with avapritinib.* — Cancer Cell 2025
  - **proposed: `demonstrated`** · basis `clinical_cns_response` · primary · human · arm `normal` · none (radiographic response / BBB penetration assertion, no quantitative exposure value given) = nan · confidence medium · weight **0.55** · **flagged for human check**
  - rationale: Abstract asserts BBB penetration and reports clinical radiographic responses in recurrent/refractory PDGFRA-altered HGG patients, indicating CNS tumor activity, though no quantitative exposure value is given.
  - span relied on: “effective blood-brain barrier penetration in mice and humans... results in radiographic response in 3/7 cases”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-007** · [PMID 38167404](https://pubmed.ncbi.nlm.nih.gov/38167404/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761696/) · `abstract_only` · `supporting` · no number
  - > We utilize this information to design, synthesize and characterize avapritinib derivatives for the determination of key pharmacophoric features to overcome drug resistance and limit potential blood-brain barrier penetration.
  - *Avapritinib-based SAR studies unveil a binding pocket in KIT and PDGFRA.* — Nat Commun 2024
  - **proposed: `unknown`** · basis `design_or_prediction` · primary · na · arm `not_applicable` · none = nan · confidence medium · weight **0.06**
  - rationale: No exposure measurement of avapritinib itself is given; text describes a drug-design goal to limit BBB penetration of derivatives, and neuro-cognitive side effects are only mentioned as a clinical rationale, not PK data.
  - span relied on: “design, synthesize and characterize avapritinib derivatives for the determination of key pharmacophoric features to overcome drug resistance and limit potential blood-brain barrier penetration”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-008** · [PMID 41961082](https://pubmed.ncbi.nlm.nih.gov/41961082/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13068680/) · `abstract_only` · `supporting` · no number
  - > Remarkably, rechallenge with single‑agent avapritinib again induced molecular remission in both peripheral blood and cerebrospinal fluid, along with near‑complete metabolic response across all previously involved sites.
  - *Avapritinib for targeting KIT D816V-mutated acute myeloid leukemia relapsed after allogeneic hematopoietic stem cell transplant with extramedullary and central nervous system involvement.* — Ann Hematol 2026
  - **proposed: `demonstrated`** · basis `clinical_cns_response` · primary · human · arm `normal` · clinical CNS response (molecular remission in CSF) = molecular remission in both peripheral blood and cerebrospinal fluid · confidence high · weight **0.65**
  - rationale: Single-agent avapritinib produced molecular remission in CSF and neurological/metabolic improvement in CNS-involved relapse, a primary clinical CNS response in a patient case, not a transporter study or co-intervention.
  - span relied on: “rechallenge with single‑agent avapritinib again induced molecular remission in both peripheral blood and cerebrospinal fluid, along with near‑complete metabolic response across all previously involved sites”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### BINIMETINIB

2 attributed of 14 retrieved sentences · 1 full text, 1 abstract-only · ChEMBL calculated flag: `predicted_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 8 drug rows

**Evidence score: `unknown`** (below_peak_threshold) — best supporting claim 0.214, best contradicting 0.0, direction +1.0. best claim weighs 0.21, below 0.5; unassessed. Corroboration: 0.214 total weight across 2 claims (does not set the band). Heaviest claims: CNS-009 (0.21), CNS-010 (0.12).

**Proposed drug verdict: `unknown`** — No primary, normal-arm claim carries a measured or clinical finding. Decisive claim(s): nan.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-009** · [PMID 41369830](https://pubmed.ncbi.nlm.nih.gov/41369830/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12799883/) · `full_text` · `supporting` · number
  - > These results highlight the potential of encorafenib plus binimetinib to provide meaningful intracranial tumor shrinkage and improved complete responses in patients with BRAF V600-mutant melanoma with brain metastases, although the considerable heterogeneity across included studies suggests that these findings should be interpreted with caution.
  - *The safety and efficacy of encorafenib plus binimetinib for brain metastases: a systematic review and meta-analysis.* — Discov Oncol 2025
  - **proposed: `demonstrated`** · basis `clinical_cns_response` · restated · human · arm `not_applicable` · intracranial response rate (CR/ORR/PR) = intracranial CR rate higher than prior studies; intracranial ORR and PR generally comparable · confidence medium · weight **0.21** · **flagged for human check**
  - rationale: Meta-analysis reports clinical intracranial tumor response (combination therapy) for BRAF V600-mutant melanoma brain metastases, indicating CNS activity; this is a drug combination, so attribution to binimetinib alone is uncertain.
  - span relied on: “The intracranial CR rate observed with encorafenib plus binimetinib was higher than that reported in prior dual, triplet, or monotherapy studies, while intracranial ORR and PR were generally comparable”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-010** · [PMID 28921565](https://pubmed.ncbi.nlm.nih.gov/28921565/) · `abstract_only` · `supporting` · number
  - > PD0325901 displayed more promising characteristics than trametinib (GSK1120212), binimetinib (MEK162), selumetinib (AZD6244), and pimasertib (AS703026): PD0325901 was the weakest substrate of P-gp and BCRP in vitro, its brain penetration was only marginally higher in Abcb1a/b;Abcg2mice, and efficient target inhibition in the brain could be achieved at clinically relevant plasma levels.
  - *The impact of P-glycoprotein and breast cancer resistance protein on the brain pharmacokinetics and pharmacodynamics of a panel of MEK inhibitors.* — Int J Cancer 2017
  - **proposed: `unknown`** · basis `measured_pk_animal` · unclear · mouse · arm `unclear` · none = nan · confidence low · weight **0.12** · **flagged for human check**
  - rationale: Text only ranks binimetinib as inferior to PD0325901 overall; no specific brain/CSF concentration, Kp,uu, or brain:plasma ratio for binimetinib itself is reported in the supplied text.
  - span relied on: “PD0325901 displayed more promising characteristics than trametinib (GSK1120212), binimetinib (MEK162), selumetinib (AZD6244), and pimasertib (AS703026)”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### COBIMETINIB

3 attributed of 19 retrieved sentences · 0 full text, 3 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 12 drug rows

**Evidence score: `contradicted`** (resolved) — best supporting claim 0.0, best contradicting 0.545, direction -1.0. best claim 0.55, direction -1.00. Corroboration: 1.09 total weight across 3 claims (does not set the band). Heaviest claims: CNS-011 (0.55), CNS-012 (0.55), CNS-013 (0.02).

**Proposed drug verdict: `contradicted`** — 2 primary mouse claim(s), all contradicted. Decisive claim(s): CNS-011, CNS-012.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-011** · [PMID 25243894](https://pubmed.ncbi.nlm.nih.gov/25243894/) · `abstract_only` · `supporting` · number
  - > The objectives of this study were to determine in vitro and in vivo if cobimetinib is a substrate of P-glycoprotein (P-gp) and/or breast cancer resistance protein (Bcrp1) and to assess the implications of efflux on cobimetinib pharmacokinetics (PK), brain penetration, and target modulation.
  - *Role of P-glycoprotein on the brain penetration and brain pharmacodynamic activity of the MEK inhibitor cobimetinib.* — Mol Pharm 2014
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma (Kp) = mean total brain to plasma ratio (Kp) at 6 h postdose was 0.3 and 0.2 in WT and Bcrp1(-/-) mice, respectively · confidence high · weight **0.55**
  - rationale: WT (and Bcrp1-/- single KO) mice show low brain:plasma Kp (0.2-0.3), indicating exclusion from brain under normal/physiological efflux conditions; high Kp only seen with Mdr1a/b knockout or elacridar co-treatment.
  - span relied on: “After an oral 10 mg/kg dose of cobimetinib, the mean total brain to plasma ratio (Kp) at 6 h postdose was 0.3 and 0.2 in WT and Bcrp1(-/-) mice, respectively.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-012** · [PMID 25243894](https://pubmed.ncbi.nlm.nih.gov/25243894/) · `abstract_only` · `supporting` · number
  - > After an oral 10 mg/kg dose of cobimetinib, the mean total brain to plasma ratio (Kp) at 6 h postdose was 0.3 and 0.2 in WT and Bcrp1(-/-) mice, respectively.
  - *Role of P-glycoprotein on the brain penetration and brain pharmacodynamic activity of the MEK inhibitor cobimetinib.* — Mol Pharm 2014
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma Kp = 0.3 (WT), 0.2 (Bcrp1-/-) · confidence high · weight **0.55**
  - rationale: Measured brain:plasma Kp of 0.3 in wild-type mice is low, indicating limited normal-brain penetration in the physiologically relevant (non-knockout) arm; Bcrp1-/- alone (no Mdr1a/b knockout) shows similarly low Kp of 0.2.
  - span relied on: “After an oral 10 mg/kg dose of cobimetinib, the mean total brain to plasma ratio (Kp) at 6 h postdose was 0.3 and 0.2 in WT and Bcrp1(-/-) mice, respectively.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-013** · [PMID 40975475](https://pubmed.ncbi.nlm.nih.gov/40975475/) · `abstract_only` · `supporting` · number
  - > Of these, we selected only the 11 which can cross the blood-brain barrier: cobimetinib, panobinostat, melphalan, rucaparib, alectinib, ponatinib, danazol, carboplatin, vandetanib, erlotinib, and gefitinib.
  - *Transcriptomic profiling unveils novel therapeutic options for drug-resistant temporal lobe epilepsy.* — Eur J Pharmacol 2025
  - **proposed: `unknown`** · basis `design_or_prediction` · restated · na · arm `not_applicable` · none = nan · confidence low · weight **0.02**
  - rationale: This is an unsupported assertion/selection criterion from a drug-repurposing screen, not a reported exposure measurement; no PK data, CSF/brain concentration, or Kp,uu given for cobimetinib.
  - span relied on: “we selected only the 11 which can cross the blood-brain barrier: cobimetinib, panobinostat, melphalan, rucaparib, alectinib, ponatinib, danazol, carboplatin, vandetanib, erlotinib, and gefitinib”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### DABRAFENIB

2 attributed of 14 retrieved sentences · 2 full text, 0 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 10 drug rows

**Evidence score: `demonstrated`** (resolved) — best supporting claim 0.612, best contradicting 0.0, direction +1.0. best claim 0.61, direction +1.00. Corroboration: 0.612 total weight across 2 claims (does not set the band). Heaviest claims: CNS-014 (0.61), CNS-015 (0.03).

**Proposed drug verdict: `demonstrated`** — 1 primary human claim(s), all demonstrated. Decisive claim(s): CNS-014.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-014** · [PMID 32817058](https://pubmed.ncbi.nlm.nih.gov/32817058/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7437885/) · `full_text` · `supporting` · no number
  - > In line with other clinical responses,the initial response of the brain lesion to dabrafenib suggested that the drug did cross the blood-brain barrier, and our data suggest that resistance was not mediated by cell-intrinsic events, so we examined if resistance was mediated by factors in the brain microenvironment.
  - *Brain microenvironment-driven resistance to immune and targeted therapies in acral melanoma.* — ESMO Open 2020
  - **proposed: `demonstrated`** · basis `clinical_cns_response` · primary · human · arm `normal` · clinical response of brain metastasis = initial response of the brain lesion to dabrafenib · confidence medium · weight **0.61** · **flagged for human check**
  - rationale: Primary clinical observation in this patient's case report: a brain metastasis responded to dabrafenib, indicating CNS tumour exposure sufficient for activity, not merely a restated literature claim.
  - span relied on: “the initial response of the brain lesion to dabrafenib suggested that the drug did cross the blood-brain barrier”
  - read from: pmc_body / Resistance to targeted therapy in the brain · **your verdict:** _______
- **CNS-015** · [PMID 38291372](https://pubmed.ncbi.nlm.nih.gov/38291372/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10826080/) · `full_text` · `supporting` · no number
  - > Finally, tovorafenib had greater CNS penetration compared with the type I RAF inhibitor dabrafenib [].
  - *LOGGIC/FIREFLY-2: a phase 3, randomized trial of tovorafenib vs. chemotherapy in pediatric and young adult patients with newly diagnosed low-grade glioma harboring an activating RAF alteration.* — BMC Cancer 2024
  - **proposed: `unknown`** · basis `review_restatement` · restated · na · arm `not_applicable` · none = nan · confidence low · weight **0.03**
  - rationale: Background-section comparative assertion citing another reference, no exposure quantity (CSF/brain concentration, Kp,uu) for dabrafenib given in text; a restated claim, not a measurement.
  - span relied on: “tovorafenib had greater CNS penetration compared with the type I RAF inhibitor dabrafenib”
  - read from: pmc_body / Background · **your verdict:** _______

### DASATINIB

9 attributed of 74 retrieved sentences · 1 full text, 8 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_record` · CNS-manifestation trial evidence on 0 drug rows

**Evidence score: `unknown`** (conflicting_best_evidence) — best supporting claim 0.95, best contradicting 0.807, direction +0.15. best evidence points both ways (support 0.95 vs exclusion 0.81); unresolved. Corroboration: 6.035 total weight across 9 claims (does not set the band). Heaviest claims: CNS-016 (0.95), CNS-020 (0.81), CNS-022 (0.81).

**Proposed drug verdict: left blank** — Primary human claims disagree (contradicted, demonstrated); left for the reviewer rather than resolved by majority.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-016** · [PMID 32493453](https://pubmed.ncbi.nlm.nih.gov/32493453/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7268320/) · `full_text` · `supporting` · number
  - > Supplementary information Supplementary information on clinical parameters and sample collection.Sequential therapies of the investigated drugs in the study cohort.Depiction of the used HPLC gradient for sample analysis.Overview of the used mass spectrometer parameters.Normalized chromatogram of a standard solution of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat obtained with the developed HPLC-QqQ MS method.Overview of the corresponding method performance parameters.Depiction of measured CCS values of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat.Depiction of the quantitation results for imatinib CSF samples
  - *Cerebrospinal fluid penetration of targeted therapeutics in pediatric brain tumor patients.* — Acta Neuropathol Commun 2020
  - **proposed: `demonstrated`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF concentration = moderate (1-10 nM) · confidence high · weight **0.95**
  - rationale: Primary human CSF measurement from Ommaya reservoir samples in pediatric brain tumor patients shows detectable dasatinib at 1-10 nM, a measured exposure in CSF, not merely an assertion.
  - span relied on: “regorafenib and dasatinib moderate (1-10 nM) penetrance”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-017** · [PMID 19491323](https://pubmed.ncbi.nlm.nih.gov/19491323/) · `abstract_only` · `limiting` · number
  - > In vivo brain distribution studies showed that the CNS distribution of dasatinib is limited, with the brain-to-plasma concentration ratios less than 0.12 in wild-type mice, which increased approximately 8-fold in Mdr1a/b(-/-) Bcrp1(-/-) mice.
  - *P-glycoprotein and breast cancer resistance protein influence brain distribution of dasatinib.* — J Pharmacol Exp Ther 2009
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma = less than 0.12 in wild-type mice · confidence high · weight **0.55**
  - rationale: Wild-type (normal transporter) mouse brain:plasma ratio <0.12 is a low measured ratio, indicating CNS exclusion in the physiologically relevant arm; knockout/inhibitor increases describe transporter effect, not patient exposure.
  - span relied on: “the CNS distribution of dasatinib is limited, with the brain-to-plasma concentration ratios less than 0.12 in wild-type mice”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-018** · [PMID 24790822](https://pubmed.ncbi.nlm.nih.gov/24790822/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4000600/) · `abstract_only` · `supporting` · number
  - > With 40 mg dasatinib administered once daily, its trough level and cerebrospinal fluid (CSF) concentration were 32 ng/mL and below the sensitivity threshold of 1 ng/mL, respectively.
  - *Philadelphia chromosome-positive acute lymphoblastic leukemia with extramedullary and meningeal relapse after allogeneic hematopoietic stem cell transplantation that was successfully treated with dasatinib.* — Springerplus 2014
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF concentration (plasma trough and CSF concentration measured directly) = trough 32 ng/mL; CSF below sensitivity threshold of 1 ng/mL · confidence high · weight **0.77**
  - rationale: Directly measured human CSF concentration of dasatinib was undetectable (below 1 ng/mL) despite measurable plasma trough of 32 ng/mL, demonstrating exclusion from CSF compartment at this dose.
  - span relied on: “The trough level and CSF concentration of dasatinib administered at a daily dose of 40 mg were 32 ng/mL and below the sensitivity threshold of 1 ng/mL, respectively.”
  - read from: pmc_body / Case description · **your verdict:** _______
- **CNS-019** · [PMID 35098970](https://pubmed.ncbi.nlm.nih.gov/35098970/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8612719/) · `abstract_only` · `supporting` · number
  - > The primary objective is to evaluate the central nervous system penetration of dasatinib and quercetin through analysis of cerebrospinal fluid collected at baseline and after 12 weeks of treatment.
  - *Senolytic Therapy to Modulate the Progression of Alzheimer's Disease (SToMP-AD): A Pilot Clinical Trial.* — J Prev Alzheimers Dis 2022
  - **proposed: `unknown`** · basis `design_or_prediction` · primary · human · arm `not_applicable` · none = nan · confidence high · weight **0.15**
  - rationale: This is a trial protocol describing a planned measurement (primary objective), not a reported result. No CSF concentration or exposure value for dasatinib is given in the text.
  - span relied on: “The primary objective is to evaluate the central nervous system penetration of dasatinib and quercetin through analysis of cerebrospinal fluid collected at baseline and after 12 weeks of treatment.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-020** · [PMID 42578491](https://pubmed.ncbi.nlm.nih.gov/42578491/) · `abstract_only` · `supporting` · number
  - > In CSF, the mean dasatinib concentration was 0.5 ± 0.2 ng/mL at 2 h.
  - *Low Dasatinib Penetration of the Blood-Brain Barrier in Children With Philadelphia Chromosome-Positive Acute Lymphoblastic Leukemia: Evidence From LC-MS/MS Analysis.* — Pediatr Blood Cancer 2026
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF concentration and plasma:CSF ratio = 0.5 ± 0.2 ng/mL at 2 h; plasma/CSF ratio 225:1 (98:1-406:1) · confidence high · weight **0.81**
  - rationale: Primary human PK measurement in paired plasma/CSF samples, normal (non-transporter-modified) arm, showing very low CSF concentration relative to therapeutic plasma levels (225:1 ratio) — direct evidence of CNS exclusion.
  - span relied on: “In CSF, the mean dasatinib concentration was 0.5 ± 0.2 ng/mL at 2 h. The median paired plasma/CSF concentration ratio was 225:1 (98:1-406:1). In conclusion, despite therapeutic systemic levels, dasatinib penetrates poorly into CSF in children with Ph + ALL.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-021** · [PMID 19491323](https://pubmed.ncbi.nlm.nih.gov/19491323/) · `abstract_only` · `supporting` · no number
  - > The objective of this study was to investigate the role of P-glycoprotein (P-gp) and breast cancer resistance protein (BCRP) in modulating the CNS penetration of dasatinib.
  - *P-glycoprotein and breast cancer resistance protein influence brain distribution of dasatinib.* — J Pharmacol Exp Ther 2009
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma = brain-to-plasma concentration ratios less than 0.12 in wild-type mice · confidence high · weight **0.55**
  - rationale: Wild-type mouse brain:plasma ratio <0.12 is a low, measured exposure ratio in the normal (non-knockout) arm, indicating CNS exclusion; knockout/inhibitor increases describe transporter role, not patient exposure.
  - span relied on: “In vivo brain distribution studies showed that the CNS distribution of dasatinib is limited, with the brain-to-plasma concentration ratios less than 0.12 in wild-type mice, which increased approximately 8-fold in Mdr1a/b(-/-) Bcrp1(-/-) mice.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-022** · [PMID 42578491](https://pubmed.ncbi.nlm.nih.gov/42578491/) · `abstract_only` · `limiting` · no number
  - > In conclusion, despite therapeutic systemic levels, dasatinib penetrates poorly into CSF in children with PhALL.
  - *Low Dasatinib Penetration of the Blood-Brain Barrier in Children With Philadelphia Chromosome-Positive Acute Lymphoblastic Leukemia: Evidence From LC-MS/MS Analysis.* — Pediatr Blood Cancer 2026
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · plasma/CSF concentration ratio = median paired plasma/CSF concentration ratio was 225:1 (98:1-406:1); CSF concentration 0.5 ± 0.2 ng/mL vs plasma 101.6 ± 42.1 ng/mL at 2h · confidence high · weight **0.81**
  - rationale: Primary human PK study in children with Ph+ALL directly measured dasatinib in paired plasma/CSF; high plasma:CSF ratio (225:1) shows poor CSF penetration despite therapeutic plasma levels, a normal (non-transporter-manipulated) clinical arm.
  - span relied on: “In conclusion, despite therapeutic systemic levels, dasatinib penetrates poorly into CSF in children with Ph + ALL.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-023** · [PMID 42578491](https://pubmed.ncbi.nlm.nih.gov/42578491/) · `abstract_only` · `supporting` · no number
  - > We measured dasatinib concentrations in paired plasma and cerebrospinal fluid (CSF) samples from children with Philadelphia chromosome-positive acute lymphoblastic leukemia (Ph+ ALL).
  - *Low Dasatinib Penetration of the Blood-Brain Barrier in Children With Philadelphia Chromosome-Positive Acute Lymphoblastic Leukemia: Evidence From LC-MS/MS Analysis.* — Pediatr Blood Cancer 2026
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · plasma:CSF concentration ratio and CSF concentration = median plasma/CSF ratio 225:1 (98:1-406:1); CSF conc 0.5 ± 0.2 ng/mL at 2h vs plasma 101.6 ± 42.1 ng/mL · confidence high · weight **0.81**
  - rationale: Primary human PK measurement in paired plasma/CSF samples shows very low CSF penetration (225:1 plasma:CSF ratio) despite therapeutic plasma levels, in normal (non-transporter-modified) patients.
  - span relied on: “The median paired plasma/CSF concentration ratio was 225:1 (98:1-406:1). In conclusion, despite therapeutic systemic levels, dasatinib penetrates poorly into CSF in children with Ph + ALL.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-024** · [PMID 42578491](https://pubmed.ncbi.nlm.nih.gov/42578491/) · `abstract_only` · `supporting` · no number
  - > After validating a liquid chromatography-tandem mass spectrometry (LC-MS/MS) assay for dasatinib in both matrices, we quantified drug concentrations in plasma and CSF and expressed blood-brain barrier penetration as the plasma-to-CSF concentration ratio.
  - *Low Dasatinib Penetration of the Blood-Brain Barrier in Children With Philadelphia Chromosome-Positive Acute Lymphoblastic Leukemia: Evidence From LC-MS/MS Analysis.* — Pediatr Blood Cancer 2026
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF:plasma concentration ratio = median paired plasma/CSF concentration ratio was 225:1 (98:1-406:1); CSF 0.5 ± 0.2 ng/mL vs plasma 101.6 ± 42.1 ng/mL at 2 h · confidence high · weight **0.81**
  - rationale: Primary human PK measurement in paired plasma/CSF samples shows a very low CSF:plasma ratio (~1:225), indicating poor BBB penetration of dasatinib into CSF, a normal (non-knockout) clinical arm.
  - span relied on: “In CSF, the mean dasatinib concentration was 0.5 ± 0.2 ng/mL at 2 h. The median paired plasma/CSF concentration ratio was 225:1 (98:1-406:1). In conclusion, despite therapeutic systemic levels, dasatinib penetrates poorly into CSF in children with Ph + ALL.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### ENCORAFENIB

3 attributed of 9 retrieved sentences · 1 full text, 2 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 7 drug rows

**Evidence score: `compartment_split`** (compartment_split) — best supporting claim 0.551, best contradicting 0.545, direction +0.01. barrier-intact compartments read contradicted (best 0.55), tumour tissue reads demonstrated (best 0.55). Corroboration: 1.641 total weight across 3 claims (does not set the band). Heaviest claims: CNS-025 (0.55), CNS-026 (0.55), CNS-027 (0.55).

**Proposed drug verdict: `demonstrated`** — 1 primary human claim(s), all demonstrated. Decisive claim(s): CNS-025.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-025** · [PMID 41369830](https://pubmed.ncbi.nlm.nih.gov/41369830/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12799883/) · `full_text` · `supporting` · number
  - > These results highlight the potential of encorafenib plus binimetinib to provide meaningful intracranial tumor shrinkage and improved complete responses in patients with BRAF V600-mutant melanoma with brain metastases, although the considerable heterogeneity across included studies suggests that these findings should be interpreted with caution.
  - *The safety and efficacy of encorafenib plus binimetinib for brain metastases: a systematic review and meta-analysis.* — Discov Oncol 2025
  - **proposed: `demonstrated`** · basis `clinical_cns_response` · primary · human · arm `not_applicable` · intracranial ORR/CR/PR (clinical response in brain metastases) = intracranial CR rate higher than prior studies; intracranial ORR and PR generally comparable · confidence medium · weight **0.55** · **flagged for human check**
  - rationale: Meta-analysis reports clinical intracranial tumor response (CR/ORR/PR) for encorafenib+binimetinib in BRAF V600-mutant brain metastases, demonstrating clinical activity at the CNS tumor site, though combined with binimetinib.
  - span relied on: “The intracranial CR rate observed with encorafenib plus binimetinib was higher than that reported in prior dual, triplet, or monotherapy studies, while intracranial ORR and PR were generally comparable, and SD fell within previously reported ranges.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-026** · [PMID 29155017](https://pubmed.ncbi.nlm.nih.gov/29155017/) · `abstract_only` · `limiting` · no number
  - > However, absolute brain concentrations and brain-to-plasma ratios remained very low in all strains, indicating intrinsically poor brain penetration of encorafenib.
  - *P-glycoprotein (MDR1/ABCB1) and Breast Cancer Resistance Protein (BCRP/ABCG2) affect brain accumulation and intestinal disposition of encorafenib in mice.* — Pharmacol Res 2017
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio and absolute brain concentration = very low in all strains · confidence high · weight **0.55** · **flagged for human check**
  - rationale: Wild-type arm (and all strains) shows low absolute brain concentrations and brain:plasma ratios, i.e. exclusion from normal brain in the physiologically normal (wild-type) condition - a contradicted finding for that arm.
  - span relied on: “absolute brain concentrations and brain-to-plasma ratios remained very low in all strains, indicating intrinsically poor brain penetration of encorafenib”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-027** · [PMID 29155017](https://pubmed.ncbi.nlm.nih.gov/29155017/) · `abstract_only` · `limiting` · no number
  - > The low brain penetration of encorafenib might limit its efficacy against malignancies positioned behind a functional blood-brain barrier, but its oral bioavailability and distribution to other tested organs (liver, kidney, spleen, testis) was high.
  - *P-glycoprotein (MDR1/ABCB1) and Breast Cancer Resistance Protein (BCRP/ABCG2) affect brain accumulation and intestinal disposition of encorafenib in mice.* — Pharmacol Res 2017
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio / brain concentration = absolute brain concentrations and brain-to-plasma ratios remained very low in all strains · confidence high · weight **0.55** · **flagged for human check**
  - rationale: Wild-type mouse brain-to-plasma ratios were measured and found very low; knockout arms showed increased but still low accumulation, confirming poor intrinsic brain penetration in normal brain tissue.
  - span relied on: “However, absolute brain concentrations and brain-to-plasma ratios remained very low in all strains, indicating intrinsically poor brain penetration of encorafenib.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### IMATINIB

21 attributed of 90 retrieved sentences · 13 full text, 8 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_record` · CNS-manifestation trial evidence on 0 drug rows

**Evidence score: `unknown`** (conflicting_best_evidence) — best supporting claim 0.95, best contradicting 0.675, direction +0.289. best evidence points both ways (support 0.95 vs exclusion 0.68); unresolved. Corroboration: 6.325 total weight across 21 claims (does not set the band). Heaviest claims: CNS-036 (0.95), CNS-035 (0.90), CNS-030 (0.68).

**Proposed drug verdict: `demonstrated`** — 2 primary human claim(s), all demonstrated. Decisive claim(s): CNS-035, CNS-036.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-028** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `limiting` · number
  - > Subsequently, it was demonstrated that thedistribution of imatinib is limited by ABCB1-mediated efflux, resulting in limited brain penetration [].
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `review_restatement` · restated · other_animal · arm `unclear` · none = nan · confidence low · weight **0.02** · **flagged for human check**
  - rationale: This Background sentence restates a prior study's finding without reporting the actual brain/plasma or CSF concentration data itself; no exposure quantity is given in this text, only a citation to another paper's conclusion.
  - span relied on: “Subsequently, it was demonstrated that the in vivo distribution of imatinib is limited by ABCB1-mediated efflux, resulting in limited brain penetration [ 5 ].”
  - read from: pmc_body / Background · **your verdict:** _______
- **CNS-029** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > However, ABCB1 is not the sole transporter expressed in the blood-brain barrier that may limit the brain distribution of imatinib.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `review_restatement` · restated · other_animal · arm `unclear` · none = nan · confidence low · weight **0.02** · **flagged for human check**
  - rationale: This Background paragraph only restates other cited studies' findings (refs 5, 6, 9) without reporting a primary measured exposure value in this paper; no quantitative ratio or concentration is given here.
  - span relied on: “it was demonstrated that the in vivo distribution of imatinib is limited by ABCB1-mediated efflux, resulting in limited brain penetration [ 5 ]. More recently, positron emission topography studies with [ N - 11 C-methyl]-imatinib have confirmed limited brain penetration in primates [ 6 ]”
  - read from: pmc_body / Background · **your verdict:** _______
- **CNS-030** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > The brain-to-plasma ratio of imatinib 2 hours after administration did not differ significantly between the two groups (P = 0.83), and similar brain-to-plasma AUCratios were observed for each group (0.070 for imatinib plus vehicle0.078 for imatinib plus tariquidar).
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma AUC ratio = 0.070 for imatinib plus vehicle versus 0.078 for imatinib plus tariquidar · confidence high · weight **0.68**
  - rationale: Vehicle (normal) arm shows brain:plasma AUC ratio of 0.070, a low absolute value indicating exclusion from normal brain; tariquidar co-administration (inhibitor arm) did not change this ratio despite increasing systemic exposure.
  - span relied on: “The brain-to-plasma ratio of imatinib 2 hours after administration did not differ significantly between the two groups (P = 0.83), and similar brain-to-plasma AUCratios were observed for each group (0.070 for imatinib plus vehicle0.078 for imatinib plus tariquidar)”
  - read from: pmc_body / Results · **your verdict:** _______
- **CNS-031** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > Table 1 Pharmacokinetics of imatinib in Balb/C mice in the presence and absence of tariquidar Imatinib alone Imatinib + Tariquidar Plasma Mean SD Mean SD Fold Change P-value C(ng/mL) 5,710.5 1,472.3 6,813.2 1,547.9 1.19 - T(hr) 0.17 - 0.17 - - - AUC(hr*ng/mL) 12,167.5 - 26,724.6 - 2.20 0.001 Liver Mean SD Mean SD Fold Change P-value C(ng/g) 26,279.7 4,560.2 46,139.1 11,000.6 1.76 - T(hr) 0.25 - 0.17 - - - AUC(hr*ng/g) 68,330.8 - 153,209.2 - 2.24 < 0.00001 Brain Mean SD Mean SD Fold Change P-value C(ng/g) 194.7 27.2 417.0 116.6 2.14 - T(hr) 2 - 2 - - - AUC(hr*ng/g) 574.23 - 1,277.7 - 2.23 0.00001 Discussio
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain concentration and AUC (imatinib alone arm) = Brain C(ng/g) 194.7 vs Plasma C(ng/mL) 5,710.5; Brain AUC 574.23 vs Plasma AUC 12,167.5 (imatinib alone) · confidence high · weight **0.68**
  - rationale: In the normal (imatinib alone) arm, brain concentration (~195 ng/g) and AUC (~574) are far below plasma values (~5,710 ng/mL, AUC ~12,168), indicating low brain penetration absent efflux inhibition.
  - span relied on: “Brain Mean SD Mean SD Fold Change P-value C(ng/g) 194.7 27.2 417.0 116.6 2.14 - T(hr) 2 - 2 - - - AUC(hr*ng/g) 574.23 - 1,277.7 - 2.23 0.00001”
  - read from: pmc_body / TABLE · **your verdict:** _______
- **CNS-032** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > The brain-to-plasma concentration ratio of imatinib 2 hours after administration was not significantly affected by tariquidar.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma concentration ratio and AUC brain-to-plasma ratio = brain-to-plasma concentration ratio at 2h; AUC 0-4 brain-to-plasma ratio, not significantly changed by tariquidar · confidence medium · weight **0.52** · **flagged for human check**
  - rationale: Normal (non-inhibitor) wild-type mouse brain-to-plasma ratio is the baseline exposure; tariquidar (efflux inhibitor) failed to increase it, implying low baseline brain penetration consistent with efflux-limited CNS exposure in normal brain.
  - span relied on: “The brain-to-plasma concentration ratio of imatinib 2 hours after administration was not significantly affected by tariquidar. In addition, the AUC 0–4 ratio for brain-to-plasma was similar in the presence or absence of tariquidar.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-033** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > Specifically, elacridar has been shown to result in a 9.3-fold increase in the brain-to-plasma concentration ratio, as compared to administration of imatinib alone [].
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `review_restatement` · restated · mouse · arm `transporter_knockout_or_inhibitor` · brain-to-plasma = 9.3-fold increase in brain-to-plasma concentration ratio with elacridar vs imatinib alone · confidence medium · weight **0.03** · **flagged for human check**
  - rationale: This is a Discussion restatement of another cited study (ref 14), using an efflux inhibitor (elacridar) arm; absolute brain concentrations not stated. Describes transporter effect, not native CNS exposure of imatinib alone.
  - span relied on: “elacridar has been shown to result in a 9.3-fold increase in the brain-to-plasma concentration ratio, as compared to administration of imatinib alone”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-034** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · number
  - > Though the increase in brain exposure to imatinib was reported to be higher with oral administration, as compared to i.v., this was only measured at 4 hours post-imatinib, and the analysis was based only on measurement of total radioactivity.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `review_restatement` · restated · mouse · arm `unclear` · brain exposure (total radioactivity) = nan · confidence low · weight **0.03** · **flagged for human check**
  - rationale: This Discussion paragraph restates and critiques a different study's (Breedveld et al.) finding without giving the current paper's own measured values; it is a restatement, and the authors flag it as unreliable (radioactivity, not parent drug).
  - span relied on: “Though the increase in brain exposure to imatinib was reported to be higher with oral administration, as compared to i.v., this was only measured at 4 hours post-imatinib, and the analysis was based only on measurement of total radioactivity.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-035** · [PMID 32493453](https://pubmed.ncbi.nlm.nih.gov/32493453/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7268320/) · `full_text` · `supporting` · number
  - > Consequently, we tested whether CSF protein levels routinely measured at the same time point as drug penetration analyzes correlated to imatinib concentrations and could indeed detect a positive correlation (Additional file: Figure S6).
  - *Cerebrospinal fluid penetration of targeted therapeutics in pediatric brain tumor patients.* — Acta Neuropathol Commun 2020
  - **proposed: `demonstrated`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF concentration = mean 77.7 nM, range 5.7–288.5 nM; detected in 75% (9/12) samples · confidence high · weight **0.90**
  - rationale: Primary human CSF measurement of imatinib in pediatric brain tumor patients, quantified directly in CSF samples with concrete concentrations, not an assertion or in-vitro prediction.
  - span relied on: “including samples for dasatinib (mean 1.2 nM, range 0.5–1.9 nM), imatinib (mean 77.7 nM, range 5.7–288.5 nM)... Imatinib and dasatinib were detected in 75% (9/12) and 66% (2/3) respectively.”
  - read from: pmc_body / Quantitation of pharmaceuticals including free drug levels and metabolites · **your verdict:** _______
- **CNS-036** · [PMID 32493453](https://pubmed.ncbi.nlm.nih.gov/32493453/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7268320/) · `full_text` · `supporting` · number
  - > Supplementary information Supplementary information on clinical parameters and sample collection.Sequential therapies of the investigated drugs in the study cohort.Depiction of the used HPLC gradient for sample analysis.Overview of the used mass spectrometer parameters.Normalized chromatogram of a standard solution of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat obtained with the developed HPLC-QqQ MS method.Overview of the corresponding method performance parameters.Depiction of measured CCS values of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat.Depiction of the quantitation results for imatinib CSF samples
  - *Cerebrospinal fluid penetration of targeted therapeutics in pediatric brain tumor patients.* — Acta Neuropathol Commun 2020
  - **proposed: `demonstrated`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF concentration = high (> 10 nM) · confidence high · weight **0.95**
  - rationale: Primary human CSF measurement via Ommaya reservoir in pediatric brain tumor patients shows imatinib at high (>10 nM) CSF concentration, directly measured exposure in CNS compartment.
  - span relied on: “ribociclib, vorinostat and imatinib showed high (> 10 nM) ... penetrance”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-037** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `limiting` · no number
  - > More recently, positron emission topography studies with [-C-methyl]-imatinib have confirmed limited brain penetration in primates [].
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `review_restatement` · restated · other_animal · arm `normal` · none = nan · confidence low · weight **0.04** · **flagged for human check**
  - rationale: Background section restating another paper's PET finding (citation 6) with no actual exposure values given; this is a secondary restatement, not primary measured data in this text.
  - span relied on: “positron emission topography studies with [ N - 11 C-methyl]-imatinib have confirmed limited brain penetration in primates [ 6 ]”
  - read from: pmc_body / Background · **your verdict:** _______
- **CNS-038** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `limiting` · no number
  - > Here, we evaluated the effect of tariquidar on the disposition of imatinib in mice, in order to provide a pharmacokinetic rationale for attempts to improve the agent's low brain penetration.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `design_or_prediction` · restated · mouse · arm `not_applicable` · none = nan · confidence low · weight **0.03**
  - rationale: Background sentence states study rationale, restating prior knowledge of low brain penetration without reporting a measured exposure value; no CSF/brain concentration or ratio given here.
  - span relied on: “in order to provide a pharmacokinetic rationale for attempts to improve the agent's low brain penetration”
  - read from: pmc_body / Background · **your verdict:** _______
- **CNS-039** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · no number
  - > Hence, it is possible that the higher imatinib dose utilized in the current study results in higher plasma concentrations of drug and, therefore, saturation of drug efflux at the blood-brain barrier.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `design_or_prediction` · unclear · mouse · arm `normal` · none = nan · confidence medium · weight **0.08**
  - rationale: This is a speculative explanatory hypothesis ("it is possible that"), not a reported measurement of imatinib brain/CSF exposure in this study; no actual brain concentration value is given here.
  - span relied on: “it is possible that the higher imatinib dose utilized in the current study results in higher plasma concentrations of drug and, therefore, saturation of drug efflux at the blood-brain barrier”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-040** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `full_text` · `supporting` · no number
  - > Based on our findings, simply doubling the dose of imatinib without addition of an inhibitor would likely result in a similar increase in overall brain exposure, due to increased plasma concentrations of drug.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `unknown`** · basis `design_or_prediction` · primary · mouse · arm `unclear` · none = nan · confidence high · weight **0.08**
  - rationale: This is a predictive/interpretive statement in the Conclusion section ("would likely result"), not a reported exposure measurement; no concentration, ratio, or Kp,uu value is given here.
  - span relied on: “simply doubling the dose of imatinib without addition of an inhibitor would likely result in a similar increase in overall brain exposure, due to increased plasma concentrations of drug”
  - read from: pmc_body / Conclusion · **your verdict:** _______
- **CNS-041** · [PMID 12604685](https://pubmed.ncbi.nlm.nih.gov/12604685/) · `abstract_only` · `supporting` · number
  - > In the wild-type mice, the brain-to-plasma STI-571 concentration ratio at all time points was low (1-3%);
  - *Distribution of STI-571 to the brain is limited by P-glycoprotein-mediated efflux.* — J Pharmacol Exp Ther 2003
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma concentration ratio = low (1-3%) · confidence high · weight **0.46**
  - rationale: Primary measured PK in wild-type (normal transporter) mice shows a low brain:plasma ratio (1-3%), indicating exclusion from normal brain, a direct contradicted finding for this compartment.
  - span relied on: “In the wild-type mice, the brain-to-plasma STI-571 concentration ratio at all time points was low (1-3%)”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-042** · [PMID 12604685](https://pubmed.ncbi.nlm.nih.gov/12604685/) · `abstract_only` · `supporting` · number
  - > When 12.5 mg/kg STI-571 was given intravenously, the brain-to-plasma ratio of STI-571 in the mdr1a/b (-/-) mice was approximately 7-fold greater than that of wild-type mice up to 120 min postdose.
  - *Distribution of STI-571 to the brain is limited by P-glycoprotein-mediated efflux.* — J Pharmacol Exp Ther 2003
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio = low (1-3%) · confidence high · weight **0.46**
  - rationale: Matched sentence reports knockout-vs-wild-type ratio (describes transporter, not patient exposure). Surrounding text gives primary wild-type measurement: brain-to-plasma ratio low (1-3%), indicating CNS exclusion under normal conditions.
  - span relied on: “In the wild-type mice, the brain-to-plasma STI-571 concentration ratio at all time points was low (1-3%)”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-043** · [PMID 25539457](https://pubmed.ncbi.nlm.nih.gov/25539457/) · `abstract_only` · `supporting` · number
  - > Brain exposure increased substantially in Mdr1a(-/-) rats for loperamide and in Mdr1a(-/-)/Abcg2(-/-) rats for imatinib and compound Y, but minimally to modestly in Abcg2(-/-) rats for dantrolene and compound X.
  - *Differential role of P-glycoprotein and breast cancer resistance protein in drug distribution into brain, CSF and peripheral nerve tissues in rats.* — Xenobiotica 2014
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · rat · arm `transporter_knockout_or_inhibitor` · brain exposure (knockout vs wild-type) and CSF:unbound brain concentration ratio = Brain exposure increased substantially in Mdr1a(-/-)/Abcg2(-/-) rats for imatinib; CSF to unbound brain concentration ratio was reduced to 1 in Mdr1a(-/-)/Abcg2(-/-) rats for imatinib · confidence high · weight **0.25**
  - rationale: Imatinib brain exposure is elevated only in double-knockout rats, indicating normal (wild-type) brain penetration is low due to active Pgp/Bcrp efflux; this describes transporter exclusion, not patient-relevant CNS exposure.
  - span relied on: “Brain exposure increased substantially in Mdr1a(-/-) rats for loperamide and in Mdr1a(-/-)/Abcg2(-/-) rats for imatinib and compound Y ... While CSF to unbound brain concentration ratio remained ≥3 in the KO animals for dantrolene, compounds X and Y, it was reduced to 1 in the Mdr1a(-/-)/Abcg2(-/-) rats for imatinib.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-044** · [PMID 25539457](https://pubmed.ncbi.nlm.nih.gov/25539457/) · `abstract_only` · `supporting` · number
  - > While CSF to unbound brain concentration ratio remained ≥3 in the KO animals for dantrolene, compounds X and Y, it was reduced to 1 in the Mdr1a(-/-)/Abcg2(-/-) rats for imatinib.
  - *Differential role of P-glycoprotein and breast cancer resistance protein in drug distribution into brain, CSF and peripheral nerve tissues in rats.* — Xenobiotica 2014
  - **proposed: `unknown`** · basis `measured_pk_animal` · primary · rat · arm `transporter_knockout_or_inhibitor` · CSF to unbound brain concentration ratio; brain exposure (Mdr1a/Abcg2 KO) = CSF to unbound brain concentration ratio reduced to 1 in Mdr1a(-/-)/Abcg2(-/-) rats; brain exposure increased substantially in Mdr1a(-/-)/Abcg2(-/-) rats · confidence medium · weight **0.21** · **flagged for human check**
  - rationale: All imatinib PK data (CSF:brain ratio, brain exposure increase) are from Mdr1a/Abcg2 knockout rats, not wild-type/normal arm, so they describe transporter effect, not patient-relevant CNS exposure.
  - span relied on: “it was reduced to 1 in the Mdr1a(-/-)/Abcg2(-/-) rats for imatinib”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-045** · [PMID 15073132](https://pubmed.ncbi.nlm.nih.gov/15073132/) · `abstract_only` · `limiting` · no number
  - > There is limited penetration of imatinib into the CSF of nonhuman primates after i.v.
  - *Plasma and cerebrospinal fluid pharmacokinetics of imatinib after administration to nonhuman primates.* — Clin Cancer Res 2004
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF:plasma AUC ratio = 5% +/-2% · confidence high · weight **0.44**
  - rationale: Primary measured PK in nonhuman primates, normal (non-transporter-modified) arm, shows low CSF:plasma ratio (5%) directly supporting the matched conclusion sentence of limited CSF penetration.
  - span relied on: “The mean CSF:plasma area under the plasma concentration versus time curve ratio for all of the animals was 5% +/-2%.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-046** · [PMID 15073132](https://pubmed.ncbi.nlm.nih.gov/15073132/) · `abstract_only` · `supporting` · no number
  - > We used a nonhuman primate model that is highly predictive of the cerebrospinal fluid penetration of drugs in humans to study the pharmacokinetics of imatinib in plasma and cerebrospinal fluid (CSF) after i.v.
  - *Plasma and cerebrospinal fluid pharmacokinetics of imatinib after administration to nonhuman primates.* — Clin Cancer Res 2004
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF:plasma AUC ratio = 5% +/-2% · confidence high · weight **0.44**
  - rationale: Primary measured PK in normal (non-transporter-modified) nonhuman primates shows low CSF:plasma ratio (5%) and limited CSF penetration, a direct exposure measurement supporting exclusion from CSF compartment.
  - span relied on: “The mean CSF:plasma area under the plasma concentration versus time curve ratio for all of the animals was 5% +/-2%. CONCLUSIONS: There is limited penetration of imatinib into the CSF of nonhuman primates after i.v. and p.o. administration.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-047** · [PMID 19591692](https://pubmed.ncbi.nlm.nih.gov/19591692/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2717937/) · `abstract_only` · `supporting` · no number
  - > Though tariquidar increased the absolute exposure of imatinib, the brain-to-plasma ratio of imatinib was unaffected.
  - *Influence of the dual ABCB1 and ABCG2 inhibitor tariquidar on the disposition of oral imatinib in mice.* — J Exp Clin Cancer Res 2009
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma AUC ratio = 0.070 for imatinib plus vehicle versus 0.078 for imatinib plus tariquidar · confidence high · weight **0.57**
  - rationale: Vehicle-arm (normal, non-transporter-modifying) brain-to-plasma ratio of 0.070 is low in absolute terms, indicating exclusion from brain; tariquidar co-dosing did not change this ratio.
  - span relied on: “similar brain-to-plasma AUC 0–4 ratios were observed for each group (0.070 for imatinib plus vehicle versus 0.078 for imatinib plus tariquidar)”
  - read from: pmc_body / Results · **your verdict:** _______
- **CNS-048** · [PMID 34896751](https://pubmed.ncbi.nlm.nih.gov/34896751/) · `abstract_only` · `supporting` · no number
  - > The contribution of BCRP to the brain and CSF distribution of the dual P-glycoprotein/BCRP substrates, imatinib and prazosin, was similar to that of BCRP-specific substrates.
  - *Investigation of the role and quantitative impact of breast cancer resistance protein on drug distribution into brain and CSF in rats.* — Drug Metab Pharmacokinet 2021
  - **proposed: `unknown`** · basis `measured_pk_animal` · primary · rat · arm `unclear` · Kp,uu,brain / Kp,uu,CSF (contribution of BCRP, no explicit value for imatinib) = nan · confidence low · weight **0.20** · **flagged for human check**
  - rationale: Abstract states imatinib's BCRP contribution resembled BCRP-specific substrates but gives no actual Kp,uu or CSF/brain concentration value for imatinib itself, so direction/magnitude of its CNS exposure cannot be judged.
  - span relied on: “The contribution of BCRP to the brain and CSF distribution of the dual P-glycoprotein/BCRP substrates, imatinib and prazosin, was similar to that of BCRP-specific substrates.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### PAZOPANIB

12 attributed of 22 retrieved sentences · 9 full text, 3 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 7 drug rows

**Evidence score: `unknown`** (conflicting_best_evidence) — best supporting claim 0.608, best contradicting 0.608, direction +0.0. best evidence points both ways (support 0.61 vs exclusion 0.61); unresolved. Corroboration: 3.922 total weight across 12 claims (does not set the band). Heaviest claims: CNS-050 (0.61), CNS-051 (0.61), CNS-053 (0.61).

**Proposed drug verdict: left blank** — Primary mouse claims disagree (contradicted, demonstrated); left for the reviewer rather than resolved by majority.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-049** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `full_text` · `supporting` · number
  - > We further demonstrated that simultaneous inhibition of P-gp and Bcrp1 mediated active efflux at the mouse BBB could significantly improve the brain penetration of pazopanib.
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain penetration/brain:plasma (implied, wild-type baseline low) = not numerically stated; described as improved only upon P-gp/Bcrp1 inhibition · confidence medium · weight **0.52** · **flagged for human check**
  - rationale: Wild-type mouse brain penetration of pazopanib was low, requiring pharmacologic P-gp/Bcrp1 inhibition to improve it - the inhibitor arm shows transporter exclusion, not patient-relevant exposure; wild-type baseline supports exclusion from normal brain.
  - span relied on: “We investigated the role of P-gp and BCRP in brain disposition of pazopanib in FVB wild type mice. We further demonstrated that simultaneous inhibition of P-gp and Bcrp1 mediated active efflux at the mouse BBB could significantly improve the brain penetration of pazopanib.”
  - read from: pmc_body / 4. Discussion · **your verdict:** _______
- **CNS-050** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `full_text` · `supporting` · number
  - > In contrast to the in vitro findings, initial in vivo experiments showed selective inhibition of P-gp or Ko143 did not have any significant influence on brain penetration of pazopanib ().
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma (Cb/Cp) = severely limited; selective P-gp or Bcrp inhibition had no significant effect on brain penetration · confidence high · weight **0.61** · **flagged for human check**
  - rationale: Wild-type FVB mice (normal arm, single-transporter inhibitors) show severely limited brain/plasma ratio for pazopanib; only dual P-gp/Bcrp1 inhibition (elacridar, a modifying co-intervention) raised exposure, confirming baseline CNS exclusion.
  - span relied on: “Distribution of pazopanib to the brain was severely limited due to active efflux. In contrast to the in vitro findings, initial in vivo experiments showed selective inhibition of P-gp or Ko143 did not have any significant influence on brain penetration of pazopanib”
  - read from: pmc_body / 4. Discussion · **your verdict:** _______
- **CNS-051** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `full_text` · `supporting` · number
  - > These results suggest that even if pazopanib is a moderate substrate of P-gp in vitro, in vivo at the mouse BBB, both P-gp and Bcrp1 act in concert to limit brain penetration of pazopanib.
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma (Cb/Cp) = severely limited; ~5-fold increase only with elacridar vs wild-type baseline · confidence high · weight **0.61**
  - rationale: Primary measured Cb/Cp in wild-type FVB mice shows severely limited brain penetration of pazopanib at baseline; elacridar-induced increase reflects efflux-inhibitor arm, not native exposure.
  - span relied on: “Distribution of pazopanib to the brain was severely limited due to active efflux.”
  - read from: pmc_body / 4. Discussion · **your verdict:** _______
- **CNS-052** · [PMID 28869476](https://pubmed.ncbi.nlm.nih.gov/28869476/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5757517/) · `full_text` · `supporting` · number
  - > We found that pazopanib crosses the blood-brain barrier (BBB) with no detectable peripheral off-side effects, and reduces p-tau in TauP301L mice.
  - *Pazopanib Reduces Phosphorylated Tau Levels and Alters Astrocytes in a Mouse Model of Tauopathy.* — J Alzheimers Dis 2017
  - **proposed: `unknown`** · basis `mechanistic_assertion` · primary · mouse · arm `normal` · none = nan · confidence low · weight **0.07** · **flagged for human check**
  - rationale: This Introduction sentence asserts BBB crossing without reporting any brain/CSF/plasma concentration, ratio, or Kp,uu value; it is a summary assertion, not a measurement.
  - span relied on: “We found that pazopanib crosses the blood-brain barrier (BBB) with no detectable peripheral off-side effects, and reduces p-tau in TauP301L mice.”
  - read from: pmc_body / Introduction · **your verdict:** _______
- **CNS-053** · [PMID 28869476](https://pubmed.ncbi.nlm.nih.gov/28869476/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5757517/) · `full_text` · `supporting` · number
  - > Results Pazopanib penetrates the blood-brain barrier Following a single intraperitoneal (IP) injection of pazopanib of 0, 5, or 10mg/kg in dimethyl sulfoxide (DMSO) in C57BL/6 mice, we found that the drug penetrates the BBB and peaks at approximately 4 hours (T) ().
  - *Pazopanib Reduces Phosphorylated Tau Levels and Alters Astrocytes in a Mouse Model of Tauopathy.* — J Alzheimers Dis 2017
  - **proposed: `demonstrated`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain concentration = Cmax in brain 450 ng/mL (5mg/kg) and 583.33 ng/mL (10mg/kg), ~1uM and ~1.3uM · confidence high · weight **0.61**
  - rationale: Primary measured brain concentration in normal (non-knockout) C57BL/6 mice after IP dosing, directly quantifying CNS exposure of pazopanib; no transporter manipulation or BBB-disrupting co-intervention involved.
  - span relied on: “The peak concentration (C max ) in the brain at the 4-hour point was 450ng/mL for the 5mg/kg dose and 583.33 ng/mL for the 10 mg/kg dose, corresponding to approximately 1μM and 1.3μM”
  - read from: pmc_body / Pazopanib penetrates the blood-brain barrier · **your verdict:** _______
- **CNS-054** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `full_text` · `supporting` · no number
  - > The fact that both these test compounds in our study are also known to modulate P-gp and BCRP functional activity (;), we selected erlotinib and canertinib as clinically relevant inhibitors for improving pazopanib brain penetration.
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - **proposed: `unknown`** · basis `design_or_prediction` · unclear · na · arm `not_applicable` · none = nan · confidence medium · weight **0.05** · **flagged for human check**
  - rationale: Discussion-section rationale for selecting inhibitors; no exposure quantity for pazopanib itself given here. Surrounding text describes in vitro P-gp/BCRP inhibitor potency comparisons, not pazopanib brain/CSF/plasma measurement.
  - span relied on: “we selected erlotinib and canertinib as clinically relevant inhibitors for improving pazopanib brain penetration”
  - read from: pmc_body / 4. Discussion · **your verdict:** _______
- **CNS-055** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `full_text` · `supporting` · no number
  - > In addition, from the clinical perspective, we show that canertinib or erlotinib, although not as potent as elacridar could be indicated as clinically relevant efflux modulators in combination therapy to enhance brain penetration of pazopanib for the treatment of recurrent brain tumors.
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma (brain partitioning/accumulation) = restrict brain partitioning (wild-type, efflux-mediated); improved only with elacridar inhibition · confidence medium · weight **0.52** · **flagged for human check**
  - rationale: Wild-type mouse PK shows efflux transporters restrict pazopanib brain accumulation (normal brain, not tumor); matched sentence is a discussion-based clinical extrapolation, not new data, so verdict rests on the surrounding primary PK statement.
  - span relied on: “ABC efflux transporters P-gp and BCRP restrict brain partitioning of pazopanib in mice”
  - read from: pmc_body / 4. Discussion · **your verdict:** _______
- **CNS-056** · [PMID 22749591](https://pubmed.ncbi.nlm.nih.gov/22749591/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3396766/) · `full_text` · `limiting` · no number
  - > We have shown in our laboratory (manuscript under revision with) that one probable reason for limited brain penetration of pazopanib is due to ATP binding cassette efflux proteins;
  - *Determination of pazopanib (GW-786034) in mouse plasma and brain tissue by liquid chromatography-tandem mass spectrometry (LC/MS-MS).* — J Chromatogr B Analyt Technol Biomed Life Sci 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma AUC ratio = AUCt plasma 1.35 ± 0.04 min*mg/mL vs brain 0.020 ± 0.001 min*mg/mL, ratio 0.015 (1.5%) · confidence high · weight **0.61**
  - rationale: Primary measured PK in wild-type mice shows brain:plasma AUC ratio of 0.015 (1.5%), a low ratio demonstrating exclusion from normal brain tissue; efflux transporter mechanism statement is unverified background restatement.
  - span relied on: “As expected, brain delivery of pazopanib was severely restricted. Plasma area under the curve from time zero to the last time point (AUC t ) was 1.35 ± 0.04 min*mg/mL, as compared to 0.020 ± 0.001 min*mg/mL in the brain, giving a ratio of 0.015. This suggested that only 1.5% of the concentration in plasma was able to reach the brain.”
  - read from: pmc_body / 3.6 Method application · **your verdict:** _______
- **CNS-057** · [PMID 22749591](https://pubmed.ncbi.nlm.nih.gov/22749591/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3396766/) · `full_text` · `supporting` · no number
  - > However, the tight endothelial junctions located in brain capillaries which are further fortified by the presence of ABC efflux transporters (blood–– brain barrier, BBB) can restrict the brain penetration of pazopanib and may lead to its therapeutic inefficacy when used as an anti-tumor agent for recurrent brain tumors.
  - *Determination of pazopanib (GW-786034) in mouse plasma and brain tissue by liquid chromatography-tandem mass spectrometry (LC/MS-MS).* — J Chromatogr B Analyt Technol Biomed Life Sci 2012
  - **proposed: `unknown`** · basis `mechanistic_assertion` · restated · na · arm `not_applicable` · none = nan · confidence high · weight **0.05**
  - rationale: Introduction-section mechanistic assertion about BBB efflux transporters restricting pazopanib, with no exposure measurement (no concentration, ratio, or Kp,uu) given in this sentence or surrounding text.
  - span relied on: “can restrict the brain penetration of pazopanib and may lead to its therapeutic inefficacy when used as an anti-tumor agent for recurrent brain tumors”
  - read from: pmc_body / 1. INTRODUCTION · **your verdict:** _______
- **CNS-058** · [PMID 22688250](https://pubmed.ncbi.nlm.nih.gov/22688250/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3573846/) · `abstract_only` · `supporting` · number
  - > However, dual P-gp/Bcrp1 inhibition by elacridar (GF120918), significantly enhanced pazopanib brain penetration by ~5-fold without altering its plasma concentrations.
  - *Enhanced brain accumulation of pazopanib by modulating P-gp and Bcrp1 mediated efflux with canertinib or erlotinib.* — Int J Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain penetration (brain accumulation relative to inhibitor-free wild-type) = ~5-fold enhancement by elacridar vs wild-type; wild-type brain accumulation not significantly altered by single transporter inhibition · confidence high · weight **0.46**
  - rationale: Measured normal-brain PK in wild-type mice (no inhibitor) shows low baseline brain accumulation limited by P-gp/Bcrp1; 5-fold increase occurs only under elacridar inhibitor arm, which describes transporter effect, not normal patient exposure.
  - span relied on: “In vivo studies indicated that specific inhibition of either P-gp (by zosuquidar or LY335979) or Bcrp1 (by Ko143) alone did not significantly alter pazopanib brain accumulation. However, dual P-gp/Bcrp1 inhibition by elacridar (GF120918), significantly enhanced pazopanib brain penetration by ~5-fold without altering its plasma concentrations.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-059** · [PMID 22749591](https://pubmed.ncbi.nlm.nih.gov/22749591/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3396766/) · `abstract_only` · `supporting` · number
  - > This method was applied to determine brain to plasma concentration ratio and relevant pharmacokinetic parameters of pazopanib after a single intravenous dose of 5 mg/kg in FVB wild type mice.
  - *Determination of pazopanib (GW-786034) in mouse plasma and brain tissue by liquid chromatography-tandem mass spectrometry (LC/MS-MS).* — J Chromatogr B Analyt Technol Biomed Life Sci 2012
  - **proposed: `unknown`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma concentration ratio = nan · confidence low · weight **0.28** · **flagged for human check**
  - rationale: The abstract states a brain:plasma ratio was measured in wild-type mice but gives no numeric value or direction; without the actual result, verdict cannot be demonstrated or contradicted.
  - span relied on: “This method was applied to determine brain to plasma concentration ratio and relevant pharmacokinetic parameters of pazopanib after a single intravenous dose of 5 mg/kg in FVB wild type mice.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-060** · [PMID 28869476](https://pubmed.ncbi.nlm.nih.gov/28869476/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5757517/) · `abstract_only` · `supporting` · number
  - > Pazopanib crosses the blood-brain barrier with no detectable peripheral off-side effects, and decreases p-tau in TauP301L mice.
  - *Pazopanib Reduces Phosphorylated Tau Levels and Alters Astrocytes in a Mouse Model of Tauopathy.* — J Alzheimers Dis 2017
  - **proposed: `unknown`** · basis `mechanistic_assertion` · primary · mouse · arm `normal` · none = nan · confidence medium · weight **0.08** · **flagged for human check**
  - rationale: Sentence is an assertion of BBB crossing with no reported exposure quantity (no brain/plasma concentration, ratio, or Kp,uu) and no CNS disease approval; a behavioral/biochemical effect (p-tau reduction) is not an exposure measurement.
  - span relied on: “pazopanib crosses the blood-brain barrier (BBB) with no detectable peripheral off-side effects, and reduces p-tau in TauP301L mice”
  - read from: pmc_body / Introduction · **your verdict:** _______

### REGORAFENIB

4 attributed of 51 retrieved sentences · 2 full text, 2 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 0 drug rows

**Evidence score: `demonstrated`** (resolved) — best supporting claim 0.95, best contradicting 0.0, direction +1.0. best claim 0.95, direction +1.00. Corroboration: 0.95 total weight across 4 claims (does not set the band). Heaviest claims: CNS-061 (0.95), CNS-063 (0.21), CNS-064 (0.14).

**Proposed drug verdict: `demonstrated`** — 1 primary human claim(s), all demonstrated. Decisive claim(s): CNS-061.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-061** · [PMID 32493453](https://pubmed.ncbi.nlm.nih.gov/32493453/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7268320/) · `full_text` · `supporting` · number
  - > Supplementary information Supplementary information on clinical parameters and sample collection.Sequential therapies of the investigated drugs in the study cohort.Depiction of the used HPLC gradient for sample analysis.Overview of the used mass spectrometer parameters.Normalized chromatogram of a standard solution of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat obtained with the developed HPLC-QqQ MS method.Overview of the corresponding method performance parameters.Depiction of measured CCS values of dasatinib, imatinib, nintedanib, panobinostat, regorafenib, ribociclib, and vorinostat.Depiction of the quantitation results for imatinib CSF samples
  - *Cerebrospinal fluid penetration of targeted therapeutics in pediatric brain tumor patients.* — Acta Neuropathol Commun 2020
  - **proposed: `demonstrated`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF concentration = moderate (1-10 nM) · confidence high · weight **0.95**
  - rationale: Primary measured CSF concentration of regorafenib in pediatric brain tumor patients via Ommaya reservoirs, reported as moderate (1-10 nM) penetrance - a detectable CSF exposure measurement.
  - span relied on: “regorafenib and dasatinib moderate (1-10 nM) penetrance”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-062** · [PMID 42573440](https://pubmed.ncbi.nlm.nih.gov/42573440/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC13471100/) · `full_text` · `supporting` · no number
  - > Although regorafenib is capable of reaching intracranial tumors, CNS exposure is limited by high plasma protein binding and active efflux transporters such as P-glycoprotein and breast cancer resistance protein at the blood–brain barrier.
  - *Pathway dysregulation and therapeutic resistance in glioblastoma: molecular mechanisms and emerging therapeutic targets.* — Future Sci OA 2026
  - **proposed: `unknown`** · basis `review_restatement` · restated · human · arm `not_applicable` · none = nan · confidence low · weight **0.06** · **flagged for human check**
  - rationale: This is a Review article paragraph citing another reference [63] for CNS PK claims; no actual exposure values (concentration, ratio, Kp,uu) are reported here, only an assertion restating prior work.
  - span relied on: “Although regorafenib is capable of reaching intracranial tumors, CNS exposure is limited by high plasma protein binding and active efflux transporters such as P-glycoprotein and breast cancer resistance protein at the blood–brain barrier.”
  - read from: pmc_body / Molecular signaling pathways and emerging therapeutic targets in GBM · **your verdict:** _______
- **CNS-063** · [PMID 39637954](https://pubmed.ncbi.nlm.nih.gov/39637954/) · `abstract_only` · `supporting` · no number
  - > Despite these overall negative findings, some data indicate improved clinical outcomes in a subset of GBM patients treated with certain PKIs (i.e., regorafenib) and encourage further research to identify PKIs with better blood-brain barrier penetration and lower risk for resistance development.
  - *Protein kinase inhibitors as targeted therapy for glioblastoma: a meta-analysis of randomized controlled clinical trials.* — Pharmacol Res 2025
  - **proposed: `unknown`** · basis `clinical_cns_response` · restated · human · arm `not_applicable` · none = nan · confidence high · weight **0.21**
  - rationale: This is a meta-analysis summary statement in an abstract; it notes a subset benefit but explicitly calls for better BBB-penetrant PKIs, implying no exposure measurement reported for regorafenib itself.
  - span relied on: “some data indicate improved clinical outcomes in a subset of GBM patients treated with certain PKIs (i.e., regorafenib) and encourage further research to identify PKIs with better blood-brain barrier penetration”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-064** · [PMID 39941744](https://pubmed.ncbi.nlm.nih.gov/39941744/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11816343/) · `abstract_only` · `supporting` · no number
  - > Additionally, the suboptimal dosing of regorafenib, due to its poor penetration of the blood-brain barrier, may reduce the likelihood of effectively targeting certain PKs.
  - *Multikinase Treatment of Glioblastoma: Evaluating the Rationale for Regorafenib.* — Cancers (Basel) 2025
  - **proposed: `unknown`** · basis `mechanistic_assertion` · unclear · human · arm `not_applicable` · none = nan · confidence high · weight **0.14**
  - rationale: This is an unsupported assertion about BBB penetration with no exposure measurement (no CSF/brain concentration, Kp,uu, or ratio) reported anywhere in the abstract text; it's a genomic/target-coverage analysis paper.
  - span relied on: “the suboptimal dosing of regorafenib, due to its poor penetration of the blood-brain barrier, may reduce the likelihood of effectively targeting certain PKs”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### RIPRETINIB

2 attributed of 5 retrieved sentences · 1 full text, 1 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_record` · CNS-manifestation trial evidence on 0 drug rows

**Evidence score: `unknown`** (no_claim_carries_a_verdict) — best supporting claim 0.0, best contradicting 0.0, direction +0.0. no attributed claim carries a demonstrated or contradicted verdict. Corroboration: 0.0 total weight across 2 claims (does not set the band). Heaviest claims: CNS-066 (0.05), CNS-065 (0.03).

**Proposed drug verdict: `unknown`** — No primary, normal-arm claim carries a measured or clinical finding. Decisive claim(s): nan.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-065** · [PMID 40656249](https://pubmed.ncbi.nlm.nih.gov/40656249/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12255365/) · `full_text` · `limiting` · no number
  - > Interestingly, ripretinib, a fourth-line TKI approved for advanced GIST, also has limited CNS penetration, underscoring an ongoing lack of therapeutic options for CNS metastases [].
  - *Cerebral Metastasis of a Gastrointestinal Stromal Tumor: A Case Report and Literature Review.* — Cureus 2025
  - **proposed: `unknown`** · basis `review_restatement` · restated · na · arm `not_applicable` · none = nan · confidence low · weight **0.03**
  - rationale: Discussion-section assertion citing an external reference, no exposure quantity (CSF/brain concentration, Kp,uu, ratio) given for ripretinib in this text; a restated claim without measurement.
  - span relied on: “ripretinib, a fourth-line TKI approved for advanced GIST, also has limited CNS penetration, underscoring an ongoing lack of therapeutic options for CNS metastases [ 6 ]”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-066** · [PMID 40656249](https://pubmed.ncbi.nlm.nih.gov/40656249/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12255365/) · `abstract_only` · `supporting` · no number
  - > This case underscores the absence of effective systemic treatments for CNS disease, as most TKIs, including imatinib and ripretinib, have poor CNS penetration.
  - *Cerebral Metastasis of a Gastrointestinal Stromal Tumor: A Case Report and Literature Review.* — Cureus 2025
  - **proposed: `unknown`** · basis `mechanistic_assertion` · restated · human · arm `not_applicable` · none = nan · confidence low · weight **0.05**
  - rationale: This is a general discussion-style assertion with no measured exposure data (no CSF/brain concentration, Kp,uu, or ratio) for ripretinib; the patient never even received the drug.
  - span relied on: “most TKIs, including imatinib and ripretinib, have poor CNS penetration”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### SELUMETINIB

2 attributed of 9 retrieved sentences · 0 full text, 2 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 12 drug rows

**Evidence score: `unknown`** (below_peak_threshold) — best supporting claim 0.0, best contradicting 0.463, direction -1.0. best claim weighs 0.46, below 0.5; unassessed. Corroboration: 0.463 total weight across 2 claims (does not set the band). Heaviest claims: CNS-068 (0.49), CNS-067 (0.46).

**Proposed drug verdict: `contradicted`** — 1 primary mouse claim(s), all contradicted. Decisive claim(s): CNS-067.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-067** · [PMID 28921565](https://pubmed.ncbi.nlm.nih.gov/28921565/) · `abstract_only` · `supporting` · number
  - > PD0325901 displayed more promising characteristics than trametinib (GSK1120212), binimetinib (MEK162), selumetinib (AZD6244), and pimasertib (AS703026): PD0325901 was the weakest substrate of P-gp and BCRP in vitro, its brain penetration was only marginally higher in Abcb1a/b;Abcg2mice, and efficient target inhibition in the brain could be achieved at clinically relevant plasma levels.
  - *The impact of P-glycoprotein and breast cancer resistance protein on the brain pharmacokinetics and pharmacodynamics of a panel of MEK inhibitors.* — Int J Cancer 2017
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain target inhibition relative to plasma concentration = target inhibition only at plasma levels far above levels in patients receiving the maximum tolerated dose · confidence medium · weight **0.46** · **flagged for human check**
  - rationale: In wildtype mice (normal arm), selumetinib only achieved brain target engagement at supratherapeutic plasma levels, indicating poor brain penetration relative to clinically achievable exposure - a contradicted finding for normal brain/CNS delivery.
  - span relied on: “target inhibition could also be demonstrated for selumetinib, but only at plasma levels far above levels in patients receiving the maximum tolerated dose”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-068** · [PMID 32939452](https://pubmed.ncbi.nlm.nih.gov/32939452/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7486535/) · `abstract_only` · `supporting` · no number
  - > We qualitatively assessed the effect of selumetinib on SNF-related spinal canal distortion, cerebrospinal fluid distribution, and spinal cord deformity on MRI.
  - *The MEK inhibitor selumetinib reduces spinal neurofibroma burden in patients with NF1 and plexiform neurofibromas.* — Neurooncol Adv 2020
  - **proposed: `unknown`** · basis `clinical_cns_response` · primary · human · arm `not_applicable` · none = nan · confidence medium · weight **0.49** · **flagged for human check**
  - rationale: Spinal neurofibromas are peripheral nerve/paraspinal tumors, not an intracranial/CNS parenchymal or CSF disease site; no CSF/brain concentration or exposure metric reported, only qualitative MRI assessment of spinal canal distortion.
  - span relied on: “Eighteen patients showed subtle to a marked improvement in SNF burden, 5 remained stable, and no worsening was observed during treatment.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### SORAFENIB

13 attributed of 44 retrieved sentences · 6 full text, 7 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 17 drug rows

**Evidence score: `contradicted`** (resolved) — best supporting claim 0.154, best contradicting 0.545, direction -0.718. best claim 0.55, direction -0.72. Corroboration: 4.614 total weight across 13 claims (does not set the band). Heaviest claims: CNS-075 (0.55), CNS-076 (0.55), CNS-069 (0.49).

**Proposed drug verdict: `contradicted`** — 3 primary mouse claim(s), all contradicted. Decisive claim(s): CNS-075, CNS-076, CNS-079.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-069** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `full_text` · `supporting` · number
  - > The CSF penetration of sorafenib was only 0.02% relative to total (free and protein bound) plasma drug exposure.
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF:plasma penetration ratio = 0.02% (3.4% after correcting for protein binding) · confidence high · weight **0.49**
  - rationale: Primary measured PK in non-human primates shows very low CSF penetration (0.02%, 3.4% free-drug corrected), indicating exclusion from CSF compartment under normal conditions.
  - span relied on: “The CSF penetration of sorafenib was only 0.02% relative to total (free and protein bound) plasma drug exposure.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-070** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `full_text` · `limiting` · no number
  - > Based on our findings of limited CSF penetration, sorafenib may act in limiting metastatic spread by controlling the primary disease [].
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF penetration = limited CSF penetration · confidence high · weight **0.49** · **flagged for human check**
  - rationale: This is the paper's own primary non-human primate PK finding (title confirms plasma/CSF PK study), stated as "limited CSF penetration" - a direct exposure finding, not a restatement, supporting exclusion from CSF.
  - span relied on: “Based on our findings of limited CSF penetration, sorafenib may act in limiting metastatic spread by controlling the primary disease”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-071** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `full_text` · `supporting` · no number
  - > Sorafenib is highly protein bound, and thus CSF penetration was calculated using an estimated free drug exposure.
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF penetration (CSF:plasma) = 0.02% relative to total plasma; 3.4% after correcting for protein binding · confidence high · weight **0.49**
  - rationale: Primary measured PK in non-human primates (normal, untreated) shows very low CSF:plasma penetration (0.02%, 3.4% free-drug corrected), indicating exclusion from CSF compartment.
  - span relied on: “The CSF penetration of sorafenib was only 0.02% relative to total (free and protein bound) plasma drug exposure. ... correcting for protein binding only minimally increased the CSF penetration to 3.4%.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-072** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `full_text` · `supporting` · no number
  - > The drug exposure of sorafenib in the CSF relative to total and free drug plasma exposure in NHP is limited.
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF:plasma exposure (total and free drug) = limited · confidence high · weight **0.49** · **flagged for human check**
  - rationale: Primary measured PK in normal non-human primates shows CSF exposure low relative to total and free plasma exposure, indicating exclusion from CSF compartment under normal (non-tumour, non-transporter-modified) conditions.
  - span relied on: “The drug exposure of sorafenib in the CSF relative to total and free drug plasma exposure in NHP is limited.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-073** · [PMID 22335402](https://pubmed.ncbi.nlm.nih.gov/22335402/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3296237/) · `full_text` · `supporting` · no number
  - > Sorafenib was chosen as the model substrate since we have previously shown that its brain penetration is restricted by BCRP and possibly by P-gp.
  - *Insight into the cooperation of P-glycoprotein (ABCB1) and breast cancer resistance protein (ABCG2) at the blood-brain barrier: a case study examining sorafenib efflux clearance.* — Mol Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · restated · mouse · arm `transporter_knockout_or_inhibitor` · brain efflux clearance / brain penetration restriction by BCRP and P-gp = brain penetration restricted by BCRP and possibly P-gp; efflux clearance decreases when BCRP absent, unchanged when P-gp alone absent · confidence medium · weight **0.09** · **flagged for human check**
  - rationale: Matched sentence restates a prior finding (citation to earlier work), but surrounding text in this paper's own study shows measured BBB efflux clearance of sorafenib restricted by BCRP in wild-type/knockout mice, indicating CNS exclusion in normal brain.
  - span relied on: “its brain penetration is restricted by BCRP and possibly by P-gp”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-074** · [PMID 32776310](https://pubmed.ncbi.nlm.nih.gov/32776310/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7677279/) · `full_text` · `supporting` · no number
  - > Future studies in younger rats are warranted to verify the influence of age on the brain penetration of sorafenib and its N-oxide.
  - *The Influence of Paracetamol on the Penetration of Sorafenib and Sorafenib N-Oxide Through the Blood-Brain Barrier in Rats.* — Eur J Drug Metab Pharmacokinet 2020
  - **proposed: `unknown`** · basis `design_or_prediction` · unclear · rat · arm `not_applicable` · none = nan · confidence high · weight **0.08**
  - rationale: Matched sentence is a forward-looking suggestion for future research, not a reported measurement. Surrounding text discusses study limitations (sampling design, animal age) without giving exposure values for sorafenib.
  - span relied on: “Future studies in younger rats are warranted to verify the influence of age on the brain penetration of sorafenib and its N-oxide.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-075** · [PMID 20952483](https://pubmed.ncbi.nlm.nih.gov/20952483/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3014301/) · `abstract_only` · `supporting` · number
  - > Steady-state brain-to-plasma concentration ratio of sorafenib was approximately 0.36 ± 0.056 in the Bcrp1(-/-) mice, 0.11 ± 0.021 in the Mdr1a/b(-/-) mice, and 0.91 ± 0.29 in the Mdr1a/b(-/-)Bcrp1(-/-) mice compared with 0.094 ± 0.007 in the wild-type mice.
  - *The role of the breast cancer resistance protein (ABCG2) in the distribution of sorafenib to the brain.* — J Pharmacol Exp Ther 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma concentration ratio = 0.094 ± 0.007 in wild-type mice (AUC brain-to-plasma coefficient 0.06) · confidence high · weight **0.55**
  - rationale: Wild-type (normal transporter) mice show low brain-to-plasma ratio (~0.09; AUC ratio 0.06), indicating active efflux restricts sorafenib's normal-brain penetration. Knockout/inhibitor arms show transporter-dependent increases, not patient-relevant exposure.
  - span relied on: “compared with 0.094 ± 0.007 in the wild-type mice”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-076** · [PMID 20952483](https://pubmed.ncbi.nlm.nih.gov/20952483/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3014301/) · `abstract_only` · `supporting` · number
  - > Sorafenib brain-to-plasma ratios increased on coadministration of the dual P-gp/BCRP inhibitor elacridar such that the ratio in wild-type mice (0.76 ± 0.24), Bcrp1(-/-) mice (1.03 ± 0.33), Mdr1a/b(-/-) mice (1.3 ± 0.29), and Mdr1a/b(-/-)Bcrp1(-/-) mice (0.73 ± 0.35) were not significantly different.
  - *The role of the breast cancer resistance protein (ABCG2) in the distribution of sorafenib to the brain.* — J Pharmacol Exp Ther 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio / equilibrium-distribution coefficient = 0.06 (AUC brain/plasma) and steady-state ratio 0.094 ± 0.007 in wild-type mice · confidence high · weight **0.55**
  - rationale: Wild-type mouse brain-to-plasma ratios (0.06, 0.094) are low, showing sorafenib is largely excluded from brain under normal (non-knockout, non-inhibitor) conditions. The elacridar/knockout data describe transporter contribution, not patient-relevant exposure.
  - span relied on: “The brain-to-plasma equilibrium-distribution coefficient (area under the concentration-time profiles for plasma/area under the concentration-time profiles for brain) was 0.06 in wild-type mice. Steady-state brain-to-plasma concentration ratio of sorafenib was approximately ... 0.094 ± 0.007 in the wild-type mice.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-077** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `abstract_only` · `supporting` · number
  - > The mean CSF penetration of sorafenib was 0.02% and 3.4% after correcting for plasma protein binding.
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF:plasma AUC ratio (CSF penetration) = 0.02% (3.4% after correcting for plasma protein binding) · confidence high · weight **0.46**
  - rationale: Primary measured CSF:plasma AUC ratio in non-human primates after IV sorafenib is very low (0.02%, 3.4% protein-binding corrected), indicating exclusion from CSF in a normal (non-transporter-modified) arm.
  - span relied on: “The mean CSF penetration of sorafenib was 0.02% and 3.4% after correcting for plasma protein binding.”
  - read from: pmc_body / Results · **your verdict:** _______
- **CNS-078** · [PMID 21072558](https://pubmed.ncbi.nlm.nih.gov/21072558/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6636925/) · `abstract_only` · `supporting` · no number
  - > The CSF penetration of sorafenib is limited relative to total and free drug exposure in plasma.
  - *The plasma and cerebrospinal fluid pharmacokinetics of sorafenib after intravenous administration in non-human primates.* — Invest New Drugs 2010
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · other_animal · arm `normal` · CSF penetration relative to plasma exposure (CSF:plasma %) = 0.02% relative to total plasma; 3.4% after correcting for protein binding · confidence high · weight **0.41**
  - rationale: Primary non-human primate IV PK study directly measured low CSF:plasma penetration (0.02%, 3.4% free-drug corrected) in normal animals, indicating CNS/CSF exclusion despite measurable, quantifiable CSF levels.
  - span relied on: “The CSF penetration of sorafenib was only 0.02% relative to total (free and protein bound) plasma drug exposure. ... correcting for protein binding only minimally increased the CSF penetration to 3.4%.”
  - read from: pmc_body / Discussion · **your verdict:** _______
- **CNS-079** · [PMID 22335402](https://pubmed.ncbi.nlm.nih.gov/22335402/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3296237/) · `abstract_only` · `supporting` · no number
  - > The present study uses the brain penetration of sorafenib to investigate these findings and attempts to explain the mechanistic basis of this cooperation with a simple theory based on affinity and capacity dependent carrier-mediated transport.
  - *Insight into the cooperation of P-glycoprotein (ABCB1) and breast cancer resistance protein (ABCG2) at the blood-brain barrier: a case study examining sorafenib efflux clearance.* — Mol Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain efflux clearance (via brain efflux index method) = Sorafenib clearance out of the brain decreased 2-fold in the Bcrp1(-/-) mice and 2.5-fold in the Mdr1a/1b(-/-)Bcrp1(-/-) mice; clearance out of brain when P-gp was absent did not change significantly compared to wild-type · confidence medium · weight **0.46** · **flagged for human check**
  - rationale: Wild-type clearance out of brain is high (efflux dominant via BCRP), implying low normal-brain exposure in the normal/wild-type arm; knockout-only reduction in clearance describes the transporter, not patient exposure.
  - span relied on: “The brain efflux index method, combined with the organotypic brain slices, was used to determine the net contribution of P-gp and BCRP to the total clearance of sorafenib out of the brain and show that its efflux at the BBB is mediated primarily by BCRP. Sorafenib clearance out of the brain decreased 2-fold in the Bcrp1(-/-) mice and 2.5-fold in the Mdr1a/1b(-/-)Bcrp1(-/-) mice.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-080** · [PMID 32776310](https://pubmed.ncbi.nlm.nih.gov/32776310/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7677279/) · `abstract_only` · `supporting` · no number
  - > Pharmacokinetic analysis revealed increased brain exposure to sorafenib and sorafenib N-oxide after co-administration of paracetamol.
  - *The Influence of Paracetamol on the Penetration of Sorafenib and Sorafenib N-Oxide Through the Blood-Brain Barrier in Rats.* — Eur J Drug Metab Pharmacokinet 2020
  - **proposed: `demonstrated`** · basis `measured_pk_animal` · primary · rat · arm `bbb_modifying_cointervention` · brain concentration/exposure = increased brain exposure to sorafenib after co-administration of paracetamol · confidence medium · weight **0.15** · **flagged for human check**
  - rationale: Measured brain tissue exposure in rats shows sorafenib does reach brain; but increase is driven by paracetamol co-intervention, not baseline sorafenib alone - flag as cointervention-modified exposure, still demonstrates brain penetration occurs.
  - span relied on: “A single administration of paracetamol increases exposure to sorafenib and sorafenib N-oxide in the brain tissue.”
  - read from: pmc_body / Key Points · **your verdict:** _______
- **CNS-081** · [PMID 36768736](https://pubmed.ncbi.nlm.nih.gov/36768736/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9917080/) · `abstract_only` · `supporting` · no number
  - > Among these problems, the presence of the blood-brain barrier of the brain and the need to use high doses of sorafenib, the existence of mechanisms for the redistribution of sorafenib and its release in the brain tissue, as well as the high resistance of gliomas and glioblastomas to therapy should be considered the main ones.
  - *Ca-Dependent Effects of the Selenium-Sorafenib Nanocomplex on Glioblastoma Cells and Astrocytes of the Cerebral Cortex: Anticancer Agent and Cytoprotector.* — Int J Mol Sci 2023
  - **proposed: `unknown`** · basis `mechanistic_assertion` · restated · na · arm `not_applicable` · none = nan · confidence high · weight **0.04**
  - rationale: Background-style narrative assertion about BBB and need for high doses, no measured exposure (no CSF/brain concentration, Kp,uu, or B:P ratio) is given anywhere in text.
  - span relied on: “the presence of the blood-brain barrier of the brain and the need to use high doses of sorafenib, the existence of mechanisms for the redistribution of sorafenib and its release in the brain tissue”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### SUNITINIB

11 attributed of 25 retrieved sentences · 3 full text, 8 abstract-only · ChEMBL calculated flag: `predicted_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 5 drug rows

**Evidence score: `unknown`** (below_peak_threshold) — best supporting claim 0.26, best contradicting 0.463, direction -0.439. best claim weighs 0.46, below 0.5; unassessed. Corroboration: 1.963 total weight across 11 claims (does not set the band). Heaviest claims: CNS-085 (0.58), CNS-090 (0.46), CNS-089 (0.33).

**Proposed drug verdict: `contradicted`** — 1 primary mouse claim(s), all contradicted. Decisive claim(s): CNS-090.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-082** · [PMID 37997517](https://pubmed.ncbi.nlm.nih.gov/37997517/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10726873/) · `full_text` · `supporting` · number
  - > One potential reason for this could be due to its limited penetration through an intact BBB.A study by Sobanska and colleagues used a rabbit model to show that the exposure of sunitinib in plasma, aqueous humor, and CSF was different depending on the time of day of drug administration (8 am dose area under the curve [AUC], CSF: 55.5 ng*h/mL vs.
  - *Chemotherapy in pediatric brain tumor and the challenge of the blood-brain barrier.* — Cancer Med 2023
  - **proposed: `contradicted`** · basis `measured_pk_animal` · restated · other_animal · arm `normal` · CSF AUC and BBB penetration percentage = CSF AUC 55.5 ng*h/mL (8am) vs 66.3 ng*h/mL (9pm); BBB penetration <5% · confidence medium · weight **0.16** · **flagged for human check**
  - rationale: This review restates a rabbit PK study (Sobanska et al.) reporting measured CSF exposure and BBB penetration <5%, a low absolute ratio indicating exclusion from CSF compartment.
  - span relied on: “sunitinib penetration through the BBB was reported to be very low (<5%) and comparable in both dosing groups”
  - read from: pmc_body / Sunitinib · **your verdict:** _______
- **CNS-083** · [PMID 37997517](https://pubmed.ncbi.nlm.nih.gov/37997517/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10726873/) · `full_text` · `supporting` · number
  - > 9 pm dose AUC, CSF: 66.3 ng*h/mL, respectively).However, sunitinib penetration through the BBB was reported to be very low (<5%) and comparable in both dosing groups.
  - *Chemotherapy in pediatric brain tumor and the challenge of the blood-brain barrier.* — Cancer Med 2023
  - **proposed: `contradicted`** · basis `measured_pk_animal` · restated · other_animal · arm `normal` · CSF AUC / BBB penetration percentage = <5% · confidence medium · weight **0.16** · **flagged for human check**
  - rationale: Rabbit PK study (cited, restated in review) measured CSF AUC and reported BBB penetration <5%, a low absolute exposure in normal (non-knockout) animals, indicating CNS exclusion in CSF compartment.
  - span relied on: “sunitinib penetration through the BBB was reported to be very low (<5%) and comparable in both dosing groups”
  - read from: pmc_body / Sunitinib · **your verdict:** _______
- **CNS-084** · [PMID 37997517](https://pubmed.ncbi.nlm.nih.gov/37997517/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10726873/) · `full_text` · `supporting` · number
  - > To overcome the limitations of the BBB, a study by Szalek and colleagues evaluated the antibiotic ciprofloxacin to modulate the BBB and enhance penetration of sunitinib.They found that rabbits treated with sunitinib + ciprofloxacin had higher 24‐h CSF exposures (AUCand C) compared to those that only received sunitinib (50.4 vs.
  - *Chemotherapy in pediatric brain tumor and the challenge of the blood-brain barrier.* — Cancer Med 2023
  - **proposed: `unknown`** · basis `measured_pk_animal` · restated · rabbit · arm `bbb_modifying_cointervention` · CSF AUC0-24 and Cmax = 50.4 vs. 155 ng*h/mL and 4.2 vs. 18 ng/mL (sunitinib alone vs. sunitinib + ciprofloxacin) · confidence medium · weight **0.05** · **flagged for human check**
  - rationale: This is a restated animal study (Szalek et al.) in the Review's Background-like narrative, using ciprofloxacin as a BBB-modulating co-intervention; the sunitinib-only CSF exposure (50.4 ng*h/mL, 4.2 ng/mL) is low but not explicitly characterized as below target engagement, and the paper is a review restating another's primary data.
  - span relied on: “rabbits treated with sunitinib + ciprofloxacin had higher 24‐h CSF exposures (AUC 0–24 and C max ) compared to those that only received sunitinib (50.4 vs. 155 ng*h/mL and 4.2 vs. 18 ng/mL)”
  - read from: pmc_body / Sunitinib · **your verdict:** _______
- **CNS-085** · [PMID 22166826](https://pubmed.ncbi.nlm.nih.gov/22166826/) · `abstract_only` · `supporting` · number
  - > The chemotherapy (gemcitabine and cisplatin) and the molecular target therapy (sunitinib) were administerd but the primary lesion and metastases was progressive and serum G-CSF concentration was elevated to 229 pg/ml.
  - *[Granulocyte-colony-stimulating factor (G-CSF)-producing carcinoma of collecting ducts of Bellini: a case report].* — Hinyokika Kiyo 2011
  - **proposed: `unknown`** · basis `clinical_cns_response` · primary · human · arm `not_applicable` · none = nan · confidence high · weight **0.58**
  - rationale: No CNS tumor or CNS disease site described; this is a renal collecting-duct carcinoma with lymph node/lung metastases. No CSF/brain exposure data or CNS clinical response reported for sunitinib.
  - span relied on: “the primary lesion and metastases was progressive and serum G-CSF concentration was elevated to 229 pg/ml”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-086** · [PMID 26813470](https://pubmed.ncbi.nlm.nih.gov/26813470/) · `abstract_only` · `supporting` · number
  - > The concentrations of sunitinib and its active metabolite (SU12662) in the plasma, CSF, AH were measured with the validated HPLC-UV method.
  - *The influence of the time-of-day administration of sunitinib on the penetration through the blood-brain and blood-aqueous humour barriers in rabbits.* — Eur Rev Med Pharmacol Sci 2016
  - **proposed: `demonstrated`** · basis `measured_pk_animal` · primary · rabbit · arm `normal` · CSF AUC0-t (and CSF:plasma penetration ratio) = Cerebrospinal AUC0-t for sunitinib in groups I and II were 55.5 and 66.3 ng×h/mL, respectively; penetration through BBB <5% · confidence medium · weight **0.26** · **flagged for human check**
  - rationale: Primary measured CSF concentrations (AUC) in normal rabbits after oral dosing, a direct CNS exposure measurement; detectable but low penetration (<5%) is a demonstrated low-level CSF exposure, not exclusion below detection.
  - span relied on: “The cerebrospinal AUC0-t for sunitinib in groups I and II were 55.5 and 66.3 ng × h/mL, respectively... the degree of sunitinib penetration through the BAB and BBB was very low (< 5%) and comparable in both groups.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-087** · [PMID 26813470](https://pubmed.ncbi.nlm.nih.gov/26813470/) · `abstract_only` · `supporting` · number
  - > After the evening administration (8 p.m.) the exposure to sunitinib in the rabbits' plasma, AH and CSF was higher than after the morning administration (8 a.m.), but the degree of sunitinib penetration through the BAB and BBB was very low (< 5%) and comparable in both groups.
  - *The influence of the time-of-day administration of sunitinib on the penetration through the blood-brain and blood-aqueous humour barriers in rabbits.* — Eur Rev Med Pharmacol Sci 2016
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · rabbit · arm `normal` · CSF:plasma penetration ratio (AUC-based, % penetration through BBB) = degree of sunitinib penetration through the BAB and BBB was very low (< 5%); CSF AUC0-t 55.5 and 66.3 ng×h/mL vs plasma AUC0-t 2051.8 and 3069.3 ng×h/mL · confidence high · weight **0.31**
  - rationale: Primary measured PK in normal rabbits (no transporter manipulation) shows CSF exposure <5% of plasma, a low absolute ratio indicating exclusion from CSF compartment - contradicted for that compartment.
  - span relied on: “the degree of sunitinib penetration through the BAB and BBB was very low (< 5%) and comparable in both groups”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-088** · [PMID 20524040](https://pubmed.ncbi.nlm.nih.gov/20524040/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2997175/) · `abstract_only` · `supporting` · no number
  - > These results indicate that sunitinib may be an important pharmacologic agent for the treatment of invasive medulloblastoma, particularly given evidence of its ability to cross the blood-brain barrier to target tumor cells, and thus warrants further in vivo testing for confirmation of efficacy.
  - *Sunitinib induces PTEN expression and inhibits PDGFR signaling and migration of medulloblastoma cells.* — J Neurooncol 2010
  - **proposed: `unknown`** · basis `mechanistic_assertion` · restated · in_vitro · arm `not_applicable` · none = nan · confidence high · weight **0.03**
  - rationale: Entire paper is in vitro cell migration/signaling assays; BBB-crossing claim is an unsupported assertion citing outside evidence, with no measured CNS exposure data (CSF, brain, or tumour tissue concentration) presented here.
  - span relied on: “particularly given evidence of its ability to cross the blood-brain barrier to target tumor cells”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-089** · [PMID 22238213](https://pubmed.ncbi.nlm.nih.gov/22238213/) · `abstract_only` · `supporting` · no number
  - > Combined elacridar plus N-desethyl sunitinib treatment increased N-desethyl sunitinib plasma and brain exposures, but not brain-to-plasma ratios in wild-type mice.
  - *P-glycoprotein (ABCB1) and breast cancer resistance protein (ABCG2) restrict brain accumulation of the active sunitinib metabolite N-desethyl sunitinib.* — J Pharmacol Exp Ther 2012
  - **proposed: `unknown`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain accumulation / brain-to-plasma ratio = not quantified for sunitinib itself in this text; metabolite N-desethyl sunitinib brain accumulation 13.7-fold increased in Abcb1a/1b(-/-)/Abcg2(-/-) mice, unchanged ratio with elacridar in wild-type · confidence low · weight **0.33** · **flagged for human check**
  - rationale: This paper's measurements (brain accumulation, knockout fold-changes, elacridar effect on ratios) are reported for the metabolite N-desethyl sunitinib, not for sunitinib itself; only an indirect comparative mention of sunitinib brain accumulation exists, with no quantitative value given.
  - span relied on: “The effect of elacridar treatment in improving brain accumulation of N-desethyl sunitinib in wild-type mice was limited compared with its effect on sunitinib brain accumulation.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-090** · [PMID 24113148](https://pubmed.ncbi.nlm.nih.gov/24113148/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3836310/) · `abstract_only` · `supporting` · no number
  - > Overall, these findings indicate that there is a cooperation at the blood-brain barrier (BBB) in restricting the brain penetration of sunitinib, and brain delivery can be enhanced by administration of a dual inhibitor.
  - *Pharmacokinetic assessment of efflux transport in sunitinib distribution to the brain.* — J Pharmacol Exp Ther 2013
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma AUC ratio = brain-to-plasma ratio in wild-type mice (baseline, before elacridar) implied low; with elacridar in WT ≈12 vs ≈17.3 in Mdr1a/b(-/-)Bcrp1(-/-) mice · confidence medium · weight **0.46** · **flagged for human check**
  - rationale: Primary mouse PK shows efflux transporters (P-gp/Bcrp) restrict sunitinib brain penetration in normal (wild-type, uninhibited) BBB; elacridar-boosted or knockout values are transporter-inhibited/knockout arms, not patient exposure.
  - span relied on: “The brain-to-plasma ratio after coadministration of elacridar in wild-type mice was ≈ 12 compared with ≈ 17.3 in Mdr1a/b(-/-)Bcrp1(-/-) mice. Overall, these findings indicate that there is a cooperation at the blood-brain barrier (BBB) in restricting the brain penetration of sunitinib”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-091** · [PMID 26813470](https://pubmed.ncbi.nlm.nih.gov/26813470/) · `abstract_only` · `supporting` · no number
  - > Therefore, the penetration of sunitinib through the blood-brain barrier (BBB) and blood-aqueous humour barrier (BAB) is an issue of growing interest.
  - *The influence of the time-of-day administration of sunitinib on the penetration through the blood-brain and blood-aqueous humour barriers in rabbits.* — Eur Rev Med Pharmacol Sci 2016
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · rabbit · arm `normal` · CSF AUC relative to plasma AUC (penetration ratio) = cerebrospinal AUC0-t 55.5 and 66.3 ng×h/mL vs plasma AUC0-t 2051.8 and 3069.3 ng×h/mL; degree of sunitinib penetration through the BBB was very low (<5%) · confidence high · weight **0.31**
  - rationale: Primary measured PK in normal (non-tumour) rabbits shows CSF exposure <5% of plasma, a low absolute penetration ratio, meeting the contradicted criterion for the CSF compartment.
  - span relied on: “the degree of sunitinib penetration through the BAB and BBB was very low (< 5%) and comparable in both groups”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-092** · [PMID 26813470](https://pubmed.ncbi.nlm.nih.gov/26813470/) · `abstract_only` · `supporting` · no number
  - > The aim of the study was to investigate the influence of the time-of-day administration on the penetration of sunitinib into the cerebrospinal fluid (CSF) and aqueous humour (AH).
  - *The influence of the time-of-day administration of sunitinib on the penetration through the blood-brain and blood-aqueous humour barriers in rabbits.* — Eur Rev Med Pharmacol Sci 2016
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · rabbit · arm `normal` · CSF AUC0-t and CSF:plasma penetration percentage = cerebrospinal AUC0-t 55.5 and 66.3 ng×h/mL vs plasma AUC0-t 2051.8 and 3069.3 ng×h/mL; penetration through BBB <5% · confidence high · weight **0.31**
  - rationale: Primary measured PK in normal (non-knockout, non-BBB-disrupting) rabbits shows CSF exposure is less than 5% of plasma exposure, a low absolute ratio indicating exclusion from CSF.
  - span relied on: “The cerebrospinal AUC0-t for sunitinib in groups I and II were 55.5 and 66.3 ng × h/mL, respectively... the degree of sunitinib penetration through the BAB and BBB was very low (< 5%) and comparable in both groups.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### TIVOZANIB

1 attributed of 2 retrieved sentences · 0 full text, 1 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_record` · CNS-manifestation trial evidence on 0 drug rows

**Evidence score: `contradicted`** (resolved) — best supporting claim 0.0, best contradicting 0.545, direction -1.0. best claim 0.55, direction -1.00. Corroboration: 0.545 total weight across 1 claims (does not set the band). Heaviest claims: CNS-093 (0.55).

**Proposed drug verdict: `contradicted`** — 1 primary mouse claim(s), all contradicted. Decisive claim(s): CNS-093.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-093** · [PMID 32234426](https://pubmed.ncbi.nlm.nih.gov/32234426/) · `abstract_only` · `limiting` · no number
  - > The modest effect of ABC transporters on tivozanib brain accumulation, if also true in humans, might mean that this drug is not strongly limited in its therapeutic efficacy against malignant lesions situated partly or completely behind the blood-brain barrier.
  - *Brain accumulation of tivozanib is restricted by ABCB1 (P-glycoprotein) and ABCG2 (breast cancer resistance protein) in mice.* — Int J Pharm 2020
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio = brain-to-plasma ratios significantly increased in Abcb1a/1b-/- (2.2-fold) and Abcb1a/1b;Abcg2-/- (2.6-fold) mice compared to wild-type mice · confidence high · weight **0.55**
  - rationale: Wild-type mice show much lower brain-to-plasma ratio than knockouts, indicating restricted normal-brain accumulation in the normal (non-knockout) arm; matched sentence itself is only a speculative restatement.
  - span relied on: “The brain-to-plasma ratios were significantly increased in Abcb1a/1b -/- (2.2-fold) and Abcb1a/1b;Abcg2 -/- (2.6-fold) mice compared to wild-type mice, indicating a modest protective role of these transporters in the blood-brain barrier.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### TOVORAFENIB

3 attributed of 4 retrieved sentences · 1 full text, 2 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 7 drug rows

**Evidence score: `unknown`** (below_peak_threshold) — best supporting claim 0.0, best contradicting 0.463, direction -1.0. best claim weighs 0.46, below 0.5; unassessed. Corroboration: 0.463 total weight across 3 claims (does not set the band). Heaviest claims: CNS-095 (0.46), CNS-094 (0.03), CNS-096 (0.02).

**Proposed drug verdict: `contradicted`** — 1 primary mouse claim(s), all contradicted. Decisive claim(s): CNS-095.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-094** · [PMID 38291372](https://pubmed.ncbi.nlm.nih.gov/38291372/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10826080/) · `full_text` · `supporting` · no number
  - > Finally, tovorafenib had greater CNS penetration compared with the type I RAF inhibitor dabrafenib [].
  - *LOGGIC/FIREFLY-2: a phase 3, randomized trial of tovorafenib vs. chemotherapy in pediatric and young adult patients with newly diagnosed low-grade glioma harboring an activating RAF alteration.* — BMC Cancer 2024
  - **proposed: `unknown`** · basis `review_restatement` · restated · na · arm `not_applicable` · none = nan · confidence low · weight **0.03**
  - rationale: Background-section assertion citing another reference [32], no exposure values (CSF/brain concentration, Kp,uu) reported in this text; a comparative claim without measurement data, restating prior work.
  - span relied on: “tovorafenib had greater CNS penetration compared with the type I RAF inhibitor dabrafenib”
  - read from: pmc_body / Background · **your verdict:** _______
- **CNS-095** · [PMID 30622172](https://pubmed.ncbi.nlm.nih.gov/30622172/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6374543/) · `abstract_only` · `supporting` · number
  - > The purpose of this study was to perform a quantitative assessment and evaluation of the influence of efflux mechanisms at the blood-brain barrier (BBB), in particular, Abcb1/P-glycoprotein (P-gp) and Abcg2/breast cancer resistance protein (Bcrp), on the brain distribution of three panRAF inhibitors: CCT196969 [1-(3-(-butyl)-1-phenyl-1-pyrazol-5-yl)-3-(2-fluoro-4-((3-oxo-3,4-dihydropyrido[2,3-b]pyrazin-8-yl)oxy)phenyl)urea], LY3009120 1-(3,3-Dimethylbutyl)-3-(2-fluoro-4-methyl-5-(7-methyl-2-(methylamino)pyrido(2,3-d)pyrimidin-6-yl)phenyl)urea, and MLN2480 [4-pyrimidinecarboxamide, 6-amino-5-chloro--[(1)-1-[5-[[[5-chloro-4-(trifluoromethyl)-2-pyridinyl]amino]carbonyl]-2-thiazolyl]ethyl]-].
  - *Brain Distribution and Active Efflux of Three panRAF Inhibitors: Considerations in the Treatment of Melanoma Brain Metastases.* — J Pharmacol Exp Ther 2019
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain distribution = limited; enhanced in transgenic mice lacking P-gp and Bcrp · confidence medium · weight **0.46** · **flagged for human check**
  - rationale: MLN2480 (tovorafenib/DAY101) brain distribution is reported as limited in wild-type mice, with enhancement only in P-gp/Bcrp knockout mice - the normal-arm finding is the contradicted exposure.
  - span relied on: “In vivo studies in mice show that the brain distribution of CCT196969, LY3009120, and MLN2480 is limited, and is enhanced in transgenic mice lacking P-gp and Bcrp.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-096** · [PMID 38884947](https://pubmed.ncbi.nlm.nih.gov/38884947/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11404696/) · `abstract_only` · `supporting` · no number
  - > The advent of pan-RAF inhibitors, notably Tovorafenib, offers a promising advance, demonstrating enhanced efficacy and better penetration of the blood-brain barrier, without the issue of paradoxical activation.
  - *A critical review of RAF inhibitors in BRAF-mutated glioma treatment.* — Pharmacogenomics 2024
  - **proposed: `unknown`** · basis `review_restatement` · restated · na · arm `not_applicable` · none = nan · confidence low · weight **0.02**
  - rationale: This is a narrative review abstract making an unsupported assertion about BBB penetration with no exposure quantity (CSF/brain concentration, Kp,uu, ratio) reported anywhere in the supplied text.
  - span relied on: “demonstrating enhanced efficacy and better penetration of the blood-brain barrier”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### TRAMETINIB

2 attributed of 13 retrieved sentences · 0 full text, 2 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_label_found;no_statement` · CNS-manifestation trial evidence on 2 drug rows

**Evidence score: `contradicted`** (resolved) — best supporting claim 0.0, best contradicting 0.545, direction -1.0. best claim 0.55, direction -1.00. Corroboration: 0.545 total weight across 2 claims (does not set the band). Heaviest claims: CNS-097 (0.55), CNS-098 (0.16).

**Proposed drug verdict: `contradicted`** — 1 primary mouse claim(s), all contradicted. Decisive claim(s): CNS-097.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-097** · [PMID 24875464](https://pubmed.ncbi.nlm.nih.gov/24875464/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4109207/) · `abstract_only` · `supporting` · no number
  - > In vitro studies indicated that trametinib is a substrate for both P-glycoprotein (P-gp) and Bcrp, efflux transporters found at the blood-brain barrier.
  - *Factors influencing the CNS distribution of a novel MEK-1/2 inhibitor: implications for combination therapy for melanoma brain metastases.* — Drug Metab Dispos 2014
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma partition coefficient (AUCbrain/AUCplasma) = approximately 5-fold higher in Mdr1a/b(-/-) and triple knockout mice when compared with wild-type and Bcrp1(-/-) mice · confidence high · weight **0.55**
  - rationale: Matched sentence is an in-vitro assertion, but surrounding text gives primary wild-type mouse PK: brain distribution restricted, ~5x lower than in P-gp knockout, showing efflux-limited normal brain exposure in the normal (wild-type) arm.
  - span relied on: “The brain distribution of trametinib was similar between the wild-type and Bcrp knockout mice.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-098** · [PMID 31063549](https://pubmed.ncbi.nlm.nih.gov/31063549/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7571492/) · `abstract_only` · `supporting` · no number
  - > In vivo, PK analysis revealed enhanced blood-brain barrier penetration of trametinib after oHSV treatment.
  - *Oncolytic HSV therapy increases trametinib access to brain tumors and sensitizes them in vivo.* — Neuro Oncol 2019
  - **proposed: `unknown`** · basis `measured_pk_animal` · primary · mouse · arm `bbb_modifying_cointervention` · brain-blood barrier penetration (unspecified exposure metric) = nan · confidence medium · weight **0.16** · **flagged for human check**
  - rationale: The measured PK increase in brain penetration is attributed to oHSV co-treatment (a BBB-modifying cointervention), not trametinib's intrinsic CNS access; no baseline/untreated exposure value given, so it does not show trametinib alone reaches CNS.
  - span relied on: “In vivo, PK analysis revealed enhanced blood-brain barrier penetration of trametinib after oHSV treatment.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______

### VEMURAFENIB

26 attributed of 42 retrieved sentences · 14 full text, 12 abstract-only · ChEMBL calculated flag: `predicted_non_permeant` · openFDA label: `no_statement` · CNS-manifestation trial evidence on 0 drug rows

**Evidence score: `contradicted`** (resolved_within_compartment) — best supporting claim 0.608, best contradicting 0.807, direction -0.248. single compartment class resolves to contradicted; whole-drug best claims had looked contested. Corroboration: 9.999 total weight across 26 claims (does not set the band). Heaviest claims: CNS-124 (0.81), CNS-123 (0.81), CNS-118 (0.81).

**Proposed drug verdict: `contradicted`** — 4 primary human claim(s), all contradicted. Decisive claim(s): CNS-117, CNS-118, CNS-123, CNS-124.

**Your drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______

- **CNS-099** · [PMID 26579371](https://pubmed.ncbi.nlm.nih.gov/26579371/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4590304/) · `full_text` · `supporting` · number
  - > Furthermore, in their knockout mouse model, the brain-to-plasma ratios of vemurafenib were increased significantly when Abc1a/1b and Abcg2 were both absent.
  - *The pharmacological impact of ATP-binding cassette drug transporters on vemurafenib-based therapy.* — Acta Pharm Sin B 2014
  - **proposed: `unknown`** · basis `review_restatement` · restated · mouse · arm `transporter_knockout_or_inhibitor` · brain-to-plasma ratio = increased significantly when Abc1a/1b and Abcg2 were both absent · confidence high · weight **0.04**
  - rationale: This Review restates another group's (Mohammed et al.) knockout-mouse PK finding; the ratio increase occurred only in the Abcb1a/1b;Abcg2-null arm, not wild-type, so it describes transporter effect, not patient-relevant exposure.
  - span relied on: “in their knockout mouse model, the brain-to-plasma ratios of vemurafenib were increased significantly when Abc1a/1b and Abcg2 were both absent”
  - read from: pmc_body / The pharmacological impact of ABC drug transporters on the bioavailability and distribution of vemurafenib · **your verdict:** _______
- **CNS-100** · [PMID 26579371](https://pubmed.ncbi.nlm.nih.gov/26579371/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4590304/) · `full_text` · `supporting` · number
  - > Durmus et al.reported that inhibition of both ABCB1 and ABCG2 could significantly improve the bioavailability (A) and brain penetration (B) of vemurafenib.
  - *The pharmacological impact of ATP-binding cassette drug transporters on vemurafenib-based therapy.* — Acta Pharm Sin B 2014
  - **proposed: `contradicted`** · basis `measured_pk_animal` · restated · mouse · arm `transporter_knockout_or_inhibitor` · brain accumulation / brain-to-plasma (WT vs knockout/inhibitor) = elacridar elevated plasma and brain accumulation in WT mice to the same levels as in Abc1a/1b-/-;Abcg2-/- mice · confidence high · weight **0.11**
  - rationale: Matched sentence is a restatement of Durmus et al.; surrounding text shows normal (WT) vemurafenib brain accumulation is low, only raised by knockout/inhibitor, indicating exclusion from normal brain under native transporter activity.
  - span relied on: “In vivo, the dual Abcb1a/1b and Abcg2 inhibitor elacridar significantly elevated the plasma levels of vemurafenib and brain accumulation in WT mice to the same levels as in Abc1a/1b−/−;Abcg2−/− mice.”
  - read from: pmc_body / The pharmacological impact of ABC drug transporters on the bioavailability and distribution of vemurafenib · **your verdict:** _______
- **CNS-101** · [PMID 26579371](https://pubmed.ncbi.nlm.nih.gov/26579371/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4590304/) · `full_text` · `supporting` · number
  - > The clinical application of a dual ABCB1 and ABCG2 inhibitor such as elacridar could possibly provide a solution to increase the oral bioavailability and enhance brain penetration of vemurafenib in patients with brain metastatic melanoma.
  - *The pharmacological impact of ATP-binding cassette drug transporters on vemurafenib-based therapy.* — Acta Pharm Sin B 2014
  - **proposed: `unknown`** · basis `review_restatement` · restated · na · arm `not_applicable` · none = nan · confidence low · weight **0.03**
  - rationale: This is a Conclusions-section review assertion/prediction with no exposure numbers reported; it proposes elacridar co-administration as a future possible solution, not a measured PK finding.
  - span relied on: “the actions of ABCB1 and ABCG2 in the GI tract and at the BBB contribute significantly to reduced oral bioavailability and limit the penetration of the brain by vemurafenib”
  - read from: pmc_body / Conclusions · **your verdict:** _______
- **CNS-102** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > These observations seem to be corroborated by a clinical study showing that the concentration of vemurafenib in cerebrospinal fluid (CSF) was < 1% of the plasma concentration [].
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `contradicted`** · basis `review_restatement` · restated · human · arm `normal` · CSF:plasma concentration ratio = < 1% of the plasma concentration · confidence medium · weight **0.09** · **flagged for human check**
  - rationale: This FEBS Open Bio paper restates a cited clinical study's finding that vemurafenib CSF concentration was <1% of plasma, a low absolute CSF:plasma ratio indicating exclusion from CSF in human patients (normal, non-transporter-modified setting).
  - span relied on: “the concentration of vemurafenib in cerebrospinal fluid (CSF) was < 1% of the plasma concentration”
  - read from: pmc_body / (untitled section) · **your verdict:** _______
- **CNS-103** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > Vemurafenib has intrinsic antitumor potential against intracranial A375 tumors The brain penetration of vemurafenib was previously reported to be significantly higher (between approximately 20‐ and 80‐fold) incompared with WT mice [,].
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `contradicted`** · basis `measured_pk_animal` · restated · mouse · arm `transporter_knockout_or_inhibitor` · brain:plasma (brain penetration fold-difference) = between approximately 20- and 80-fold higher in Abcb1a/b;Abcg2 -/- compared with WT mice · confidence medium · weight **0.09** · **flagged for human check**
  - rationale: This is a restated prior finding (citations 18,19) that vemurafenib brain penetration is 20-80x higher only in transporter-knockout mice vs WT, meaning WT (normal) brain exposure is low - a transporter-driven exclusion finding, not demonstrated CNS delivery.
  - span relied on: “The brain penetration of vemurafenib was previously reported to be significantly higher (between approximately 20‐ and 80‐fold) in Abcb1a/b;Abcg2 −/− compared with WT mice”
  - read from: pmc_body / Vemurafenib has intrinsic antitumor potential against intracranial A375 tumors · **your verdict:** _______
- **CNS-104** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > Vemurafenib penetration into subcutaneous tumors is similar in WT andmice and as we found that vemurafenib was equally effective (Fig.) and did not result in body weight loss (Fig.), we selected these dose regimens for the efficacy study against intracranial A375 tumors.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `unknown`** · basis `measured_pk_animal` · primary · mouse · arm `transporter_knockout_or_inhibitor` · subcutaneous tumor penetration (dose-leveled comparison between WT and knockout) = Vemurafenib penetration into subcutaneous tumors is similar in WT and Abcb1a/b;Abcg2 −/− mice · confidence medium · weight **0.23** · **flagged for human check**
  - rationale: Measurement is in subcutaneous tumor, not CNS, and is a cross-strain dose-leveling comparison, not CNS exposure data. No CSF/brain/intracranial-tumor concentration reported here for vemurafenib.
  - span relied on: “Vemurafenib penetration into subcutaneous tumors is similar in WT andmice and as we found that vemurafenib was equally effective (Fig.) and did not result in body weight loss (Fig.), we selected these dose regimens for the efficacy study against intracranial A375 tumors.”
  - read from: pmc_body / Dose adaptions between WT and Abcb1a/b;Abcg2 −/− mice are needed to level the systemic exposure of vemurafenib between strains · **your verdict:** _______
- **CNS-105** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > These drug distribution data are in line with the observed intracranial antitumor efficacy (Fig.), as vemurafenib tumor concentrations were similar between WT mice receiving 25 mg·kgand WT mice receiving 10 mg·kgof vemurafenib with concomitant elacridar, but lower than inmice receiving 10 or 25 mg·kgvemurafenib.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `demonstrated`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · tumour tissue concentration (brain metastasis tumor core) = Vemurafenib penetrated into the tumor core in WT mice, but the levels were approximately half of those achieved in Abcb1a/b;Abcg2 −/− mice · confidence high · weight **0.61**
  - rationale: WT (normal, non-knockout) mice show measurable vemurafenib penetration into the brain metastasis tumor core, a disrupted-BBB CNS compartment, distinct from the negligible normal-brain penetration also reported.
  - span relied on: “Vemurafenib penetrated into the tumor core in WT mice, but the levels were approximately half of those achieved in Abcb1a/b;Abcg2 −/− mice.”
  - read from: pmc_body / P‐gp and BCRP reduce vemurafenib penetration in MBMs · **your verdict:** _______
- **CNS-106** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > Intracranial A375 tumors develop therapy resistance despite sufficient vemurafenib tumor penetration and target inhibition As mentioned above, the A375 MBM model is responsive to vemurafenib, but developed therapy resistance after just a few days of treatment inmice receiving 10 mg·kgvemurafenib (Fig.).
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `demonstrated`** · basis `measured_pk_animal` · primary · mouse · arm `transporter_knockout_or_inhibitor` · tumour and brain region vemurafenib concentration = vemurafenib concentrations in various brain regions... were not different in Abcb1a/b;Abcg2-/- mice and WT mice also receiving elacridar; tumor concentration was even higher at the later time point · confidence medium · weight **0.23** · **flagged for human check**
  - rationale: Measured tumour/brain region vemurafenib concentrations demonstrate penetration into intracranial tumour tissue; levels were similar between Abcb1a/b;Abcg2-/- and WT+elacridar arms, indicating P-gp/BCRP are not limiting tumour exposure, consistent with the section title's claim.
  - span relied on: “the vemurafenib concentrations in various brain regions in tumor‐bearing mice treated for a short (5 days) or long (10 days) period were not different in Abcb1a/b;Abcg2 −/− mice and WT mice also receiving elacridar (Fig. 4A–D ). In fact, in contrast to the observed antitumor efficacy at 5 and 10 days of treatment (Fig. 2E ), the vemurafenib concentration in the tumor regions of these mice was even higher at the later time point (Fig. 4E ).”
  - read from: pmc_body / Intracranial A375 tumors develop therapy resistance despite sufficient vemurafenib tumor penetration and target inhibition · **your verdict:** _______
- **CNS-107** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > Since the vemurafenib concentration in responsive short‐term (5 days) treated tumors and resistant long‐term (10 days) treated tumors was similar, we explored alternative ways by which intracranial A375 tumor may acquire resistance in a small pilot cohort we had available for immunohistochemical analysis (= 2 per group).
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `demonstrated`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · vemurafenib tumor concentration = similar concentration in short-term (5 day) and long-term (10 day) treated intracranial tumors · confidence high · weight **0.61**
  - rationale: Measured vemurafenib concentration directly in intracranial A375 tumor tissue in mice, consistent with the section title noting "sufficient vemurafenib tumor penetration." This is a primary measured exposure in tumour tissue, not normal brain/CSF.
  - span relied on: “the vemurafenib concentration in responsive short‐term (5 days) treated tumors and resistant long‐term (10 days) treated tumors was similar”
  - read from: pmc_body / Intracranial A375 tumors develop therapy resistance despite sufficient vemurafenib tumor penetration and target inhibition · **your verdict:** _______
- **CNS-108** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · number
  - > 4 Vemurafenib concentrations in short‐term and long‐term treated intracranial A375 tumors.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `demonstrated`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · tumour tissue concentration / tissue-plasma ratio = levels approximately half of those achieved in Abcb1a/b;Abcg2-/- mice · confidence high · weight **0.61**
  - rationale: In wild-type mice (normal arm, no transporter knockout/inhibitor), vemurafenib measurably penetrated intracranial tumor tissue, demonstrating CNS tumour exposure despite reduced levels vs knockout arm; normal brain was separately negligible.
  - span relied on: “Vemurafenib penetrated into the tumor core in WT mice, but the levels were approximately half of those achieved in Abcb1a/b;Abcg2 −/− mice.”
  - read from: pmc_body / P‐gp and BCRP reduce vemurafenib penetration in MBMs · **your verdict:** _______
- **CNS-109** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · no number
  - > Several preclinical studies have demonstrated that vemurafenib [,], dabrafenib [], and encorafenib [] exhibit very poor brain penetration in mice as a result of efficient efflux by P‐glycoprotein (P‐gp;
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `contradicted`** · basis `measured_pk_human` · restated · human · arm `normal` · CSF:plasma concentration ratio = < 1% · confidence high · weight **0.35** · **flagged for human check**
  - rationale: Surrounding text cites a clinical (human) PK study reporting vemurafenib CSF concentration <1% of plasma, a clearly low ratio indicating CNS exclusion from CSF, though this is a restatement of another paper's finding.
  - span relied on: “a clinical study showing that the concentration of vemurafenib in cerebrospinal fluid (CSF) was < 1% of the plasma concentration”
  - read from: pmc_body / (untitled section) · **your verdict:** _______
- **CNS-110** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · no number
  - > Therefore, P‐gp/BCRP inhibitors might help to improve the clinical response of MBMs to vemurafenib by increasing its brain penetration, but pinpointing the mechanism behind the brain‐specific acquired resistance will likely be necessary to produce durable responses.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `demonstrated`** · basis `preclinical_cns_efficacy` · primary · mouse · arm `normal` · intracranial antitumor efficacy / clinical response of brain metastases = MBMs can respond to vemurafenib, most likely as a result of compromised BBB integrity · confidence medium · weight **0.34** · **flagged for human check**
  - rationale: Text shows vemurafenib produces antitumor response in intracranial brain metastases in normal (WT) mice at compromised BBB, demonstrating tumour-tissue exposure/activity; KO/elacridar arms show transporter effect, not baseline exposure.
  - span relied on: “we find that MBMs can respond to vemurafenib, most likely as a result of compromised BBB integrity”
  - read from: pmc_body / (untitled section) · **your verdict:** _______
- **CNS-111** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · no number
  - > Dose adaptions between WT andmice are needed to level the systemic exposure of vemurafenib between strains The aim of this study was to assess the impact of P‐gp and BCRP at the BBB on the intracranial efficacy of vemurafenib against MBMs by comparing WT andmice.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `unknown`** · basis `design_or_prediction` · primary · mouse · arm `transporter_knockout_or_inhibitor` · plasma AUC = plasma AUC significantly higher in Abcb1a/b;Abcg2 −/− mice compared with WT mice receiving the same dose · confidence high · weight **0.06**
  - rationale: This passage only reports plasma pharmacokinetics (dose-leveling exercise) in WT vs knockout mice, not any CNS/brain/CSF/tumour exposure measurement for vemurafenib, so no CNS-delivery verdict is supported.
  - span relied on: “Similar to earlier studies, the plasma area under the curve (AUC) was significantly higher in Abcb1a/b;Abcg2 −/− mice compared with WT mice receiving the same dose (Table 1 ).”
  - read from: pmc_body / Dose adaptions between WT and Abcb1a/b;Abcg2 −/− mice are needed to level the systemic exposure of vemurafenib between strains · **your verdict:** _______
- **CNS-112** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `full_text` · `supporting` · no number
  - > P‐gp and BCRP reduce vemurafenib penetration in MBMs P‐gp and BCRP limit the brain penetration of vemurafenib by virtue of their efflux function at the BBB [,].
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `unknown`** · basis `mechanistic_assertion` · restated · mouse · arm `unclear` · none = nan · confidence medium · weight **0.04** · **flagged for human check**
  - rationale: Matched sentence cites prior references (18,19), a restated mechanistic claim with no exposure numbers. Surrounding text describes plasma concentrations and clearance induction, not a brain:plasma or CSF ratio value.
  - span relied on: “P‐gp and BCRP limit the brain penetration of vemurafenib by virtue of their efflux function at the BBB [ 18 , 19 ].”
  - read from: pmc_body / P‐gp and BCRP reduce vemurafenib penetration in MBMs · **your verdict:** _______
- **CNS-113** · [PMID 22454535](https://pubmed.ncbi.nlm.nih.gov/22454535/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3383040/) · `abstract_only` · `supporting` · number
  - > The steady-state brain-to-plasma ratio of vemurafenib was 0.035 ± 0.009 in Mdr1a/b(-/-) mice, 0.009 ± 0.006 in Bcrp1(-/-) mice, and 1.00 ± 0.19 in Mdr1a/b(-/-)Bcrp1(-/-) mice compared with 0.012 ± 0.004 in wild-type mice.
  - *Impact of P-glycoprotein (ABCB1) and breast cancer resistance protein (ABCG2) on the brain distribution of a novel BRAF inhibitor: vemurafenib (PLX4032).* — J Pharmacol Exp Ther 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio = 0.012 ± 0.004 in wild-type mice (brain distribution coefficient 0.004 in wild-type mice) · confidence high · weight **0.55**
  - rationale: Wild-type (normal) mouse brain-to-plasma ratio is low (0.012, and AUC-based coefficient 0.004), indicating restricted CNS penetration via P-gp/BCRP efflux; knockout arms show transporter-dependent increase, not patient-relevant exposure.
  - span relied on: “compared with 0.012 ± 0.004 in wild-type mice”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-114** · [PMID 23020847](https://pubmed.ncbi.nlm.nih.gov/23020847/) · `abstract_only` · `supporting` · number
  - > We aimed to establish whether oral availability and brain penetration of vemurafenib could be restricted by the multidrug efflux transporters P-glycoprotein (P-gp/ABCB1) and breast cancer resistance protein (BCRP/ABCG2), as these might limit therapeutic efficacy, especially against brain metastases.
  - *Oral availability and brain penetration of the B-RAFV600E inhibitor vemurafenib can be enhanced by the P-GLYCOprotein (ABCB1) and breast cancer resistance protein (ABCG2) inhibitor elacridar.* — Mol Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio = Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice · confidence high · weight **0.55**
  - rationale: Wild-type-arm brain-to-plasma ratio is low (baseline, not increased); high ratio only appears in double-knockout mice, describing transporter effect not patient-relevant exposure - WT data support exclusion from normal brain.
  - span relied on: “Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice, indicating pronounced overlapping functions of these transporters in reducing vemurafenib brain accumulation.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-115** · [PMID 23020847](https://pubmed.ncbi.nlm.nih.gov/23020847/) · `abstract_only` · `supporting` · number
  - > Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice, indicating pronounced overlapping functions of these transporters in reducing vemurafenib brain accumulation.
  - *Oral availability and brain penetration of the B-RAFV600E inhibitor vemurafenib can be enhanced by the P-GLYCOprotein (ABCB1) and breast cancer resistance protein (ABCG2) inhibitor elacridar.* — Mol Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio = Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice · confidence high · weight **0.55**
  - rationale: In wild-type (normal) mice, vemurafenib brain accumulation is low; only double-knockout of Abcb1a/1b and Abcg2 restores it 21.4-fold, showing active efflux excludes drug from brain under normal transporter conditions.
  - span relied on: “Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice, indicating pronounced overlapping functions of these transporters in reducing vemurafenib brain accumulation.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-116** · [PMID 23020847](https://pubmed.ncbi.nlm.nih.gov/23020847/) · `abstract_only` · `supporting` · number
  - > As predicted by previously described pharmacokinetic modeling, halving the amount of active efflux transport at the WT blood-brain barrier by testing heterozygous Abcb1a/1b(+/-);Abcg2(+/-) mice had little impact on vemurafenib brain accumulation.
  - *Oral availability and brain penetration of the B-RAFV600E inhibitor vemurafenib can be enhanced by the P-GLYCOprotein (ABCB1) and breast cancer resistance protein (ABCG2) inhibitor elacridar.* — Mol Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio = Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice · confidence high · weight **0.55**
  - rationale: WT-arm brain-to-plasma ratio is low and only rises massively in double-knockout mice, showing efflux transporters normally exclude vemurafenib from brain; matched sentence (het mice) itself shows little change, consistent with exclusion in normal animals.
  - span relied on: “Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice, indicating pronounced overlapping functions of these transporters in reducing vemurafenib brain accumulation.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-117** · [PMID 25933211](https://pubmed.ncbi.nlm.nih.gov/25933211/) · `abstract_only` · `limiting` · number
  - > In conclusion, our preliminary results highlight for the first time a low CSF vemurafenib penetration rate associated with a large interindividual variability in patients treated for metastatic BRAF-V600 mutated melanoma and brain metastases.
  - *Cerebrospinal fluid concentrations of vemurafenib in patients treated for brain metastatic BRAF-V600 mutated melanoma.* — Melanoma Res 2015
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF:plasma concentration ratio = 0.98±0.84% · confidence high · weight **0.81**
  - rationale: Primary human PK measurement in patients on standard dosing shows CSF:plasma ratio ~1%, explicitly described as low penetration, consistent with CNS exclusion from CSF.
  - span relied on: “The mean ratio of the CSF : plasma concentration was 0.98±0.84%. ... a low CSF vemurafenib penetration rate”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-118** · [PMID 25933211](https://pubmed.ncbi.nlm.nih.gov/25933211/) · `abstract_only` · `supporting` · number
  - > The mean plasma and CSF concentrations of vemurafenib were 53.4±26.2 and 0.47±0.37 mg/l, respectively.
  - *Cerebrospinal fluid concentrations of vemurafenib in patients treated for brain metastatic BRAF-V600 mutated melanoma.* — Melanoma Res 2015
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF:plasma concentration ratio = CSF 0.47±0.37 mg/l vs plasma 53.4±26.2 mg/l; mean CSF:plasma ratio 0.98±0.84% · confidence high · weight **0.81**
  - rationale: Primary human PK measurement in patients shows CSF concentration ~1% of plasma, explicitly described as low penetration rate; direct measured exposure data in CSF compartment, not tumor tissue.
  - span relied on: “The mean plasma and CSF concentrations of vemurafenib were 53.4±26.2 and 0.47±0.37 mg/l, respectively. The mean ratio of the CSF : plasma concentration was 0.98±0.84%... a low CSF vemurafenib penetration rate”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-119** · [PMID 37953496](https://pubmed.ncbi.nlm.nih.gov/37953496/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10761933/) · `abstract_only` · `supporting` · number
  - > We intracranially implanted A375 melanoma cells in wild-type (WT) and Abcb1a/b;Abcg2mice, characterized the tumor BBB, analyzed drug levels in plasma and brain lesions after oral vemurafenib administration, and determined the efficacy against brain metastases and subcutaneous lesions.
  - *Acquired and intrinsic resistance to vemurafenib in BRAF-driven melanoma brain metastases.* — FEBS Open Bio 2023
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain lesion (tumour) drug concentration / vemurafenib penetration into MBM = vemurafenib achieved greater antitumor efficacy against MBMs in Abcb1a/b;Abcg2 -/- mice compared with WT mice; expression of these transporters limited vemurafenib penetration into A375 MBMs · confidence medium · weight **0.46** · **flagged for human check**
  - rationale: In WT (normal transporter) mice, P-gp/BCRP limited vemurafenib penetration into brain metastases versus knockout mice; this is a measured PK finding showing exclusion in the tumour compartment under normal transporter arm.
  - span relied on: “P-gp and BCRP are expressed in MBM-associated brain endothelium both in patients and in A375 xenografts and expression of these transporters limited vemurafenib penetration into A375 MBMs”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-120** · [PMID 41097037](https://pubmed.ncbi.nlm.nih.gov/41097037/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12524707/) · `abstract_only` · `supporting` · number
  - > Further ranking according to their blood-brain barrier permeability, as well as structural and transcriptomic similarities to known anti-GBM drugs, revealed SP600125, vemurafenib, FG-7142, dibenzoylmethane, and phensuximide as the most promising for GMT inhibition.
  - *Transcriptomic-Driven Drug Repurposing Reveals SP600125 as a Promising Drug Candidate for the Treatment of Glial-Mesenchymal Transition in Glioblastoma.* — Int J Mol Sci 2025
  - **proposed: `unknown`** · basis `design_or_prediction` · primary · na · arm `not_applicable` · none = nan · confidence high · weight **0.07**
  - rationale: This is an in-silico ranking by predicted BBB permeability, not a measured exposure value. No PK data, CSF/brain concentration, or clinical CNS activity for vemurafenib is reported.
  - span relied on: “Further ranking according to their blood-brain barrier permeability, as well as structural and transcriptomic similarities to known anti-GBM drugs, revealed SP600125, vemurafenib, FG-7142, dibenzoylmethane, and phensuximide as the most promising for GMT inhibition.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-121** · [PMID 22454535](https://pubmed.ncbi.nlm.nih.gov/22454535/) · [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3383040/) · `abstract_only` · `limiting` · no number
  - > These data indicate that the brain distribution of vemurafenib is severely restricted at the blood-brain barrier because of active efflux by both P-gp and BCRP.
  - *Impact of P-glycoprotein (ABCB1) and breast cancer resistance protein (ABCG2) on the brain distribution of a novel BRAF inhibitor: vemurafenib (PLX4032).* — J Pharmacol Exp Ther 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain-to-plasma ratio (AUC brain/AUC plasma) = 0.004 (brain distribution coefficient) / 0.012 ± 0.004 steady-state brain-to-plasma ratio in wild-type mice · confidence high · weight **0.55**
  - rationale: Wild-type mouse brain:plasma ratios (0.004 and 0.012) are very low, indicating restricted CNS penetration in the normal (non-knockout) arm; knockout/inhibitor values are transporter characterization, not patient-relevant exposure.
  - span relied on: “the brain distribution coefficient ... of vemurafenib was 0.004 in wild-type mice ... compared with 0.012 ± 0.004 in wild-type mice”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-122** · [PMID 23020847](https://pubmed.ncbi.nlm.nih.gov/23020847/) · `abstract_only` · `supporting` · no number
  - > Our data suggest that elacridar coadministration may be considered to improve the therapeutic efficacy of vemurafenib, especially for brain metastases located behind a functional blood-brain barrier.
  - *Oral availability and brain penetration of the B-RAFV600E inhibitor vemurafenib can be enhanced by the P-GLYCOprotein (ABCB1) and breast cancer resistance protein (ABCG2) inhibitor elacridar.* — Mol Pharm 2012
  - **proposed: `contradicted`** · basis `measured_pk_animal` · primary · mouse · arm `normal` · brain:plasma ratio = Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice · confidence high · weight **0.55**
  - rationale: Wild-type mice (normal arm) show low brain accumulation of vemurafenib, restricted by Abcb1/Abcg2; high ratios only occur in double-knockout mice, which describes transporter function, not patient exposure.
  - span relied on: “Brain-to-plasma ratios of vemurafenib (oral, 25 mg/kg) were not increased in Abcg2(-/-) mice, only 1.7-fold in Abcb1a/1b(-/-) mice, but 21.4-fold in Abcb1a/1b(-/-);Abcg2(-/-) mice, indicating pronounced overlapping functions of these transporters in reducing vemurafenib brain accumulation.”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-123** · [PMID 25933211](https://pubmed.ncbi.nlm.nih.gov/25933211/) · `abstract_only` · `supporting` · no number
  - > The concentrations of vemurafenib in the CSF and the plasma were measured by high-performance liquid chromatography.
  - *Cerebrospinal fluid concentrations of vemurafenib in patients treated for brain metastatic BRAF-V600 mutated melanoma.* — Melanoma Res 2015
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF:plasma concentration ratio = mean ratio of the CSF:plasma concentration was 0.98±0.84% · confidence high · weight **0.81**
  - rationale: Primary human PK measurement in normal treatment (no knockout/inhibitor) shows CSF:plasma ratio ~1%, explicitly described as low penetration, in CSF compartment specifically.
  - span relied on: “The mean ratio of the CSF : plasma concentration was 0.98±0.84%. ... a low CSF vemurafenib penetration rate associated with a large interindividual variability”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
- **CNS-124** · [PMID 25933211](https://pubmed.ncbi.nlm.nih.gov/25933211/) · `abstract_only` · `supporting` · no number
  - > Further investigations with larger cohorts are required to study the relationship between CSF vemurafenib concentrations and cerebral response.
  - *Cerebrospinal fluid concentrations of vemurafenib in patients treated for brain metastatic BRAF-V600 mutated melanoma.* — Melanoma Res 2015
  - **proposed: `contradicted`** · basis `measured_pk_human` · primary · human · arm `normal` · CSF:plasma ratio = mean ratio of the CSF:plasma concentration was 0.98±0.84% · confidence high · weight **0.81**
  - rationale: Primary human PK measurement in melanoma patients shows CSF:plasma ratio ~1%, explicitly described as low CSF penetration - direct evidence of CNS exclusion from this compartment.
  - span relied on: “The mean ratio of the CSF : plasma concentration was 0.98±0.84%...our preliminary results highlight for the first time a low CSF vemurafenib penetration rate”
  - read from: pubmed_abstract / Abstract · **your verdict:** _______
