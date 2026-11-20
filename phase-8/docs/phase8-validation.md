# Validating the pipeline against targets with NF clinical precedent

The Phase 8 prompt asks for a test on a small set of known NF-relevant genes, with divergences
reported. The scope ruling of 2026-11-19 made that set objective rather than hand-picked: the
targets of drugs actually trialled in neurofibromatosis, which the Phase 4 trial table records in
its `nf_specific` flag.

**What this establishes.** The pipeline recovers the approved NF drug's target in every stratum
that drug was trialled in, and scores it near the top where the stratum is well covered. It
recovers 41 of 71 manifestation-level gene and stratum pairs, and 33 of 45 genes somewhere. Every
one of the 30 misses has a traceable cause, and none of them is a scoring failure: 13 are genes
the expression evidence ranked below the top-200 cap, and 17 are genes Phase 3 did not call
differentially expressed in that stratum at all.

**What it does not establish.** This tests recall of the already-known, and parts of the pipeline
were built from the same trial evidence, so it is a sanity check, not an independent validation. A
pipeline that cannot recover selumetinib's target is demonstrably broken; passing does not prove
the converse.

## Three corrections the build forced

The scope ruling pinned the population "so it is not re-derived wrongly". Every pinned number
reproduces exactly: 435 `nf_specific` trial rows, 209 distinct trials, 40 interventions matched to
a Phase 4 drug, 165 target genes by any interaction, 35 by a directional interaction type. The
last reproduces from DGIdb `interaction_types` alone; ChEMBL mechanism action types give 31 and
the union 39.

**1. The 40-intervention figure rests on a join against the wrong table.** `matches_phase4_drug`
is computed against `phase4-chembl-drugs.csv`, but the table that maps a drug to a target is
`phase4-drug-interactions.csv.gz`, which also carries drugs reached through DGIdb and Open
Targets. Matching against the interaction table gives **68 interventions, not 40**. The 28
recovered include everolimus, sirolimus and temsirolimus, which between them appear in 13
NF-specific trials and carry a directional MTOR interaction, plus tipifarnib, imiquimod,
carboplatin, temozolomide and methotrexate.

This matters for the ruling's own example. mTOR, which the ruling names as something the set
should contain, reaches the pinned 35 only through metformin, and metformin's single NF-flagged
trial is OCT1 pharmacogenetics in type 2 diabetes. The set below is built on the 68.

**2. `nf_specific` by provenance admits trials that are not NF trials.** The flag qualifies a
trial two ways: it came from an NF-restricted `_disease_*` query, or its title or conditions name
an NF disease. Seven of the 68 interventions have no NF-flagged trial that names an NF disease
anywhere. Two of those trials are plainly not NF: NCT03710564 (brolucizumab against aflibercept in
age-related macular degeneration) and NCT00588172 (metformin in type 2 diabetes). Three others are
solid-tumour or low-grade-glioma basket trials that plausibly enrol NF cohorts through eligibility
criteria the committed table does not carry; they are kept and flagged `provenance_only`, which is
43 of the set's 275 rows.

**3. The ruling's symptomatic-care examples half hold.** Checking each drug against its actual
trial rather than its drug class:

| Intervention | Decision | Why |
|---|---|---|
| Acetaminophen | excluded | Co-administered in a selumetinib bioavailability and food-effect study in healthy participants. Not a therapy under test, and not symptomatic care either |
| Tanezumab | excluded | Anti-NGF antibody trialled for pain due to schwannomatosis. Targeted, but at a pain mediator rather than an NF disease process |
| Aspirin | **kept** | Its NF trial is "Study of Aspirin in Patients With Vestibular Schwannoma", a disease-modifying hypothesis, not analgesia |
| Diclofenac sodium | **kept** | Topical, applied to cutaneous neurofibromas after laser microporation: directed at the lesion |
| Lamotrigine | **kept** | "Effect of Lamotrigine on Cognition in NF1": directed at the NF1 synaptic-plasticity mechanism |

Five interventions are excluded in total, three of them because their only NF-flagged trial is not
an NF trial. All five, and the three contested keeps, are recorded with the NCT number that
decides them in `phase-8/data/phase8-validation-exclusions.csv`.

## The set

45 genes, 42 drugs, 77 trials, 275 rows, 102 gene by disease by manifestation combinations.
A gene enters it when a drug with a directional interaction against it, meaning inhibitor,
antagonist, agonist, blocker or modulator in either DGIdb's interaction types or ChEMBL's
mechanism action types, was an intervention in an NF-specific trial. 41 genes arrive through
DGIdb, 27 through ChEMBL mechanism, 5 through both.

Disease is derived per row and the basis is recorded: 153 rows from an NF disease named in the
trial, 105 from an NF-restricted query's disease scope, 17 from the manifestation implying the
disease within the nine strata Phase 3b selected. `disease_scope` is blank on every
manifestation-query trial, which is why the derivation is needed at all.

71 of the 102 combinations name a manifestation. The other 31 come from disease-level trials,
which name no manifestation, and are checked against any stratum of that disease.

## Result

| Outcome | Combinations |
|---|---|
| scored by Phase 6 in that stratum | 41 |
| in the full expression table but below the top-200 cap | 13 |
| not called differentially expressed in that stratum | 17 |
| disease-level trial, checked against any stratum of the disease | 31 |

Manifestation-level recall is **41 of 71, 57.8%**. 33 of the 45 genes are scored in at least one
stratum. Of the 23 genes reaching the set only through a disease-level trial, 18 are scored
somewhere in that disease.

**The hard case passes.** Selumetinib is the approved NF1 agent, and both its targets are
recovered in every manifestation stratum its trials speak to:

| Gene | Stratum | Rank in stratum | Score |
|---|---|---|---|
| MAP2K2 | NF1 Optic pathway glioma | 1 | 0.776 |
| MAP2K2 | NF2-SWN Vestibular schwannoma | 2 | 0.728 |
| MAP2K1 | NF1 Optic pathway glioma | 4 | 0.660 |
| MAP2K2 | NF1 Cutaneous neurofibroma | 9 | 0.660 |
| MAP2K2 | NF1 Plexiform neurofibroma | 38 | 0.720 |
| MAP2K2 | NF1 MPNST | 53 | 0.720 |
| MAP2K1 | NF2-SWN Vestibular schwannoma | 65 | 0.619 |
| MAP2K1 | NF1 MPNST | 94 | 0.680 |
| MAP2K1 | NF1 Cutaneous neurofibroma | 317 | 0.561 |
| MAP2K1 | NF1 Plexiform neurofibroma | 390 | 0.612 |

BRAF and RAF1 also reach rank 2 in NF1 optic pathway glioma, and EGFR rank 5 and HDAC1/HDAC3
rank 6 in NF2-SWN vestibular schwannoma.

## The misses, and what causes each

**13 are the top-200 cap.** Every one is present in `phase3-expression-targets.csv.gz` for its
stratum and absent from `phase3-candidate-targets.csv`, so Phase 4 never annotated it and Phase 6
never scored it. Seven of the 13 are sunitinib's targets in MPNST: KIT, KDR, CSF1R, FGFR1, FLT1,
PDGFB and LATS2. The rest are everolimus against AKT1 and diclofenac against PTGS1 in cutaneous
neurofibroma, sorafenib against FLT1 and PDGFRA and vincristine against HIF1A in optic pathway
glioma, and crizotinib against MET in vestibular schwannoma.

This is ruling 3's cost measured on named drugs rather than on a gene count. The cap is a
presentation device for the Phase 3b chart, and here it is the single largest cause of a
clinically precedented target failing to reach the scored list.

**17 were not called differentially expressed in that stratum.** Six are in optic pathway glioma
and four in vestibular schwannoma. Among them are MTOR in plexiform and cutaneous neurofibroma,
CDK4 and CDK6 in ANNUBP, and ABL1 in plexiform neurofibroma.

Be careful what this says. `phase3-expression-targets.csv.gz` holds genes Phase 3 called in at
least one dataset or scored by aggregation, not every gene measured. The measured universe is
`build/phase3/universe.csv`, which is not committed, so from this repository "measured but not
called" cannot be separated from "never measured". These 17 are reported as not differentially
expressed, never as not expressed or not relevant.

**None is a scoring failure.** No combination reached Phase 4's dossier and then failed to be
scored by Phase 6. Where the pipeline saw a clinically precedented target, it scored it.

## Reproducing

```
python phase-8/scripts/phase8_validate.py
```

Reads the capped list for ranking and the full table to separate "below the cap" from "not
called", and says so in `phase8-validation-summary.json` under `list_used`, per ruling 3.

| File | What |
|---|---|
| `phase-8/data/phase8-validation-set.csv` | 275 rows: gene, drug, disease and its basis, manifestation, trial, interaction evidence |
| `phase-8/data/phase8-validation-exclusions.csv` | the five exclusions and three contested keeps, each with the NCT number that decides it |
| `phase-8/data/phase8-validation-results.csv` | one row per gene by disease by manifestation, with the outcome and rank |
| `phase-8/data/phase8-validation-summary.json` | the counts above |
| `phase-8/scripts/phase8_validate.py` | the check, regenerable |
