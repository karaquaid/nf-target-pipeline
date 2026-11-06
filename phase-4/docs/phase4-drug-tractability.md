# Phase 4: drug interaction, selectivity and tractability layer

Run 2026-11-04.

## Scope

Phase 3b selected 9 disease and manifestation combinations. For those, Phase 4 queries the union of the expression-derived and literature-derived candidate lists: 1,930 distinct genes over 3,752 target rows (3,398 expression only, 327 literature only, 27 both).

Of those genes, 1,861 resolved to a current HGNC symbol directly and 41 through a symbol rename. 27 are clone-based or LOC identifiers from array platform annotations that resolve to no gene, and 1 is a literature label naming a process rather than a gene product. Those rows are carried as not queryable, never as targets with no drug found.

## Sources queried

| Source | What it supplied | Coverage |
| --- | --- | --- |
| DGIdb | drug-gene interaction claims from about 40 upstream databases | 844 of 1,929 genes, 18,295 claims |
| Open Targets | known drugs, tractability buckets, chemical probes | 286 of 1,892 targets with a drug, 51,436 tractability assignments |
| ChEMBL | drug records, max_phase, route booleans, mechanisms of action | 4,005 molecules, 1,680 with a mechanism, 984 approved |
| ClinicalTrials.gov | NF-relevant interventional trials and their drugs | 456 trials, 346 drug interventions, 79 matching a candidate drug |
| openFDA | labels with route of administration, Drugs@FDA approvals, FAERS | 491 labels, 470 approval records, 463 drugs with FAERS reports, over 1,255 drugs in scope |
| Guide to Pharmacology | curated affinities and ligand selectivity profiles | 461 of 1,929 symbols matched a target, 4,379 interactions, 2,000 ligands profiled |


## What the drug layer found

848 of 1,930 candidate targets have at least one drug interaction from some source, and 189 have at least one approved drug. A further 932 have no drug but do carry an Open Targets tractability call, which is the repurposing gap this phase exists to surface. 150 have neither.

| Disease | Manifestation | Targets | With a drug | With an approved drug | Undrugged but tractable | Route-appropriate drugs |
| --- | --- | --- | --- | --- | --- | --- |
| NF1 | ANNUBP / atypical neurofibroma | 63 | 43 | 10 | 19 | 210 |
| NF1 | Bone defects | 93 | 42 | 16 | 41 | 316 |
| NF1 | Cutaneous neurofibroma | 425 | 173 | 38 | 234 | 615 |
| NF1 | Malignant peripheral nerve sheath tumor (MPNST) | 858 | 393 | 86 | 438 | 1,083 |
| NF1 | Optic pathway glioma | 424 | 176 | 45 | 183 | 110 |
| NF1 | Plexiform neurofibroma | 808 | 378 | 85 | 405 | 1,190 |
| NF2-SWN | Non-vestibular schwannoma | 221 | 95 | 25 | 98 | 353 |
| NF2-SWN | Pain | 192 | 67 | 6 | 97 | 53 |
| NF2-SWN | Vestibular schwannoma | 668 | 309 | 77 | 302 | 1,041 |

## Delivery route and CNS penetration

The filter was applied to 39,138 target-drug pairs. 33,349 carry no clinical route in ChEMBL and no openFDA label, which is the expected state for a preclinical screening hit and is recorded as unknown rather than inappropriate. Of the pairs where a route is known, 427 are flagged delivery-inappropriate and kept for audit: 267 topical-only drugs against a manifestation needing a systemic route, 144 systemic drugs predicted not to cross the blood-brain barrier against a CNS manifestation, and 16 biologics against a CNS manifestation.

The CNS flag is a prediction from ChEMBL's calculated molecular properties, not a permeability measurement: ChEMBL holds no experimental blood-brain-barrier data. Across 4,005 drugs it reads 1,773 predicted permeant, 1,771 predicted non-permeant, 221 biologics and 240 with no calculated properties. The thresholds are stated in phase-4/scripts/phase4_admet.py and in phase-4/data/phase4-admet-provenance.json.

Optic pathway glioma is the only selected manifestation that triggers the CNS requirement. Cutaneous neurofibroma and ANNUBP / atypical neurofibroma are the only two where topical delivery is acceptable.

## Clinical stage

456 interventional trials are recorded across the selected manifestations and the three disease umbrellas, naming 345 distinct drug interventions. 79 of those match a drug in the Phase 4 candidate set by name. A candidate drug with a high ChEMBL max_phase but no NF trial is a repurposing hypothesis; one with an NF trial is an existing clinical fact about this disease, and the dossier keeps the two apart.

| Manifestation | Interventional trials |
| --- | --- |
| Optic pathway glioma | 111 |
| Malignant peripheral nerve sheath tumor (MPNST) | 102 |
| Vestibular schwannoma | 93 |
| Plexiform neurofibroma | 59 |
| Non-vestibular schwannoma | 41 |
| Cutaneous neurofibroma | 23 |
| ANNUBP / atypical neurofibroma | 5 |
| Pain | 2 |
| Bone defects | 1 |

## Selectivity

306 candidate targets carry at least one curated Guide to Pharmacology ligand interaction, over 2,525 distinct ligands. For 2,000 of those ligands the whole human target profile was retrieved from the ligand side, so the breadth count means every target the database records for that ligand, not only the ones on this project's list.

1,290 profiled ligands hit only one target within one log unit of their best recorded affinity.

## Safety

Safety signals attach to the drug, not the target. Across the flagged target-drug pairs, 1,736 involve a drug whose openFDA label carries a boxed warning and 179 involve a drug ChEMBL records as withdrawn from a market.

FAERS report counts were retrieved for 463 drugs. A report count is a count of reports mentioning the drug. It has no denominator, and it rises with how widely and how long a drug has been used, so it is a signal for Phase 6 to weight rather than a safety verdict.

## Sources named in the plan that are not in this phase

- **DrugBank Open Data**: go.drugbank.com is outside the sandbox allowlist and its download requires account registration. Approval status rests on Drugs@FDA alone.
- **SIDER**: sideeffects.embl.de is outside the sandbox allowlist. There is no package-insert side-effect frequency data in this phase; FAERS is the only post-market safety source.
- **ProbeMiner**: the optional selectivity cross-check in the plan; not attempted, since Open Targets chemical probes and Guide to Pharmacology affinities already cover the question at this depth.

- **Amass Connector**: The Amass Connector the plan suggested evaluating as a single replacement for ClinicalTrials.gov, openFDA and DrugBank does not exist in this deployment's connector catalogue, so the three sources were wired separately.

Two integration surprises worth recording, both resolved with a key obtained mid-run:

- The Guide to Pharmacology REST API stopped being open: it now returns HTTP 401 without a registered API key, which is issued manually on request. The project plan described it as a live open query. Kara obtained a key rather than substituting a different selectivity source.
- The first openFDA pass ran anonymously and exhausted the request budget (1,000 per day per IP) partway through, so the FAERS layer returned nothing: an empty result that would have read as an absence of adverse events. The script was changed to record a failed request as a failure rather than collapse it into an empty result, and the whole pass was re-run the same day with an API key. All 252 requests returned, none failed, and the FAERS layer is populated. The label and approval counts are unchanged from the first pass, which confirms those two endpoints had completed before the budget ran out; 491 labels and 470 approval records over 1,255 drugs in scope is genuine openFDA coverage, not a truncated fetch.

A third is a schema drift rather than an access problem: Open Targets no longer exposes Target.knownDrugs. The field is Target.drugAndClinicalCandidates, and Drug.isApproved, Drug.maximumClinicalTrialPhase and Drug.hasBeenWithdrawn are gone, replaced by Drug.maximumClinicalStage. Code written from older documentation fails against the current API.

## Outputs

| File | Contents |
| --- | --- |
| phase4-targets.csv | the Phase 4 input list, one row per gene, disease and manifestation |
| phase4-identifiers.csv | symbol to UniProt and Ensembl, with unresolved symbols kept |
| phase4-symbol-corrections.csv | the two platform-annotation corruptions and the one non-gene label |
| phase4-drug-interactions.csv.gz | one row per target and drug, with the source of each claim |
| phase4-opentargets-tractability.csv | tractability buckets per target and modality |
| phase4-chembl-drugs.csv.gz | drug records including max_phase and route booleans |
| phase4-chembl-mechanisms.csv.gz | mechanism of action per drug |
| phase4-nf-trials.csv, phase4-trial-drugs.csv | NF interventional trials and their drugs |
| phase4-openfda-labels.csv, phase4-openfda-approvals.csv, phase4-faers.csv | route, approval and adverse event data |
| phase4-admet.csv.gz | calculated properties and the CNS penetration flag |
| phase4-gtop-interactions.csv.gz, phase4-gtop-selectivity.csv | curated affinities and ligand breadth |
| phase4-drug-route-flags.csv.gz | the delivery-route verdict per target, manifestation and drug |
| phase4-target-dossier.csv | the consolidated per-target deliverable |

## Reproducing this

```
python phase-4/scripts/phase4_targets.py
python phase-4/scripts/phase4_identifiers.py
python phase-4/scripts/phase4_dgidb.py
python phase-4/scripts/phase4_opentargets.py
python phase-4/scripts/phase4_chembl.py
python phase-4/scripts/phase4_clinicaltrials.py
OPENFDA_API_KEY=... python phase-4/scripts/phase4_openfda.py
python phase-4/scripts/phase4_admet.py
GTPAPIKEY=... python phase-4/scripts/phase4_guidetopharmacology.py
python phase-4/scripts/phase4_dossier.py
python phase-4/scripts/phase4_figure.py
python phase-4/scripts/build_phase4_report.py
```

Only phase4_identifiers.py runs offline; it reads the committed mygene cache. The rest touch the network. Two need a key, read from the environment and never written to any output.
