# Phase 2 pre-flight: classification review packet

**18 datasets** - every comparative-design dataset whose Phase 1a confidence came out medium or low. 14 are in the human-only first-pass set; the rest are mouse-model datasets, deferred with the rest of the mouse track but listed so the review is complete.

These are the datasets Phase 2 would ingest, so the labels that matter here are the ones that decide a differential-expression contrast: which samples are NF cases, which are controls, and whether the germline call holds.

**How to read the audit lines.** Phase 1a stored a confidence value but not the reasoning behind it. The *why it is not a clean call* text below is a fresh audit of each GEO record (record text plus the stored labels), so it is a hypothesis about where the uncertainty sits, not a recovered value. Where that audit claimed a stored field looks wrong (10 datasets), the claim was checked and carries an adjudication line.

**5 of 18 reviewed so far.** Datasets you have ruled on carry a **Decision** line naming the contrast they enter Phase 2 with.

| verdict | meaning |
|---|---|
| likely defect in the stored label | the stored value is probably wrong and should be corrected |
| needs a human check | the record cannot settle it; a paper or supplementary table can |
| checked, consistent with the column definition | the audit's claim does not hold |

## Human-only first-pass set

### [E-TABM-69](https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-TABM-69) - medium confidence

*Transcription profiling of human neurofibromatosis type 1*

- **Labels:** NF1 / Plexiform neurofibroma;Malignant peripheral nerve sheath tumor (MPNST) | germline_nf_patient (basis: stated_nf_cohort) | subtype_or_grade_comparison | expression_array
- **Samples:** 20 in the series, 0 in scope, 0 NF cases, 0 controls
- **Sample labels:** (none labelled)
- **Evidence recorded in Phase 1a:** Plexiform neurofibroma (PN-*) and grade III MPNST samples from one NF1 cohort (Henri Mondor); two-colour arrays against a pooled reference.
- **Phase 1a notes:** Pooled 'pool-cut' reference channel, not a biological control; NF1 status stated at series level only.
- **Why it is not a clean call:** NF1 status is stated once at series level and never per sample, and the ArrayExpress rows carry no sample-level labels at all, so no case/control split exists for this dataset.
- **Also:** Two-colour arrays against a pooled 'pool-cut' reference channel, which is a technical reference, not a biological control arm.
- **What would settle it:** Read the SDRF for per-sample tumour type and NF1 status, then decide whether the pooled-reference design can enter a per-dataset DE contrast at all.
- **Decision (Kara): include** - contrast: MPNST vs plexiform neurofibroma (between-subtype, within NF1)
  - Sample-level labels derived from the SDRF and recorded in phase-2/data/phase2-non-geo-samples.csv: 10 two-colour arrays, cy5 carrying one tumour each (6 plexiform neurofibroma: PN-3, PN-4, PN-5, PN-6, PN-M-1, PN-M-2; 4 MPNST: MPNST-1, -2, -4, -5) against a cy3 pool of dermal neurofibromas shared by every array. Because both arms share that reference it cancels in the between-arm contrast, so the missing control arm does not block this dataset; it does mean no tumour-vs-normal contrast is possible here, since the reference is itself NF tumour tissue. Either Hybridization Name or Array Data File works as the array key: the SDRF holds 10 distinct Hybridization Name values, each carrying exactly the cy3/cy5 pair of one array.

### [GSE120687](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE120687) - medium confidence

*The Role of the RNA-binding protein HuR in MPNST growth and metastasis*

- **Labels:** NF1 / Cutaneous neurofibroma;Plexiform neurofibroma;Malignant peripheral nerve sheath tumor (MPNST) | mixed_nf_and_sporadic (basis: per_sample_nf_status) | subtype_or_grade_comparison | bulk_rnaseq | co-assays: chip_or_binding;other | **superseries**
- **Samples:** 86 in the series, 74 in scope, 28 NF cases, 23 controls (control_isogenic_engineered)
- **Sample labels:** nf_case_tumor=28; control_isogenic_engineered=23; treated_or_perturbed=23; comparator_sporadic_same_tumor=12
- **Evidence recorded in Phase 1a:** cell type: dermal neurofibroma / plexiform neurofibroma / MPNST_NF1-derived vs MPNST_sporadic, HuR IP vs IgG IP
- **Phase 1a notes:** SuperSeries of HuR CLIP-seq across NF1-associated tissues (dermal/plexiform NF, NF1-derived MPNST) plus sporadic MPNST comparator; exact sample split uncertain from partial list.
- **Why it is not a clean call:** SuperSeries gives only 28/86 samples; cell type labels like 'MPNST_NF1-derived' don't state germline vs somatic NF1 loss, so NF status is inferred from naming only
- **Also:** control_types='control_isogenic_engineered' is asserted but no engineered/isogenic line appears in the shown samples (only IgG IP controls)
- **What would settle it:** Pull full sample list (all 86 GSMs) and check SubSeries descriptions/linked publication for how 'NF1-derived' vs 'sporadic' MPNST lines were defined
- **Decision (Kara (ChIP) + agent (consequence applied)): ChIP data dropped per Kara; dataset leaves the comparative launch set, perturbation arm retained in the logs** - contrast: none usable for Phase 2; the only abundance contrast is a 3-vs-3 shHuR knockdown in one cell line
  - Kara: the ChIP data is not needed. Applied to all 86 samples in phase-2/data/phase2-sample-overrides.csv: 40 ChIP-seq samples excluded as 'excluded_chip' (BRD2, BRD3, BRD4, H3K27ac, H3K4me3, H3K4me1 and inputs). Dropping them does not by itself make the series usable, because the 40 array samples are also immunoprecipitations - 20 HuR IP and 20 matched IgG IP across dermal neurofibroma (4+4), plexiform neurofibroma (4+4), NF1-derived MPNST (6+6) and sporadic MPNST (6+6) - so they measure HuR-bound transcript enrichment, not abundance, and are tagged 'excluded_rip_not_abundance'. What remains is the 6 RNA-seq samples, a 3-vs-3 shHuR versus shControl knockdown in ST88-14, tagged 'perturbation_arm_deferred' and kept in the logs as later target-validation evidence (does knocking down a candidate move the gene set?) rather than as a case/control input. Consequence applied: study_design in_vitro_perturbation, comparative_design false, so the comparative set goes 49 -> 48 and the human launch set 29 -> 28. Reversible if you want the series kept as a DE input - but there is no abundance contrast in it to run.
- **Flagged stored field** - likely defect in the stored label: control_types='control_isogenic_engineered' is not supported by the sample list: the series' only controls are assay controls - 20 IgG immunoprecipitation samples in the RIP/array arm and 6 inputs in the ChIP arm, which carries no IgG antibody - and no isogenic or engineered line appears in any of the 86 samples. The stored count of 23 matches neither set. If so this dataset has no biological control arm and belongs in the no-control fallback.

### [GSE145064](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE145064) - medium confidence

*Targeting RABL6A-RB1 signaling suppresses malignant peripheral nerve sheath tumors*

- **Labels:** NF1 / Plexiform neurofibroma;Malignant peripheral nerve sheath tumor (MPNST) | germline_nf_patient (basis: inferred) | subtype_or_grade_comparison | bulk_rnaseq
- **Samples:** 46 in the series, 46 in scope, 46 NF cases, 0 controls
- **Sample labels:** nf_case_tumor=46
- **Evidence recorded in Phase 1a:** patient-matched MPNSTs and precursor lesions; per-sample disease state 'Plexiform Neurofibroma' vs 'MPNST' in same patients
- **Phase 1a notes:** No explicit 'NF1' statement, but PNF precursor-to-MPNST design in matched patients is the canonical NF1 progression pattern; NF1 status not confirmed per-patient in shown text.
- **Why it is not a clean call:** No NF1 mention anywhere in title/summary/design or sample metadata; disease state fields only say 'Plexiform Neurofibroma' or 'MPNST', not NF1 status per patient
- **Also:** Not all 14 patients shown have both PNF and MPNST samples (e.g. PT12, PT15, PT8, PT9 variants) so matched-progression inference may not hold uniformly
- **What would settle it:** Read linked publication's patient table/methods for explicit NF1 germline status per patient
- **Decision (Kara (resolved by full-text check)): include** - contrast: MPNST vs patient-matched plexiform neurofibroma, paired on patient
  - Germline question settled at cohort level from the linked publication (PMID 32086342, full text via NCBI PMC - the article is not open access on Europe PMC, whose fullTextXML returns 500). The paper's Results state the tissue microarray was 'of 32 patient-matched NF/PNF and MPNST pairs that included 3 ANNUBPs from 12 NF1 patients cared for at the Iowa NF Clinic', its Methods add '12 paired neurofibromas and MPNSTs ..., 1 unpaired neurofibroma and 2 unpaired MPNSTs' from the University of Iowa Department of Pathology under IRB 201507708, and the results section is headed 'in NF1 patient specimens'. The RNA-seq (deposited as GSE145064) was run on FFPE cores adjacent to those TMA cores. Two counts do not reconcile in the retrieved text: the paper ties the phrase '12 NF1 patients' to the paired TMA cohort, while the GEO series carries 15 distinct patient ids, and nothing in the full text says the 3 unpaired specimens came from 3 further patients or that the cohort totals 15. So germline_basis moves from 'inferred' to 'stated_nf_cohort' - a cohort-level statement, not per-patient sequencing, since the word 'germline' never appears - and confidence stays medium until the patient mapping is settled, which needs the paper's supplementary material or the authors. GEO composition: 46 samples, 21 plexiform neurofibroma and 25 MPNST across 15 patient ids, 10 of which carry both arms, so the contrast can be run paired. No normal-tissue arm exists in the series (the paper's normal peripheral nerve was on the TMA, not in the RNA-seq), so it stays a no-control-fallback dataset. Library is FFPE exome-capture RNA-seq (Agilent SureSelect RNA Direct, All Exon V6 + COSMIC), not poly-A, which is another reason it must not be pooled into a shared matrix; the authors' own analysis used Kallisto plus Sleuth. The 3 ANNUBPs identified on pathology review are not separable from the GEO disease_state field, which carries only the two labels.

### [GSE163071](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE163071) - medium confidence

*NF1 mutation drives neuronal activity-dependent optic glioma initiation*

- **Labels:** NF1 / Optic pathway glioma | mixed_nf_and_sporadic (basis: per_sample_nf_status) | subtype_or_grade_comparison | bulk_rnaseq
- **Samples:** 44 in the series, 22 in scope, 13 NF cases, 9 controls (control_unaffected_donor_normal)
- **Sample labels:** comparator_sporadic_same_tumor=18; nf_case_tumor=13; control_unaffected_donor_normal=9; comparator_non_nf_tumor=4
- **Evidence recorded in Phase 1a:** per-sample field 'nf1: Yes' marks NF1-associated pilocytic astrocytomas; title 'NF1 mutation drives...optic glioma initiation'; design includes NF1-associated PA, sporadic PA, non-neoplastic brain
- **Phase 1a notes:** Per-sample nf1 status distinguishes germline NF1-associated PA from sporadic PA/GBM; only NF1-positive tumor samples are in scope.
- **Why it is not a clean call:** Per-sample 'nf1=Yes/No' field doesn't state whether it reflects germline NF1 diagnosis or tumor's somatic NF1 mutation status, yet scope requires germline-only cases.
- **Also:** CTL_8/9/10 are listed as 'Human tumor tissue' with tumor=PA, not non-neoplastic brain, conflicting with stored control_type 'control_unaffected_donor_normal'.
- **What would settle it:** Check linked publication/methods or full GEO characteristics for how NF1 status was determined (clinical diagnosis vs tumor sequencing) and confirm CTL sample origin.
- **Decision (Kara): include, with sample-level removals (all traps resolved)** - contrast: NF1-associated pilocytic astrocytoma (13) vs non-neoplastic brain (7)
  - Kara's ruling on the three annotation traps, plus CTL_11: remove the sporadic pilocytic astrocytomas, the ambiguously labelled PA_33, and CTL_11. Applied in phase-2/data/phase2-sample-overrides.csv over the 44 GEO samples: 13 NF1-associated PA kept as cases; 7 non-neoplastic brain kept as controls (CTL_1 to CTL_7); 18 sporadic PA removed, which includes CTL_8, CTL_9 and CTL_10 whose CTL titles contradict their tumour annotation; 4 glioblastoma removed as comparators; PA_33 removed as annotated control tissue titled PA; CTL_11 removed as source='Human control tissue' with nf1=CTL but tumor=PA. In-scope samples fall from the stored 22 to 20 and controls from 9 to 7; no sample is left unresolved. Reading the contrast: the controls are cortex from DIPG patients plus one matched normal, not optic pathway tissue, so tissue source is confounded with case/control status - see the control_types correction.
- **Flagged stored field** - likely defect in the stored label: Resolved from the linked publication (PMID 34040258, Nature 2021, doi 10.1038/s41586-021-03580-6; full text via NCBI PMC, Europe PMC fullTextXML 500s for it) plus the full 44-sample GEO characteristics. NF1 status: the paper defines its groups only as 'Neurofibromatosis-1 syndrome-associated' versus 'sporadic (occurring in patients without NF1)' pilocytic astrocytoma and describes no mutation analysis, germline testing or diagnostic criteria - samples came from the paediatric tumour banks at St. Louis Children's Hospital, UCLA and Stanford under their IRBs, so NF1 status is a clinical/syndrome attribution carried with the bank record, not tumour or germline sequencing. GEO does carry a per-sample nf1=Yes/No/CTL flag, so germline_basis='per_sample_nf_status' describes the metadata correctly, but the method behind the flag is unstated and confidence should stay medium on the same footing as GSE145064. CTL origin: control_types='control_unaffected_donor_normal' is wrong. Extended Data Table 1 lists the RNA-seq non-neoplastic brain group as NOP454N (location N/A) plus DIPG46N, DIPG51N, DIPG48N and DIPG70N - frontal cortex from diffuse intrinsic pontine glioma patients - so four of five are non-neoplastic tissue from children with a different brain tumour, and NOP454N pairs by id with the NF1-PA sample NOP454, i.e. matched normal from a tumour patient. Neither is an unaffected donor. Note the paper's RNA-seq table lists 24 samples while GEO deposits 44 (13 nf1=Yes PA, 18 sporadic PA, 4 glioblastoma, 8 nf1=CTL/tumor=CTL, 1 ambiguous), so the table does not map 1:1 onto the series. Separately, GEO's own titles mislead: CTL_8, CTL_9 and CTL_10 are annotated source='Human tumor tissue', nf1=No, tumor=PA, i.e. sporadic tumours despite the CTL name, and CTL_11 is source='Human control tissue' with nf1=CTL but tumor=PA, which is self-inconsistent and is the ninth sample in the stored control count.

### [GSE172221](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE172221) - medium confidence

*A genetic mouse model of malignant peripheral nerve sheath tumor with postnatal Nf1 and p53 loss recapitulates the histology and transcriptome of human tumors*

- **Labels:** NF1 / Malignant peripheral nerve sheath tumor (MPNST);Plexiform neurofibroma;Cutaneous neurofibroma | mixed_nf_and_sporadic (basis: engineered_genotype) | subtype_or_grade_comparison | bulk_rnaseq
- **Samples:** 44 in the series, 22 in scope, 22 NF cases, 0 controls
- **Sample labels:** nf_case_tumor=22; other_or_unclear=22
- **Evidence recorded in Phase 1a:** postnatal deletion of a Nf1;Trp53 cis-conditional allele...compare these models and with human MPNST, plexiform neurofibromas (PNF), and neurofibromas (NF)
- **Phase 1a notes:** Mouse arms are clearly engineered Nf1-loss MPNST models (in scope); human MPNST/PNF/NF samples lack stated per-sample germline NF1 status, so their NF association is unconfirmed.
- **Why it is not a clean call:** Human MPNST/PNF/NF samples (diagnosis=MPNST only, no genotype field) lack any stated germline NF1 status, so they could be sporadic tumors with somatic loss
- **Also:** Lats-Nes/Lats-Plp arms are Lats1/2 conditional knockouts, not Nf1/Trp53 models, yet are folded into the in-scope count alongside NP-Plp/NPcis
- **What would settle it:** Check linked publication (GSE172221) methods/patient table for human sample NF1 germline/clinical status; confirm whether Lats-PNST arms are intended as NF-pathway models
- **Decision (Kara): defer to the mouse pass - excluded from the first pass, retained in the logs** - contrast: none in the first pass; Nf1;Trp53 GEM-MPNST vs the models' own comparators if the mouse track opens
  - Deferred, not dropped. The 12 Nf1;Trp53 mouse tumours (9 NP-Plp, 3 NPcis) carry de_role 'case_mouse_deferred' in phase-2/data/phase2-sample-overrides.csv, so they are recoverable by that tag rather than by re-reading the paper. The 10 Lats1;2 samples stay 'excluded_not_nf_model' whether or not mouse data is admitted later, since the publication's own finding is that they are transcriptomically distinct from Nf1;p53-driven tumours and cluster with human PNF/NF. The 22 human samples stay 'excluded_nf_status_unstated' and would need the authors to resolve. The n_samples_in_scope correction to 12 in phase-2/data/phase2-label-corrections.csv is written to apply when the mouse track opens; it has no effect on the human-only first pass, where this dataset contributes zero samples. If the mouse track does open, note the remaining limit: NP-Plp spans two genotypes mimicking sporadic ([Nf1;Trp53]fl/+) and NF1-associated ([Nf1;Trp53]fl/Nf1-) MPNST, which GEO's 'mouse line=NP-Plp' does not distinguish.
- **Flagged stored field** - likely defect in the stored label: Both questions resolved from the linked publication (PMID 34647023, Neuro-Oncol Adv 2021, doi 10.1093/noajnl/vdab129, open access) plus the full 44-sample GEO characteristics. (1) Human NF1 status is NOT stated anywhere available. GEO carries only diagnosis=MPNST/PNF/NF for the 22 human samples, and the paper identifies them only as 'our (SJ collection) human samples' with no patient table, no NF1 or germline annotation and no human-tissue IRB statement in the full text. Under the germline-only rule the human arm therefore cannot be admitted - which is what Phase 1a already did, labelling all 22 human samples other_or_unclear. (2) The Lats arms are explicitly NOT NF-pathway models. The paper states 'Hippo pathway mutations are rarely found in MPNST', frames the Lats1;2 models as a published alternative whose transcriptomic resemblance to human MPNST was untested, and its central finding is that 'Nf1;p53-driven GEM-MPNST were distinct from Lats-driven GEM-MPNST and resembled human MPNST more closely'; on UMAP the Lats tumours clustered with GEM-neurofibroma and human PNF/NF rather than human MPNST. NF2/merlin is never mentioned. So Phase 1a's in-scope count of 22, which labelled all 10 Lats samples nf_case_tumor, is wrong: the NF-genotype samples are the 12 Nf1;Trp53 ones (9 NP-Plp, 3 NPcis). Consequence for this first pass: with mouse deferred and the human arm unlabelable, GSE172221 contributes zero samples to Phase 2, the same shape as GSE292071 and GSE5675. One further limit for the deferred mouse track: NP-Plp spans two genotypes mimicking sporadic ([Nf1;Trp53]fl/+) and NF1-associated ([Nf1;Trp53]fl/Nf1-) MPNST, and GEO's 'mouse line=NP-Plp' does not distinguish them.

### [GSE179043](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE179043) - medium confidence

*Transcriptional programs dictating Schwann cell transformation in MPNST*

- **Labels:** NF1 / Plexiform neurofibroma;Malignant peripheral nerve sheath tumor (MPNST) | germline_nf_patient (basis: per_sample_nf_status) | subtype_or_grade_comparison | bulk_rnaseq | co-assays: chip_or_binding | **superseries**
- **Samples:** 50 in the series, 36 in scope, 36 NF cases, 0 controls
- **Sample labels:** nf_case_tumor=36; comparator_sporadic_same_tumor=14
- **Evidence recorded in Phase 1a:** tumor type: benign NF / tumor type: MPNST; plexiform neurofibroma samples listed per patient
- **Phase 1a notes:** Human NF1 patient benign NF, plexiform NF, and MPNST tumors; one Lats1/2-deficient mouse MPNST model sample included
- **Why it is not a clean call:** SuperSeries defers all design detail to subseries ('Refer to individual Series'); per-sample NF1 germline status is inferred only from ID prefixes (NF1-, pNF-2-) vs unlabeled MPNST-x names, not stated directly.
- **Also:** Lats1/2-deficient mouse model sample is a Hippo-pathway knockout, not a canonical engineered NF1/NF2 genotype, so its in/out-of-scope status is unclear.
- **What would settle it:** Open each subseries' sample characteristics (or linked publication) to confirm germline NF1 status for MPNST-2..12 and genotype rationale for the Lats1/2 mouse tumor.

### [GSE207400](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE207400) - medium confidence

*Malignant Peripheral Nerve Sheath Tumors are Comprised of Two Epigenetic Subgroups with Distinct Molecular Landscapes, Outcomes and Therapeutic Targets: Bulk RNA Seq Samples*

- **Labels:** NF1 / Malignant peripheral nerve sheath tumor (MPNST);ANNUBP / atypical neurofibroma;Other | mixed_nf_and_sporadic (basis: per_sample_nf_status) | subtype_or_grade_comparison | bulk_rnaseq
- **Samples:** 48 in the series, 26 in scope, 26 NF cases, 0 controls
- **Sample labels:** nf_case_tumor=26; comparator_sporadic_same_tumor=22
- **Evidence recorded in Phase 1a:** genotype: NF1 vs genotype: Sporadic listed per sample; disease state spans Benign_NF, PremalignantNF, MPNST grades
- **Phase 1a notes:** Cohort mixes NF1-germline and sporadic PNSTs across neurofibroma/atypical/MPNST spectrum; only genotype:NF1 samples in scope.
- **Why it is not a clean call:** genotype field just says 'NF1' per sample with no indication whether this means germline NF1 syndrome or merely somatic/tumor NF1 mutation status
- **Also:** No patient-level clinical/germline testing data given; 'NF1' vs 'Sporadic' could reflect tumor genotyping rather than syndromic diagnosis
- **What would settle it:** Check the associated publication/methods for how genotype was determined (germline testing vs tumor NF1 mutation/LOH) for each sample

### [GSE2841](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE2841) - medium confidence

*Expression Profiling of pheochromocytomas of various genetic origins*

- **Labels:** NF1 / Other | mixed_nf_and_sporadic (basis: per_sample_nf_status) | subtype_or_grade_comparison | expression_array
- **Samples:** 76 in the series, 2 in scope, 2 NF cases, 0 controls
- **Sample labels:** comparator_sporadic_same_tumor=35; comparator_non_nf_tumor=31; other_or_unclear=8; nf_case_tumor=2
- **Evidence recorded in Phase 1a:** sample P167 annotated 'genetic class: NF1' among a cohort of pheochromocytomas with MEN2A, VHL, SDHB, sporadic and other genetic origins
- **Phase 1a notes:** Cohort is mostly sporadic/other hereditary syndromes; only NF1-genetic-class samples are germline NF1-associated; pheochromocytoma not in fixed manifestation list so tagged Other
- **Why it is not a clean call:** Only P167 is visible as 'genetic class=NF1' among 28/76 shown samples; the stored n_nf_case_samples=2 can't be verified from the truncated list, and classification basis (germline-confirmed vs clinical NF1 diagnosis) isn't stated.
- **Also:** Genetic class labels (MEN2A, VHL, B_SDHB, NF1, SPOR) look like clinical/syndromic groupings, not confirmed molecular germline testing results.
- **What would settle it:** Pull full 76-sample metadata table and the linked paper's methods to see how 'genetic class=NF1' was assigned (germline sequencing vs clinical dx).

### [GSE292071](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE292071) - medium confidence

*A Single-cell Atlas of Schwannoma Across Genetic Backgrounds and Anatomic Locations*

- **Labels:** NF2-SWN / Vestibular schwannoma;Non-vestibular schwannoma | mixed_nf_and_sporadic (basis: stated_nf_cohort) | subtype_or_grade_comparison | single_cell_rnaseq
- **Samples:** 151 in the series, 0 in scope, 0 NF cases, 0 controls
- **Sample labels:** other_or_unclear=151
- **Evidence recorded in Phase 1a:** tumors from 22 patients with NF2-related schwannomatosis, non-NF2-related schwannomatosis, and sporadic schwannomas
- **Phase 1a notes:** Cohort mixes germline NF2/SWN patients with sporadic schwannomas; per-sample diagnosis not given in metadata.
- **Why it is not a clean call:** Cohort mixes NF2-related schwannomatosis, non-NF2-related schwannomatosis, and sporadic cases, but per-sample diagnosis isn't given in sample metadata (all 151 tissue entries just say 'Schwannoma/tumor')
- **Also:** Can't tell how many of the 22 patients are germline NF2-SWN vs sporadic, so in-scope sample count is unknown rather than truly zero
- **What would settle it:** Check supplementary patient table or paper's cohort table mapping patient IDs (SCHW001, SCHW2-5 etc.) to NF2-SWN/non-NF2-SWN/sporadic diagnosis
- **Flagged stored field** - needs a human check: Zero in-scope samples despite an NF2-SWN cohort: per-sample diagnosis is absent from the sample metadata, so the count is unknown rather than truly zero. Resolve from the paper's cohort table before Phase 2 drops the dataset.

### [GSE325204](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE325204) - medium confidence

*Base transcriptomes of seven, untreated patient-derived MPNST cell lines, two of which are PRC2-WT and five PRC2-LoF*

- **Labels:** NF1 / Malignant peripheral nerve sheath tumor (MPNST) | mixed_nf_and_sporadic (basis: cell_line_provenance) | subtype_or_grade_comparison | bulk_rnaseq
- **Samples:** 21 in the series, 9 in scope, 9 NF cases, 0 controls
- **Sample labels:** other_or_unclear=9; nf_case_tumor=9; comparator_sporadic_same_tumor=3
- **Evidence recorded in Phase 1a:** Cell lines S462, 90-8TL (908TL) and sNF96.2 (SNF962) are known NF1 patient-derived MPNST lines; STS26T is a documented sporadic (non-NF1) MPNST line
- **Phase 1a notes:** HSSCH2, JH-2-002, JH-2-079-c NF status not stated in record text; record frames PRC2 WT/LoF, not NF status, per line
- **Why it is not a clean call:** Record text never states NF1 status for any line; PRC2 WT/LoF is the only genotype given, so NF-case assignment for S462/908TL/SNF962 relies on outside knowledge, not the record
- **Also:** HSSCH2, JH-2-002, JH-2-079-c NF status is completely unstated, yet 9 of 21 samples were counted as NF-case and 9 as 'other_or_unclear'
- **What would settle it:** Check original publication/cell line repository (Cellosaurus/ATCC) for documented NF1 germline status of each of the 7 lines, esp. HSSCH2, JH-2-002, JH-2-079-c
- **Flagged stored field** - needs a human check: Three of six cell lines (HS-Sch-2, JH-2-002, JH-2-079-c) have unverified NF1 provenance; only S462, 90-8TL and sNF96.2 are established NF1-patient lines.

### [GSE56598](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE56598) - medium confidence

*Wide methylation analysis in vestibular schwannoma*

- **Labels:** NF2-SWN / Vestibular schwannoma;Non-vestibular schwannoma | mixed_nf_and_sporadic (basis: per_sample_nf_status) | subtype_or_grade_comparison | expression_array | co-assays: methylation | **superseries**
- **Samples:** 89 in the series, 20 in scope, 6 NF cases, 14 controls (control_unaffected_donor_normal)
- **Sample labels:** other_or_unclear=31; comparator_sporadic_same_tumor=30; control_unaffected_donor_normal=14; comparator_non_nf_tumor=8; nf_case_tumor=6
- **Evidence recorded in Phase 1a:** subtype: NF2 associated vs subtype: Sporadical, per-sample labeling of vestibular schwannoma tumors
- **Phase 1a notes:** Only 24/89 samples shown; 3 NF2-associated VS visible, rest sporadic/non-vestibular comparators; counts likely incomplete
- **Why it is not a clean call:** Record is a SuperSeries ('Refer to individual Series') with only 28/89 samples shown, so NF2-vs-sporadic status for most samples is unverifiable from this text alone.
- **Also:** assay_class='expression_array' contradicts the title 'Wide methylation analysis in vestibular schwannoma', suggesting wrong/merged metadata.
- **What would settle it:** Open the individual SubSeries records (platform + full sample sheet) to confirm assay type and get per-sample NF2 status for all 89 samples.
- **Flagged stored field** - checked, consistent with the column definition: assay_class is correct as expression_array: the series' GEO DataSet Type is 'Methylation profiling by genome tiling array; Expression profiling by array', and the methylation content is already flagged in co_assays. The control_types claim stands as a check: the visible samples are tumours, not unaffected-donor normals.

### [GSE5675](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE5675) - medium confidence

*Pilocytic astrocytoma*

- **Labels:** NF1 / Non-optic LGG | mixed_nf_and_sporadic (basis: stated_nf_cohort) | subtype_or_grade_comparison | expression_array
- **Samples:** 41 in the series, 0 in scope, 0 NF cases, 0 controls
- **Sample labels:** other_or_unclear=41
- **Evidence recorded in Phase 1a:** gene expression profiling on 41 primary PAs arising sporadically and in patients with neurofibromatosis type 1 (NF1)
- **Phase 1a notes:** Cohort mixes sporadic and NF1-associated PAs; sample-level NF1 status not given in shown records.
- **Why it is not a clean call:** Cohort explicitly mixes sporadic and NF1-associated PAs but sample-level NF1 status isn't given in the shown sample titles/metadata, so in-scope N can't be determined
- **Also:** n_samples_in_scope/n_nf_case_samples/n_sporadic_samples_excluded all stored as 0 despite summary stating NF1 patients are included, suggesting counts weren't actually extracted
- **What would settle it:** Check full sample metadata via GEO 'Web Link' (supplementary table) for per-sample NF1 status to split the 41 into NF1 vs sporadic
- **Flagged stored field** - needs a human check: Same shape as GSE292071: the summary states NF1-associated pilocytic astrocytomas are included, but no per-sample NF1 status is in the metadata, so every sample fell out of scope and the dataset would contribute nothing.

### [GSE66743](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE66743) - medium confidence

*Gene expression in malignant peripheral nerve sheat tumours and benign neurofibromas*

- **Labels:** NF1 / Malignant peripheral nerve sheath tumor (MPNST) | mixed_nf_and_sporadic (basis: per_sample_nf_status) | subtype_or_grade_comparison | expression_array
- **Samples:** 38 in the series, 25 in scope, 25 NF cases, 0 controls
- **Sample labels:** nf_case_tumor=25; comparator_sporadic_same_tumor=13
- **Evidence recorded in Phase 1a:** hereditary status: Neurofibromatosis type 1 given per-patient for many MPNST samples; others labeled Sporadic
- **Phase 1a notes:** 30 MPNSTs (17 NF1, 13 sporadic per-sample) + 8 neurofibromas; hereditary status for neurofibroma subset not shown/unknown
- **Why it is not a clean call:** The 8 neurofibroma samples have no hereditary-status field anywhere in the record (notes admit 'not shown/unknown'), yet n_samples_in_scope=25 = 17 NF1 MPNST + all 8 neurofibromas treated as in-scope.
- **Also:** Sample list shows only 28/38 records, all MPNST; the hereditary status of the 2 unlisted MPNST patients can't be verified from this record.
- **What would settle it:** Check full GEO sample metadata/supplementary clinical table for the 8 neurofibroma samples' hereditary status and the 2 missing MPNST entries.
- **Flagged stored field** - needs a human check: The in-scope count assumes all 8 neurofibromas are NF1-associated, which the stored notes themselves flag as unknown.

### [GSE77205](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE77205) - medium confidence

*Cell-type dependent enhancer binding of the EWS/ATF1 fusion gene in clear cell sarcomas*

- **Labels:** NF1 / Malignant peripheral nerve sheath tumor (MPNST) | mixed_nf_and_sporadic (basis: per_sample_nf_status) | subtype_or_grade_comparison | expression_array | co-assays: chip_or_binding | **superseries**
- **Samples:** 35 in the series, 4 in scope, 4 NF cases, 0 controls
- **Sample labels:** comparator_non_nf_tumor=31; nf_case_tumor=4
- **Evidence recorded in Phase 1a:** MPNST 830/937/1080/1082 :: sample type: NF1 patient | tissue: surgically resected human sarcoma sample
- **Phase 1a notes:** 4 of 35 samples are NF1-patient MPNSTs used as comparator; rest are clear cell sarcoma (EWS/ATF1) and mouse models, unrelated to NF.
- **Why it is not a clean call:** MPNST 830/937/1080/1082 are labeled 'sample type=NF1 patient' but the study is about EWS/ATF1 clear cell sarcoma biology; no confirmation these are germline NF1 vs sporadic NF1-associated MPNST used only as a histologic comparator
- **Also:** ASSAY and ORGANISM fields are blank at the SuperSeries level, so assay_class='expression_array' can't be confirmed from this record (samples look like ChIP-seq, e.g. input DNA)
- **What would settle it:** Open the MPNST SubSeries/sample GEO pages and linked publication methods to check if NF1 status is germline-confirmed and what assay was run on these 4 samples
- **Flagged stored field** - checked, consistent with the column definition: Not a false positive: the stored notes already record that 4 of 35 samples are NF1-patient MPNSTs used as comparators inside a clear-cell-sarcoma (EWS/ATF1) study. assay_class expression_array is right and the ChIP content is flagged in co_assays. The Phase 2 question is whether 4 samples with no control arm are worth ingesting.

## Mouse-model datasets (deferred)

### [GSE265875](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE265875) - low confidence

*Somatic muscle engineering faithfully recapitulates a molecular spectrum of high-risk sarcomas*

- **Labels:** NF1 / Malignant peripheral nerve sheath tumor (MPNST) | mixed_nf_and_sporadic (basis: engineered_genotype) | tumor_vs_normal | bulk_rnaseq | co-assays: methylation | **superseries**
- **Samples:** 195 in the series, 29 in scope, 17 NF cases, 12 controls (control_isogenic_engineered)
- **Sample labels:** comparator_non_nf_tumor=166; nf_case_tumor=17; control_isogenic_engineered=12
- **Evidence recorded in Phase 1a:** genotype: sgNf1; sgp53 tumor samples present alongside ASPSCR1-TFE3 and KRASG12V sarcoma models in same SuperSeries
- **Phase 1a notes:** SuperSeries spans multiple engineered sarcoma genotypes; only sgNf1;sgp53 arm is NF-related, rest are non-NF sarcoma models (ASPSCR1-TFE3, KRAS, BCOR)
- **Why it is not a clean call:** SuperSeries bundles unrelated GEM sarcoma models (ASPSCR1-TFE3, KRAS, BCOR, Nf1); only 3 of the claimed 17 Nf1 samples are visible in the shown 28/195 records, so NF1 scope/count can't be confirmed from text.
- **Also:** Title/summary never mention NF1 or neurofibromatosis - sgNf1;sgp53 appears used as a generic tumor-suppressor-loss sarcoma driver alongside p53/BCOR/KRAS, not as a disease-focused NF1 model.
- **What would settle it:** Pull the full 195-sample metadata table (or the Nf1-specific SubSeries GSE) to confirm actual n of sgNf1;sgp53 tumor and matched control samples.
- **Flagged stored field** - needs a human check: Case and control counts (17/12) exceed what is visible in the fetched sample records (3 Nf1 tumours, 6 muscle controls); the rest of the series was not shown to the classifier.

### [GSE137152](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE137152) - medium confidence

*Sustained fetal hematopoiesis causes juvenile death from leukemia: evidence from a dual-age-specific mouse model*

- **Labels:** NF1 / Hematologic malignancies | engineered_nf_model (basis: engineered_genotype) | tumor_vs_normal | bulk_rnaseq
- **Samples:** 6 in the series, 6 in scope, 3 NF cases, 3 controls (control_isogenic_engineered)
- **Sample labels:** nf_case_tumor=3; control_isogenic_engineered=3
- **Evidence recorded in Phase 1a:** JMML age specificity depends on dosage of Pten and Nf1; Nf1 LOH causes monocytosis in juvenile mice with Pten haploinsufficiency
- **Phase 1a notes:** Combined Pten/Nf1 engineered mouse model of JMML; Nf1 LOH is core to phenotype though Pten is co-driver
- **Why it is not a clean call:** Sample sheet just labels genotype as generic 'JMML' vs 'WT' without specifying which Pten/Nf1 allelic combination each of the 3 JMML replicates carries, despite the summary describing multiple distinct genotype combinations (Pten+/-;Nf1LOH, Pten-/-;Nf1LOH, etc.)
- **Also:** ORGANISM and ASSAY fields are blank in the record, so species and assay type are only inferable from context, not stated
- **What would settle it:** Check the GEO sample characteristics/supplementary table or linked paper for the exact genotype of each N3xx/N4xx sample ID used in the JMML group

### [GSE231603](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE231603) - medium confidence

*Nf1 Deficiency Increases Mammary Collagen Deposition and Restricts Adipocyte Differentiation Before Tumor Formation*

- **Labels:** NF1 / Other | engineered_nf_model (basis: engineered_genotype) | tumor_vs_normal | bulk_rnaseq
- **Samples:** 80 in the series, 80 in scope, 65 NF cases, 15 controls (control_isogenic_engineered)
- **Sample labels:** nf_case_nontumor=42; nf_case_tumor=23; control_isogenic_engineered=15
- **Evidence recorded in Phase 1a:** Nf1-deficient rat model...to accurately model the germline monoallelic NF1 mutations in NF1 patients
- **Phase 1a notes:** Engineered Nf1-deficient rat lines vs wildtype; mammary stroma/pre-tumor profiling; breast cancer phenotype not in fixed list, coded Other.
- **Why it is not a clean call:** Genotype codes IF, PS, IFPS are undefined abbreviations for the three 'Nf1-mutated rat lines' - unclear what alleles/mutations they represent or if all are true germline monoallelic Nf1 models
- **Also:** ORGANISM and ASSAY fields are blank in the record, leaving species/platform only inferable from free-text DESIGN line
- **What would settle it:** Check GEO sample characteristics/legend or the associated paper's methods for the IF/PS/IFPS rat line definitions and their Nf1 allele structure

### [GSE78895](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE78895) - medium confidence

*Rictor/mTORC2 signaling has opposing functions in adult glioma and childhood SHH medulloblastoma*

- **Labels:** NF1 / High grade glioma | mixed_nf_and_sporadic (basis: engineered_genotype) | tumor_vs_normal | expression_array
- **Samples:** 32 in the series, 23 in scope, 13 NF cases, 10 controls (control_isogenic_engineered)
- **Sample labels:** nf_case_tumor=13; control_isogenic_engineered=10; comparator_sporadic_same_tumor=9
- **Evidence recorded in Phase 1a:** p53 loss combined with germline Nf1 mutation; genotype hGFAP-cre;p53KO/+;Nf1+/flox and p53flox/flox;Nf1KO/+ gliomas
- **Phase 1a notes:** Series mixes engineered Nf1-mutant gliomas with non-Nf1 p53-only gliomas and normal brain controls in same platform.
- **Why it is not a clean call:** Genotype shown is 'Nf1+/flox' (one null, one floxed allele) with hGFAP-cre; text never confirms Cre excises the remaining flox allele to give biallelic Nf1 loss in the tumor.
- **Also:** Only 28/32 samples listed; visible Nf1+/flox 'Astrocytoma' group is 9, but stored label claims 13 NF-case samples - the 4 unseen samples can't be checked.
- **What would settle it:** Pull full GSM list/sample metadata for all 32 samples and check the paper's methods for confirmed biallelic Nf1 deletion (LOH/IHC) in the Nf1+/flox tumors.
