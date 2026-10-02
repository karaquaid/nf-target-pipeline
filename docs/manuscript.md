# Manuscript draft: nf-target-pipeline

**Status:** working draft. Framing is settled: a resource paper whose method is also a
resource, so the protocol is written to be reused rather than as internal detail.
Phases 1a and 1b are complete and written as prose; everything downstream is an outline.
Do not circulate.

**How to read the markers.**

- `[FILL IN]` marks something only you can supply: authorship, affiliations, framing
  decisions, clinical judgement, anything about the funder relationship.
- `[OUTLINE]` marks a section whose content does not exist yet because the phase has not
  run. The bullets under it say what will go there and what it depends on.
- `[CHECK]` marks a claim I drafted that I think is right but have not verified against a
  primary source, or that rests on a judgement you may want to make differently.

**Numbers.** Every count in the Phase 1a and 1b sections comes from the committed tables as
of this draft. They are not final: the Phase 1b PDF queue still has 40 papers, and reading
any of them can move a row between evidence tiers. Before submission, re-read the numbers
off `phase-1b/docs/phase1b-literature-targets.md` and `phase-1a/docs/phase1a-dataset-scope.md`,
which are regenerated from the tables, rather than editing them here by hand.

| Phase | Status | Section here |
|---|---|---|
| 1a dataset scope | complete | Methods 2.3, Results 3.1 |
| 1b literature targets | complete | Methods 2.4, Results 3.2 and 3.3 |
| 2 ingestion and preprocessing | not started | Methods 2.5 outline |
| 3 expression-derived candidates | not started | Methods 2.6, Results 3.4 outline |
| 3b coverage review | not started, human decision point | Methods 2.7, Results 3.5 outline |
| 4 tractability and drug layer | not started | Methods 2.8, Results 3.6 outline |
| 5 cross-disease validation | not started | Methods 2.9, Results 3.7 outline |
| 6 evidence scoring | not started | Methods 2.10, Results 3.8 outline |
| 7 convergence with literature | not started | Methods 2.11, Results 3.9 outline |
| 8 agent workflow | not started | Methods 2.12 outline |
| 9 evaluation | not started | Results 3.10 outline |

---

## Title

This is a resource paper with two resources: the NF evidence map (the tables) and the method
that produced it (the protocol and the code). Both claims have to be made explicitly, because
a reader who takes it for a findings paper will ask why there is no validated hit, and a
reader who takes it for a pure data descriptor will not reuse the protocol.

> `[FILL IN]` Pick one. Both say resource plus method; they differ in which leads.
>
> 1. "An evidence-graded map of candidate drug targets in neurofibromatosis, and a
>    provenance-tracking protocol for building one in a rare disease"
> 2. "Grading the evidence behind rare-disease drug targets: a neurofibromatosis target map
>    and a reusable verification protocol"

**Authors:** `[FILL IN]`
**Affiliations:** `[FILL IN]`
**Corresponding author:** `[FILL IN]`

**Suggested article type:** resource, database or methods article depending on the journal.
`[FILL IN]` A journal that has both a resource and a protocol format may want this split in
two; a single paper is only worth it if the protocol is presented as transferable rather than
as the methods behind our tables.

## Abstract

> `[OUTLINE]` Write last, once Phase 3b has fixed the scope. Structure, 250 words:
>
> - Background, 2 sentences: NF target discovery is constrained less by biology than by
>   evidence that is scattered, unverified, and mostly about one disease.
> - Gap, 1 sentence: published target claims are not graded by whether anyone read the paper,
>   and expression data coverage is unknown per manifestation.
> - What we did, 3 sentences: dataset inventory, literature target map with full-text
>   verification, expression-derived candidates, convergence analysis.
> - Numbers, 2 sentences: pull the final counts from the phase write-ups.
> - What it means, 2 sentences: where the evidence actually is, and which manifestations
>   cannot be prioritised on current evidence regardless of method.

## 1. Introduction

Neurofibromatosis type 1 (NF1), NF2-related schwannomatosis (NF2-SWN) and schwannomatosis
(SWN) are germline tumour-predisposition syndromes whose manifestations span peripheral nerve
sheath tumours, central nervous system tumours, skeletal and cardiovascular features, pain,
and cognitive and behavioural phenotypes. The genetic causes have been known for three
decades, and one targeted therapy, the MEK1/2 inhibitor selumetinib, is approved for
inoperable plexiform neurofibroma. Beyond that single node, therapeutic options remain
limited, and most manifestations have no targeted agent at all.

Target discovery in this setting is limited less by the absence of candidate biology than by
the state of the evidence about it. Three problems recur.

1. **Published target claims are not graded by how well they were checked.** A claim that a
   gene is a therapeutic target in a schwannoma carries the same apparent weight whether it
   rests on a randomised trial, a single cell-line experiment, or a sentence in a review
   abstract that no one has traced to its source.
2. **Expression data is scattered and unevenly distributed across manifestations.** Public
   datasets exist, but how many bear on a given manifestation, in which organism, and with
   what comparator, has not been established. A manifestation can appear to lack candidate
   targets simply because no dataset addresses it.
3. **The three diseases are not evidentially comparable.** Work concentrates on NF1 and on a
   few tumour types, so a method that treats all disease and manifestation combinations
   symmetrically will report absence of evidence as evidence of absence.

> `[FILL IN]` One paragraph on why this matters clinically, written from your own practice
> and the patient community's priorities. Pain and cognitive phenotypes are where the
> evidence is thinnest and, I suspect, where unmet need is highest, but that is your
> judgement to make and to cite, not mine.

We present two linked resources that address these three problems directly.

The first is an evidence map for NF: an inventory of the public expression data that exists
per disease and manifestation, and a candidate target list in which every claim carries the
depth at which it was checked, the papers behind it, and whether those papers were read in
full or only as abstracts.

The second is the method that produced it, which we present as a protocol rather than as
internal detail. Its components are generic: a fixed manifestation vocabulary applied
verbatim so coverage can be counted across heterogeneous sources; a three-route ladder for
obtaining full text that recovers substantially more papers than any single route; a
per-paper verdict rubric that judges each claim against the complete article body and records
what the body actually studies; a provenance schema in which every row states its evidence
tier and access route; scope exclusions implemented as reversible flags rather than
deletions; and outputs regenerated by committed code so that prose and tables cannot drift.
None of this is specific to neurofibromatosis. It is specific to the situation of a rare
disease whose literature is small enough to read exhaustively and uneven enough that counting
papers misleads.

> `[CHECK]` The novelty claim needs care. Target-prioritisation frameworks are not new, and
> Open Targets already scores gene-disease associations at scale. What we claim is narrower
> and, I think, defensible: that grading each claim by verification depth changes the ranking,
> and that the protocol for doing so is transportable to other rare diseases. A survey of
> existing rare-disease prioritisation frameworks belongs here before submission, and if one
> already grades by full-text verification, this claim has to be rewritten rather than
> softened.

## 2. Methods

### 2.1 Design principles and reusable components

Six commitments shape every phase, and they are the part of this work we expect to transfer
to other rare diseases. Each is stated here once rather than repeated per phase, with the
file that implements it.

1. **A fixed label vocabulary, applied verbatim.** Disease and manifestation labels are fixed
   in advance (Section 2.2) and never invented at the point of use, so coverage can be counted
   across datasets, papers and candidates on the same axes. The cost is a residual "Other"
   bucket, which we report rather than hide.
2. **Provenance travels with every claim.** Each target row states how many papers support
   it, which papers, whether each was read in full or only as an abstract, by which retrieval
   route, and the resulting evidence tier. A reader can audit any single row back to an
   article body without rerunning anything.
3. **Absence is distinguished from unverified presence.** A claim nobody has checked is
   tiered `abstract only` rather than scored as weak evidence, and a manifestation with no
   rows is reported as empty rather than omitted. The two are different findings and the
   tables keep them apart.
4. **Scope exclusions are flags plus derived tables, never deletions.** Sporadic evidence,
   germline driver genes and contradicted rows are excluded from the candidate list by a
   filter in one script, while the full annotated table retains them. Any exclusion can be
   reversed, widened or audited by changing that filter.
5. **Outputs are regenerated by committed code.** The write-ups, coverage matrices and figures
   are produced by scripts in the repository, so a count in prose cannot drift from the table
   it describes. Counts that describe past process rather than current state are held in an
   explicit history block with the commit that established each.
6. **Human decisions are recorded as decisions.** Scope choices, the manifestation
   prioritisation in Phase 3b, and every hand override of a model call are written down with
   their rationale, so a later reader can tell a judgement from a computation.

| Reusable component | Where it lives |
|---|---|
| Disease and manifestation vocabulary | `docs/project-plan.md` |
| Search strategy and per-record classification rubric | `phase-1a/scripts/phase1a_geo_search.py`, `phase1a_classify.py` |
| Three-route full-text retrieval ladder | described in Section 2.4 |
| Per-paper claim verdict rubric | described in Section 2.4 |
| Provenance and evidence-tier schema | `phase-1b/data/phase1b-candidate-targets.csv` columns |
| Target annotation scheme (biomarker, genotype-restricted, microenvironment) | `phase-1b/data/phase1b-target-annotations.csv` |
| Scope filter and derived-table pattern | `phase-1b/scripts/make_phase1b_candidates.py` |
| Report and figure regeneration | `phase-1b/scripts/build_phase1b_report.py`, `make_phase1b_figure.py` |

> `[CHECK]` The retrieval ladder and the verdict rubric are currently described in prose in
> Section 2.4 rather than packaged as a standalone script. If the protocol is a headline
> resource, they should be extracted into `scripts/` as a reusable module with the disease
> vocabulary as a parameter. That is a modest piece of work and it would make the transfer
> claim concrete rather than aspirational.

### 2.2 Disease and manifestation labelling standard

Every dataset, paper and candidate target carries a disease label (NF1, NF2-SWN or SWN) and
one or more manifestation labels drawn verbatim from a fixed twenty-term vocabulary: Bone
defects; Cardiovascular issues; Cognition / Behavioral / Learning; Sleep; Cutaneous
neurofibroma; Ependymoma; Gastrointestinal stromal tumor (GIST); Hematologic malignancies;
High grade glioma; Malignant peripheral nerve sheath tumor (MPNST); Meningioma; Optic
pathway glioma; Non-optic LGG; Pain; Plexiform neurofibroma; ANNUBP / atypical neurofibroma;
Pulmonary disease; Non-vestibular schwannoma; Vestibular schwannoma; Other. The vocabulary is
fixed in advance so that coverage can be counted across heterogeneous sources, and labels are
never invented at the point of use.

Sporadic tumours are out of scope. Evidence that cannot be attributed to germline NF disease
is excluded, including sporadic tumours carrying the same somatic lesion, such as
*NF2*-mutant sporadic meningioma. This is a scope decision rather than a claim that the
biology differs, and its consequences are quantified in Results.

> `[CHECK]` The vocabulary has no disease-level slot, so a claim about NF1 as a whole with no
> manifestation attached is forced into "Other". We hit this repeatedly in Phase 1b. If a
> term is added before submission, every count in this draft changes.

### 2.3 Public expression dataset inventory (Phase 1a)

Twenty-seven E-utilities queries against GEO DataSets, one per manifestation plus
disease-level and mouse-model catch-alls, restricted to series records and expression assay
types, returned 415 series. For each hit the series and per-sample SOFT headers were
retrieved, 12,778 sample records in total. Each series was classified by a single model pass
against a written scope rubric covering disease, manifestations, the basis of its NF
association, material, study design, single-cell status and control types; in-scope series
then had every sample labelled individually. Six free-text ArrayExpress searches added five
experiments not mirrored from GEO, curated by hand. Superseries and subseries pairs share
samples, so datasets were deduplicated for counting. Scripts and tables are listed in the
Phase 1a write-up.

### 2.4 Literature-derived target identification (Phase 1b)

Thirty-two PubMed queries spanning the three diseases crossed with the manifestation
vocabulary, relevance-sorted and restricted to 2005 onward, returned 492 articles; abstracts
were retrieved for 482. Each abstract was passed to a model extraction step returning gene,
disease, manifestation or manifestations from the fixed list, role, mechanism and study
system, with instructions not to extract cohort-defining gene mentions or assay reagents.
Gene strings were normalised against official HGNC symbols; entities that are genuinely a
family, complex or pathway were retained as the label and expanded into constituent gene
symbols in a separate column.

Every target claim was then verified against full text where full text could be obtained.
Three retrieval routes were used in sequence: the NCBI PMC open-access package, the Europe
PMC open-access subset, and NCBI efetch against PMC identifiers, which returns NIH author
manuscripts that the Europe PMC endpoint refuses. Papers reachable by none of these were
obtained as publisher PDFs by the corresponding author under institutional subscription and
matched to the corpus by DOI, or by title where the file carried no DOI. For each paper, every
target claim attributed to it was judged against the complete article body with reference
sections removed, returning a verdict of supported, partially supported or not supported, the
mechanism as stated in the full text, the study system, and the manifestation the body
actually studies. Manifestation corrections were applied per paper rather than per row, so a
paper that studies a different manifestation moves only its own support. Verdicts from a later
round supersede earlier ones.

Rows were assigned an evidence tier from their verdicts: full-text supported, full-text
partial, or abstract only. Rows whose read papers contradict the claim are excluded from the
candidate list and retained in an annotated audit table. The germline NF disease genes
(*NF1*, *NF2*, *SMARCB1*, *LZTR1*, *SPRED1*) are likewise excluded as candidates, since their
role is established, and retained with a flag. Preprints are identified by DOI prefix and
journal string and flagged at both paper and row level.

Three further flags were curated per target label: whether the entity is more useful as a
biomarker than as something a drug acts on, whether it is relevant only to patients carrying
a particular genotype, and whether a drug against it would act primarily on the tumour
microenvironment rather than the tumour cell. Assignment was a model pass over each label's
own extracted mechanism together with known pharmacology, reviewed by hand, with three calls
overridden. These flags are curated judgement rather than extracted evidence, and are
superseded by the Phase 4 tractability data where the two disagree.

### 2.5 Expression data ingestion and preprocessing (Phase 2)

> `[OUTLINE]` Depends on the Phase 3b organism decision. Will cover:
>
> - Which datasets from the Phase 1a inventory were ingested, and the selection rule.
> - Platform handling: array versus RNA-seq, raw files versus processed matrices, and what
>   happened to the 16 datasets that ship processed matrices only.
> - Normalisation and the mouse-to-human ortholog mapping, if mouse is carried.
> - Batch correction method and how its effect was assessed.
> - The fallback for datasets with no healthy control, which is load-bearing here rather
>   than optional: most human tumour series in the inventory have no normal comparator.
> - `[FILL IN]` Whether a no-control dataset may contribute to a candidate at all, or only
>   corroborate one derived from a controlled comparison.

### 2.6 Expression-derived candidate identification (Phase 3)

> `[OUTLINE]` Will cover: differential expression method and thresholds; pathway enrichment,
> extending the existing KEGG mapping step to run from expression rather than pre-selected
> gene names; how candidates inherit disease and manifestation labels from their source
> datasets; how direction of effect is recorded, which matters because a tumour-suppressor
> loss and an overexpressed kinase are not the same kind of candidate.
>
> `[FILL IN]` Statistical choices: per-dataset analysis then meta-analysis, or pooled
> analysis after batch correction. This was flagged as an open methodological decision in the
> plan review and is not yet resolved.

### 2.7 Evidence coverage review and manifestation prioritisation (Phase 3b)

> `[OUTLINE]` A human decision point by design. Will cover: the aggregation of literature
> evidence from Phase 1b and expression evidence from Phase 3 per disease and manifestation;
> the coverage visualisation; the decision about which manifestations carry into Phase 4; and
> the rationale, recorded so that deferred manifestations are visibly deferred rather than
> silently dropped.
>
> `[FILL IN]` The decision itself and its reasoning.

### 2.8 Drug interaction, selectivity and tractability layer (Phase 4)

> `[OUTLINE]` Will cover, for candidates from the selected manifestations only: known drug
> interactions; curated selectivity; clinical stage; approval and availability status; safety
> signals; and the delivery-route filter, which accepts topical delivery for skin-localised
> manifestations, requires a systemic route elsewhere, and additionally requires
> blood-brain-barrier penetration for CNS manifestations.
>
> Source availability constrains this section and should be stated plainly: ChEMBL and
> ClinicalTrials.gov are queryable directly, while several sources named in the plan were
> unreachable from the analysis environment when tested and would need either a granted
> network exception or a bulk-download integration. `[CHECK]` Re-test before writing, since
> the set of reachable sources has changed once already.
>
> `[FILL IN]` Whether a target with no existing probe or drug is reported as untractable or
> as unassessed. These are different claims and the distinction matters for the rare-disease
> audience, where an untractable target may still be the right biology.

### 2.9 Cross-disease mechanistic validation (Phase 5)

> `[OUTLINE]` Will cover: disease-term standardisation through Mondo; mechanistic
> cross-checks against related rare diseases; and the Monarch knowledge graph as a partial
> ground truth. The RAS axis is the obvious cross-disease link to test first, since LZTR1
> acts in a cullin-RING complex that ubiquitinates RAS and therefore places schwannomatosis
> on the same pathway as NF1.

### 2.10 Evidence strength scoring (Phase 6)

> `[OUTLINE]` Will cover the rubric combining drug-interaction evidence, tractability,
> clinical stage, approval status, cross-disease support, safety and the delivery-route flag
> into one confidence signal per candidate, with disease and manifestation labels preserved
> through scoring.
>
> `[FILL IN]` The weights, and three specific decisions the earlier phases have already
> raised: how much less an abstract-only literature claim counts than a full-text-verified
> one; whether a biomarker-flagged target is downweighted or excluded; and whether a
> preprint-only row can clear the threshold at all.

### 2.11 Convergence of expression and literature evidence (Phase 7)

> `[OUTLINE]` Will cover the comparison of the expression-derived and literature-derived
> candidate lists: overlap, and targets found by only one route. Literature-only matches are
> weighted by evidence tier, so a convergence with an abstract-only row is reported
> differently from one with a full-text-supported row. Expression-only candidates are the
> genuinely new material and need their own treatment.

### 2.12 Agent operation and reproducibility (Phase 8)

> `[OUTLINE]` Will cover how the pipeline runs as an agent-operated workflow, and the
> reproducibility arrangements. The latter is partly in place and can be described now:
> phase outputs are regenerated by committed scripts rather than by session-local code, so
> the write-ups and figures cannot drift from the tables; every scope filter is a flag plus a
> derived table rather than a deletion; and each phase's work is reviewed as a pull request
> before merge.

## 3. Results

### 3.1 The public expression data landscape is uneven and partly mouse

Of 415 GEO series retrieved, 235 were excluded on reading the record, leaving 180 GEO series
plus 5 ArrayExpress experiments, which deduplicate to 160 counted datasets covering 4,634
labelled samples, of which 3,662 are in scope and 330 were excluded as sporadic. Most
exclusions were not NF-related at all: the string "NF1" also retrieves nuclear factor 1 and
sporadic cancers carrying somatic *NF1* mutations among many others.

The collection is split between organisms, 78 human and 70 mouse datasets with 9 mixed, and
the split is not random with respect to manifestation. Human data carries the nerve sheath
tumours, with MPNST at 41 human against 15 mouse datasets and plexiform neurofibroma at 19
against 16. Mouse data carries the central nervous system manifestations: optic pathway
glioma is 11 mouse against 2 human, and NF1-associated high-grade glioma is mouse-only.
Restricting the pipeline to human data would therefore not merely shrink the collection, it
would make two manifestations structurally unavailable, and a later zero would mean that the
only available data had been excluded.

Dataset count also overstates analysis capacity. Only 48 of the 160 datasets have a
comparative design that feeds differential expression directly, 20 tumour versus normal and
28 subtype or grade comparisons; 71 are in vitro perturbation experiments, useful for target
validation rather than case-control analysis. Eighty-six datasets contain any control sample,
and matched normal nerve is the scarce commodity.

Five manifestations have no dataset at all under the germline-only scope: Cardiovascular
issues, Sleep, Ependymoma, GIST and Pulmonary disease.

> Table 1. Datasets and in-scope samples per manifestation by organism. Source:
> `phase-1a/data/phase1a-coverage.csv`.
>
> Figure 1. Datasets per manifestation, human versus mouse. Source:
> `phase-1a/docs/phase1a-coverage.png`.

### 3.2 The literature-derived target map, graded by verification depth

The literature sweep yields **309 candidate rows over 182 target labels covering 247 distinct
gene symbols, drawn from 234 papers**, where a row is one gene by disease by manifestation
claim. Full text was read for 155 of the 234 papers, 127 through the three programmatic
routes and 28 as publisher PDFs supplied by the corresponding author. A wider audit table of
348 rows retains the germline driver genes and the contradicted rows with flags.

Evidence tiers divide the candidate list into 194 full-text supported rows, 50 full-text
partial, and 65 resting on abstracts alone. The partial tier is not a weaker biological claim
but a looser attribution: the paper supports the target while studying a different disease or
manifestation than the row asserts.

By disease the list is 214 NF1 rows, 89 NF2-SWN and 6 SWN. The schwannomatosis figure is a
direct consequence of the scope decisions rather than of search depth: *LZTR1* and *SMARCB1*
are most of what the SWN literature offers, and both are excluded as germline drivers. Any
prioritisation that treats SWN as evidentially comparable to the other two diseases is
reading a list whose best-studied genes were removed by design.

Coverage falls away sharply outside the principal tumour types. Nine manifestations hold
fewer than ten candidate rows each, and Sleep holds none at all, every one of its claims
having failed full-text verification. These are statements about this corpus, not about the
biology, and the GIST case shows why the distinction matters: its mechanistic literature sits
in sporadic KIT-mutant disease, which the germline-only scope excludes.

> Figure 2. Candidate rows per manifestation, panelled by disease and stacked by verification
> depth. Source: `phase-1b/docs/figures/phase1b-coverage-verification.png`.
>
> Table 2. The candidate target list. Source: `phase-1b/data/phase1b-candidate-targets.csv`.

> `[OUTLINE]` One paragraph naming the best-evidenced targets per disease, written once
> Phase 3b has fixed which manifestations the paper foregrounds. The Phase 1b write-up has
> the material with verified citations: the MEK1/2 axis in NF1, the loss-of-function
> progression markers, the pain axis built on the neurofibromin-CRMP2 interface, the Hippo
> and PAK and PI3K nodes in NF2-SWN, VEGFA as the one NF2 target with real clinical use, and
> the RAS link in SWN.

### 3.3 Most verified targets are not conventional drug targets

Of the 182 candidate labels, 55 are flagged as more useful as biomarkers than as drug
targets, 19 as relevant only to patients carrying a particular genotype, and 42 as acting
primarily on the tumour microenvironment. **Ninety-three labels carry none of the three
flags**, and those are the closest thing this phase produces to conventional tumour-cell drug
targets.

The biomarker group is dominated by tumour-suppressor losses, where the lesion is an absence
with nothing to inhibit, and by proliferation and lineage markers. This is a substantive
finding rather than a bookkeeping note: a naive reading of the NF literature would promote
*CDKN2A*, PRC2 components and *TP53* as high-confidence targets on the strength of their
evidence, when their clinical utility is stratification. The mutation-restricted group
matters for the same reason, since a target relevant to a tumour subtype is not a target for
the disease.

> Table 3. Per-label annotations. Source: `phase-1b/data/phase1b-target-annotations.csv`.

### 3.4 Expression-derived candidates

> `[OUTLINE]` Phase 3. Counts per disease and manifestation, direction of effect, and the
> pathway-level picture.

### 3.5 Evidence coverage and the prioritisation decision

> `[OUTLINE]` Phase 3b. The combined coverage view and the manifestations carried forward.

### 3.6 Tractability and drug availability

> `[OUTLINE]` Phase 4, for the selected manifestations only.

### 3.7 Cross-disease mechanistic support

> `[OUTLINE]` Phase 5.

### 3.8 Scored candidate list

> `[OUTLINE]` Phase 6. The headline deliverable: the prioritised, evidence-scored list.

### 3.9 Convergence between expression and literature evidence

> `[OUTLINE]` Phase 7. Overlap, expression-only candidates, literature-only candidates
> weighted by evidence tier.

### 3.10 Evaluation against known NF targets

> `[OUTLINE]` Phase 9. Recovery of established targets as a positive control, and what the
> pipeline ranks above or below them.

## 4. Discussion

Two results already constrain how NF target prioritisation should be done, and both are
about the shape of the evidence rather than about any single target.

**Verification depth does not follow evidence volume.** Among manifestations holding twenty
or more candidate rows, the share anchored in a paper read in full varies several-fold, so
the best-studied manifestation is not necessarily the best-verified one. A prioritisation
that counts papers without grading them will rank a manifestation by how much has been
written about it rather than by how much has been checked.

**Most well-evidenced NF targets are not things a drug acts on.** With a majority of labels
flagged as biomarker-like, microenvironment-directed or genotype-restricted, a pipeline that
ranks candidates by evidence strength alone will put stratification markers at the top. The
flags are a first attempt at separating these; Phase 4 tractability data will do it properly.

> `[OUTLINE]` Add once Phases 3 to 7 have run:
>
> - Whether expression and literature evidence converge, and what the expression-only
>   candidates look like.
> - Whether the manifestations with thin literature also have thin expression data, which
>   determines whether the gap is a search problem or a data problem.
> - How the three diseases compare once both evidence streams are in.

> `[FILL IN]` What this means for the NF community and for the funder, and what you would
> want a follow-up study to do. Also your own read on the single-reader verification design:
> we chose one model pass per paper with no adjudication, which is defensible for triage and
> not for a systematic review, and a reader may challenge it.

### 4.1 Comparison with existing resources

> `[OUTLINE]` Position against Open Targets, DGIdb and any NF-specific target compilations.
> `[CHECK]` I have not surveyed NF-specific target resources, and if one exists this section
> becomes load-bearing: the paper then has to say what it adds rather than what it builds.

### 4.2 Transferability beyond NF

The evidence map is NF-specific. The protocol is not, and the conditions under which it pays
off are statable: a disease whose literature is small enough that every retrieved paper can
be read, heterogeneous enough that claims arrive at different levels of evidence, and uneven
enough across subphenotypes that counting papers gives the wrong ranking. Most rare diseases
meet those conditions; common-disease oncology largely does not, because the corpus is too
large to verify exhaustively.

Three components should transfer with no modification: the retrieval ladder, the per-paper
verdict rubric, and the flag-plus-derived-table pattern for scope filters. The fixed
manifestation vocabulary transfers as a pattern but not as content, since it has to be
rebuilt per disease, ideally from an existing clinical standard rather than drafted fresh.
The target annotation flags are the least transferable, since the biomarker-versus-target
judgement depends on the pharmacology of the specific gene set.

> `[FILL IN]` Whether to make the transfer claim concrete by applying the protocol to a
> second disease before submission. One worked second case would move this section from an
> argument to a demonstration, and would also test whether the vocabulary step is as
> mechanical as I have claimed. It is also the single most expensive thing this paper could
> ask for, so it may be a follow-up rather than part of this work.

## 5. Limitations

Extraction from abstracts and verification of full text are both single model passes with no
second reader and no adjudication. Recall against a gold standard has not been measured in
either direction, so the list is a triage instrument rather than a systematic review.

Rows in the abstract-only tier are not weaker claims about biology; they are claims nobody has
checked. Sixty-five such rows remain, and 40 papers are still unread because no free route
reaches them. Their absence from the verified set reflects access, not quality.

Eighty-five candidate rows carry no mechanism text, either because the abstract stated none or
because the verifier returned a verdict without mechanism prose. `[FILL IN]` Decide whether to
fill these from abstracts with a provenance marker, or leave them empty and say so.

Six papers are preprints and ten rows rest on a preprint alone; all are also single-paper and
abstract-only, so they are weak on more than one axis. Preprint detection is by DOI prefix and
journal string, so a preprint on an unusual server could be unflagged.

The sporadic exclusion removes real mechanistic biology, most visibly in meningioma, GIST and
high-grade glioma, where much of the published mechanism comes from sporadic tumours carrying
the same somatic lesion. The excluded rows are retained and the exclusion is reversible per
manifestation.

Dataset classification in Phase 1a is also model-assigned from GEO records alone, so a series
whose record omits germline status is scored out of scope even if the samples are NF-derived.

> `[OUTLINE]` Add preprocessing, statistical and database-coverage limitations as those
> phases run.

## 6. Data and code availability

All code, tables and per-phase write-ups are in the repository at
`github.com/karaquaid/nf-target-pipeline`, MIT licensed. Phase outputs are regenerated by
committed scripts, so every count in the write-ups traces to a table in the same commit. Raw
expression data is not redistributed; the inventory lists accessions.

> `[FILL IN]` Whether to archive a release at Zenodo for a citable DOI at submission, and
> whether the supplied PDFs stay out of the repository, which they must for copyright.

## 7. Author contributions, funding and competing interests

> `[FILL IN]` Contributions, in whatever taxonomy the target journal uses.
>
> `[FILL IN]` How to describe the use of an AI agent in the Methods and in any
> author-contribution statement. Most journals now require a disclosure of AI assistance and
> prohibit listing a model as an author. The honest description is that a Claude agent
> executed the searches, extraction, verification and analysis under your direction, and that
> every scope decision was yours; the phrasing should match the target journal's policy.

Funding: this work is part of Anthropic's AI for Science Rare Disease Research Program, in
which the Children's Tumor Foundation participates. `[FILL IN]` Grant number or award
identifier, and whether Anthropic requires specific acknowledgement wording.

Competing interests: `[FILL IN]`

## 8. References

> `[OUTLINE]` Assemble at submission from `phase-1b/data/phase1b-references.csv`, which
> carries DOI, PMC identifier, access route and preprint status for all 234 papers. The ones
> cited in prose so far, all verified against retrieved records rather than recalled:
>
> - Dombi et al. 2016, selumetinib phase 1 in plexiform neurofibroma. 10.1056/NEJMoa1605943
> - Gross et al. 2020, SPRINT phase 2. 10.1056/NEJMoa1912735
> - Kim et al. 2024, longer-term selumetinib safety and efficacy. 10.1093/neuonc/noae121
> - Chaney et al. 2020, *CDKN2A* loss at the atypical transition. 10.1158/0008-5472.CAN-19-1429
> - Cortes-Ciriano et al. 2023, PRC2 loss in MPNST. 10.1158/2159-8290.CD-22-0786
> - Moutal et al. 2017 and Khanna et al. 2019, neurofibromin-CRMP2 and NF1 pain.
>   10.1097/j.pain.0000000000001026, 10.1097/j.pain.0000000000001648
> - Karajannis et al. 2021, everolimus phase 0 in NF2. 10.1158/1535-7163.MCT-21-0143
> - Fujii et al. 2020, bevacizumab in NF2-associated vestibular schwannoma. 10.2176/nmc.oa.2019-0194
> - Jones et al. 2025, spatial profiling and CD44 in bevacizumab failure. 10.1038/s41467-025-57586-z
> - Steklov et al. 2018, LZTR1 and RAS ubiquitination. 10.1126/science.aap7607
> - Laws et al. 2025, TEAD1 inhibition in merlin-inactivated Schwann cells, a preprint.
>   10.1101/2025.11.15.688608
> - Niinuma et al. 2018, GIST molecular pathogenesis, cited for NF1-associated GIST lacking
>   KIT and PDGFRA mutations. 10.21037/tgh.2018.01.02

## Appendix: figure and table inventory

| Item | Status | Source |
|---|---|---|
| Figure 1, datasets per manifestation by organism | exists | `phase-1a/docs/phase1a-coverage.png` |
| Figure 2, candidate rows by manifestation and verification depth | exists | `phase-1b/docs/figures/phase1b-coverage-verification.png` |
| Figure 3, combined literature and expression coverage | Phase 3b | to be generated |
| Figure 4, scored candidate list | Phase 6 | to be generated |
| Figure 5, convergence between evidence streams | Phase 7 | to be generated |
| Table 1, dataset and sample coverage | exists | `phase-1a/data/phase1a-coverage.csv` |
| Table 2, candidate target list | exists | `phase-1b/data/phase1b-candidate-targets.csv` |
| Table 3, per-label target annotations | exists | `phase-1b/data/phase1b-target-annotations.csv` |
| Table 4, reference list with access and provenance | exists | `phase-1b/data/phase1b-references.csv` |
| Supplementary, audit table with excluded rows | exists | `phase-1b/data/phase1b-literature-targets.csv` |
