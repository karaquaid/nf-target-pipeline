# Targeted look: PARP1 in NF1 MPNST

Phase 7 called this "the closest thing to independent corroboration at mechanism level" —
literature target PARP1 against five replicated base-excision-repair expression candidates in
a 44-gene KEGG pathway. Examined 2026-11-17 at Kara's request.

**The convergence does not survive. PARP1 does — on different evidence than Phase 7 credited.**

## 1. The expression side is a proliferation readout, not a BER signal

MPNST-versus-benign-PNST is inherently a malignant-versus-benign contrast, so replication and
repair machinery rises across the board. Against the same contrast:

| pathway | KEGG genes | replicated | % of pathway | replicated up / down | median rank |
|---|---|---|---|---|---|
| DNA replication | 36 | 16 | **44.4%** | 15 / 1 | 341 |
| Mismatch repair | 23 | 8 | **34.8%** | 8 / 0 | 222 |
| Cell cycle | 158 | 38 | 24.1% | 36 / 2 | 275 |
| **Base excision repair** | **44** | **10** | **22.7%** | **10 / 0** | **238** |
| Homologous recombination | 138 | 23 | 16.7% | 23 / 0 | 346 |
| Nucleotide excision repair | 63 | 9 | 14.3% | 9 / 0 | 286 |
| Spliceosome | 184 | 9 | 4.9% | 8 / 1 | 510 |
| Ribosome | 302 | 9 | 3.0% | 8 / 1 | 545 |

BER is **fourth**, below DNA replication and mismatch repair, and indistinguishable from cell
cycle. Every replication- and repair-associated pathway is elevated against housekeeping
comparators at 3–5%. BER surfaced in Phase 7 only because it is small enough (44 genes) to pass
the near-miss specificity cut of ≤100 genes; DNA replication is *more* enriched but had no
literature target mapped to it, and cell cycle was excluded by size.

Background for scale: 1,141 of 7,518 genes with evidence in this contrast are `B_replicated`,
70% of them up. A pathway being coherently up here is the expected case, not a finding.

Table: `phase7-mpnst-parp1-pathway-context.csv`.

## 2. It was ten genes, not five — the cap truncated it

Phase 7 reported five BER genes because the Phase 3 candidate list is capped at the top 200 per
comparison class. Ten BER genes are `B_replicated` and **all ten are up**:

| in the candidate list | rank | | below the cap | rank |
|---|---|---|---|---|
| LIG1 | 93 | | TDP1 | 275 |
| POLD1 | 160 | | PCNA | 336 |
| NEIL3 | 183 | | POLD2 | 536 |
| FEN1 | 186 | | POLE2 | 676 |
| RFC2 | **200** | | PNKP | 762 |

RFC2 sits exactly on the cap. The five Phase 7 named are not a biological set; they are the part
of one signature that fell above an arbitrary line. This is the Phase 3 truncation cap acting as
a silent filter on a downstream analysis — worth remembering wherever that cap is reviewed.

Table: `phase7-mpnst-ber-genes.csv` (28 BER rows with any evidence).

## 3. PARP1 itself was measured, and it is up

PARP1 is absent from the Phase 3 **candidate** table, which is why Phase 7 filed it as
literature-only. It is not absent from the data:

- measured in **6 of the MPNST datasets**
- significant in **1** of them, FDR 1.6e-3, median log2FC **+1.26**, direction up
- tier `C_single_dataset`, rank 2,547 — below the candidate cut because it replicated in only
  one dataset, not because nothing was seen

Phase 6 therefore scores PARP1 with `s_expression` unassessed, which is correct under the
absence-is-not-evidence rule, but a reader should know the expression evidence exists at C tier.

## 4. The literature claim was never an overexpression claim

Phase 1b's PARP1 row (PMID 42310314, full text read, mouse model):

> Olaparib combined with selumetinib suppressed tumour growth by 61.6% in an NF1-18B MPNST
> PDOX model, with loss of PARylation confirming target engagement.

That is a **pharmacological combination result**, not a claim that PARP1 is overexpressed. The
expression signature and the literature claim are different kinds of evidence; pathway
co-membership matched them, but the expression data was never the right corroboration for a
synthetic-lethality-style drug hypothesis. Phase 7's framing of this as independent
corroboration was wrong, and the near-miss heuristic is what produced it.

## 5. PARP1 remains a strong candidate — for reasons Phase 7 did not cite

| | |
|---|---|
| Phase 6 rank in NF1 MPNST | **22 of 858** |
| Phase 6 score | 0.75, on **3 of 5** components (no expression, no mechanism) |
| drugs mapped | 47, of which 7 approved |
| best max phase | **4** — olaparib, niraparib, rucaparib, talazoparib |
| tractability | "Approved Drug" bucket, 10 buckets, small molecule |
| safety | 0 black-box, 0 withdrawn |
| CNS delivery | not applicable; MPNST does not carry `bbb_required` |

It ranks 22nd *without* an expression component. The case rests on an in vivo result with
confirmed target engagement, plus a mature approved-drug class — which is a better case than
the pathway coincidence Phase 7 offered.

## 6. The combination is untested in NF1 MPNST

Searching the Phase 4 trial tables, exactly **one** PARP inhibitor appears in any NF trial:
**veliparib**, in NCT00946335 — a completed Phase 1 in **optic pathway glioma**, not MPNST.
No olaparib, niraparib, rucaparib or talazoparib trial in NF appears in these tables.

The proposed partner, **selumetinib, is the FDA-approved NF1 agent**. So the specific hypothesis
— a PARP inhibitor plus selumetinib in NF1 MPNST — is supported by one in vivo study and has not
been taken into an NF trial.

Discrepancy, flagged not resolved: the Phase 4 dossier records `n_drugs_in_nf_trials = 2` for
PARP1. Only veliparib reproduces from `phase4-trial-drugs.csv`, by exact and by first-token
matching. The second drug could not be identified.

## What should follow

1. **Correct the Phase 7 record** so the PARP1 convergence is not cited as mechanism-level
   corroboration. Done — this file is referenced from `phase7-literature-validation.md`.
2. **The near-miss specificity rule needs a proliferation control.** It selected BER over the
   more-enriched DNA replication purely on pathway size. Any future pathway near-miss in a
   malignant-versus-benign contrast should be compared against the contrast's own background
   before being reported as a finding.
3. **PARP1 is worth carrying on its drug profile**, not on expression. If a single target were
   taken forward from NF1 MPNST on tractability grounds, this is a defensible choice.

## Limits

Single contrast (`nf1_mpnst_vs_benign_pnst`), single literature paper in a mouse PDOX model,
and no new literature search was run for this look — it reads the committed Phase 1b, 3, 4, 6
and 7 tables only. Pathway membership is KEGG as committed in Phase 3. No statistical test of
BER-versus-background enrichment was performed; the comparison is descriptive, and the ordering
of pathways is what carries the argument, not a p-value.
