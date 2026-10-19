# Project Plan: nf-target-pipeline

**Grant:** Anthropic AI for Science, rare disease research call
**Goal:** Build a Claude-agent-operable pipeline that takes raw expression data as input and outputs a prioritized, evidence-scored list of candidate drug targets for rare disease research (starting with NF).

---

## Disease and Manifestation Labeling Standard

Every dataset (Phase 1a) and target (Phase 1b, 3, 4, 5, 6, 7) must be labeled with:

- **Disease:** NF1, NF2-SWN, or SWN (schwannomatosis). Use "Other" or "Not specified" only if the source genuinely doesn't distinguish, and flag that as a gap rather than guessing.
- **Manifestation(s):** one or more from this fixed list, applied as-is (don't paraphrase or substitute synonyms): Bone defects; Cardiovascular issues; Cognition / Behavioral / Learning; Sleep; Cutaneous neurofibroma; Ependymoma; Gastrointestinal stromal tumor (GIST); Hematologic malignancies; High grade glioma; Malignant peripheral nerve sheath tumor (MPNST); Meningioma; Optic pathway glioma; Non-optic LGG; Pain; Plexiform neurofibroma; ANNUBP / atypical neurofibroma; Pulmonary disease; Non-vestibular schwannoma; Vestibular schwannoma; Other

**Sporadic tumors are out of scope.** Only germline/NF-associated material counts as evidence. A dataset or paper concerning sporadic tumors with somatic NF1/NF2 loss (most published meningioma work, a large share of vestibular schwannoma and high-grade glioma work) is excluded rather than relabeled; this was applied retroactively to Phase 1b. Where a cohort is mixed, keep the dataset/paper and exclude the sporadic samples at the sample level rather than dropping the whole record. Record what the exclusion removed (accession or PMID, and count) so the decision is auditable and reversible, since the same molecular lesion in sporadic tissue may be worth revisiting if a later phase runs short of evidence.

A dataset or target can carry more than one manifestation label if it's genuinely relevant to more than one (e.g. a gene implicated in both plexiform neurofibroma and MPNST progression). Carry these two labels through every downstream phase so the final scored candidate list (Phase 6) and comparison (Phase 7) can be filtered/grouped by disease and manifestation, not just by gene name.

## Compute Requirements

- Start laptop-first, using Claude Science to run the pipeline locally (macOS/Linux). Most of the work here (API queries against DGIdb/ChEMBL/Guide to Pharmacology/Monarch, plus standard differential expression and pathway enrichment on bulk RNA-seq/microarray data) is not GPU-heavy and doesn't need dedicated compute provisioned upfront
- Escalate only if scope expands to single-nuclei/spatial transcriptomics datasets (e.g., snRNA-seq datasets like GSE232766), which produce much larger matrices than the bulk NF2 datasets identified in Phase 1a. If that happens, Claude Science can draft and submit that specific job to an HPC cluster or to Modal (cloud compute), scaling from a single GPU to hundreds as needed, rather than requiring bigger hardware from day one
- No need to pre-provision cloud compute or an HPC account before starting; revisit this only if a specific phase's dataset size clearly exceeds laptop capacity

## Version Control (GitHub)

- Repo name: **`nf-target-pipeline`** (karaquaid/nf-target-pipeline)
- Track this project in this GitHub repo from the start, using Claude Science (or Claude Code as a fallback) for repo setup and ongoing git operations (commits, branches, PRs) throughout every phase below
- Repo structure: one folder per phase, each with its own `data/`, `docs/` and `scripts/` subfolders (`phase-1a/`, `phase-1b/`, and `phase-2/` onward as each phase lands), so everything a phase produced sits together. `/docs/project-plan.md` and `README.md` stay at the repo root as the cross-phase source of truth. `data/` holds small reference files only, e.g. candidate target lists and coverage tables; raw expression data stays out of the repo given file size and any data-use terms
- Commit at the end of each phase, not just at the end of the project, so the repo reflects real progress and gives you a rollback point if a later phase's approach doesn't pan out
- Keep this plan document itself in the repo (e.g. `/docs/project-plan.md`) and update it in place as scope shifts, rather than letting the repo and the plan drift apart

## Phase 1a: Scope and Data Source Finalization

**Status:** run 2026-09-29; results and open decisions in `phase-1a/docs/phase1a-dataset-scope.md`. The committed tables are the record of that sweep, so a re-run's new series are never folded in silently. Re-runs since: 2026-10-02 returned the same 415 series with identical per-query hit counts, and 2026-10-19 returned 418, leaving three new series unclassified. They need a classify-or-defer call before the Phase 2 launch set is treated as closed.

**Claude tools:** GEO and ArrayExpress/BioStudies connectors (omics-archives) for the search, NCBI E-utilities directly for the re-runnable script, web search for spot-checks

- Run the dataset search as a versioned script in the phase's `scripts/` folder rather than as an interactive search, so the exact query strings and search date are recorded and the sweep can be re-run and diffed later. Every accession in the final table must resolve against NCBI before it is reported, which removes accession hallucination as a category and leaves spot-checks to confirm relevance only
- Sources: GEO is primary, ArrayExpress/BioStudies secondary (expect mostly legacy or mirrored records). SRA is not searched as a separate source: human expression submissions with no GEO series are rare and carry no usable disease labeling
- Restrict to expression assay types ("Expression profiling by array" / "by high throughput sequencing"); unfiltered keyword hits pull in ChIP-seq, ATAC, methylation and miRNA series. Collect single-cell/single-nucleus series but mark them deferred (see Compute Requirements)
- Label each dataset with disease (NF1, NF2-SWN, or SWN) and manifestation(s) per the labeling standard above, and record the basis for the disease label (stated NF patient cohort / per-sample NF status / engineered NF genotype / inferred), since the standard excludes sporadic tumors
- Include both human and mouse-model datasets, with an `organism` column. Mouse datasets are a separate analysis track (ortholog mapping required) and are counted separately in the Phase 3b coverage chart, so a zero there reads as "no human tissue" rather than "no evidence". Whether mouse data carries into Phases 2-3 is a decision to make from the Phase 1a counts, not in advance
- Record a `study_design` column (tumor vs normal / tumor-subtype or grade comparison / in vitro perturbation / xenograft / single-arm profiling), because only the comparative designs feed Phase 3 differential expression
- Document controls with an explicit taxonomy rather than a yes/no flag: matched adjacent normal tissue; unaffected-donor normal tissue or primary Schwann cells; isogenic or engineered control; non-NF tumor comparator; none. "Healthy control" barely exists for nerve tissue, and which kind of control a dataset has determines the batch-effect handling needed in Phase 2. Control counts are not a GEO metadata field: they come from parsing per-sample characteristics and titles, whose completeness varies widely between series
- Deduplicate superseries/subseries and re-deposited cohorts before counting, so samples are not double-counted downstream
- Record per-dataset data availability (raw counts / raw array files / processed matrix only / none), since that decides Phase 2 ingestability
- Deliverables mirror the Phase 1b schema so Phase 3b can join them: a dataset-level table, a long dataset x disease x manifestation table over the fixed vocabulary with explicit zero rows, a per-sample manifest that doubles as Phase 2's input list, and an exclusions table recording sporadic and off-scope datasets
- Finalize scope statement: primary focus is candidate drug/target identification; batch-effect correction and no-control-dataset handling are secondary/bonus capabilities, not the headline

## Phase 1b: Literature-Derived Target Identification (runs in parallel with Phases 1a–2)

**Claude tools:** Advanced Research (literature search across NF1/NF2/schwannomatosis), web search

- Search the literature for genes/targets already implicated in NF1, NF2, and schwannomatosis, sourced directly via search rather than a pre-curated paper set
- Label each target found with disease (NF1, NF2-SWN, or SWN) and manifestation(s) per the labeling standard above
- For each paper cited, record whether Claude had access to the full text or only the abstract/metadata, so findings drawn from abstracts alone can be weighted differently from those drawn from full text
- Compile this into a literature-derived candidate target list, independent of the expression-data pipeline
- Hold this list for comparison against the expression-derived candidate list in Phase 7, to check overlap and surface targets one approach finds that the other misses

## Phase 2: Data Ingestion and Preprocessing

**Status:** pre-flight review complete (2026-10-08). All 18 medium/low-confidence comparative datasets were adjudicated one by one in `phase-2/docs/phase2-classification-review.md`; the rulings live in `phase-2/data/phase2-review-diagnosis.json`, the resulting label changes in `phase-2/data/phase2-label-corrections.csv`, and the per-sample inclusion/exclusion calls in `phase-2/data/phase2-sample-overrides.csv`.

**Claude tools:** Claude Code (writing/debugging ingestion and preprocessing scripts)

- **First pass is human-only.** Mouse and rat datasets are a separate later track, not a parallel one. Datasets deferred there (GSE172221, GSE265875, GSE137152, GSE231603, GSE78895, and the mouse arms of mixed series) stay in the logs with their sample labels so the mouse pass starts from a finished manifest rather than a fresh sweep
- **Launch set: 22 datasets.** All comparative-design datasets containing human material (29, including E-TABM-69 from ArrayExpress), minus the 7 the pre-flight review took out: GSE120687 (immunoprecipitation arms only, no abundance contrast), GSE172221 (human arm's NF status unstated), GSE2841 (2 clinically attributed NF1 pheochromocytomas, no NF contrast), GSE325204 (comparator arm is two non-NF1 lines Cellosaurus classifies as melanoma), GSE56598 (NF2 status annotated only on the methylation arm), GSE5675 (no per-sample NF1 status, publication closed), GSE77205 (4 NF1 MPNSTs whose only in-series comparator is clear cell sarcoma)
- **`phase2-sample-overrides.csv` is authoritative** for which samples enter a contrast, overriding the Phase 1a per-sample labels. Sporadic samples inside mixed cohorts, mouse samples inside mixed-organism series, non-expression assays (ChIP, ATAC, methylation, RIP) and ambiguously labelled samples are excluded there with a reason, never deleted
- **No single merged matrix.** The 29 comparative human datasets span 28 distinct GPL platforms, so the pipeline runs per-dataset differential expression and combines the results by rank-based meta-analysis in Phase 3. Preprocessing therefore standardizes each dataset to its own normalized matrix plus a sample table, not to a common gene-by-sample matrix
- Single-cell datasets in the launch set are pseudobulked to one profile per patient (not per plate, well or library) before entering the per-dataset contrast
- Batch-effect correction applies within a dataset (platform, batch, FFPE vs fresh), not across them; cross-dataset heterogeneity is handled by the meta-analysis step instead
- Composition of the 22: 8 expression array, 7 bulk RNA-seq, 7 single-cell; 18 raw array files, 2 raw counts, 2 processed-matrix-only
- Keep the fallback for datasets with no control arm explicit: under the human-only first pass **7 of the 22 carry a human control sample** (GSE108524 4, GSE14038 10, GSE141801 7, GSE163071 9 by the frozen Phase 1a labels and 7 after the sample overrides, GSE232516 2, GSE234071 2, GSE41747 3 of its 18). Counting by `control_types` gives 10 and counting by labelled samples of any organism gives 9, because GSE181985 and GSE244433 carry only mouse isogenic controls and GSE41747's remaining 15 controls are mouse; those drop with the mouse track. E-MEXP-258 records `control_types = control_unaffected_donor_normal` with `n_control_samples = 0`, since ArrayExpress rows carry no sample-level labels, so it becomes the eighth only if the ArrayExpress labelling pass confirms the control arm. Either way most contrasts are between-subtype (MPNST vs neurofibroma, NF2-SWN vs non-NF2 schwannomatosis) rather than tumour vs normal. Write down what that assumes before running it
- **The overrides file has no arm column.** `phase2-sample-overrides.csv` records `de_role` (case / control / excluded_*) but not which side of the contrast a case sits on, while `phase2-non-geo-samples.csv` already carries `de_arm`. Six of the seven stated contrasts are between-subtype or between-genotype rather than case vs control, so the arm assignment currently survives only in the free-text `reason` field: GSE292071's 104 kept plates are all `de_role = case`, with the 11 NF2-SWN against 5 non-NF2-SWN patients recoverable only by reading that text. Add `de_arm` to the GEO overrides schema and backfill it for the datasets with a stated contrast before any design matrix is built
- Ingest readiness as labelled, from `phase-2/data/phase2-launchset-readiness.csv` (regenerate with `python phase-2/scripts/phase2_launchset_readiness.py`): **6 of the 22 are ready today**, and 9 once `de_arm` is backfilled, because GSE145064, GSE163071 and GSE66743 have nothing else outstanding. The rest need one of five things. (1) Mouse arms still in scope inside mixed series need `case_mouse_deferred` tags before the manifest step: GSE41747 48 samples, GSE244433 11, GSE181985 8, GSE179043 3. (2) Six datasets carry a single sample label among their in-scope samples and no stated contrast, so a contrast would have to come from subtype or grade text in `characteristics`, which has no column: GSE138347, GSE232528, GSE239561, GSE318927, GSE344687, GSE218493. (3) GSE218493 and GSE244433 need a ruling rather than a column: GSE218493 is 1 cutaneous against 1 plexiform neurofibroma, which is not a contrast at any n, and deferring GSE244433's mouse arm leaves exactly 1 human sample, so it has no human contrast and should come off the 22 for this pass while staying in the logs. (4) E-MEXP-258 still has no sample-level labels. (5) GSE207400 and GSE292071 are processed-matrix-only
- Remaining pre-ingestion items: the `de_arm` backfill above; expression-file selection for the two launch-set series carrying ChIP co-assays (GSE179043, GSE344687); a stated policy for the 2 processed-matrix-only datasets (GSE207400, GSE292071), which means accepting the authors' normalization and recording it; verifying that raw downloads actually resolve for every launch-set dataset, which has not been checked for any of them; labelling E-MEXP-258 and recording an explicit exclusion line for the 3 ArrayExpress rows outside the launch set (E-MEXP-2766 non-comparative, E-MTAB-13334 and E-MTAB-14222 mouse)
- Raw downloads land outside the repo under `build/phase2/` (already covered by `.gitignore`), never in `/data`. Check free disk before the first fetch: the 7 single-cell datasets dominate the footprint on a 16 GB laptop, and per Compute Requirements that is the trigger to move a specific step to Modal or an HPC cluster rather than to resize the laptop
- Establish a reproducible preprocessing pipeline per dataset, with the ingestion manifest, the per-dataset normalized matrix and the sample table all written to disk so Phase 3 can be re-run without re-downloading

### Methodological calls to settle before the pipeline is written

Each of these fixes what a per-dataset output file has to contain, so settling them now is cheaper than retrofitting 22 result files later. The recommendations are proposals for Kara to ratify or overrule, not decisions already taken.

1. **Differential expression engine per assay class.** Proposed: `limma` with `trend=TRUE` on the 8 expression arrays, `limma-voom` or `DESeq2` on the 2 raw-count sets (pick one and use it for both), and `limma-trend` on pseudobulked single-cell counts, so the 7 single-cell sets go through a sample-level test rather than a cell-level one.
2. **Meta-analysis method, which Phase 3 consumes.** Proposed: robust rank aggregation across per-dataset gene rankings. That choice means every per-dataset output must carry the full ranked gene list with a signed statistic and a direction, not only the genes passing a per-dataset threshold.
3. **Gene identifier space and mapping source, pinned by version.** The 22 span 17 distinct GPL platforms (28 across the 29 comparative human datasets). Proposed: map everything to HGNC symbols via a pinned Ensembl release, record the release in the manifest, and keep the original probe or gene id in the per-dataset output so a remap does not require a re-download.
4. **What the no-control fallback asserts.** With 7 control-carrying datasets out of 22, most contrasts compare two tumour states. Proposed: state in the manifest, per dataset, which arm is the reference and that the result is a between-state difference rather than a disease-vs-normal effect, so Phase 3 never mixes the two readings in one ranking.
5. **Which covariates ComBat may see.** Batch correction is within-dataset only, but none of platform, batch, or FFPE vs fresh exists as a column today; all three sit inside free-text `characteristics`. Proposed: extract them into the per-dataset sample table during ingestion, and run correction only where a covariate is actually populated.
6. **Patient id extraction per single-cell dataset.** Pseudobulk is defined as one profile per patient, so each single-cell dataset needs a stated rule for recovering the patient from sample titles; GSE292071 is several Smart-seq plates per patient and is the test case.

## Phase 3: Candidate Target Identification

**Claude tools:** Claude Code (analysis scripts for differential expression/pathway enrichment)

- Extend the existing KEGG-based pathway mapping step to work directly from raw expression data rather than pre-selected target names
- Run differential expression once per dataset against that dataset's own contrast (recorded in `phase-2/data/phase2-review-diagnosis.json`), then combine across datasets by rank-based meta-analysis rather than pooling samples; the launch set spans 28 platforms and most contrasts are between-subtype rather than tumour vs normal, so effect sizes are not comparable on a common scale
- Generate an initial candidate gene/target list from expression signal (e.g., differential expression, pathway enrichment)
- Label each candidate with disease (NF1, NF2-SWN, or SWN) and manifestation(s) per the labeling standard above, based on which dataset(s) it was derived from

## Phase 3b: Evidence Coverage Review and Manifestation Prioritization (decision point)

**Claude tools:** Claude Code (aggregation script and coverage chart)

- Aggregate candidate counts and evidence volume (number of supporting papers from Phase 1b, number of supporting datasets/candidates from Phase 3) per disease (NF1, NF2-SWN, SWN) x manifestation combination
- Generate a coverage visualization (heatmap or grouped bar chart) showing target count and evidence depth for each disease/manifestation combination, so sparse vs. well-supported areas are visible at a glance
- Review the chart and decide which manifestation(s) have enough evidence to justify carrying into Phase 4's drug-identification work now, versus which to defer given the budget/timeline constraints
- This is a human decision point, not something Claude should decide unprompted; document the decision and rationale (e.g., in `/docs`) so deprioritized manifestations are clearly deferred, not silently dropped
- Only the manifestation(s) selected here carry forward into Phases 4–7; deferred manifestations' candidate lists stay in the repo for a future pass

## Phase 4: Drug Interaction, Selectivity, and Tractability Layer

**Claude tools:** Claude Code (building/testing the DGIdb, Guide to Pharmacology, ClinicalTrials.gov, openFDA/DailyMed, and DrugBank API integrations), **ChEMBL connector** (compound_search, drug_search, get_mechanism, target_search, get_bioactivity, get_admet, grounds queries directly in the database instead of Claude's training data), **ClinicalTrials.gov connector** (search_trials, get_trial_details, search_by_sponsor, grounds clinical-stage queries directly in the database)

- Query DGIdb/ChEMBL for each candidate target **from the manifestation(s) selected in Phase 3b** to identify existing drugs with known interactions
- Query the **IUPHAR/BPS Guide to Pharmacology** (guidetopharmacology.org) REST API for expert-curated selectivity data, filtering target-ligand interactions by affinity to assess how selective a given drug/compound is for the candidate target versus related targets
- Note: Guide to Pharmacology has a documented, queryable API (JSON), so this integrates as a live query rather than a bulk-download/parsing step
- Optional secondary check: **ProbeMiner** (probeminer.icr.ac.uk), a computational selectivity score built on ChEMBL/BindingDB data via canSAR, useful as a cross-check against Guide to Pharmacology's curated selectivity calls. No public API found, so this would mean bulk-download/parsing similar to the earlier Chemical Probes Portal approach, add only if the cross-check is worth that integration cost
- **Clinical stage:** use ChEMBL's `max_phase` field (already available via the ChEMBL connector) as a fast first-pass filter, then query the **ClinicalTrials.gov connector** for trial-level detail (status, phase, conditions studied) on candidates that clear that filter
- **Approval status and availability:** query **DrugBank Open Data** (approved/investigational/experimental/withdrawn status, route of administration) and **openFDA** (Drugs@FDA approval history, structured label data). Neither has a connector, so both are bulk-download/parse integrations, similar cost to the Chemical Probes Portal approach
- **Safety, beyond ChEMBL's `get_admet`:** query **openFDA FAERS** for real-world post-market adverse event signals, and **SIDER** for side-effect frequency mined from package inserts, as two independent safety checks
- **Consolidation option:** before wiring ClinicalTrials.gov, openFDA, and DrugBank separately, evaluate the **Amass Connector** (unifies drugs, trials, regulatory approvals, genes, and patents: `get_amass_drugcore_record`, `get_amass_trialcore_record`, `get_amass_regulatorycore_record`), which may cover the same ground as those three sources through one connector instead of three separate scrapers
- **Delivery route and CNS-penetration filter:** pull the route-of-administration field from DailyMed/openFDA labels for each candidate drug, then cross-reference against the candidate's manifestation label from Phase 1b/3. Skin-localized manifestations (Cutaneous neurofibroma, ANNUBP/atypical neurofibroma) accept topical delivery; every other manifestation requires a systemic route (oral, IV, subcutaneous, etc.). For CNS-relevant manifestations specifically (Optic pathway glioma, High grade glioma, Non-optic LGG, Cognition/Behavioral/Learning), additionally check blood-brain-barrier penetration via ChEMBL's `get_admet` data, since a systemic drug that can't cross the BBB is still inappropriate for those targets. Flag mismatches explicitly (e.g., "topical-only, excluded for GIST target") rather than silently dropping them, so the rationale is auditable later
- Open gap: still need a source for tractability assessment on targets with no existing probe or drug; Compound VALET remains a candidate for this once it has more documentation, otherwise evaluate alternatives or literature-based review

## Phase 5: Cross-Disease Mechanistic Validation (Monarch Integration)

**Claude tools:** Claude Code (Mondo/DisMech/Monarch KG API integration)

- Standardize disease terms using Mondo
- Run DisMech mechanistic cross-checks to see whether similar mechanisms appear in related rare diseases
- Use Monarch KG as a partial ground-truth source to sanity-check candidate targets

## Phase 6: Evidence Strength Scoring

**Claude tools:** Claude Code (implementing/testing the scoring rubric)

- Define a scoring rubric that combines drug-interaction evidence, tractability, clinical stage, approval status, cross-disease mechanistic support, safety data, and the delivery-route/CNS-penetration flag into a single confidence signal per candidate
- Exclude or heavily downweight candidates flagged as delivery-inappropriate in Phase 4 (e.g., topical-only for a non-skin manifestation) rather than scoring them on the same footing as appropriate candidates
- Flag candidates with insufficient evidence rather than presenting all hits as equally strong
- Preserve each candidate's disease and manifestation labels through scoring so the final output can be filtered/grouped by both, not just ranked by score

## Phase 7: Literature Validation Layer

**Claude tools:** Claude Code (comparison/overlap scripts), Advanced Research (if new literature gaps surface)

- Compare the expression-derived candidate list against the literature-derived candidate list from Phase 1b, to check overlap and identify targets found by only one approach; weight literature-only matches by whether that finding was confirmed via full text or abstract-only per Phase 1b's access notes
- Use literature review as a fallback analysis path for datasets flagged unusable earlier in the pipeline

## Phase 8: Claude-Agent Workflow Integration

**Claude tools:** Claude Code (agent/orchestration build), Claude Agent SDK if you want the finished pipeline running as a standalone tool rather than inside chat sessions

- Wrap Phases 3–7 into a Claude-agent-operable workflow (agent orchestrates queries across KEGG, DGIdb/ChEMBL, Guide to Pharmacology, Monarch, and literature sources)
- Test the agent on a small set of known NF-relevant genes to validate outputs against expected results

## Phase 9: Testing and Evaluation

**Claude tools:** Claude Code (running the pipeline, debugging), Advanced Research (checking candidate quality against literature-known targets)

- Run the full pipeline end-to-end on selected GEO datasets
- Evaluate candidate quality against literature-known NF drug targets where possible
- Iterate on scoring rubric and data source integrations based on results

## Phase 10: Documentation and Reporting

**Claude tools:** Claude (Word/docx skill for the written report), Claude (PowerPoint skill if a slide-based report is wanted for the funder)

- Document the pipeline architecture, data sources, and scoring methodology
- Prepare progress reporting for Anthropic per grant requirements
- Track spend against the ~$10–20K budget scope

## Open Items to Resolve

- Revisit Compound VALET once it has more documentation for the remaining tractability gap; safety is now largely covered by ChEMBL's ADMET data, openFDA FAERS, and SIDER. A real Open Targets connector also exists if you want to reconsider it for tractability despite moving away from it earlier
- Evaluate the Amass Connector as a possible single replacement for the separate ClinicalTrials.gov, openFDA, and DrugBank integrations before building all three
- Resolved: the launch set is the 22 datasets named in Phase 2, and mouse-model datasets do not carry into the Phase 2-3 first pass; they are a separate later track off the same manifest. Both are recorded in the Phase 2 section rather than here
- Two Phase 2 rulings still need Kara: whether GSE244433 comes off the 22 once its mouse arm is deferred (1 human sample left, no contrast), and what to do with the six single-label datasets whose contrast would have to be read out of free-text sample annotation (GSE138347, GSE232528, GSE239561, GSE318927, GSE344687, GSE218493)
- The six methodological calls under Phase 2 need ratifying before pipeline code is written, since they decide the contents of all 22 per-dataset output files
- Several sources named in Phases 4-5 have no connector on this platform (DGIdb, Guide to Pharmacology, DrugBank, SIDER, ProbeMiner, Monarch/Mondo/DisMech, the Amass Connector) and several of their domains are blocked by the sandbox network allowlist. Each needs either an approved domain or a substitute (Open Targets, openFDA, ChEMBL, ClinicalTrials.gov and KEGG are reachable) before Phase 4-5 wiring starts

## Appendix: Phase 1a / 1b Prompts

**Model/modality guidance:** Prefer **Claude Science** over regular claude.ai chat for this phase specifically. Claude Science natively connects to GEO (alongside ChEMBL, UniProt, PDB, Ensembl, Reactome, ClinVar, and more), so Prompt 1's dataset search becomes a live structured query rather than search-and-verify. It also runs a built-in reviewer agent that checks citations and calculations automatically, a stronger hallucination safeguard than manual spot-checking. Use Claude Opus 5 for both prompts either way, this step is synthesis-heavy (reconciling many database hits and papers into coverage judgment calls), not high-volume/low-latency work. No pre-curated paper set is needed for Prompt 2, it sources papers directly via search (PubMed connector/Advanced Research). If running in regular claude.ai chat instead, turn on Advanced Research for both prompts.

**Minimizing hallucination:**
- In Claude Science, GEO's native connection plus the reviewer agent largely covers this; still spot-check any accession number that ends up in the final list, since that's a detail worth a human sanity check regardless of the safeguards upstream
- Connect the **PubMed connector** for Prompt 2 (available in both claude.ai and Claude Science), so literature claims are grounded in the actual database rather than general web search snippets
- For Prompt 2, require Claude to report full-text vs. abstract-only access per paper, since a claim drawn only from an abstract carries more uncertainty than one verified against full text
- If running Prompt 1 in regular claude.ai chat rather than Claude Science, no dedicated GEO/ArrayExpress/SRA connector exists there, so have Claude fetch directly from NCBI's own GEO pages rather than relying on search snippets, and manually spot-check accession numbers

**Prompt 1 (Phase 1a: dataset search)**

> I'm scoping public gene expression data sources for a neurofibromatosis (NF1, NF2-SWN, schwannomatosis) drug target discovery pipeline. Search GEO (primary) and ArrayExpress/BioStudies (secondary) for expression datasets (bulk RNA-seq, microarray, and single-cell/single-nucleus) covering: cutaneous neurofibroma, plexiform neurofibroma, ANNUBP/atypical neurofibroma, MPNST, optic pathway glioma and the other NF1 manifestations; vestibular and non-vestibular schwannoma, meningioma and ependymoma (NF2-SWN); and SMARCB1/LZTR1-driven schwannomatosis. Restrict to expression assay types. Include both human and mouse-model datasets and label each with its organism.
>
> Exclude sporadic tumors: a dataset counts only if its samples are NF-associated (germline NF1/NF2/SMARCB1/LZTR1, an explicitly NF patient cohort, or an engineered NF genotype). For mixed cohorts, keep the dataset and mark which samples are sporadic. Record how germline/NF status was established for each dataset, and keep the excluded datasets in a separate table rather than dropping them silently.
>
> For each dataset report: accession, platform/assay type, organism, disease (NF1, NF2-SWN, or SWN), manifestation(s) from the fixed list in this plan applied as-is, study design (tumor vs normal / tumor-subtype or grade comparison / in vitro perturbation / xenograft / single-arm profiling), total sample count, control samples broken down by type (matched adjacent normal, unaffected-donor normal, isogenic or engineered, non-NF tumor comparator, none), data availability (raw counts / raw array files / processed matrix only / none), any superseries-subseries relation, publication, and link.
>
> Run this as a script that records the exact query strings and the search date, and verify that every reported accession resolves against NCBI. Present results grouped by disease and manifestation, and show disease/manifestation combinations with zero coverage explicitly rather than omitting them.

**Prompt 2 (Phase 1b: literature-derived targets, run in parallel)**

> Search the literature (PubMed and other relevant databases) for genes/targets implicated as disease drivers or therapeutic targets in NF1, NF2, and schwannomatosis. For each target, note: gene/target name, disease (specifically NF1, NF2-SWN, or SWN, flag as "not specified" if the source doesn't distinguish), manifestation(s) from this fixed list (apply as-is, don't paraphrase): Bone defects; Cardiovascular issues; Cognition / Behavioral / Learning; Sleep; Cutaneous neurofibroma; Ependymoma; Gastrointestinal stromal tumor (GIST); Hematologic malignancies; High grade glioma; Malignant peripheral nerve sheath tumor (MPNST); Meningioma; Optic pathway glioma; Non-optic LGG; Pain; Plexiform neurofibroma; ANNUBP / atypical neurofibroma; Pulmonary disease; Non-vestibular schwannoma; Vestibular schwannoma; Other. Also note the proposed mechanism and which paper(s) support it.
>
> For every paper you cite, explicitly state whether you had access to the full text or only the abstract/title/metadata. If a finding is drawn only from an abstract, flag it as lower-confidence than one confirmed against full text.
>
> Compile this into a single candidate target list I can later compare against an expression-data-derived candidate list, so keep the format simple: one row per gene/target/manifestation combination, not organized by paper.

## Appendix: Phase 2 Prompt

**Model/modality guidance:** Claude Code with Sonnet 5. This is well-established methodology (standard preprocessing, batch correction like ComBat) turned into working scripts, not a task needing Opus-level judgment.

**Minimizing hallucination:** No dedicated GEO-download connector exists. Have Claude Code fetch the current GEOparse/GEOquery documentation directly rather than writing from memorized API syntax, since package APIs shift across versions.

> Write a preprocessing pipeline that ingests the Phase 2 launch set (the 22 datasets named in the Phase 2 section of this plan, listed with their readiness status in `phase-2/data/phase2-launchset-readiness.csv`) and standardizes **each dataset to its own normalized matrix plus a sample table**, not to one merged matrix: the launch set spans 17 distinct platforms and most contrasts are between-subtype, so cross-dataset pooling is handled by rank-based meta-analysis in Phase 3 instead. Take sample membership and contrast arm from `phase-2/data/phase2-sample-overrides.csv` and `phase-2/data/phase2-non-geo-samples.csv`, which override the Phase 1a per-sample labels, and flag samples with missing metadata rather than guessing. Pseudobulk single-cell datasets to one profile per patient. For datasets with no control arm, record per dataset which arm is the reference and document what the between-state comparison assumes. Include batch-effect correction (e.g., ComBat) as a separate, clearly labeled within-dataset step so it can be toggled off, and only where its covariate is actually populated. Cite the exact package/version and doc source you used for each preprocessing function, and verify current syntax against that source rather than a remembered API.

## Appendix: Phase 3 Prompt

**Model/modality guidance:** Claude Code with Sonnet 5. Standard differential expression/pathway enrichment code.

**Minimizing hallucination:** Have Claude fetch the current KEGG REST API documentation directly before writing the pathway-mapping code, since endpoint syntax should be verified against source rather than memory.

> Using the preprocessed expression matrix from Phase 2, run differential expression analysis and pathway enrichment to generate an initial candidate gene/target list. Extend the existing KEGG-based pathway mapping approach so it works from raw expression data rather than pre-selected target names. Verify KEGG REST API endpoint syntax against current documentation before writing the query code. Label each candidate target with disease (NF1, NF2-SWN, or SWN, based on which dataset it was derived from) and manifestation(s) from the fixed list in this plan's labeling standard.

## Appendix: Phase 3b Prompt

**Model/modality guidance:** Claude Code with Sonnet 5 for the aggregation script and chart; this is a data summarization task, not a judgment call. You (Kara) make the actual prioritization decision from the chart.

**Minimizing hallucination:** This phase only aggregates counts already produced in Phases 1b and 3, so there's little room for new hallucinated facts. The main risk is silently dropping a disease/manifestation combination with zero hits instead of showing it as an explicit zero.

> Combine the literature-derived candidate list from Phase 1b and the expression-derived candidate list from Phase 3. For every combination of disease (NF1, NF2-SWN, SWN) and manifestation (from the fixed list in this plan), count: number of literature-supported targets, number of expression-derived targets, and total supporting papers/datasets. Show combinations with zero evidence explicitly rather than omitting them. Generate a heatmap or grouped bar chart of this coverage, save it to `/docs`, and present the underlying counts as a table so I can decide which manifestation(s) to prioritize for Phase 4.

## Appendix: Phase 4 Prompt

**Model/modality guidance:** Claude Code with Sonnet 5 for the API wiring itself; use Opus 5 for the delivery-route/CNS-penetration filtering logic and if you decide to revisit the Open Targets tractability/safety question, since both are judgment calls rather than routine code.

**Minimizing hallucination:** Connect the **ChEMBL connector** (compound_search, drug_search, get_mechanism, target_search, get_bioactivity, get_admet) and the **ClinicalTrials.gov connector** (search_trials, get_trial_details) so drug-interaction, selectivity, and clinical-stage queries hit real databases directly instead of Claude recalling data from training. For Guide to Pharmacology, DrugBank, openFDA, and DailyMed, no connector exists yet, so verify current API/data-format syntax against each one's own documentation before wiring the query.

> For each candidate target in the manifestation(s) selected in Phase 3b, query DGIdb/ChEMBL for existing drug interactions (use the ChEMBL connector where possible), query the Guide to Pharmacology API for expert-curated selectivity data, and use ChEMBL's max_phase field plus the ClinicalTrials.gov connector for clinical stage. Query DrugBank Open Data and openFDA for approval status, and openFDA FAERS plus SIDER for safety signals beyond ChEMBL's ADMET data. For each candidate drug, pull its route of administration from DailyMed/openFDA labels and flag it as inappropriate if the route doesn't match the target's manifestation (topical is only appropriate for Cutaneous neurofibroma and ANNUBP/atypical neurofibroma; all other manifestations need a systemic route). For CNS-relevant manifestations (Optic pathway glioma, High grade glioma, Non-optic LGG, Cognition/Behavioral/Learning), additionally check blood-brain-barrier penetration via ChEMBL's ADMET data. For targets with no drug match, note this explicitly rather than leaving it blank. Report per-target: known drugs (if any), clinical stage, approval status, selectivity data, safety signals, route/CNS-penetration flag, and source for each claim.

## Appendix: Phase 5 Prompt

**Model/modality guidance:** Claude Code with Sonnet 5 for the API wiring; Opus 5 for interpreting DisMech mechanistic cross-check results, since judging whether two diseases share a mechanism is a reasoning task, not routine code.

**Minimizing hallucination:** No Monarch-specific connector exists. Have Claude fetch current Mondo, DisMech, and Monarch KG API documentation directly before writing integration code, rather than relying on remembered endpoint structures.

> Standardize the candidate targets' associated disease terms using Mondo, then run DisMech mechanistic cross-checks to identify whether the same mechanism appears in other rare diseases. Use Monarch KG as a partial ground-truth check. Verify all three APIs' current endpoint syntax against their own documentation before writing the integration code, and report the source/version for each API call.

## Appendix: Phase 6 Prompt

**Model/modality guidance:** Claude Opus 5. Designing the scoring rubric is a judgment call combining several evidence types into one confidence signal, worth the deeper reasoning; implementation of the rubric in code can drop to Sonnet 5 once the logic is defined.

**Minimizing hallucination:** This phase works entirely from data already retrieved in Phases 4–5, so the main risk is Claude quietly filling gaps in that data rather than flagging them. Instruct it explicitly not to do that.

> Using the drug-interaction, selectivity, mechanistic, and (where available) safety data gathered in Phases 4–5, propose a scoring rubric that combines this evidence into a single confidence signal per candidate target. For any candidate missing a data type, flag it as missing rather than estimating or inferring a value. Preserve each candidate's disease (NF1, NF2-SWN, or SWN) and manifestation label(s) alongside its score so results can be filtered/grouped by both. Show your rubric logic explicitly before applying it, so it can be reviewed before being run across the full candidate list.

## Appendix: Phase 7 Prompt

**Model/modality guidance:** Claude Opus 5, since judging whether two independently-derived target lists genuinely overlap (versus superficially similar gene names) is a reasoning task.

**Minimizing hallucination:** Reuse the **PubMed connector** from Phase 1b for any literature fallback lookups needed for datasets flagged unusable.

> Compare the expression-derived candidate list from Phase 3/6 against the literature-derived candidate list from Phase 1b, matching on gene/target AND on disease (NF1, NF2-SWN, SWN) plus manifestation, since the same gene can be relevant to one disease/manifestation combination in one list and a different one in the other. Report exact overlaps, near-misses (same pathway/mechanism but different specific gene, or same gene but different manifestation), and targets found by only one approach. Weight literature-only matches by whether Phase 1b confirmed that finding via full text or abstract-only. For any dataset flagged unusable earlier in the pipeline, use PubMed (via the connector) to find literature-based candidates as a fallback, and cite the specific paper for each.

## Appendix: Phase 8 Prompt

**Model/modality guidance:** Claude Code with Sonnet 5 for building the orchestration; switch to Opus 5 specifically for debugging integration failures across phases, since diagnosing where a multi-step agent workflow broke is where deeper reasoning pays off most.

**Minimizing hallucination:** No connector changes here beyond what's already wired into Phases 2–7. The main risk is the agent silently masking an upstream API failure. Instruct it to surface failures rather than substituting placeholder data.

> Wrap the Phase 3–7 steps into a single Claude-agent-operable workflow. If any API call in this chain fails or returns no data, the agent must report that failure explicitly rather than proceeding with a placeholder or estimated value. Test the full workflow on [a small set of known NF-relevant genes], and report where outputs diverge from expected results.

## Appendix: Phase 9 Prompt

**Model/modality guidance:** Claude Opus 5, since judging candidate quality against known biology is a reasoning task, not routine execution.

**Minimizing hallucination:** Use the **PubMed connector** for grounding literature comparisons rather than general web search.

> Run the full pipeline end-to-end on the finalized GEO datasets. Evaluate candidate quality by comparing outputs against literature-known NF drug targets (use the PubMed connector to verify each comparison against an actual paper, not a remembered claim). Report where the pipeline's output diverges from known biology, and whether that divergence suggests a scoring rubric issue or a genuinely novel finding.

## Appendix: Phase 10 Prompt

**Model/modality guidance:** Claude Sonnet 5 is sufficient for drafting; use the docx skill for the written report and the pptx skill if a slide-based report is wanted for the funder.

**Minimizing hallucination:** This phase should only restate findings already generated and verified in earlier phases. Instruct Claude not to introduce new claims about data sources, tools, or results that weren't part of the actual pipeline run.

> Draft a progress report documenting the pipeline architecture, data sources used, and scoring methodology, based only on what was actually run in Phases 1–9. Do not introduce new claims about tools, data sources, or results beyond what's in the prior phase outputs. Flag anywhere you're uncertain rather than smoothing over a gap.
