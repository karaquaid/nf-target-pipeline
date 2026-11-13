#!/usr/bin/env python3
"""Phase 6, stage 2: propose a CNS-delivery verdict for each attributed claim.

Stage 1 seated every claim in its source paragraph. This stage reads each packet
and proposes a verdict against the three-state rubric the project plan settled on
2026-11-10 - demonstrated / contradicted / unknown - together with the basis it
rests on, the species and experimental arm the measurement came from, and a
verbatim span from the supplied text supporting the call.

What this stage replaces: the Phase 5 keyword `direction` label, which is a regex
over penetration words and cannot see whether a sentence reports a measurement or
restates one, which arm a number came from, or which way the number points. That
label is kept in the tables as a sorting aid and is NOT an input here.

What this stage does NOT do: decide. Every output column is prefixed `proposed_`
and the blank human columns from the review sheet are carried through untouched.
A drug-level verdict is aggregated by an explicit rule in this file - not by the
model - and any drug whose decisive claims disagree is left blank and flagged for
review rather than resolved by majority.

Reads   data/phase6-cns-adjudication-sheet.csv
        data/phase6-cns-claim-context.json   (stage 1 cache; no network needed)
Writes  data/phase6-cns-adjudication-proposed.csv
        data/phase6-cns-adjudication-rollup.csv   (proposed_* columns added)
        data/phase6-cns-adjudication-model-run.json
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "phase-6-evidence-scoring" / "data"

VERDICT_RUBRIC = """
Score CNS delivery for the named drug in exactly one of three states.

demonstrated - the supplied text reports measured exposure of the drug in the CNS
  compartment (CSF concentration, brain tissue concentration, Kp,uu, or a
  brain-to-plasma ratio that is not trivially low), or reports approval/clinical
  activity against a CNS tumour or CNS disease site for this drug.
contradicted - the supplied text reports measured pharmacokinetics showing the
  drug is excluded from the CNS: a brain-to-plasma or CSF-to-plasma ratio that is
  low in absolute terms, drug not detectable in CSF, or exposure below the
  concentration needed for target engagement.
unknown - everything else. An assertion that a drug does or does not cross the
  blood-brain barrier with no exposure data behind it in the supplied text is
  unknown. A restatement of another paper's finding is unknown. A prediction, a
  design goal, or an in-vitro permeability assay alone is unknown.

unknown means unassessed. It is NOT a negative finding and must not be used to
express doubt about a measurement that is present. If a measurement is in the
text, judge its direction; if none is, return unknown.

Three traps this corpus is full of:
1. A brain-to-plasma ratio measured in transporter-knockout mice (Mdr1a/b, Bcrp1,
   Abcb1, Abcg2) or under an efflux inhibitor (tariquidar, elacridar) describes
   the transporter, not the exposure a patient gets. Record the arm. A ratio that
   is low in the wild-type arm of such a study IS a contradicted finding; a ratio
   that is high only in the knockout arm is not a demonstrated one.
2. A sentence in a Background, Introduction or Discussion section, or in a Review
   article, is usually restating work done elsewhere. Primary measurement sits in
   Results, in a table, or in the abstract of the paper that made it.
3. A number in the sentence is often not an exposure measurement at all - it can
   be a p-value, a dose, a patient count or a survival figure. Only an exposure
   quantity supports demonstrated or contradicted.

A fourth trap, which cost the first run two wrong calls:
4. The matched sentence is the reason the paper was retrieved, not the limit of
   the evidence. If the surrounding text from the same paper carries a
   measurement about THIS drug, adjudicate on that measurement and set
   basis_location to surrounding_text - do not return unknown because the matched
   sentence alone is an assertion. Conversely, an exposure increase produced by a
   co-intervention that opens the blood-brain barrier (an oncolytic virus,
   focused ultrasound, mannitol, a bradykinin agonist) is not evidence that the
   drug reaches the CNS on its own: set experimental_arm to
   bbb_modifying_cointervention.

A fifth distinction, which the first two runs could not express:
5. Record which COMPARTMENT the exposure was measured in. A drug can be excluded
   from cerebrospinal fluid and normal brain while still reaching an intracranial
   tumour, where the barrier is disrupted - that is one of the commonest findings
   in this literature and it is not a contradiction. Use `tumour_tissue` only when
   the text says the measurement is in tumour or metastasis tissue, `csf` or
   `normal_brain` when it names those, `brain_unspecified` when it says brain
   without saying which, and `plasma_only` when no CNS compartment was sampled.
   Judge the verdict for the compartment measured; do not downgrade a tumour
   measurement because CSF exposure is low, or vice versa.

Judge only from the text supplied. Do not use anything you know about this drug
from elsewhere, EXCEPT that the development codes listed under "also known as"
below name the same molecule - a paper using one of those codes is about this
drug. Quote the span you rely on verbatim; if no span in the supplied text
carries the call, the verdict is unknown with low confidence.
""".strip()

TOOL = {
    "name": "adjudicate_claim",
    "description": "Record a CNS-delivery verdict for one claim sentence.",
    "input_schema": {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["demonstrated", "contradicted", "unknown"]},
            "evidence_basis": {
                "type": "string",
                "enum": [
                    "measured_pk_human",
                    "measured_pk_animal",
                    "clinical_cns_response",
                    "preclinical_cns_efficacy",
                    "mechanistic_assertion",
                    "review_restatement",
                    "design_or_prediction",
                ],
            },
            "primary_or_restated": {"type": "string", "enum": ["primary", "restated", "unclear"]},
            "species": {
                "type": "string",
                "enum": ["human", "mouse", "rat", "other_animal", "in_vitro", "na"],
            },
            "experimental_arm": {
                "type": "string",
                "enum": [
                    "normal",
                    "transporter_knockout_or_inhibitor",
                    "bbb_modifying_cointervention",
                    "not_applicable",
                    "unclear",
                ],
            },
            "metric": {
                "type": "string",
                "description": "Exposure quantity named, e.g. brain:plasma, CSF:plasma, Kp,uu, CSF concentration, brain concentration, or none.",
            },
            "value": {
                "type": "string",
                "description": "The value as the text states it, verbatim, or an empty string.",
            },
            "compartment": {
                "type": "string",
                "enum": [
                    "csf",
                    "normal_brain",
                    "tumour_tissue",
                    "brain_unspecified",
                    "plasma_only",
                    "not_applicable",
                ],
                "description": "Which compartment the exposure was measured in. tumour_tissue only when the text says the measurement is in tumour or metastasis tissue.",
            },
            "basis_location": {
                "type": "string",
                "enum": ["matched_sentence", "surrounding_text", "both", "none"],
                "description": "Where in the supplied text the evidence behind the verdict sits.",
            },
            "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            "quoted_support": {
                "type": "string",
                "description": "Verbatim span from the supplied text that carries the verdict. Empty if none does.",
            },
            "rationale": {"type": "string", "description": "At most 40 words."},
            "needs_human_check": {"type": "boolean"},
        },
        "required": [
            "verdict",
            "evidence_basis",
            "primary_or_restated",
            "species",
            "experimental_arm",
            "compartment",
            "basis_location",
            "metric",
            "value",
            "confidence",
            "quoted_support",
            "rationale",
            "needs_human_check",
        ],
    },
}


def build_prompt(p: dict, synonyms: list[str] | None = None) -> str:
    pub_types = ", ".join(p.get("pub_types") or []) or "not recorded"
    aka = ", ".join(synonyms or []) or "none recorded"
    context = p.get("context_text") or "(no surrounding text could be retrieved)"
    return f"""Adjudicate one CNS-delivery claim.

RUBRIC
{VERDICT_RUBRIC}

DRUG UNDER ASSESSMENT: {p['moiety']}
  also known as (same molecule, ChEMBL synonyms): {aka}

PAPER
  title: {p['title']}
  journal/year: {p.get('journal','')} {p.get('year','') or ''}
  publication types: {pub_types}
  access level of the matched sentence: {p['access']}
  located in section: {p.get('context_section','')} (block type: {p.get('context_kind','')})

MATCHED SENTENCE (the claim to adjudicate)
  {" ".join(str(p['sentence']).split())}

SURROUNDING TEXT FROM THAT SECTION
  {" ".join(str(context).split())[:6000]}

Call adjudicate_claim once. The verdict is about {p['moiety']} only; if the
surrounding text measures a different drug, that is not evidence about this one.
"""


def aggregate(claims: pd.DataFrame) -> dict:
    """Drug-level proposal from claim verdicts, by explicit rule.

    Decisive = a primary (not restated) claim from a normal arm - not a
    transporter knockout/inhibitor arm and not one where a co-intervention opened
    the blood-brain barrier - whose verdict is not unknown. Human measurement outranks animal. A drug whose
    decisive claims disagree at the same level is NOT resolved here: it is left
    blank and flagged, because picking a side is the reviewer's call.
    """
    decisive = claims[
        (claims["proposed_primary_or_restated"] == "primary")
        & (claims["proposed_experimental_arm"].isin(["normal", "not_applicable"]))
        & (claims["proposed_verdict"] != "unknown")
    ]
    if decisive.empty:
        return {
            "proposed_drug_verdict": "unknown",
            "proposed_decisive_claim_ids": "",
            "proposed_drug_rationale": "No primary, normal-arm claim carries a measured or clinical finding.",
            "proposal_conflict": False,
        }
    for level in ("human", "mouse", "rat", "other_animal"):
        tier = decisive[decisive["proposed_species"] == level]
        if tier.empty:
            continue
        verdicts = set(tier["proposed_verdict"])
        ids = ", ".join(tier["claim_id"])
        if len(verdicts) == 1:
            v = verdicts.pop()
            return {
                "proposed_drug_verdict": v,
                "proposed_decisive_claim_ids": ids,
                "proposed_drug_rationale": f"{len(tier)} primary {level} claim(s), all {v}.",
                "proposal_conflict": False,
            }
        return {
            "proposed_drug_verdict": "",
            "proposed_decisive_claim_ids": ids,
            "proposed_drug_rationale": (
                f"Primary {level} claims disagree ("
                + ", ".join(sorted(verdicts))
                + "); left for the reviewer rather than resolved by majority."
            ),
            "proposal_conflict": True,
        }
    return {
        "proposed_drug_verdict": "unknown",
        "proposed_decisive_claim_ids": "",
        "proposed_drug_rationale": "Decisive claims carry no usable species.",
        "proposal_conflict": False,
    }


def main(host=None) -> None:
    """Run the adjudication pass.

    `host` is the kernel SDK object that provides `llm` and `reasoning_model`. It
    only exists inside the analysis kernel, so this stage is invoked as
    `import phase6_cns_adjudicate as m; m.main(host)` rather than from a shell.
    """
    if host is None:  # pragma: no cover - resolved from the kernel namespace
        import builtins
        import __main__

        host = getattr(__main__, "host", None) or getattr(builtins, "host", None)
    if host is None or not hasattr(host, "llm"):
        raise SystemExit(
            "This stage needs the kernel SDK: run it in the python kernel as "
            "`import phase6_cns_adjudicate as m; m.main(host)`."
        )

    sheet = pd.read_csv(DATA / "phase6-cns-adjudication-sheet.csv")
    packets = json.loads((DATA / "phase6-cns-claim-context.json").read_text())
    syn_path = DATA / "phase6-drug-synonyms.json"
    syn = json.loads(syn_path.read_text())["drugs"] if syn_path.exists() else {}

    reqs, order = [], []
    for cid in sheet["claim_id"]:
        p = packets[cid]
        reqs.append(
            {
                "prompt": build_prompt(p, syn.get(p["moiety"], {}).get("synonyms")),
                "tools": [TOOL],
                "tool_choice": {"type": "tool", "name": "adjudicate_claim"},
                "max_tokens": 1200,
                "thinking": {"type": "disabled"},
                "model": host.reasoning_model(),
            }
        )
        order.append(cid)

    results = host.llm(reqs, max_concurrency=8)

    rows, errors = [], []
    for cid, r in zip(order, results):
        if "error" in r or not r.get("tool_use"):
            errors.append({"claim_id": cid, "error": r.get("error", "no tool_use returned")})
            rows.append({"claim_id": cid})
            continue
        out = {"claim_id": cid}
        out.update({f"proposed_{k}": v for k, v in r["tool_use"]["input"].items()})
        rows.append(out)

    prop = pd.DataFrame(rows)
    merged = sheet.merge(prop, on="claim_id", how="left")
    # Context provenance travels with the verdict: a reviewer must be able to see
    # what the proposal was allowed to read.
    for col in ("context_source", "context_section", "match_frac"):
        merged[col] = merged["claim_id"].map(lambda c: packets[c].get(col))
    merged["pub_types"] = merged["claim_id"].map(
        lambda c: "; ".join(packets[c].get("pub_types") or [])
    )
    # Guard, applied after the model rather than asked of it: a measured-PK
    # verdict with no numeric value in the recorded value field is exactly the
    # qualitative over-call that put trametinib on `demonstrated` in run 1.
    no_number = (
        merged["proposed_verdict"].isin(["demonstrated", "contradicted"])
        & merged["proposed_evidence_basis"].fillna("").str.startswith("measured_pk")
        & ~merged["proposed_value"].fillna("").astype(str).str.contains(r"\d")
    )
    merged.loc[no_number, "proposed_needs_human_check"] = True
    merged["flagged_measured_pk_without_a_number"] = no_number
    merged.to_csv(DATA / "phase6-cns-adjudication-proposed.csv", index=False)

    rollup = pd.read_csv(DATA / "phase6-cns-adjudication-rollup.csv")
    agg = []
    for _, r in rollup.iterrows():
        claims = merged[merged["moiety"] == r["moiety"]]
        agg.append(aggregate(claims) if len(claims) else {
            "proposed_drug_verdict": "unknown",
            "proposed_decisive_claim_ids": "",
            "proposed_drug_rationale": "No attributed claim; nothing to read.",
            "proposal_conflict": False,
        })
    for k in agg[0]:
        rollup[k] = [a[k] for a in agg]
    # Triage column: where the read disagrees with the calculated descriptor flag.
    rollup["disagrees_with_chembl_flag"] = [
        (v == "demonstrated" and "non_permeant" in str(f))
        or (v == "contradicted" and f == "predicted_permeant")
        for v, f in zip(rollup["proposed_drug_verdict"], rollup["chembl_calculated_flag"])
    ]
    rollup.to_csv(DATA / "phase6-cns-adjudication-rollup.csv", index=False)

    run = {
        "stage": "phase6_cns_adjudicate.py",
        "model": results[0].get("model") if results else None,
        "claims_submitted": len(order),
        "claims_returned": int(prop["claim_id"].notna().sum() - len(errors)),
        "errors": errors,
        "verdict_counts": merged["proposed_verdict"].value_counts(dropna=False).to_dict(),
        "basis_counts": merged["proposed_evidence_basis"].value_counts(dropna=False).to_dict(),
        "needs_human_check": int(merged["proposed_needs_human_check"].fillna(False).sum()),
        "drug_verdicts": rollup["proposed_drug_verdict"].value_counts(dropna=False).to_dict(),
        "conflicts": rollup.loc[rollup["proposal_conflict"] == True, "moiety"].tolist(),
        "note": (
            "Proposals only. Human verdict columns ship blank; the Phase 5 keyword "
            "direction label was not shown to the model."
        ),
    }
    (DATA / "phase6-cns-adjudication-model-run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(json.dumps(run, indent=2)[:2000])


if __name__ == "__main__":
    main()
