#!/usr/bin/env python3
"""Generate the Phase 4 write-up.

Follows the Phase 1b and Phase 3 report convention: every current-state
number in the prose is recomputed from the committed tables at build time,
counts that describe the process rather than the current tables live in
PROCESS_HISTORY with their source, and the build fails if the generated
text contains an em dash.

Run from the repo root, after the Phase 4 scripts:
  python phase-4/scripts/build_phase4_report.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

# Facts about how the phase was run that no committed table records.
PROCESS_HISTORY = {
    "run_date": "2026-11-04",
    "gtop_key": (
        "The Guide to Pharmacology REST API stopped being open: it now returns HTTP 401 "
        "without a registered API key, which is issued manually on request. The project "
        "plan described it as a live open query. Kara obtained a key rather than "
        "substituting a different selectivity source."
    ),
    "openfda_budget": (
        "The first openFDA pass ran anonymously and exhausted the request budget (1,000 per "
        "day per IP) partway through, so the FAERS layer returned nothing: an empty result "
        "that would have read as an absence of adverse events. The script was changed to "
        "record a failed request as a failure rather than collapse it into an empty result, "
        "and the whole pass was re-run the same day with an API key. All 252 requests "
        "returned, none failed, and the FAERS layer is populated. The label and approval "
        "counts are unchanged from the first pass, which confirms those two endpoints had "
        "completed before the budget ran out; 491 labels and 470 approval records over "
        "1,255 drugs in scope is genuine openFDA coverage, not a truncated fetch."
    ),
    "amass": (
        "The Amass Connector the plan suggested evaluating as a single replacement for "
        "ClinicalTrials.gov, openFDA and DrugBank does not exist in this deployment's "
        "connector catalogue, so the three sources were wired separately."
    ),
}

UNAVAILABLE = {
    "DrugBank Open Data": "go.drugbank.com is outside the sandbox allowlist and its download "
    "requires account registration. Approval status rests on Drugs@FDA alone.",
    "SIDER": "sideeffects.embl.de is outside the sandbox allowlist. There is no "
    "package-insert side-effect frequency data in this phase; FAERS is the only "
    "post-market safety source.",
    "ProbeMiner": "the optional selectivity cross-check in the plan; not attempted, since "
    "Open Targets chemical probes and Guide to Pharmacology affinities already cover the "
    "question at this depth.",
}


def read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def fmt(value) -> str:
    return f"{int(value):,}"


def build(root: Path) -> str:
    data = root / "phase-4/data"
    targets = pd.read_csv(data / "phase4-targets.csv")
    identifiers = pd.read_csv(data / "phase4-identifiers.csv")
    dossier = pd.read_csv(data / "phase4-target-dossier.csv")
    routes = pd.read_csv(data / "phase4-drug-route-flags.csv.gz")
    interactions = pd.read_csv(data / "phase4-drug-interactions.csv.gz")
    tract = pd.read_csv(data / "phase4-opentargets-tractability.csv")
    admet = pd.read_csv(data / "phase4-admet.csv.gz")
    trials = read(data / "phase4-nf-trials.csv")
    trial_drugs = read(data / "phase4-trial-drugs.csv")
    selectivity = read(data / "phase4-gtop-selectivity.csv")
    faers = read(data / "phase4-faers.csv")
    labels = read(data / "phase4-openfda-labels.csv")

    prov = {}
    for name in ("dgidb", "opentargets", "chembl", "openfda", "trials", "admet", "gtop"):
        path = data / f"phase4-{name}-provenance.json"
        if path.exists():
            prov[name] = json.loads(path.read_text())

    lines: list = []
    add = lines.append

    add("# Phase 4: drug interaction, selectivity and tractability layer")
    add("")
    add(f"Run {PROCESS_HISTORY['run_date']}.")
    add("")

    add("## Scope")
    add("")
    combos = targets[["disease", "manifestation"]].drop_duplicates()
    add(
        f"Phase 3b selected {len(combos)} disease and manifestation combinations. For those, "
        f"Phase 4 queries the union of the expression-derived and literature-derived candidate "
        f"lists: {fmt(targets['gene_symbol'].nunique())} distinct genes over "
        f"{fmt(len(targets))} target rows "
        f"({fmt((targets['evidence_source'] == 'expression').sum())} expression only, "
        f"{fmt((targets['evidence_source'] == 'literature').sum())} literature only, "
        f"{fmt((targets['evidence_source'] == 'both').sum())} both)."
    )
    add("")
    resolved = identifiers["match_type"].value_counts()
    add(
        f"Of those genes, {fmt(resolved.get('exact_symbol', 0))} resolved to a current HGNC "
        f"symbol directly and {fmt(resolved.get('alias_only', 0))} through a symbol rename. "
        f"{fmt(resolved.get('unresolved', 0))} are clone-based or LOC identifiers from array "
        "platform annotations that resolve to no gene, and "
        f"{fmt(resolved.get('not_a_gene_symbol', 0))} is a literature label naming a process "
        "rather than a gene product. Those rows are carried as not queryable, never as "
        "targets with no drug found."
    )
    add("")

    add("## Sources queried")
    add("")
    add("| Source | What it supplied | Coverage |")
    add("| --- | --- | --- |")
    if "dgidb" in prov:
        add(
            f"| DGIdb | drug-gene interaction claims from about 40 upstream databases | "
            f"{fmt(prov['dgidb']['genes_with_interaction'])} of "
            f"{fmt(prov['dgidb']['genes_queried'])} genes, "
            f"{fmt(prov['dgidb']['interaction_rows'])} claims |"
        )
    if "opentargets" in prov:
        add(
            f"| Open Targets | known drugs, tractability buckets, chemical probes | "
            f"{fmt(prov['opentargets']['targets_with_a_drug'])} of "
            f"{fmt(prov['opentargets']['targets_queried'])} targets with a drug, "
            f"{fmt(prov['opentargets']['tractability_rows'])} tractability assignments |"
        )
    if "chembl" in prov:
        add(
            f"| ChEMBL | drug records, max_phase, route booleans, mechanisms of action | "
            f"{fmt(prov['chembl']['molecules_returned'])} molecules, "
            f"{fmt(prov['chembl']['drugs_with_a_mechanism'])} with a mechanism, "
            f"{fmt(prov['chembl']['approved_drugs'])} approved |"
        )
    if "trials" in prov:
        add(
            f"| ClinicalTrials.gov | NF-relevant interventional trials and their drugs | "
            f"{fmt(prov['trials']['distinct_trials'])} trials, "
            f"{fmt(prov['trials']['distinct_interventions'])} drug interventions, "
            f"{fmt(prov['trials']['interventions_matching_a_phase4_drug'])} matching a "
            "candidate drug |"
        )
    if "openfda" in prov:
        add(
            f"| openFDA | labels with route of administration, Drugs@FDA approvals, FAERS | "
            f"{fmt(prov['openfda']['drugs_with_a_label'])} labels, "
            f"{fmt(prov['openfda']['drugs_with_a_drugsfda_record'])} approval records, "
            f"{fmt(prov['openfda']['drugs_with_faers_reports'])} drugs with FAERS reports, "
            f"over {fmt(prov['openfda']['drugs_in_scope'])} drugs in scope |"
        )
    if "gtop" in prov:
        add(
            f"| Guide to Pharmacology | curated affinities and ligand selectivity profiles | "
            f"{fmt(prov['gtop']['symbols_with_a_gtop_target'])} of "
            f"{fmt(prov['gtop']['symbols_queried'])} symbols matched a target, "
            f"{fmt(prov['gtop']['interaction_rows'])} interactions, "
            f"{fmt(prov['gtop'].get('ligands_profiled', 0))} ligands profiled |"
        )
    add("")

    if "openfda" in prov:
        if prov["openfda"].get("failed_requests"):
            add(
                f"openFDA coverage is partial: {fmt(prov['openfda']['failed_requests'])} "
                "requests failed and the drugs they covered are unassessed, not negative."
            )
        elif not prov["openfda"].get("api_key_used", False):
            add(
                "**The openFDA row is not complete coverage.** That pass ran without an API "
                "key, against a budget of 1,000 requests per day per IP, and the budget ran "
                "out during the run. The version of the script that recorded failures did "
                "not exist yet, so the exact shortfall is not known. The drugs it did not "
                "reach are unassessed: absent label, approval or adverse-event data for a "
                "drug in this build does not mean none exists. The re-run with a key is "
                "outstanding."
            )
        add("")

    add("## What the drug layer found")
    add("")
    with_drug = dossier.loc[dossier["n_drugs"] > 0, "gene_symbol"].nunique()
    total_targets = dossier["gene_symbol"].nunique()
    approved = dossier.loc[dossier["n_drugs_approved"] > 0, "gene_symbol"].nunique()
    undrugged_tractable = dossier.loc[
        (dossier["n_drugs"] == 0) & dossier["top_tractability_bucket"].notna(), "gene_symbol"
    ].nunique()
    no_call = dossier.loc[
        (dossier["n_drugs"] == 0) & dossier["top_tractability_bucket"].isna(), "gene_symbol"
    ].nunique()
    add(
        f"{fmt(with_drug)} of {fmt(total_targets)} candidate targets have at least one drug "
        f"interaction from some source, and {fmt(approved)} have at least one approved drug. "
        f"A further {fmt(undrugged_tractable)} have no drug but do carry an Open Targets "
        f"tractability call, which is the repurposing gap this phase exists to surface. "
        f"{fmt(no_call)} have neither."
    )
    add("")

    add("| Disease | Manifestation | Targets | With a drug | With an approved drug | "
        "Undrugged but tractable | Route-appropriate drugs |")
    add("| --- | --- | --- | --- | --- | --- | --- |")
    for (disease, manifestation), block in dossier.groupby(["disease", "manifestation"]):
        add(
            f"| {disease} | {manifestation} | {fmt(block['gene_symbol'].nunique())} | "
            f"{fmt(block.loc[block['n_drugs'] > 0, 'gene_symbol'].nunique())} | "
            f"{fmt(block.loc[block['n_drugs_approved'] > 0, 'gene_symbol'].nunique())} | "
            f"{fmt(block.loc[(block['n_drugs'] == 0) & block['top_tractability_bucket'].notna(), 'gene_symbol'].nunique())} | "
            f"{fmt(block['n_route_appropriate_drugs'].sum())} |"
        )
    add("")

    add("## Delivery route and CNS penetration")
    add("")
    flags = routes["route_flag"].value_counts()
    excluded = int(
        flags.get("excluded_topical_only", 0)
        + flags.get("excluded_not_bbb_penetrant", 0)
        + flags.get("excluded_biologic_cns", 0)
    )
    add(
        f"The filter was applied to {fmt(len(routes))} target-drug pairs. "
        f"{fmt(flags.get('route_unknown', 0))} carry no clinical route in ChEMBL and no "
        "openFDA label, which is the expected state for a preclinical screening hit and is "
        "recorded as unknown rather than inappropriate. Of the pairs where a route is known, "
        f"{fmt(excluded)} are flagged delivery-inappropriate and kept for audit: "
        f"{fmt(flags.get('excluded_topical_only', 0))} topical-only drugs against a "
        f"manifestation needing a systemic route, "
        f"{fmt(flags.get('excluded_not_bbb_penetrant', 0))} systemic drugs predicted not to "
        f"cross the blood-brain barrier against a CNS manifestation, and "
        f"{fmt(flags.get('excluded_biologic_cns', 0))} biologics against a CNS manifestation."
    )
    add("")
    cns_counts = admet["cns_penetration_flag"].value_counts()
    add(
        "The CNS flag is a prediction from ChEMBL's calculated molecular properties, not a "
        "permeability measurement: ChEMBL holds no experimental blood-brain-barrier data. "
        f"Across {fmt(len(admet))} drugs it reads "
        f"{fmt(cns_counts.get('predicted_permeant', 0))} predicted permeant, "
        f"{fmt(cns_counts.get('predicted_non_permeant', 0))} predicted non-permeant, "
        f"{fmt(cns_counts.get('not_applicable_biologic', 0))} biologics and "
        f"{fmt(cns_counts.get('unknown', 0))} with no calculated properties. The thresholds "
        "are stated in phase-4/scripts/phase4_admet.py and in "
        "phase-4/data/phase4-admet-provenance.json."
    )
    add("")
    add(
        "Optic pathway glioma is the only selected manifestation that triggers the CNS "
        "requirement. Cutaneous neurofibroma and ANNUBP / atypical neurofibroma are the only "
        "two where topical delivery is acceptable."
    )
    add("")

    if len(trials):
        add("## Clinical stage")
        add("")
        matched_interventions = (
            trial_drugs.loc[trial_drugs["matches_phase4_drug"], "intervention_key"].nunique()
            if len(trial_drugs)
            else 0
        )
        add(
            f"{fmt(trials['nct_id'].nunique())} interventional trials are recorded across the "
            f"selected manifestations and the three disease umbrellas, naming "
            f"{fmt(trial_drugs['intervention_key'].nunique()) if len(trial_drugs) else 0} "
            f"distinct drug interventions. {fmt(matched_interventions)} of those match a drug "
            "in the Phase 4 candidate set by name. A candidate drug with a high ChEMBL "
            "max_phase but no NF trial is a repurposing hypothesis; one with an NF trial is an "
            "existing clinical fact about this disease, and the dossier keeps the two apart."
        )
        add("")
        per_manifestation = (
            trials[trials["manifestation"] != ""]
            .groupby("manifestation")["nct_id"]
            .nunique()
            .sort_values(ascending=False)
        )
        add("| Manifestation | Interventional trials |")
        add("| --- | --- |")
        for manifestation, count in per_manifestation.items():
            add(f"| {manifestation} | {fmt(count)} |")
        add("")

    add("## Selectivity")
    add("")
    if len(selectivity):
        profiled = selectivity[selectivity.get("selectivity_profiled") == True]  # noqa: E712
        add(
            f"{fmt(selectivity['gene_symbol'].nunique())} candidate targets carry at least one "
            f"curated Guide to Pharmacology ligand interaction, over "
            f"{fmt(selectivity['ligand_id'].nunique())} distinct ligands. For "
            f"{fmt(profiled['ligand_id'].nunique()) if len(profiled) else 0} of those ligands "
            "the whole human target profile was retrieved from the ligand side, so the "
            "breadth count means every target the database records for that ligand, not only "
            "the ones on this project's list."
        )
        if len(profiled):
            selective = profiled[profiled["n_targets_within_window"] <= 1]
            add("")
            add(
                f"{fmt(selective['ligand_id'].nunique())} profiled ligands hit only one target "
                "within one log unit of their best recorded affinity."
            )
    else:
        add(
            "Not assessed. The Guide to Pharmacology selectivity table is absent from this "
            "build, so every selectivity field in the dossier reads not assessed rather than "
            "none found."
        )
    add("")

    add("## Safety")
    add("")
    boxed = int((routes.get("has_boxed_warning") == True).sum()) if "has_boxed_warning" in routes else 0  # noqa: E712
    withdrawn = int((routes.get("withdrawn_flag") == True).sum()) if "withdrawn_flag" in routes else 0  # noqa: E712
    add(
        f"Safety signals attach to the drug, not the target. Across the flagged target-drug "
        f"pairs, {fmt(boxed)} involve a drug whose openFDA label carries a boxed warning and "
        f"{fmt(withdrawn)} involve a drug ChEMBL records as withdrawn from a market."
    )
    if len(faers) and "drug_key" in faers.columns:
        add("")
        add(
            f"FAERS report counts were retrieved for {fmt(faers['drug_key'].nunique())} drugs. "
            "A report count is a count of reports mentioning the drug. It has no denominator, "
            "and it rises with how widely and how long a drug has been used, so it is a signal "
            "for Phase 6 to weight rather than a safety verdict."
        )
    else:
        add("")
        add(
            "FAERS returned no usable counts in this build, so post-market adverse event data "
            "is not assessed."
        )
    add("")

    add("## Sources named in the plan that are not in this phase")
    add("")
    for source, reason in UNAVAILABLE.items():
        add(f"- **{source}**: {reason}")
    add("")
    add(f"- **Amass Connector**: {PROCESS_HISTORY['amass']}")
    add("")
    add("Two integration surprises worth recording, both resolved with a key obtained mid-run:")
    add("")
    add(f"- {PROCESS_HISTORY['gtop_key']}")
    add(f"- {PROCESS_HISTORY['openfda_budget']}")
    add("")
    add(
        "A third is a schema drift rather than an access problem: Open Targets no longer "
        "exposes Target.knownDrugs. The field is Target.drugAndClinicalCandidates, and "
        "Drug.isApproved, Drug.maximumClinicalTrialPhase and Drug.hasBeenWithdrawn are gone, "
        "replaced by Drug.maximumClinicalStage. Code written from older documentation fails "
        "against the current API."
    )
    add("")

    add("## Outputs")
    add("")
    add("| File | Contents |")
    add("| --- | --- |")
    add("| phase4-targets.csv | the Phase 4 input list, one row per gene, disease and manifestation |")
    add("| phase4-identifiers.csv | symbol to UniProt and Ensembl, with unresolved symbols kept |")
    add("| phase4-symbol-corrections.csv | the two platform-annotation corruptions and the one non-gene label |")
    add("| phase4-drug-interactions.csv.gz | one row per target and drug, with the source of each claim |")
    add("| phase4-opentargets-tractability.csv | tractability buckets per target and modality |")
    add("| phase4-chembl-drugs.csv.gz | drug records including max_phase and route booleans |")
    add("| phase4-chembl-mechanisms.csv.gz | mechanism of action per drug |")
    add("| phase4-nf-trials.csv, phase4-trial-drugs.csv | NF interventional trials and their drugs |")
    add("| phase4-openfda-labels.csv, phase4-openfda-approvals.csv, phase4-faers.csv | route, approval and adverse event data |")
    add("| phase4-admet.csv.gz | calculated properties and the CNS penetration flag |")
    add("| phase4-gtop-interactions.csv.gz, phase4-gtop-selectivity.csv | curated affinities and ligand breadth |")
    add("| phase4-drug-route-flags.csv.gz | the delivery-route verdict per target, manifestation and drug |")
    add("| phase4-target-dossier.csv | the consolidated per-target deliverable |")
    add("")

    add("## Reproducing this")
    add("")
    add("```")
    add("python phase-4/scripts/phase4_targets.py")
    add("python phase-4/scripts/phase4_identifiers.py")
    add("python phase-4/scripts/phase4_dgidb.py")
    add("python phase-4/scripts/phase4_opentargets.py")
    add("python phase-4/scripts/phase4_chembl.py")
    add("python phase-4/scripts/phase4_clinicaltrials.py")
    add("OPENFDA_API_KEY=... python phase-4/scripts/phase4_openfda.py")
    add("python phase-4/scripts/phase4_admet.py")
    add("GTPAPIKEY=... python phase-4/scripts/phase4_guidetopharmacology.py")
    add("python phase-4/scripts/phase4_dossier.py")
    add("python phase-4/scripts/phase4_figure.py")
    add("python phase-4/scripts/build_phase4_report.py")
    add("```")
    add("")
    add(
        "Only phase4_identifiers.py runs offline; it reads the committed mygene cache. The "
        "rest touch the network. Two need a key, read from the environment and never written "
        "to any output."
    )
    add("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()

    text = build(root)
    if "\u2014" in text or "\u2013" in text:
        raise SystemExit("generated text contains an em or en dash; rewrite the sentence")

    out = root / "phase-4/docs/phase4-drug-tractability.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out} ({len(text.splitlines())} lines)")


if __name__ == "__main__":
    main()
