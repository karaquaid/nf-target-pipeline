#!/usr/bin/env python3
"""Regenerate docs/phase1b-literature-targets.md from the Phase 1b tables.

Every count in the write-up that describes the CURRENT state of the list is
computed here from the CSVs, so the prose, the coverage table and the figure
caption cannot drift from the data. Counts that describe the PROCESS (how many
articles a search returned, how many rows a past round dropped) are not
recoverable from the tables and are held in PROCESS_HISTORY below, with the
commit that established each one.

Usage (from the repository root):

    python scripts/build_phase1b_report.py
    python scripts/build_phase1b_report.py --out docs/phase1b-literature-targets.md

Requires pandas. Run scripts/make_phase1b_figure.py to regenerate Figure 1.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_phase1b_figure import DISEASES, MANIFESTATIONS  # noqa: E402

# Process counts, each fixed at the point the round ran. Not derivable from the
# current tables: they describe work done, including rows that no longer exist.
PROCESS_HISTORY = {
    "n_queries": 32,
    "n_articles": 492,
    "n_abstracts": 482,
    "n_papers_with_targets": 303,
    "rows_first_version": 547,
    "rows_sporadic_dropped": 168,  # disease could not be attributed: PR #2
    "rows_failed_verification_dropped": 2,  # PR #2
    "papers_round1": 56,  # NCBI PMC route, part judged from excerpts
    "papers_epmc_oa": 89,  # PR #4
    "pairs_epmc": 254,
    "pairs_excerpt_cleanup": 9,  # PR #4, commit 7f34ddb
    "papers_author_manuscript": 28,  # PR #5, commit 230eb10
    "pairs_author_manuscript": 35,
    "rows_whole_text_dropped": 20,  # PR #4
    "pdfs_supplied": 29,  # PR #6
    "pdfs_read": 20,
    "pdfs_already_held": 9,
    "pairs_pdf": 64,
    "pdf_verdicts": "37 supported, 15 partially supported, 12 not supported",
    "rows_pdf_dropped": 16,
    "rows_moved_up_by_pdfs": 52,
    "rows_removed_by_pdfs": 11,
    "relabels_whole_text": 42,
    "relabels_manual_other": 5,
    "relabels_author_manuscript": 1,
    "relabels_pdf": 2,
}

TIER_ORDER = [
    "full text - supported",
    "full text - partial",
    "full text - not supported",
    "abstract only",
]


def flag_summary(candidates: pd.DataFrame) -> dict:
    """Counts for the three curated target annotations, per label and per row."""
    labels = candidates.drop_duplicates("gene_target")
    flags = ["likely_biomarker", "mutation_restricted", "tme_target"]
    clean = ~labels.likely_biomarker & ~labels.mutation_restricted & ~labels.tme_target
    unflagged = labels[clean]
    supported = candidates[candidates.evidence_tier == "full text - supported"]
    return {
        "n_labels": len(labels),
        "labels": {f: int(labels[f].sum()) for f in flags},
        "rows": {f: int(candidates[f].sum()) for f in flags},
        "n_clean": int(clean.sum()),
        "clean_supported": sorted(
            set(supported[supported.gene_target.isin(unflagged.gene_target)].gene_target)
        ),
        "biomarker_and_tme": int((labels.likely_biomarker & labels.tme_target).sum()),
        "n_overridden": int((labels.annotation_source != "model").sum()),
        "top_mutation_contexts": [
            f"{r.gene_target} ({r.mutation_context.split(',')[0].strip()})"
            for r in labels[labels.mutation_restricted]
            .nlargest(4, "n_supporting_papers").itertuples()
        ],
    }


def collect(targets: pd.DataFrame, candidates: pd.DataFrame, refs: pd.DataFrame,
            queue: pd.DataFrame) -> dict:
    """Every current-state number the write-up quotes."""
    cov = (
        candidates.pivot_table(index="manifestation", columns="disease",
                               values="gene_target", aggfunc="count", fill_value=0)
        .reindex(MANIFESTATIONS)
        .fillna(0)
        .astype(int)
    )
    for disease in DISEASES:
        if disease not in cov:
            cov[disease] = 0
    cov = cov[DISEASES]
    cov["total"] = cov.sum(axis=1)

    tiers = candidates.evidence_tier.value_counts()
    supported = int(tiers.get("full text - supported", 0))
    per_bar = candidates.groupby(["disease", "manifestation"]).size()
    sup_per_bar = (
        candidates[candidates.evidence_tier == "full text - supported"]
        .groupby(["disease", "manifestation"])
        .size()
        .reindex(per_bar.index)
        .fillna(0)
    )
    big = (sup_per_bar / per_bar)[per_bar >= 20]
    access = refs.access_used.value_counts()
    read_in_full = int(refs.access_used.astype(str).str.startswith("full_text").sum())
    drivers = targets[targets.driver_gene]

    return {
        "cov": cov,
        "n_rows_full": len(targets),
        "n_labels_full": targets.gene_target.nunique(),
        "n_rows": len(candidates),
        "n_labels": candidates.gene_target.nunique(),
        "n_genes": len({g for s in candidates.constituent_genes.fillna("")
                        for g in str(s).split(";") if g}),
        "n_papers": len(refs),
        "read_in_full": read_in_full,
        "unread": len(refs) - read_in_full,
        "access": {k: int(v) for k, v in access.items()},
        "tiers": {t: int(tiers.get(t, 0)) for t in TIER_ORDER},
        "anchored": len(candidates) - int(tiers.get("abstract only", 0)),
        "pct_supported": round(100 * supported / len(candidates)),
        "n_big_bars": int(len(big)),
        "big_lo": round(100 * big.min()),
        "big_hi": round(100 * big.max()),
        "by_disease": {d: int((candidates.disease == d).sum()) for d in DISEASES},
        "label_types": candidates.label_type.value_counts().to_dict(),
        "pairs_whole_body": int(candidates.verdicts_from_whole_body.sum()),
        "n_drivers": len(drivers),
        "driver_counts": drivers.gene_target.value_counts().to_dict(),
        "driver_supported": int((drivers.evidence_tier == "full text - supported").sum()),
        "n_preprints": int(refs.is_preprint.sum()),
        # Detection reports bioRxiv under two DOI prefixes; collapse to one name.
        "preprint_servers": (
            refs[refs.is_preprint].preprint_server.astype(str)
            .str.replace("bioRxiv/medRxiv", "bioRxiv", regex=False)
            .value_counts().to_dict()
        ),
        "n_preprint_only": int(candidates.preprint_only.sum()),
        "preprint_only": [f"{r.gene_target} ({r.disease}, {r.manifestation})"
                          for r in candidates[candidates.preprint_only].itertuples()],
        "papers_no_candidate": int((~refs.supports_candidate_rows).sum()),
        "queue_open": int((queue.pdf_status == "still needed").sum()),
        "queue_judged": int((queue.pdf_status == "judged from your PDF").sum()),
        "rows_anchored_by_pdf": int(queue.rows_anchored_by_pdf.sum()),
        "thin": {m: int(cov.loc[m, "total"]) for m in MANIFESTATIONS
                 if 0 < cov.loc[m, "total"] < 10},
        "empty": [m for m in MANIFESTATIONS if cov.loc[m, "total"] == 0],
        "no_supported": [m for m in MANIFESTATIONS if cov.loc[m, "total"] > 0 and
                         candidates[(candidates.manifestation == m) &
                                    (candidates.evidence_tier == "full text - supported")].empty],
        "top": {d: candidates[(candidates.disease == d)].nlargest(1, "n_supporting_papers")
                for d in DISEASES},
        "flags": flag_summary(candidates),
    }


def phrase(counts: dict, joiner: str = ", ") -> str:
    return joiner.join(f"{k} ({v})" for k, v in counts.items())


def build(s: dict, h: dict) -> str:
    cov = s["cov"]
    cov_rows = "\n".join(
        f"| {m} | {cov.loc[m, 'NF1']} | {cov.loc[m, 'NF2-SWN']} | {cov.loc[m, 'SWN']} "
        f"| {cov.loc[m, 'total']} |" for m in MANIFESTATIONS
    )
    thin = ", ".join(f"{m} ({n})" for m, n in sorted(s["thin"].items(), key=lambda kv: kv[1]))
    mek = s["top"]["NF1"].iloc[0]
    # Tiers with no rows are omitted rather than printed as zeros.
    tier_rows = "\n".join(f"| {tier} | {count} |" for tier, count in s["tiers"].items() if count)
    f = s["flags"]

    return f"""# Phase 1b: literature-derived candidate targets

Phase 1b asks what the published literature already proposes as a molecular target in
neurofibromatosis, and how well each of those proposals is actually evidenced. It is
deliberately independent of the expression arm of the pipeline: no expression data was
consulted, and the list is held for the Phase 7 comparison, where agreements and
one-sided findings between the two derivations are examined. Every target carries a
disease label (NF1, NF2-SWN, SWN) and one or more manifestations from the project's
fixed twenty-term vocabulary, applied verbatim.

The phase is complete. It produced a **candidate list of {s['n_rows']} gene x disease x
manifestation rows over {s['n_labels']} target labels covering {s['n_genes']} distinct
gene symbols, drawn from {s['n_papers']} papers**, of which {s['read_in_full']} were read
in full. {s['anchored']} of the {s['n_rows']} rows are anchored in at least one paper
verified against its complete text; {s['tiers']['abstract only']} rest on abstracts alone
and are labelled as such. A wider annotated table of {s['n_rows_full']} rows is retained
for audit, the difference being the germline NF genes excluded as targets.

## Outputs

| File | What it holds |
|---|---|
| `data/phase1b-candidate-targets.csv` | The prioritisation input. {s['n_rows']} rows, germline NF genes excluded. |
| `data/phase1b-literature-targets.csv` | All {s['n_rows_full']} verified rows with a `driver_gene` flag, for audit. |
| `data/phase1b-references.csv` | {s['n_papers']} papers: DOI, PMC id, access route, preprint status, targets supported, manifestations covered, resolvable link. |
| `data/phase1b-coverage.csv` | The coverage matrix below, machine-readable. |
| `data/phase1b-target-annotations.csv` | Per-label curated flags: biomarker-like, mutation-restricted, microenvironment target. |
| `data/phase1b-upload-priority.csv` | PDF queue and progress tracker: {s['queue_open']} papers still worth fetching. |
| `docs/figures/phase1b-coverage-verification.png` | Figure 1. |
| `scripts/make_phase1b_figure.py` | Regenerates Figure 1 from the candidate table. |
| `scripts/build_phase1b_report.py` | Regenerates this document from the tables. |

## How the list was built

1. **Search.** {h['n_queries']} PubMed queries spanning NF1, NF2-SWN and SWN crossed with the fixed manifestation vocabulary, relevance-sorted, 18 results per query, `date_from=2005`, returned {h['n_articles']} unique PMIDs; metadata and abstracts were retrieved for {h['n_abstracts']}. {h['n_papers_with_targets']} of those papers named at least one molecular target presented as a driver, modifier or therapeutic target.
2. **Abstract extraction.** Each abstract was passed to a model extraction step returning gene, disease, manifestation(s) from the fixed list, role, mechanism and study system, with explicit instructions not to extract cohort-defining gene mentions or assay reagents. Calls that failed transiently were re-run rather than dropped.
3. **Symbol normalisation.** Gene strings were mapped through an alias table and validated against official HGNC symbols. Alias-permissive matching was rejected after it mapped common shorthand onto unrelated genes, so validation uses official symbols only with the residue curated by hand. Labels that are genuinely a family, complex or pathway are kept as the label and expanded in `constituent_genes`, with `label_type` recording which kind of entity each is: {phrase(s['label_types'])}. Two labels are not gene products at all. HYALURONAN, a glycosaminoglycan, carries the enzymes that synthesise and degrade it in `constituent_genes` (HAS1-3, HYAL1-4, SPAM1, CEMIP, CEMIP2) so that later phases have something to query, and those symbols are curated rather than extracted from the paper, which measures the polysaccharide itself. The clemastine row names a drug effect with no target attached and is still unexpanded.
4. **First verification round.** Full text was sought through the PubMed connector's NCBI PMC route, which reached {h['papers_round1']} papers. Part of that round was judged from short gene-centred excerpts rather than complete articles, which left those verdicts provisional. Both limits were later traced to the retrieval route rather than to access.
5. **Review round.** Four scope decisions were applied: rows whose disease could not be attributed were dropped, excluding sporadic tumours from the project ({h['rows_sporadic_dropped']} rows, from a first version of {h['rows_first_version']}); {h['rows_failed_verification_dropped']} rows that failed verification outright were dropped; manifestation labels were corrected from full text at the level of the individual paper rather than the whole row; and family labels were kept with the `constituent_genes` column added.
6. **Whole-text verification.** Europe PMC's `/{{PMCID}}/fullTextXML` endpoint holds a larger open-access subset than the NCBI route, and {h['papers_epmc_oa']} of the papers proved retrievable there. All {h['pairs_epmc']} row-paper pairs among them were re-judged against complete bodies, reference sections stripped, one reasoning pass per paper, no excerpting. {h['rows_whole_text_dropped']} single-paper rows were dropped as contradicted by their own paper on full reading.
7. **Excerpt cleanup.** The remaining pairs still carrying excerpt-based verdicts were re-judged over complete bodies recovered from Europe PMC or NCBI efetch ({h['pairs_excerpt_cleanup']} pairs). No row now rests on an excerpt verdict.
8. **Author-manuscript harvest.** Open-access status and readability turned out to be different things: an NIH author manuscript can sit free in PMC while the publisher version is paywalled, and Europe PMC's open-access endpoint refuses those while NCBI efetch serves them. That route added {h['papers_author_manuscript']} papers and {h['pairs_author_manuscript']} judged pairs at no cost.
9. **Supplied PDFs.** {h['pdfs_supplied']} PDFs were supplied from subscription access for papers no free route could reach. All matched corpus papers by DOI, or by title where the file carried none; {h['pdfs_already_held']} were papers already read by another route. The other {h['pdfs_read']} were read in full and their {h['pairs_pdf']} pairs judged on the same rubric ({h['pdf_verdicts']}). {h['rows_moved_up_by_pdfs']} rows moved up a tier, {h['rows_removed_by_pdfs']} abstract-only rows were removed as contradicted, and {h['rows_pdf_dropped']} rows were dropped in total.
10. **Manifestation cleanup.** Papers filed under "Other" that in fact study a vocabulary manifestation were moved: {h['relabels_manual_other']} by hand on review, alongside {h['relabels_whole_text'] + h['relabels_author_manuscript'] + h['relabels_pdf']} moved automatically where the full text disagreed with the abstract. All moves are per paper, so a paper that studies a different manifestation moves only its own support.
11. **Preprint flagging.** {s['n_preprints']} papers are preprints rather than peer-reviewed articles ({phrase(s['preprint_servers'])}). `is_preprint` and `preprint_server` mark them per paper; `n_preprint_papers` and `preprint_only` mark the rows that depend on them.
12. **Driver-gene exclusion.** The germline NF disease genes were excluded as candidates, on the grounds that their role is established and re-prioritising them tells the project nothing.

Verdicts from a later round override earlier ones, and {s['pairs_whole_body']} of the row-paper pairs behind the current list have been judged against a complete article body.

## The current list

| Evidence tier | Rows |
|---|---|
{tier_rows}

By disease: NF1 {s['by_disease']['NF1']} rows, NF2-SWN {s['by_disease']['NF2-SWN']},
SWN {s['by_disease']['SWN']}. No row here is contradicted by its own papers: rows whose
full text does not support the claim are excluded from the candidate list and kept only in
the audit table, where their tier and supporting papers remain visible. The
`full text - partial` tier is different and stays: the target is real but the disease or
manifestation attribution is looser than the row claims.

## Coverage by disease and manifestation

| Manifestation | NF1 | NF2-SWN | SWN | Total |
|---|---|---|---|---|
{cov_rows}

![Stacked horizontal bars of candidate target rows per manifestation, one panel per disease, shaded by whether the strongest supporting paper was read in full text or only as an abstract](figures/phase1b-coverage-verification.png)

**Figure 1. Coverage and verification depth by disease and manifestation.** Bar length is
the number of candidate target rows (n = {s['n_rows']} claims, germline NF genes
excluded); shading is the provenance of the strongest supporting paper behind each row.
Panels share an x axis, so bar lengths are comparable across diseases; a grey dot marks a
manifestation with no rows at all in that disease. {s['tiers']['full text - supported']} of
{s['n_rows']} rows ({s['pct_supported']} percent) are anchored in a paper read in full, and
in the {s['n_big_bars']} manifestations holding 20 or more rows that share runs from
{s['big_lo']} to {s['big_hi']} percent, so the principal tumour types are well evidenced.
What the figure shows is how sharply coverage falls away from them: {thin} rows
respectively, no rows at all for {', '.join(s['empty'])}, and no full-text-supported target
for {', '.join(s['no_supported'])}.

## What the evidence says

### NF1

{s['by_disease']['NF1']} rows. The MEK1/2 axis dominates and is the only NF-relevant target
in this sweep with regulatory-grade human evidence. Selumetinib in inoperable plexiform
neurofibroma is the strongest row in the list ({int(mek.n_supporting_papers)} supporting
papers), running from the phase 1 dose-finding cohort
([Dombi 2016](https://doi.org/10.1056/NEJMoa1605943)) through the phase 2 SPRINT trial that
supported approval ([Gross 2020](https://doi.org/10.1056/NEJMoa1912735)) to longer-term
safety and efficacy data ([Kim 2024](https://doi.org/10.1093/neuonc/noae121)). The same node
carries into NF1-associated glioma, both optic pathway and non-optic low-grade.

Malignant progression is the second well-supported axis, and it is a loss-of-function story
rather than a druggable-kinase one. *CDKN2A* deletion marks the plexiform to atypical
transition ([Chaney 2020](https://doi.org/10.1158/0008-5472.CAN-19-1429)), and PRC2 component
loss separates MPNST from its benign precursors
([Cortes-Ciriano 2023](https://doi.org/10.1158/2159-8290.CD-22-0786)). Both are tumour
suppressor losses: strong stratification markers, poor direct drug targets, which is the
direction-of-effect distinction the Phase 6 rubric has to encode.

NF1 pain retains a mechanistically coherent set built on the neurofibromin-CRMP2 interface
and downstream N-type calcium channel regulation
([Moutal 2017](https://doi.org/10.1097/j.pain.0000000000001026);
[Khanna 2019](https://doi.org/10.1097/j.pain.0000000000001648)), and is the clearest
non-tumour manifestation with a nameable target. Both nodes were confirmed over complete
text: CRMP2 freed from neurofibromin drives CaV2.2 and NaV1.7 trafficking in sensory
neurons, shown by CRISPR truncation of *Nf1*.

### NF2-SWN

{s['by_disease']['NF2-SWN']} rows. Merlin loss converges on the Hippo pathway and on PAK and
PI3K signalling, and the therapeutic literature is preclinical or early-phase rather than
approved. Everolimus reached a phase 0 trial in vestibular schwannoma and meningioma
([Karajannis 2021](https://doi.org/10.1158/1535-7163.MCT-21-0143)). Whole-text reading
strengthened the Hippo node: YAP1-TEAD in vestibular schwannoma, dropped from the first
version as an unattributable "Other" row, is now supported in its proper manifestation, on
TEAD1 inhibition reversing tumorigenic signalling in merlin-inactivated Schwann cells
([Laws 2025](https://doi.org/10.1101/2025.11.15.688608), a preprint). The PAK arm is weaker
than the abstracts suggested: reading the PAK and Hippo combination study in full
([Benton 2024](https://doi.org/10.1371/journal.pone.0305121)) returned no supported verdict
on either row it touches, leaving PAK1/2 as a partial row in non-vestibular schwannoma,
where PAK binding to merlin and PAK inhibition in NF2-deficient lines are shown but the
vestibular attribution is not. Merlin-deficient meningioma has been targeted through
NEDD8-pathway and selumetinib combination
([Lyons Rimmer 2020](https://doi.org/10.3390/cancers12071744)).

VEGFA is the one NF2 target with real-world clinical use, bevacizumab for NF2-associated
vestibular schwannoma ([Fujii 2020](https://doi.org/10.2176/nmc.oa.2019-0194)). Spatial
profiling of the same tumours adds a target the abstract sweep would have missed:
CD44-positive Schwann cells are more abundant in bevacizumab-failure tumours
([Jones 2025](https://doi.org/10.1038/s41467-025-57586-z)), a resistance marker rather than a
primary target, and the kind of row that only appears when the body is read.

### SWN (schwannomatosis)

{s['by_disease']['SWN']} rows, and the driver exclusion is what makes that number so small:
*LZTR1* and *SMARCB1* were most of what the SWN literature offers, and both are now held in
the audit table rather than the candidate list. What survives is the RAS axis, which is the
useful cross-disease link, since LZTR1 acts in a CUL3 complex that ubiquitinates RAS
([Steklov 2018](https://doi.org/10.1126/science.aap7607)) and puts schwannomatosis on the
same pathway as NF1, plus a small set of inflammatory mediators in pain from mouse models.
Pain is the dominant clinical problem in schwannomatosis and no target with a mechanism
beyond the predisposition genes reached this list, which is a genuine gap rather than a
search artefact.

## Target annotations

Three flags travel with every target label, to stop the prioritisation treating unlike
things alike. They are **curated judgement, not extracted evidence**: each was assigned by
a model reading the row's own mechanism text together with what is known of the target's
pharmacology, then reviewed, with {f['n_overridden']} calls overridden by hand. They are
stored once per label in `data/phase1b-target-annotations.csv` and joined onto both tables,
so changing a call means editing that file, not a row.

| Flag | Labels | Rows | What it means |
|---|---|---|---|
| `likely_biomarker` | {f['labels']['likely_biomarker']} of {f['n_labels']} | {f['rows']['likely_biomarker']} | More useful for stratification, diagnosis or monitoring than as something a drug acts on. Dominated by tumour-suppressor losses, where the lesion is an absence, and by proliferation and lineage markers. |
| `mutation_restricted` | {f['labels']['mutation_restricted']} | {f['rows']['mutation_restricted']} | Relevant only to patients carrying a particular genotype. `mutation_context` names it, for example {'; '.join(f['top_mutation_contexts'])}. |
| `tme_target` | {f['labels']['tme_target']} | {f['rows']['tme_target']} | A drug would act on the microenvironment (endothelium, macrophages, mast cells, T cells, matrix) rather than on the Schwann-lineage tumour cell. |

{f['n_clean']} labels carry none of the three, and those are the closest thing this phase has
to conventional tumour-cell drug targets. {f['biomarker_and_tme']} labels carry both the
biomarker and microenvironment flags, typically secreted or immune markers measured in serum.

The flags are properties of the target, not of a manifestation, so a label that behaves
differently in two settings gets the call that dominates its evidence here, with the
tension recorded in `annotation_note`. KIT is the clearest such case: mast-cell recruitment
in plexiform neurofibroma is microenvironment biology, while the GIST row is tumour-cell.

These are a prioritisation aid, not a tractability assessment. Phase 4 queries ChEMBL and
the other target databases directly, and where it disagrees with a flag here, Phase 4 wins.

## Access and provenance

Full text was read for {s['read_in_full']} of {s['n_papers']} papers:
{phrase(s['access'], joiner='; ')}. {s['unread']} remain unread. Open-access status and
readability are not the same thing, and any later phase that needs full text should try
NCBI efetch before concluding a paper is unreachable, and link readers to
`europepmc.org/article/MED/<pmid>` rather than the DOI, which resolves to the publisher
paywall.

`data/phase1b-upload-priority.csv` doubles as work queue and progress record.
`pdf_status` says whether a paper was judged from a supplied PDF ({s['queue_judged']}), was
supplied but already in hand, or is still needed ({s['queue_open']}); `pdf_filename` names
the file and `rows_anchored_by_pdf` records what each one bought, {s['rows_anchored_by_pdf']}
rows in total. Papers still needed keep their rank, so the queue resumes where it stopped.

## Scope decisions

Each of these is a scope choice rather than a quality judgement, and each is reversible
because the excluded evidence is retained rather than deleted.

1. **Sporadic tumours are excluded.** Evidence that cannot be attributed to germline NF1, NF2-SWN or SWN was dropped, {h['rows_sporadic_dropped']} rows at the time. Somatic *NF2* loss in sporadic meningioma is the same molecular lesion as the germline case, so if Phase 3b selects meningioma or high-grade glioma these are the first rows to reconsider; they are reconstructible from the references table and the sweep output.
2. **Germline NF genes are excluded as candidates.** {s['n_drivers']} rows: {phrase(s['driver_counts'])}. {s['driver_supported']} of them were full-text supported, so this removed well-evidenced rows on scope grounds. They are retained in `phase1b-literature-targets.csv` with `driver_gene = True`.
3. **Recurrent somatic drivers are kept.** CDKN2A and CDKN2B, PRC2 components, TP53, MTAP, PTEN, RB1 and the RAS genes remain candidates despite being well described in NF tumour genetics, because they carry the malignant-progression signal Phase 6 stratification depends on.
4. **Rows contradicted by full text are excluded.** Where the papers read do not support the claim, the row leaves the candidate list even if a co-supporting paper is still unread, on the grounds that a contradicted claim should not be prioritised while it waits for confirmation it is unlikely to get. It keeps its row, tier and papers in the audit table, so re-reading a remaining paper can restore it.

## Limitations

Extraction is model-based over abstracts and verification is a single-reader model pass over
full text, with no second reader and no adjudication. Recall against a gold standard has not
been measured in either direction.

Rows in the abstract-only tier are not weaker claims about biology; they are claims nobody
has checked. The {s['tiers']['abstract only']} rows in that tier should not be weighed
against the {s['tiers']['full text - supported']} confirmed rows as though the difference
were biological.

{s['n_preprint_only']} rows rest on a preprint alone: {'; '.join(s['preprint_only'])}. Each is
also single-paper, so they are weak on more than one axis and should not clear a Phase 6
threshold unaided. Preprint status is detected from DOI prefix and journal string; the Europe
PMC publication-type cross-check could not be run when the service was returning errors, so a
preprint on an unusual server could be unflagged.

{', '.join(s['no_supported'])} has rows but no full-text-supported target, and
{', '.join(s['empty'])} has no rows at all after every one of its claims failed whole-text
verification. Both are statements about this corpus rather than about the biology: the
mechanistic GIST literature sits in sporadic KIT-mutant disease, which the sporadic exclusion
removes.

The manifestation vocabulary has no disease-level slot, so whole-disease review claims with no
manifestation to attach to are pooled into "Other" alongside genuine phenotypes. Three real NF
phenotypes are also absent from the fixed list: retinal neovascularization, pheochromocytoma
and cafe-au-lait macules. This will recur in every future extraction pass until the vocabulary
gains a term.

Queries were capped at 18 results each and date-filtered from 2005, so highly cited older
primary work is under-represented, and citation-graph expansion was not performed.

## Reproducing

From the repository root, in this order:

    python scripts/make_phase1b_candidates.py   # candidate list from the audit table
    python scripts/build_phase1b_report.py      # this document and the coverage matrix
    python scripts/make_phase1b_figure.py       # Figure 1

All three read only the CSVs in `data/`. Re-run them after any change to the row set rather
than editing numbers by hand. The first applies the scope filters, so changing what counts
as excluded means editing that script and re-running all three.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--out", type=Path,
                        default=Path("docs/phase1b-literature-targets.md"))
    args = parser.parse_args()

    targets = pd.read_csv(args.data / "phase1b-literature-targets.csv")
    candidates = pd.read_csv(args.data / "phase1b-candidate-targets.csv")
    refs = pd.read_csv(args.data / "phase1b-references.csv", dtype={"pmid": str})
    queue = pd.read_csv(args.data / "phase1b-upload-priority.csv", dtype={"pmid": str})

    stats = collect(targets, candidates, refs, queue)
    text = build(stats, PROCESS_HISTORY)
    if "\u2014" in text:
        raise AssertionError("em dash in generated text; project style forbids it")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    stats["cov"].to_csv(args.data / "phase1b-coverage.csv")
    print(f"wrote {args.out} ({len(text)} chars) and {args.data}/phase1b-coverage.csv")


if __name__ == "__main__":
    main()
