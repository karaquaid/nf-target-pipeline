# Project Plan: nf-target-pipeline

**Grant:** Anthropic AI for Science, rare disease research call
**Goal:** Build a Claude-agent-operable pipeline that takes raw expression data as input and outputs a prioritized, evidence-scored list of candidate drug targets for rare disease research (starting with NF).

---

## Disease and Manifestation Labeling Standard

Every dataset (Phase 1) and target (Phase 1b, 3, 4, 5, 6, 7) must be labeled with:

- **Disease:** NF1, NF2-SWN, or SWN (schwannomatosis). Use "Other" or "Not specified" only if the source genuinely doesn't distinguish, and flag that as a gap rather than guessing.
- **Manifestation(s):** one or more from this fixed list, applied as-is (don't paraphrase or substitute synonyms): Bone defects; Cardiovascular issues; Cognition / Behavioral / Learning; Sleep; Cutaneous neurofibroma; Ependymoma; Gastrointestinal stromal tumor (GIST); Hematologic malignancies; High grade glioma; Malignant peripheral nerve sheath tumor (MPNST); Meningioma; Optic pathway glioma; Non-optic LGG; Pain; Plexiform neurofibroma; ANNUBP / atypical neurofibroma; Pulmonary disease; Non-vestibular schwannoma; Vestibular schwannoma; Other

A dataset or target can carry more than one manifestation label if it's genuinely relevant to more than one (e.g. a gene implicated in both plexiform neurofibroma and MPNST progression). Carry these two labels through every downstream phase so the final scored candidate list (Phase 6) and comparison (Phase 7) can be filtered/grouped by disease and manifestation, not just by gene name.

## Compute Requirements

- Start laptop-first, using Claude Science to run the pipeline locally (macOS/Linux). Most of the work here (API queries against DGIdb/ChEMBL/Guide to Pharmacology/Monarch, plus standard differential expression and pathway enrichment on bulk RNA-seq/microarray data) is not GPU-heavy and doesn't need dedicated compute provisioned upfront
- Escalate only if scope expands to single-nuclei/spatial transcriptomics datasets (e.g., snRNA-seq datasets like GSE232766), which produce much larger matrices than the bulk NF2 datasets identified in Phase 1. If that happens, Claude Science can draft and submit that specific job to an HPC cluster or to Modal (cloud compute), scaling from a single GPU to hundreds as needed, rather than requiring bigger hardware from day one
- No need to pre-provision cloud compute or an HPC account before starting; revisit this only if a specific phase's dataset size clearly exceeds laptop capacity

## Version Control (GitHub)

- Repo name: **`nf-target-pipeline`** (karaquaid/nf-target-pipeline)
- Track this project in this GitHub repo from the start, using Claude Science (or Claude Code as a fallback) for repo setup and ongoing git operations (commits, branches, PRs) throughout every phase below
- Suggested repo structure: `/scripts` (ingestion, analysis, API integration code from Phases 2–6, 8), `/docs` (this project plan, scoring rubric writeups, grant progress reports from Phase 10), `/data` (small reference files only, e.g. candidate target lists; raw expression data stays out of the repo given file size and any data-use terms)
- Commit at the end of each phase, not just at the end of the project, so the repo reflects real progress and gives you a rollback point if a later phase's approach doesn't pan out
- Keep this plan document itself in the repo (e.g. `/docs/project-plan.md`) and update it in place as scope shifts, rather than letting the repo and the plan drift apart

## Phase 1: Scope and Data Source Finalization

**Claude tools:** Advanced Research (multi-source dataset search), web search (spot-checks and follow-up)

- Run a comprehensive search for public gene expression datasets (GEO, ArrayExpress, SRA) covering NF1, NF2, and schwannomatosis tumor types, using Claude's Advanced Research tool given the breadth of sources and disease subtypes involved
- Label each dataset found with disease (NF1, NF2-SWN, or SWN) and manifestation(s) per the labeling standard above
- Confirm public GEO datasets to use as the primary/starting data source (since Portal/Synodos data upload approval is not yet in place)
- Document which datasets have healthy controls vs. not, to define which need batch-effect handling as a secondary capability
- Flag any dataset only accessible through the NF Data Portal/Synapse rather than directly public on GEO/ArrayExpress, since those may carry different data-use terms
- Explicitly confirm that no NF-OSI/Synodos data will be uploaded into Claude at any point in this phase of the project
- Finalize scope statement: primary focus is candidate drug/target identification; batch-effect correction and no-control-dataset handling are secondary/bonus capabilities, not the headline

## Phase 1b: Literature-Derived Target Identification (runs in parallel with Phases 1–2)

**Claude tools:** Advanced Research (literature search across NF1/NF2/schwannomatosis), web search

- Search the literature for genes/targets already implicated in NF1, NF2, and schwannomatosis, sourced directly via search rather than a pre-curated paper set
- Label each target found with disease (NF1, NF2-SWN, or SWN) and manifestation(s) per the labeling standard above
- For each paper cited, record whether Claude had access to the full text or only the abstract/metadata, so findings drawn from abstracts alone can be weighted differently from those drawn from full text
- Compile this into a literature-derived candidate target list, independent of the expression-data pipeline
- Hold this list for comparison against the expression-derived candidate list in Phase 7, to check overlap and surface targets one approach finds that the other misses

## Phase 2: Data Ingestion and Preprocessing

**Claude tools:** Claude Code (writing/debugging ingestion and preprocessing scripts), Synapse.org connector (if pulling anything you're authorized to access there directly rather than manually)

- Build ingestion scripts to pull and standardize raw expression data from selected GEO datasets
- Implement (as secondary capability) batch-effect correction methods and a fallback approach for datasets lacking healthy controls
- Establish a reproducible preprocessing pipeline that outputs a clean expression matrix ready for downstream analysis

## Phase 3: Candidate Target Identification

**Claude tools:** Claude Code (analysis scripts for differential expression/pathway enrichment)

- Extend the existing KEGG-based pathway mapping step to work directly from raw expression data rather than pre-selected target names
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
- Decide final list of GEO datasets to launch with
- Determine whether/when to revisit NF-OSI/Synodos data inclusion pending Sage, NTAP, and Gilbert Family Foundation approval

## Appendix: Phase 1 / 1b Prompts

**Model/modality guidance:** Prefer **Claude Science** over regular claude.ai chat for this phase specifically. Claude Science natively connects to GEO (alongside ChEMBL, UniProt, PDB, Ensembl, Reactome, ClinVar, and more), so Prompt 1's dataset search becomes a live structured query rather than search-and-verify. It also runs a built-in reviewer agent that checks citations and calculations automatically, a stronger hallucination safeguard than manual spot-checking. Use Claude Opus 5 for both prompts either way, this step is synthesis-heavy (reconciling many database hits and papers into coverage judgment calls), not high-volume/low-latency work. No pre-curated paper set is needed for Prompt 2, it sources papers directly via search (PubMed connector/Advanced Research). If running in regular claude.ai chat instead, turn on Advanced Research for both prompts.

**Minimizing hallucination:**
- In Claude Science, GEO's native connection plus the reviewer agent largely covers this; still spot-check any accession number that ends up in the final list, since that's a detail worth a human sanity check regardless of the safeguards upstream
- Connect the **PubMed connector** for Prompt 2 (available in both claude.ai and Claude Science), so literature claims are grounded in the actual database rather than general web search snippets
- For Prompt 2, require Claude to report full-text vs. abstract-only access per paper, since a claim drawn only from an abstract carries more uncertainty than one verified against full text
- If running Prompt 1 in regular claude.ai chat rather than Claude Science, no dedicated GEO/ArrayExpress/SRA connector exists there, so have Claude fetch directly from NCBI's own GEO pages rather than relying on search snippets, and manually spot-check accession numbers

**Prompt 1 (Phase 1: dataset search)**

> I'm scoping public gene expression data sources for a neurofibromatosis (NF1, NF2, and schwannomatosis) drug target discovery pipeline. Search GEO, ArrayExpress, and SRA (bulk RNA-seq, microarray, and single-cell/single-nucleus) for expression datasets covering: cutaneous neurofibroma, plexiform neurofibroma, MPNST (NF1); vestibular schwannoma and other schwannomas, meningioma (NF2/schwannomatosis); and SMARCB1/LZTR1-driven schwannomatosis specifically.
>
> For each dataset, report: accession number, platform/assay type, disease (specifically NF1, NF2-SWN, or SWN, flag as "not specified" if the source doesn't distinguish), manifestation(s) from this fixed list (apply as-is, don't paraphrase): Bone defects; Cardiovascular issues; Cognition / Behavioral / Learning; Sleep; Cutaneous neurofibroma; Ependymoma; Gastrointestinal stromal tumor (GIST); Hematologic malignancies; High grade glioma; Malignant peripheral nerve sheath tumor (MPNST); Meningioma; Optic pathway glioma; Non-optic LGG; Pain; Plexiform neurofibroma; ANNUBP / atypical neurofibroma; Pulmonary disease; Non-vestibular schwannoma; Vestibular schwannoma; Other. Also report total sample count, number of matched healthy/normal-tissue controls (flag zero-control datasets explicitly), and a link.
>
> Separately flag any dataset only accessible through the NF Data Portal/Synapse rather than directly public on GEO/ArrayExpress, since those may carry different data-use terms.
>
> Present results as a table grouped by disease and manifestation, and call out any disease/manifestation combination with sparse or no coverage.

**Prompt 2 (Phase 1b: literature-derived targets, run in parallel)**

> Search the literature (PubMed and other relevant databases) for genes/targets implicated as disease drivers or therapeutic targets in NF1, NF2, and schwannomatosis. For each target, note: gene/target name, disease (specifically NF1, NF2-SWN, or SWN, flag as "not specified" if the source doesn't distinguish), manifestation(s) from this fixed list (apply as-is, don't paraphrase): Bone defects; Cardiovascular issues; Cognition / Behavioral / Learning; Sleep; Cutaneous neurofibroma; Ependymoma; Gastrointestinal stromal tumor (GIST); Hematologic malignancies; High grade glioma; Malignant peripheral nerve sheath tumor (MPNST); Meningioma; Optic pathway glioma; Non-optic LGG; Pain; Plexiform neurofibroma; ANNUBP / atypical neurofibroma; Pulmonary disease; Non-vestibular schwannoma; Vestibular schwannoma; Other. Also note the proposed mechanism and which paper(s) support it.
>
> For every paper you cite, explicitly state whether you had access to the full text or only the abstract/title/metadata. If a finding is drawn only from an abstract, flag it as lower-confidence than one confirmed against full text.
>
> Compile this into a single candidate target list I can later compare against an expression-data-derived candidate list, so keep the format simple: one row per gene/target/manifestation combination, not organized by paper.

## Appendix: Phase 2 Prompt

**Model/modality guidance:** Claude Code with Sonnet 5. This is well-established methodology (standard preprocessing, batch correction like ComBat) turned into working scripts, not a task needing Opus-level judgment.

**Minimizing hallucination:** No dedicated GEO-download connector exists. Have Claude Code fetch the current GEOparse/GEOquery documentation directly rather than writing from memorized API syntax, since package APIs shift across versions. If you reconnect the **Synapse.org connector**, use it to verify any dataset's provenance/metadata directly against Synapse rather than trusting a scraped description.

> Write a preprocessing pipeline that ingests the GEO datasets identified in Phase 1 [list accessions], standardizes them into a single expression matrix, and flags samples with missing metadata. For datasets without healthy controls, implement a fallback approach and document what that fallback assumes. Include batch-effect correction (e.g., ComBat) as a separate, clearly labeled step so it can be toggled off. Cite the exact package/version and doc source you used for each preprocessing function, and verify current syntax against that source rather than a remembered API.

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
