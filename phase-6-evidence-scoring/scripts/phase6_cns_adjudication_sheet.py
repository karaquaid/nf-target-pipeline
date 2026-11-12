#!/usr/bin/env python3
"""Build the Phase 6 CNS-delivery adjudication review sheet.

The Phase 5 CNS literature pass (phase5-cns-literature-claims.csv) ends with a
keyword direction label that is explicitly NOT an adjudication: the commit that
produced it flags trametinib's brain-to-plasma paper as the counterexample, a
sentence the classifier calls `supporting` while the finding is efflux-limited
penetration. Phase 6 scores CNS delivery three-state (demonstrated / contradicted
/ unknown), so the 124 attributed claims - the subset where the retrieved drug is
actually named in the sentence - need a read before the rubric can use them.

This script does no judging. It assembles the reading material: one row per
attributed claim with the quoted sentence, PMID, access level and links, grouped
by active moiety, with blank verdict columns to fill; one rollup row per moiety
carrying the verdicts the pipeline already holds (ChEMBL calculated descriptor
flag, openFDA label verdict, clinical-trial-in-CNS-manifestation evidence) so the
reader can see what the literature read has to overturn or confirm.

Inputs  (phase-5-mechanistic-validation/data/)
  phase5-cns-literature-claims.csv   452 sentences, 124 attributed
  phase5-cns-literature-by-drug.csv  per-moiety screening counts
  phase5-label-cns-verdicts.csv      openFDA label-text verdicts
  phase5-drug-matches.csv.gz         per-drug flags from Phases 4-5

Outputs (phase-6-evidence-scoring/)
  data/phase6-cns-adjudication-sheet.csv    124 claim rows + blank verdict cols
  data/phase6-cns-adjudication-rollup.csv    20 moiety rows + blank verdict cols
  docs/phase6-cns-adjudication-sheet.md      the readable sheet, grouped by drug
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
P5 = ROOT / "phase-5-mechanistic-validation" / "data"
OUT_DATA = ROOT / "phase-6-evidence-scoring" / "data"
OUT_DOCS = ROOT / "phase-6-evidence-scoring" / "docs"

# Controlled vocabularies the reader fills in. Kept here so the CSV, the markdown
# sheet and any downstream merge all read from one definition.
VERDICTS = ["demonstrated", "contradicted", "unknown"]
EVIDENCE_BASIS = [
    "measured_pk_human",        # CSF, brain tissue or Kp,uu measured in people
    "measured_pk_animal",       # brain:plasma or Kp,uu measured in an animal model
    "clinical_cns_response",    # intracranial response / CNS remission, no PK number
    "preclinical_cns_efficacy", # survival or tumour control in an intracranial model
    "mechanistic_assertion",    # efflux-substrate or permeability claim, no exposure
    "review_restatement",       # restates another paper's finding
    "design_or_prediction",     # computed, designed-for or predicted penetration
]
PRIMARY = ["primary", "restated", "unclear"]
SPECIES = ["human", "mouse", "rat", "other_animal", "in_vitro", "na"]

BLANK_CLAIM_COLS = [
    "verdict",            # demonstrated | contradicted | unknown
    "evidence_basis",     # from EVIDENCE_BASIS
    "primary_or_restated",
    "species",
    "metric",             # Kp,uu | brain:plasma | CSF:plasma | CSF conc | none
    "value",              # as stated in the sentence, verbatim
    "reviewer_note",
]
BLANK_DRUG_COLS = ["drug_verdict", "decisive_claim_ids", "drug_rationale"]


def _year(raw: str) -> str:
    """publication_date is stored as a stringified dict from the PubMed record."""
    try:
        return str(ast.literal_eval(raw).get("year", ""))
    except Exception:
        return ""


def _journal(raw: str) -> str:
    try:
        d = ast.literal_eval(raw)
        return d.get("iso_abbreviation") or d.get("title") or ""
    except Exception:
        return ""


def build() -> dict:
    claims = pd.read_csv(P5 / "phase5-cns-literature-claims.csv")
    by_drug = pd.read_csv(P5 / "phase5-cns-literature-by-drug.csv")
    labels = pd.read_csv(P5 / "phase5-label-cns-verdicts.csv")
    matches = pd.read_csv(P5 / "phase5-drug-matches.csv.gz", low_memory=False)

    att = claims[claims["drug_named_in_sentence"] == True].copy()  # noqa: E712

    att["pub_year"] = att["publication_date"].map(_year)
    att["journal_abbrev"] = att["journal"].map(_journal)
    att["pubmed_url"] = "https://pubmed.ncbi.nlm.nih.gov/" + att["pmid"].astype(str) + "/"
    att["pmc_url"] = att["pmcid"].apply(
        lambda p: "" if pd.isna(p) else f"https://www.ncbi.nlm.nih.gov/pmc/articles/{p}/"
    )

    # Read order within a drug: full text with a number is the most decidable,
    # abstract-only without a number the least. Stable claim ids follow that order
    # so the markdown sheet and the CSV can be read side by side.
    att["_rank"] = (
        (att["access"] != "full_text").astype(int) * 2
        + (~att["has_number"].astype(bool)).astype(int)
    )
    att = att.sort_values(["moiety", "_rank", "pmid"], kind="mergesort").reset_index(drop=True)
    att["claim_id"] = [f"CNS-{i:03d}" for i in range(1, len(att) + 1)]

    sheet_cols = [
        "claim_id", "moiety", "pmid", "pmcid", "access", "keyword_direction",
        "has_number", "sentence", "title", "journal_abbrev", "pub_year",
        "pubmed_url", "pmc_url", "doi",
    ]
    sheet = att.rename(columns={"direction": "keyword_direction"})[sheet_cols].copy()
    for col in BLANK_CLAIM_COLS:
        sheet[col] = ""

    # --- per-moiety rollup: counts plus the verdicts already in the pipeline ----
    drug_names = set(matches["drug_name"].dropna().unique())
    roll = []
    for _, m in by_drug.iterrows():
        variants = [v.strip() for v in str(m["label_variants"]).split("|") if v.strip()]
        present = [v for v in variants if v in drug_names]
        sub = matches[matches["drug_name"].isin(present)]
        cns_req = sub[sub["bbb_required"] == True]  # noqa: E712
        delivery = sub["cns_delivery_evidence"].fillna("")
        ids = sheet.loc[sheet["moiety"] == m["moiety"], "claim_id"].tolist()
        lab = labels[labels["drug_name"].isin(variants)]["label_verdict"].dropna().unique()
        roll.append(
            {
                "moiety": m["moiety"],
                "label_variants": m["label_variants"],
                "claims_attributed": int(m["claims_attributed"]),
                "claims_total": int(m["claims_total"]),
                "attributed_full_text": int(m["attributed_full_text"]),
                "attributed_abstract_only": int(m["attributed_abstract_only"]),
                "attributed_with_a_number": int(m["attributed_with_a_number"]),
                "claim_id_range": f"{ids[0]}-{ids[-1]}" if ids else "",
                # verdicts already held by the pipeline, for contrast
                "chembl_calculated_flag": ";".join(sorted(sub["cns_penetration_flag"].dropna().unique())),
                "openfda_label_verdict": ";".join(sorted(lab)) or "no_record",
                "rows_with_cns_trial_evidence": int((delivery == "clinical_trial_in_cns_manifestation").sum()),
                "n_rows_cns_required": int(len(cns_req)),
                "n_nf_trials_max": int(sub["n_nf_trials"].fillna(0).max()) if len(sub) else 0,
            }
        )
    rollup = pd.DataFrame(roll)
    for col in BLANK_DRUG_COLS:
        rollup[col] = ""
    # Drugs with attributed claims first, most claims first; zero-claim moieties last.
    rollup = rollup.sort_values(
        ["claims_attributed", "attributed_full_text"], ascending=False, kind="mergesort"
    ).reset_index(drop=True)

    OUT_DATA.mkdir(parents=True, exist_ok=True)
    OUT_DOCS.mkdir(parents=True, exist_ok=True)
    sheet.to_csv(OUT_DATA / "phase6-cns-adjudication-sheet.csv", index=False)
    rollup.to_csv(OUT_DATA / "phase6-cns-adjudication-rollup.csv", index=False)
    write_markdown(sheet, rollup)

    return {
        "claims_total": int(len(claims)),
        "claims_attributed": int(len(sheet)),
        "moieties_with_claims": int(sheet["moiety"].nunique()),
        "moieties_without_claims": int((rollup["claims_attributed"] == 0).sum()),
        "papers": int(att["pmid"].nunique()),
        "full_text": int((sheet["access"] == "full_text").sum()),
        "abstract_only": int((sheet["access"] == "abstract_only").sum()),
        "with_a_number": int(sheet["has_number"].astype(bool).sum()),
    }


def write_markdown(sheet: pd.DataFrame, rollup: pd.DataFrame) -> None:
    L: list[str] = []
    A = L.append
    A("# Phase 6 review sheet: adjudicating the CNS delivery claims\n")
    A(
        "The Phase 5 literature pass retrieved 452 CNS-relevant sentences for the 20 "
        "active moieties behind the shortlist drug labels, of which **124 actually name "
        "the drug they were retrieved for**. Those 124 are below, grouped by moiety. The "
        "other 328 mention a different drug than the one the paper was retrieved for and "
        "are not evidence about that drug.\n"
    )
    A("## What to decide\n")
    A(
        "Phase 6 scores CNS delivery three-state (project plan, Phase 6, settled "
        "2026-11-10). Fill `verdict` per claim against those definitions:\n"
    )
    A("| verdict | what qualifies |")
    A("| --- | --- |")
    A(
        "| `demonstrated` | measured exposure in the CNS compartment (CSF, brain tissue, "
        "Kp,uu, brain:plasma above a trivial ratio), or approval/trial activity in a CNS "
        "indication for the relevant manifestation |"
    )
    A(
        "| `contradicted` | measured pharmacokinetics showing CNS exclusion - the state "
        "the pipeline currently has no source for, which is why this read exists |"
    )
    A(
        "| `unknown` | everything else, including assertions without exposure data, "
        "review restatements and predictions. Scored as unassessed, never as a negative |"
    )
    A("")
    A(
        "`keyword_direction` is the Phase 5 regex label and is **a sorting aid, not a "
        "verdict** - it was wrong on trametinib's brain-to-plasma paper, calling an "
        "efflux-limited finding `supporting`. Read the sentence, not the label.\n"
    )
    A("Controlled vocabularies for the remaining columns:\n")
    A(f"- `evidence_basis`: {', '.join('`' + v + '`' for v in EVIDENCE_BASIS)}")
    A(f"- `primary_or_restated`: {', '.join('`' + v + '`' for v in PRIMARY)}")
    A(f"- `species`: {', '.join('`' + v + '`' for v in SPECIES)}")
    A(
        "- `metric` / `value`: the quantity as the sentence states it (`Kp,uu`, "
        "`brain:plasma`, `CSF:plasma`, `CSF concentration`, `none`), copied verbatim\n"
    )
    A(
        "A claim read from an abstract can still be decisive when the abstract states the "
        "measurement itself - record it and leave `access` as the provenance, as Phase 1b "
        "does. The drug-level verdict goes in "
        "`data/phase6-cns-adjudication-rollup.csv`; a drug needs one `demonstrated` or "
        "`contradicted` claim it rests on, named in `decisive_claim_ids`.\n"
    )

    A("## Where each drug stands before the read\n")
    A(
        "| moiety | attributed claims | full text | with a number | claim ids | ChEMBL calculated flag | openFDA label | rows w/ CNS trial evidence | max NF trials |"
    )
    A("| --- | ---: | ---: | ---: | --- | --- | --- | ---: | ---: |")
    for _, r in rollup.iterrows():
        A(
            f"| {r['moiety']} | {r['claims_attributed']} | {r['attributed_full_text']} | "
            f"{r['attributed_with_a_number']} | {r['claim_id_range'] or '-'} | "
            f"{r['chembl_calculated_flag'] or '-'} | {r['openfda_label_verdict']} | "
            f"{r['rows_with_cns_trial_evidence']} | {r['n_nf_trials_max']} |"
        )
    A("")
    zero = rollup[rollup["claims_attributed"] == 0]["moiety"].tolist()
    if zero:
        A(
            f"{len(zero)} moieties carry no attributed claim and so cannot move off "
            f"`unknown` on literature evidence: {', '.join(zero)}. "
            "They are listed in the rollup so the absence is recorded rather than silent.\n"
        )

    A("## The claims\n")
    for moiety, grp in sheet[sheet["moiety"] != ""].groupby("moiety", sort=False):
        rr = rollup[rollup["moiety"] == moiety].iloc[0]
        A(f"### {moiety}\n")
        A(
            f"{len(grp)} attributed of {rr['claims_total']} retrieved sentences · "
            f"{rr['attributed_full_text']} full text, {rr['attributed_abstract_only']} "
            f"abstract-only · ChEMBL calculated flag: `{rr['chembl_calculated_flag'] or 'none'}` · "
            f"openFDA label: `{rr['openfda_label_verdict']}` · "
            f"CNS-manifestation trial evidence on {rr['rows_with_cns_trial_evidence']} drug rows\n"
        )
        A("**Drug verdict:** _______  (`demonstrated` / `contradicted` / `unknown`), resting on claim id(s): _______\n")
        for _, c in grp.iterrows():
            num = "number" if bool(c["has_number"]) else "no number"
            src = f"[PMID {c['pmid']}]({c['pubmed_url']})"
            if c["pmc_url"]:
                src += f" · [PMC]({c['pmc_url']})"
            A(f"- **{c['claim_id']}** · {src} · `{c['access']}` · `{c['keyword_direction']}` · {num}")
            # 11 of the 124 sentences carry line breaks from the PMC full text; they
            # would split the blockquote, so whitespace is collapsed for display only.
            # The CSV keeps the sentence exactly as Phase 5 extracted it.
            quoted = " ".join(str(c["sentence"]).split())
            A(f"  - > {quoted}")
            A(f"  - *{c['title'].strip()}* — {c['journal_abbrev']} {c['pub_year']}")
            A("  - verdict: _______ · basis: _______ · primary/restated: _______ · species: _______ · metric/value: _______")
        A("")

    (OUT_DOCS / "phase6-cns-adjudication-sheet.md").write_text("\n".join(L))


if __name__ == "__main__":
    summary = build()
    (OUT_DATA / "phase6-cns-adjudication-provenance.json").write_text(
        json.dumps(
            {
                "built_by": "phase-6-evidence-scoring/scripts/phase6_cns_adjudication_sheet.py",
                "inputs": [
                    "phase-5-mechanistic-validation/data/phase5-cns-literature-claims.csv",
                    "phase-5-mechanistic-validation/data/phase5-cns-literature-by-drug.csv",
                    "phase-5-mechanistic-validation/data/phase5-label-cns-verdicts.csv",
                    "phase-5-mechanistic-validation/data/phase5-drug-matches.csv.gz",
                ],
                "verdict_vocabulary": VERDICTS,
                "evidence_basis_vocabulary": EVIDENCE_BASIS,
                "note": (
                    "No adjudication is performed here. Verdict columns ship blank; the "
                    "Phase 5 keyword direction label is carried as a sorting aid only."
                ),
                "counts": summary,
            },
            indent=2,
        )
        + "\n"
    )
    print(json.dumps(summary, indent=2))
