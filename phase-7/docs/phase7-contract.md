# Phase 7 contract: inputs and ratified methodological calls

Settled 2026-11-17 (Kara) before any comparison code was written. This file is the
authority for Phase 7 scripts; the phase record (`phase7-literature-validation.md`)
reports results against it.

## Comparison inputs

The two lists compared are:

- **Expression-derived**: `phase-3/data/phase3-candidate-targets.csv`, with the
  pipe-delimited `manifestations` column exploded to one row per manifestation.
  1,255 unique NF1 genes and 585 unique NF2-SWN genes across nine
  disease x manifestation strata.
- **Literature-derived**: `phase-1b/data/phase1b-candidate-targets.csv` in full
  (303 rows), not the subset that survived into Phase 4.

**The Phase 6 scored table is not an input.** Its `s_literature` component is
derived from the same Phase 1b table, so comparing Phase 6 against Phase 1b would
be partly circular — it would score agreement between a list and one of its own
ingredients. Phase 6 is used only to attach the final score to a target once the
match class has been decided independently.

**The Phase 4 join is not an input either.** `phase4_targets.py` restricted the
literature side to strata with `expr_targets > 0`, which silently dropped 91 of the
303 Phase 1b rows. Phase 7 reinstates them (see Call 2).

### Recorded asymmetry: the expression side is manifestation-ambiguous

A Phase 3 candidate is labelled with every manifestation its contrast could speak
to, not one. `nf1_pnst_vs_normal` labels 398 genes
`Cutaneous neurofibroma|MPNST|Plexiform neurofibroma`, and
`nf2swn_painful_vs_non_painful_schwannoma` labels 192 genes
`Non-vestibular schwannoma|Pain|Vestibular schwannoma`. The literature side assigns
one manifestation per row. A manifestation-level match is therefore generous on the
expression side and strict on the literature side.

Consequence for scripts: carry `expr_manifestation_specific` (true when the
source contrast named a single manifestation) on every expression row, and never
report a cross-manifestation near-miss that is an artefact of one multi-label
comparison class.

## Call 1 — composite literature labels get their own match class

56 of the 212 in-stratum Phase 1b rows are `family`, `pathway` or `complex` labels
(median 3 constituent genes, max 14: `MAP2K1/2 (MEK1/2)`, `PRC2 (EED/SUZ12/EZH2)`,
`PI3K (family)`, `EPH receptors`). Phase 4 expanded them and matched constituents
as if named.

**Ruling:** expand constituents, but record the match class separately.

| match class | meaning | count |
|---|---|---|
| `exact_named_gene` | the paper named this gene | 16 genes |
| `via_composite_label` | matched only through a family/pathway/complex label | 6 genes |

The six reached only through a composite label are E2F1, EZH2, FGFR1, MAPK3, PAK3,
WWTR1. Both numbers are carried so a reviewer can collapse them or not. A paper
saying "PI3K family" is not a paper naming PIK3CD; a paper saying "MEK1/2" does name
MAP2K1 and MAP2K2 — the class, not the count, is what preserves that distinction.

## Call 2 — targets in strata with no expression contrast are reported, as "no expression contrast found"

91 Phase 1b rows (69 unique targets) sit in 13 strata with no expression candidate:
NF2-SWN Meningioma 29, NF1 Other 11, NF1 High grade glioma 10, NF1 Pain 9,
NF1 Cognition/Behavioral/Learning 6, NF1 Cardiovascular 5, NF1 GIST 4,
NF1 Non-optic LGG 4, SWN Pain 4, NF2-SWN Ependymoma 3, NF1 Hematologic
malignancies 2, NF1 Pulmonary disease 2, SWN Non-vestibular schwannoma 2.
53 of the 91 are full-text supported.

**Ruling:** report all 91 as literature-only finds in a separately marked section.

**Wording is part of the ruling (Kara):** the flag reads **`no expression contrast
found`**, never "no expression contrast exists". The pipeline searched a defined
set of repositories with a defined query bank; a stratum with no dataset in that
launch set is a gap in what was found, not an established absence. Scripts must not
emit the word "exists" in this column or in any derived label.

## Call 3 — access weight is the existing Phase 1b evidence tier, as an ordinal

| `evidence_tier` | `access_weight` |
|---|---|
| full text - supported | 1.0 |
| full text - partial | 0.6 |
| abstract only | 0.3 |

The tier label travels in the same table as the number, so every weight stays
auditable back to a reading decision Phase 1b actually made. `preprint_only` is
carried as its own flag and is **not** folded into the weight (7 in-stratum rows).
The 0.6 and 0.3 steps are a judgement call, not a measurement, and are recorded as
such.

In-stratum access profile: 141 full-text supported, 30 full-text partial,
41 abstract only; 34 rows rest on no full text at all.

## Fallback scope (corrected 2026-11-17)

An earlier reading of this session claimed the five `ingested_no_ranking` datasets
map onto the deferred strata. That was wrong and is corrected here.

Of 18 unusable-dataset x stratum pairs (5 ingested-but-unrankable, 7 removed at the
Phase 2 pre-flight review), only **three** leave a stratum with no expression
evidence at all. The rest are strata where other launch-set datasets still supply
candidates — losing GSE181985 did not leave plexiform neurofibroma uncovered, it
still has 743 expression candidates.

| stratum | dataset lost | why unusable | lit targets already held |
|---|---|---|---|
| NF2-SWN Meningioma | GSE232528 | 14 NF2-patient meningiomas, single arm | 29 |
| NF1 Non-optic LGG | GSE5675 | removed at pre-flight; 0 samples in scope | 4 |
| NF1 Other | GSE2841 | removed at pre-flight; 2 samples in scope | 11 |

The literature fallback path runs on these three only. NF2-SWN Meningioma is the
substantive case. `NF1 Other` is a catch-all label rather than a disease entity, so
a fallback query bank for it is defined by what the 11 held targets are about, not
by the label.

Full table: `phase-7/data/phase7-fallback-scope.csv`.
