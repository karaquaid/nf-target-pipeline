# Phase 3b: evidence coverage review and manifestation prioritisation

Decision date: 2026-11-04. Decided by: Kara.

## Decision

All seven Phase 3 strata that produced a candidate carry into Phase 4. No candidate-bearing stratum is deferred.

This selects 9 disease and manifestation combinations, drawn from 7 of the 8 Phase 3 strata. The remaining stratum, nf1_benign_subtype_vs_pnf, produced no significant gene at all and so selects nothing.

Deprioritised combinations are deferred, not dropped: their Phase 1b rows stay in the repo and can be taken through Phase 4 in a later pass without rerunning anything upstream.

## Combinations carried into Phase 4

| Disease | Manifestation | Literature targets | Expression targets | Cross-dataset supported | Datasets | Overlap genes |
| --- | --- | --- | --- | --- | --- | --- |
| NF1 | Malignant peripheral nerve sheath tumor (MPNST) | 66 | 780 | 771 | 9 | 11 |
| NF1 | Plexiform neurofibroma | 45 | 743 | 695 | 9 | 8 |
| NF1 | Cutaneous neurofibroma | 17 | 398 | 386 | 2 | 0 |
| NF1 | Bone defects | 5 | 81 | 0 | 2 | 0 |
| NF1 | Optic pathway glioma | 13 | 400 | 0 | 1 | 1 |
| NF1 | ANNUBP / atypical neurofibroma | 9 | 54 | 0 | 2 | 1 |
| NF2-SWN | Vestibular schwannoma | 40 | 585 | 321 | 3 | 6 |
| NF2-SWN | Pain | 0 | 192 | 0 | 1 | 0 |
| NF2-SWN | Non-vestibular schwannoma | 17 | 192 | 0 | 1 | 0 |

5 of the 9 selected combinations have at least one gene named by both the literature list and the expression list:

- NF1 Malignant peripheral nerve sheath tumor (MPNST): BIRC5; CENPF; DLK1; E2F1; EZH2; PLK1; PTEN; RRM2; SOX10; SPP1
- NF1 Plexiform neurofibroma: BIRC5; EGFR; FGFR1; KIT; POSTN; PROS1; SOX10; SPP1
- NF2-SWN Vestibular schwannoma: CD44; CEMIP; EGFR; PAK3; WWTR1; YAP1
- NF1 Optic pathway glioma: MAPK3
- NF1 ANNUBP / atypical neurofibroma: TP53

## What each selected combination rests on

| Stratum | Disease | Contrasts | Datasets | Tier A | Tier B | Tier C |
| --- | --- | --- | --- | --- | --- | --- |
| nf1_glioma_vs_normal_brain | NF1 | 1 | 1 | 0 | 0 | 400 |
| nf1_mpnst_vs_benign_pnst | NF1 | 8 | 7 | 121 | 279 | 0 |
| nf1_pnst_vs_normal | NF1 | 3 | 2 | 0 | 386 | 14 |
| nf2swn_schwannoma_vs_normal | NF2-SWN | 2 | 2 | 10 | 311 | 79 |
| nf2swn_painful_vs_non_painful_schwannoma | NF2-SWN | 1 | 1 | 0 | 0 | 192 |
| nf1_bone_vs_normal | NF1 | 2 | 2 | 0 | 0 | 81 |
| nf1_atypical_vs_benign_pnst | NF1 | 3 | 2 | 0 | 0 | 54 |

4 of the 7 producing strata carry no cross-dataset support at all, so every candidate they contribute is tier C, significant in one dataset only: nf1_atypical_vs_benign_pnst, nf1_bone_vs_normal, nf1_glioma_vs_normal_brain, nf2swn_painful_vs_non_painful_schwannoma. 2 rest on a single dataset: nf1_glioma_vs_normal_brain, nf2swn_painful_vs_non_painful_schwannoma.

Two label caveats that change how the table above reads, both carried forward into Phase 4 rather than corrected here:

- Cutaneous neurofibroma's expression evidence comes entirely from the nf1_pnst_vs_normal stratum, which is labelled for MPNST, plexiform neurofibroma and cutaneous neurofibroma together. Those genes are a shared nerve sheath tumour against normal nerve signature, not a cutaneous-specific one.
- NF2-SWN Pain and NF2-SWN non-vestibular schwannoma both rest solely on the painful against non-painful schwannoma stratum, whose strongest enriched pathway is cornified envelope formation, a skin signature most likely reflecting differing overlying tissue between the arms.

## Deferred

13 combinations have literature targets but no expression contrast anywhere in the Phase 2 launch set, so Phase 4 has no expression-derived candidate to query for them:

| Disease | Manifestation | Literature targets | Full-text supported | Papers |
| --- | --- | --- | --- | --- |
| NF2-SWN | Meningioma | 29 | 20 | 18 |
| NF1 | Other | 11 | 6 | 7 |
| NF1 | High grade glioma | 10 | 5 | 7 |
| NF1 | Pain | 9 | 5 | 18 |
| NF1 | Cognition / Behavioral / Learning | 6 | 2 | 8 |
| NF1 | Cardiovascular issues | 5 | 2 | 2 |
| NF1 | Gastrointestinal stromal tumor (GIST) | 4 | 0 | 8 |
| NF1 | Non-optic LGG | 4 | 3 | 9 |
| SWN | Pain | 4 | 4 | 1 |
| NF2-SWN | Ependymoma | 3 | 2 | 2 |
| NF1 | Hematologic malignancies | 2 | 1 | 2 |
| NF1 | Pulmonary disease | 2 | 1 | 2 |
| SWN | Non-vestibular schwannoma | 2 | 2 | 3 |

The largest of these is NF2-SWN Meningioma with 29 literature targets over 18 papers. It has no contrast-bearing dataset because the standing Phase 2 policy excludes sporadic material as a reference arm, so the sporadic comparators in GSE232528 were dropped and the dataset entered the manifest single-armed.

A further 38 combinations have neither kind of evidence and are shown as explicit zeros in phase-3b/data/phase3b-coverage.csv rather than omitted.

Schwannomatosis is the starkest gap: it holds 6 literature targets across 2 manifestations and no dataset anywhere in the launch set, so it contributes nothing to Phase 4. GSE292071 is the only launch-set dataset carrying a non-NF2 schwannomatosis contrast and its deposit is unusable.

## What this means for Phase 4

Phase 4 queries the union of the expression-derived and literature-derived candidates for the selected combinations. The delivery route filter applies as follows: topical delivery is acceptable only for ANNUBP / atypical neurofibroma, Cutaneous neurofibroma; every other selected manifestation requires a systemic route. Blood-brain-barrier penetration is additionally required for Optic pathway glioma.

Because four producing strata carry tier C evidence only, Phase 6 should be expected to downweight a large share of what Phase 4 annotates. That is the intended consequence of the wide selection, not a defect in it.

## Reproducing this

```
python phase-3b/scripts/phase3b_coverage.py
python phase-3b/scripts/phase3b_figure.py
python phase-3b/scripts/build_phase3b_report.py
```

Outputs: phase-3b/data/phase3b-coverage.csv (all 60 combinations, zeros included),
phase-3b/data/phase3b-stratum-summary.csv, phase-3b/docs/figures/phase3b-coverage.png,
and this document.
