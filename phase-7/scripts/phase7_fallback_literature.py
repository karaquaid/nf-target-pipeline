#!/usr/bin/env python3
"""Phase 7 literature fallback for the three strata left with no expression evidence.

Why this script exists
----------------------
`phase-7/data/phase7-fallback-scope.csv` lists 18 unusable-dataset x stratum pairs.
Only three of them leave a stratum with *no* expression candidate at all (verified
against `phase-3/data/phase3-candidate-targets.csv`, which has 0 rows in each):

    NF2-SWN / Meningioma        lost GSE232528 (14 NF2-patient meningiomas, single arm)
    NF1     / Non-optic LGG     lost GSE5675   (pilocytic astrocytoma; 0 samples in scope)
    NF1     / Other             lost GSE2841   (pheochromocytoma panel; 2 samples in scope)

For those three only, this script runs a PubMed query bank through the PubMed MCP
connector, screens abstracts for proposed molecular targets, retrieves full text
where PMC has it, verifies each claim against the complete article body, and writes
a candidate table that is column-compatible with Phase 1b.

Standards this script is bound by
---------------------------------
* Disease labels are exactly NF1 / NF2-SWN / SWN; manifestation labels are taken
  verbatim from the project's fixed vocabulary. Both are fixed per stratum here,
  never invented by the extraction step.
* `evidence_tier` uses Phase 1b's three values exactly: `full text - supported`,
  `full text - partial`, `abstract only`.
* A claim verified against the article body outranks one taken from an abstract,
  and the difference is recorded per paper in `paper_access`, never blurred.
* Absence of evidence is never reported as negative evidence. Where a query or a
  stratum returned nothing, the tables say the search FOUND nothing.
* Every candidate row carries at least one PMID that this script actually read back
  from a live connector response.

How to run it
-------------
The PubMed MCP connector and `host.llm` both live on the `repl` kernel's `host`
object, so the search, retrieval and model stages run there. That kernel cannot read
this repository (it is outside its sandbox), so copy this file and the work
directory into the shared workspace first and run the copy:

    import runpy, sys                                  # in the `repl` kernel
    WS = "<shared workspace path>"
    sys.argv = ["phase7_fallback_literature.py", "search", "--workdir", WS + "/phase7work"]
    runpy.run_path(WS + "/phase7_fallback_literature.py",
                   init_globals={"HOST": host}, run_name="__main__")

`aggregate` needs no network and no model, but it does need the repository (it reads
`phase-1b/data/phase1b-candidate-targets.csv` and the curation file), so run it from
the repo root with `--workdir` pointing at the same cache:

    python phase-7/scripts/phase7_fallback_literature.py aggregate --workdir <ws>/phase7work

Stages, in order (each caches to `--workdir`, default `phase-7/work/`, so a stage can
be re-run without repeating the one before it):

    search      PubMed connector search_articles over the query bank
    metadata    get_article_metadata -> titles + abstracts
    screen      host.llm abstract-level target extraction (Phase 1b rubric)
    fulltext    convert_article_ids for PMCIDs, then lib/europepmc_client for JATS bodies
    verify      host.llm whole-body verification, one reasoning pass per paper
    aggregate   writes the two deliverable CSVs

`aggregate` needs no network and no model; it is pure file I/O over the caches.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from collections import defaultdict

PUBMED_SERVER = "directory-f5d400df-ea7e-41b4-8fa7-34cfba605551"  # "PubMed" MCP connector

# A PMC record can exist while carrying only a title/front-matter stub. Anything
# shorter than this is not an article body and must not be tiered as full text.
MIN_BODY_CHARS = 3000

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DATA = os.path.join(REPO, "phase-7", "data")
PHASE1B = os.path.join(REPO, "phase-1b", "data", "phase1b-candidate-targets.csv")

# ---------------------------------------------------------------------------
# Fixed configuration. Per the literature-target-map protocol, the vocabulary and
# the query bank are frozen before the run and are only ever added to, never edited.
# ---------------------------------------------------------------------------

SEARCH_PARAMS = dict(max_results=25, sort="relevance", date_from="2005")

# Germline NF disease genes: excluded as candidates project-wide (Phase 1b scope
# decision 2). They are not re-prioritised here either.
DRIVER_GENES = {"NF1", "NF2", "SMARCB1", "LZTR1", "SPRED1"}

STRATA = {
    "NF2-SWN|Meningioma": {
        "disease": "NF2-SWN",
        "manifestation": "Meningioma",
        "dataset_lost": "GSE232528",
        "scope_note": (
            "NF2-associated (germline NF2 / merlin-deficient) meningioma. GSE232528 "
            "profiled 14 NF2-patient meningiomas as a single arm, so no within-dataset "
            "contrast could be formed."
        ),
    },
    "NF1|Non-optic LGG": {
        "disease": "NF1",
        "manifestation": "Non-optic LGG",
        "dataset_lost": "GSE5675",
        "scope_note": (
            "NF1-associated low-grade glioma outside the optic pathway. GSE5675 is a "
            "pilocytic astrocytoma series removed at the Phase 2 pre-flight review "
            "(0 samples attributable to NF1 patients in scope)."
        ),
    },
    "NF1|Other": {
        "disease": "NF1",
        "manifestation": "Other",
        "dataset_lost": "GSE2841",
        "scope_note": (
            "'Other' is a catch-all label, not a disease entity, so the query bank is "
            "defined by (a) what the lost dataset would have served and (b) what the 11 "
            "Phase 1b targets already filed here are actually about. GSE2841 is a "
            "pheochromocytoma panel of mixed genetic origin (2 NF1 samples in scope). "
            "The held targets cluster on NF1 vasculopathy / moyamoya (MRVI1, RNF213) and "
            "NF1 endothelial biology (AKT1, VEGFA); the remainder (RAS (pan), HRAS, KRAS, "
            "MAPK pathway, RAS/MAPK pathway, SOS2, IDH1) are whole-disease review claims "
            "or a single case report with no phenotype to attach to. The fallback is "
            "therefore scoped to the two real phenotypes that 'Other' is standing in for - "
            "NF1-associated pheochromocytoma and NF1 vasculopathy - and NOT to the "
            "whole-disease RAS/MAPK review claims, for which no expression contrast could "
            "stand in anyway."
        ),
    },
}

# (stratum_key, query_id, PubMed query, what the query is for)
QUERY_BANK = [
    # --- NF2-SWN Meningioma: the substantive case -------------------------------
    ("NF2-SWN|Meningioma", "mng_target",
     "(neurofibromatosis type 2[Title/Abstract] OR NF2[Title/Abstract]) AND meningioma[Title/Abstract] "
     "AND (therapeutic target[Title/Abstract] OR drug target[Title/Abstract] OR targeted therapy[Title/Abstract])",
     "Direct target claims in NF2-associated meningioma."),
    ("NF2-SWN|Meningioma", "mng_merlin_signal",
     "(merlin[Title/Abstract] OR NF2[Title/Abstract]) AND meningioma[Title/Abstract] "
     "AND (inhibitor[Title/Abstract] OR signaling[Title/Abstract] OR signalling[Title/Abstract])",
     "Merlin-loss signalling nodes and the agents that hit them."),
    ("NF2-SWN|Meningioma", "mng_hippo",
     "meningioma[Title/Abstract] AND (NF2[Title/Abstract] OR merlin[Title/Abstract]) "
     "AND (Hippo[Title/Abstract] OR YAP[Title/Abstract] OR TEAD[Title/Abstract])",
     "The Hippo axis, the dominant merlin-loss node in Phase 1b's NF2 rows."),
    ("NF2-SWN|Meningioma", "mng_tme",
     "meningioma[Title/Abstract] AND (NF2[Title/Abstract] OR merlin[Title/Abstract]) "
     "AND (tumor microenvironment[Title/Abstract] OR macrophage[Title/Abstract] OR immune[Title/Abstract])",
     "Mirrors the lost dataset's own topic: GSE232528 reports an immunogenic, "
     "macrophage-infiltrated subtype enriched in NF2-patient meningioma."),
    ("NF2-SWN|Meningioma", "mng_trial",
     "meningioma[Title/Abstract] AND neurofibromatosis[Title/Abstract] "
     "AND (clinical trial[Title/Abstract] OR phase II[Title/Abstract] OR treatment[Title/Abstract])",
     "Clinically tested agents, which carry a named target."),
    ("NF2-SWN|Meningioma", "mng_expression",
     "meningioma[Title/Abstract] AND (NF2[Title/Abstract] OR merlin[Title/Abstract]) "
     "AND (transcriptomic[Title/Abstract] OR expression profiling[Title/Abstract] OR RNA sequencing[Title/Abstract])",
     "Expression-profiling papers: the closest literature analogue to the lost contrast."),
    # --- NF1 Non-optic LGG ------------------------------------------------------
    ("NF1|Non-optic LGG", "lgg_target",
     "(neurofibromatosis type 1[Title/Abstract] OR NF1[Title/Abstract]) "
     "AND (low-grade glioma[Title/Abstract] OR low grade glioma[Title/Abstract]) "
     "AND (therapeutic target[Title/Abstract] OR targeted therapy[Title/Abstract] OR inhibitor[Title/Abstract])",
     "Direct target claims in NF1 low-grade glioma."),
    ("NF1|Non-optic LGG", "lgg_pilocytic",
     "(neurofibromatosis type 1[Title/Abstract] OR NF1[Title/Abstract]) AND pilocytic astrocytoma[Title/Abstract] "
     "AND (target[Title/Abstract] OR pathogenesis[Title/Abstract] OR expression[Title/Abstract])",
     "The lost dataset's own tumour type (GSE5675 is a pilocytic astrocytoma series)."),
    ("NF1|Non-optic LGG", "lgg_nonoptic_sites",
     "(neurofibromatosis type 1[Title/Abstract] OR NF1[Title/Abstract]) "
     "AND (brainstem glioma[Title/Abstract] OR cerebellar astrocytoma[Title/Abstract] "
     "OR non-optic glioma[Title/Abstract] OR extra-optic[Title/Abstract])",
     "Anatomically non-optic NF1 glioma, to keep the stratum distinct from OPG."),
    ("NF1|Non-optic LGG", "lgg_mek_mtor",
     "(neurofibromatosis type 1[Title/Abstract] OR NF1[Title/Abstract]) "
     "AND (pediatric low-grade glioma[Title/Abstract] OR paediatric low-grade glioma[Title/Abstract]) "
     "AND (MEK inhibitor[Title/Abstract] OR mTOR[Title/Abstract] OR trametinib[Title/Abstract] "
     "OR selumetinib[Title/Abstract] OR everolimus[Title/Abstract])",
     "The trial literature behind the four targets Phase 1b already holds here."),
    # --- NF1 Other (scoped: see STRATA['NF1|Other']['scope_note']) ---------------
    ("NF1|Other", "oth_pheo",
     "(neurofibromatosis type 1[Title/Abstract] OR NF1[Title/Abstract]) "
     "AND (pheochromocytoma[Title/Abstract] OR phaeochromocytoma[Title/Abstract] OR paraganglioma[Title/Abstract]) "
     "AND (therapeutic target[Title/Abstract] OR pathogenesis[Title/Abstract] OR expression[Title/Abstract])",
     "NF1-associated pheochromocytoma: the phenotype the lost dataset (GSE2841) would have served."),
    ("NF1|Other", "oth_pheo_expression",
     "(neurofibromatosis type 1[Title/Abstract] OR NF1[Title/Abstract]) "
     "AND (pheochromocytoma[Title/Abstract] OR paraganglioma[Title/Abstract]) "
     "AND (gene expression profiling[Title/Abstract] OR transcriptome[Title/Abstract] OR cluster[Title/Abstract])",
     "Expression-profiling papers on the same tumour type as the lost contrast."),
    ("NF1|Other", "oth_vasculopathy",
     "(neurofibromatosis type 1[Title/Abstract] OR NF1[Title/Abstract]) "
     "AND (vasculopathy[Title/Abstract] OR moyamoya[Title/Abstract] OR arterial stenosis[Title/Abstract] "
     "OR vascular lesion[Title/Abstract])",
     "NF1 vasculopathy / moyamoya, the axis MRVI1 and RNF213 sit on in Phase 1b."),
    ("NF1|Other", "oth_endothelial",
     "(neurofibromatosis type 1[Title/Abstract] OR NF1[Title/Abstract]) "
     "AND (endothelial[Title/Abstract] OR angiogenesis[Title/Abstract] OR neovascularization[Title/Abstract]) "
     "AND (target[Title/Abstract] OR inhibitor[Title/Abstract] OR signaling[Title/Abstract])",
     "NF1 endothelial biology, the axis AKT1 and VEGFA sit on in Phase 1b."),
]

# ---------------------------------------------------------------------------
# Model prompts. Both mirror the Phase 1b rubric.
# ---------------------------------------------------------------------------

SCREEN_SYSTEM = """You extract proposed molecular targets from biomedical abstracts for a
neurofibromatosis drug-target map. You are strict and you never invent.

Rules:
1. Extract an entity ONLY if the abstract presents it as a driver, modifier, resistance
   mechanism or therapeutic target in the disease and manifestation named in the prompt.
2. Do NOT extract: the germline disease gene where it merely defines the cohort
   (NF1, NF2, SMARCB1, LZTR1, SPRED1); cell-type or lineage markers used to identify
   cells; assay reagents; genes named only as background citation to other people's work.
3. If the abstract is not about the disease AND manifestation named in the prompt,
   return an empty list. Sporadic tumours with no germline NF attribution are out of scope.
4. Keep a family, pathway or complex as the label it is written as, set label_type
   accordingly, and list its constituent human gene symbols separately.
5. mechanism must be one sentence stating what the abstract itself says, not what you know.
6. Returning an empty list is a correct and common answer."""

VERIFY_SYSTEM = """You verify a target claim against the COMPLETE body of the article it is
drawn from, for a neurofibromatosis drug-target map.

You are given the whole article text. Judge only what THIS article shows.

Verdicts:
- supported: the article's own data or its own clinical result supports this entity as a
  driver, modifier, resistance mechanism or therapeutic target in the stated disease AND
  the stated manifestation. A review article may be 'supported' only if it states the claim
  for this disease and manifestation as a conclusion of the review.
- partial: the entity is real in this article but the disease or the manifestation
  attribution is looser than the claim states (for example the article shows it in a
  different NF manifestation, or in sporadic disease with the NF case only in discussion).
- not_supported: the article does not support the claim, or supports it only by citing
  other people's work.

Rules: a result the article cites from another paper is NOT this article's support.
Do not use knowledge from outside the article. Be willing to return not_supported."""

SCREEN_TOOL = {
    "name": "extract_targets",
    "description": "Return the molecular targets this abstract proposes for the given stratum.",
    "input_schema": {
        "type": "object",
        "properties": {
            "in_scope": {
                "type": "boolean",
                "description": "True if the abstract is about the named disease and manifestation.",
            },
            "out_of_scope_reason": {"type": "string"},
            "targets": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "gene_target": {"type": "string", "description": "Label as written, e.g. EGFR, PI3K (family), Hippo pathway."},
                        "label_type": {"type": "string", "enum": ["gene", "family", "pathway", "complex", "drug", "other"]},
                        "constituent_genes": {"type": "array", "items": {"type": "string"}},
                        "role": {"type": "string", "enum": ["driver", "modifier", "therapeutic_target", "resistance", "biomarker"]},
                        "mechanism": {"type": "string"},
                        "study_system": {"type": "string", "description": "e.g. human tissue, cell line, mouse model, clinical trial, review"},
                    },
                    "required": ["gene_target", "label_type", "role", "mechanism", "study_system"],
                },
            },
        },
        "required": ["in_scope", "targets"],
    },
}

VERIFY_TOOL = {
    "name": "verify_claims",
    "description": "Judge each claim against the complete article body.",
    "input_schema": {
        "type": "object",
        "properties": {
            "verdicts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "gene_target": {"type": "string"},
                        "verdict": {"type": "string", "enum": ["supported", "partial", "not_supported"]},
                        "mechanism_from_body": {"type": "string"},
                        "study_system": {"type": "string"},
                        "evidence_sentence": {"type": "string", "description": "The article's own sentence that decides the verdict."},
                    },
                    "required": ["gene_target", "verdict", "mechanism_from_body", "study_system"],
                },
            }
        },
        "required": ["verdicts"],
    },
}

# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _load(path, default=None):
    if os.path.exists(path):
        with open(path) as fh:
            return json.load(fh)
    return default


def _dump(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True)
    os.replace(tmp, path)
    return path


def _mcp(host, method, **kw):
    return host.mcp(PUBMED_SERVER, method, **kw)


def _norm_label(s):
    return re.sub(r"\s+", " ", (s or "").strip())


def _key(s):
    """Loose key for comparing target labels across tables."""
    s = _norm_label(s).upper()
    s = re.sub(r"[\s\-_/().,]+", "", s)
    return s


# ---------------------------------------------------------------------------
# Stages
# ---------------------------------------------------------------------------


def stage_search(host, work):
    out = []
    for stratum, qid, query, rationale in QUERY_BANK:
        r = _mcp(host, "search_articles", query=query, **SEARCH_PARAMS)
        out.append({
            "stratum": stratum,
            "disease": STRATA[stratum]["disease"],
            "manifestation": STRATA[stratum]["manifestation"],
            "query_id": qid,
            "query": query,
            "rationale": rationale,
            "max_results": SEARCH_PARAMS["max_results"],
            "date_from": SEARCH_PARAMS["date_from"],
            "sort": SEARCH_PARAMS["sort"],
            "n_hits_total": r.get("total_count"),
            "n_returned": r.get("returned_count", len(r.get("pmids", []))),
            "pmids": r.get("pmids", []),
            "query_translation": r.get("query_translation", ""),
        })
        print(f"  {qid:22s} total={r.get('total_count'):>6}  returned={len(r.get('pmids', []))}")
    return _dump(out, os.path.join(work, "search.json"))


def stage_metadata(host, work):
    searches = _load(os.path.join(work, "search.json"), [])
    pmids = sorted({p for s in searches for p in s["pmids"]})
    print(f"  {len(pmids)} unique PMIDs across {len(searches)} queries")
    meta = {}
    # The connector silently truncates get_article_metadata to 20 records per call:
    # asking for 40 returns the first 20 with no error and count=20. Chunk at 20.
    for i in range(0, len(pmids), 20):
        chunk = pmids[i:i + 20]
        r = _mcp(host, "get_article_metadata", pmids=chunk)
        for a in r.get("articles", []):
            pmid = str(a.get("identifiers", {}).get("pmid") or "")
            if pmid:
                meta[pmid] = {
                    "pmid": pmid,
                    "doi": a.get("identifiers", {}).get("doi", ""),
                    "pmcid": a.get("identifiers", {}).get("pmc", "") or "",
                    "title": a.get("title", ""),
                    "abstract": a.get("abstract", "") or "",
                    "journal": a.get("journal", ""),
                    "date": a.get("publication_date", ""),
                }
        time.sleep(0.2)
    print(f"  metadata retrieved for {len(meta)} / {len(pmids)}")
    return _dump(meta, os.path.join(work, "metadata.json"))


def stage_screen(host, work):
    searches = _load(os.path.join(work, "search.json"), [])
    meta = _load(os.path.join(work, "metadata.json"), {})
    # one screening call per (stratum, pmid): the same paper can be screened for
    # two strata and must be judged separately against each.
    pairs = []
    seen = set()
    for s in searches:
        for p in s["pmids"]:
            if (s["stratum"], p) in seen or p not in meta:
                continue
            seen.add((s["stratum"], p))
            pairs.append((s["stratum"], p))
    reqs = []
    for stratum, pmid in pairs:
        st = STRATA[stratum]
        m = meta[pmid]
        reqs.append({
            "prompt": (
                f"Disease: {st['disease']}\nManifestation: {st['manifestation']}\n"
                f"Scope of this stratum: {st['scope_note']}\n\n"
                f"PMID {pmid}\nTitle: {m['title']}\nJournal: {m['journal']} {m['date']}\n\n"
                f"Abstract:\n{m['abstract'] or '(no abstract available)'}"
            ),
            "system": SCREEN_SYSTEM,
            "tools": [SCREEN_TOOL],
            "tool_choice": {"type": "tool", "name": "extract_targets"},
            "max_tokens": 2000,
            "model": host.reasoning_model(),
        })
    print(f"  screening {len(reqs)} (stratum, paper) pairs")
    results = host.llm(reqs, max_concurrency=12)
    claims = []
    n_err = 0
    for (stratum, pmid), res in zip(pairs, results):
        if "error" in res or not res.get("tool_use"):
            n_err += 1
            continue
        inp = res["tool_use"]["input"]
        if not inp.get("in_scope"):
            continue
        for t in inp.get("targets", []):
            label = _norm_label(t.get("gene_target"))
            if not label or _key(label) in {_key(g) for g in DRIVER_GENES}:
                continue
            claims.append({
                "stratum": stratum,
                "pmid": pmid,
                "gene_target": label,
                "label_type": t.get("label_type", "gene"),
                "constituent_genes": t.get("constituent_genes", []),
                "role": t.get("role", ""),
                "mechanism_abstract": t.get("mechanism", ""),
                "study_system": t.get("study_system", ""),
            })
    print(f"  {len(claims)} abstract-level claims; {n_err} screening calls failed")
    return _dump(claims, os.path.join(work, "claims.json"))


def stage_fulltext(host, work):
    """Retrieve article bodies through the shared Europe PMC / NCBI JATS client.

    Changed 2026-11-19 to satisfy the retrieval ruling of 2026-11-17. This stage
    used the PubMed connector's `get_full_text_article`, whose PMC extraction drops
    italic markup; journals italicise gene symbols, so a symbol could vanish from
    the body a verdict was then formed against. `lib/europepmc_client` renders JATS
    and checks its own output: `symbol_check` lists any inline-markup string that
    failed to survive, and an empty list is the guarantee the connector could not
    give.

    The connector is still used, but only for what it is reliable at: resolving a
    PMID to a PMCID where Europe PMC has no record of one.

    Note on the committed table. `phase7-fallback-candidates.csv` was produced
    before this change, under the connector route, and stands as produced; the
    stability measurement puts the binary supported-or-not call at 3.9%. Re-running
    it is a separate decision.
    """
    sys.path.insert(0, os.path.join(REPO, "lib"))
    import europepmc_client as epmc

    claims = _load(os.path.join(work, "claims.json"), [])
    meta = _load(os.path.join(work, "metadata.json"), {})
    pmids = sorted({c["pmid"] for c in claims})
    # PMCID from the metadata record first, the connector's converter for the rest.
    pmcid = {p: meta[p]["pmcid"] for p in pmids if meta.get(p, {}).get("pmcid")}
    missing = [p for p in pmids if p not in pmcid]
    for i in range(0, len(missing), 50):
        r = _mcp(host, "convert_article_ids", ids=missing[i:i + 50], id_type="pmid")
        for rec in r.get("records", []):
            if rec.get("pmcid"):
                pmcid[str(rec["pmid"])] = rec["pmcid"]
    print(f"  {len(pmids)} papers carrying a claim; {len(pmcid)} have a PMCID")

    bodies = _load(os.path.join(work, "fulltext.json"), {})
    failures = _load(os.path.join(work, "fulltext-failures.json"), {})
    todo = [p for p in pmids if p not in bodies]
    routes: dict[str, int] = {}
    for n_done, p in enumerate(todo, 1):
        try:
            got = epmc.get_fulltext(pmid=p, pmcid=pmcid.get(p))
        except Exception as exc:
            # A retrieval failure is recorded, never dropped: a paper whose body
            # could not be fetched must stay distinguishable from one that has none.
            failures[p] = f"{exc.__class__.__name__}: {exc}"[:200]
            print(f"  ! PMID {p}: {failures[p]}")
            continue
        if got["error"]:
            failures[p] = got["error"]
            continue
        body = got["text"]
        n = len(body)
        if n < MIN_BODY_CHARS:
            failures[p] = f"{n}-char stub, not an article body"
            print(f"  PMC record for PMID {p} is a {n}-char stub, not a body; "
                  "treated as not retrieved")
            continue
        if got["symbol_check"]:
            # The client's own guarantee failed. That is a defect in the renderer,
            # not a property of the paper, so it stops the run rather than feeding
            # a damaged body to the reader.
            raise RuntimeError(
                f"PMID {p}: {len(got['symbol_check'])} inline string(s) dropped by the "
                f"JATS renderer, e.g. {got['symbol_check'][:5]}. Do not verify against "
                "this body."
            )
        routes[got["route"]] = routes.get(got["route"], 0) + 1
        bodies[p] = {"pmcid": got["pmcid"], "n_chars": n, "body": body,
                     "route": got["route"], "retrieval": "europepmc_client"}
        if n_done % 10 == 0:
            _dump(bodies, os.path.join(work, "fulltext.json"))
        time.sleep(0.3)
    _dump(bodies, os.path.join(work, "fulltext.json"))
    _dump(failures, os.path.join(work, "fulltext-failures.json"))
    by_route = ", ".join(f"{k} {v}" for k, v in sorted(routes.items())) or "none"
    print(f"  full text retrieved for {len(bodies)} / {len(pmids)} papers "
          f"(by route: {by_route}); {len(failures)} recorded as not retrieved")
    return os.path.join(work, "fulltext.json")


def stage_verify(host, work):
    claims = _load(os.path.join(work, "claims.json"), [])
    bodies = _load(os.path.join(work, "fulltext.json"), {})
    meta = _load(os.path.join(work, "metadata.json"), {})
    # One reasoning pass per (paper, stratum) over the COMPLETE body, judging all of
    # that paper's claims at once. No excerpting: rule 2 of the protocol.
    groups = defaultdict(list)
    for c in claims:
        if c["pmid"] in bodies:
            groups[(c["pmid"], c["stratum"])].append(c)
    keys = sorted(groups)
    reqs = []
    for pmid, stratum in keys:
        st = STRATA[stratum]
        cs = groups[(pmid, stratum)]
        claim_list = "\n".join(f"- {c['gene_target']}: {c['mechanism_abstract']}" for c in cs)
        body = bodies[pmid]["body"]
        reqs.append({
            "prompt": (
                f"Disease: {st['disease']}\nManifestation: {st['manifestation']}\n\n"
                f"Claims drawn from the abstract of PMID {pmid} "
                f"({meta.get(pmid, {}).get('title', '')}):\n{claim_list}\n\n"
                f"=== COMPLETE ARTICLE TEXT ===\n{body}\n=== END ARTICLE ===\n\n"
                "Judge every claim above against this article body."
            ),
            "system": VERIFY_SYSTEM,
            "tools": [VERIFY_TOOL],
            "tool_choice": {"type": "tool", "name": "verify_claims"},
            "max_tokens": 4000,
            "model": host.reasoning_model(),
        })
    print(f"  verifying {sum(len(groups[k]) for k in keys)} claims over {len(keys)} full-text passes")
    results = host.llm(reqs, max_concurrency=6)
    verdicts = []
    n_err = 0
    n_malformed = 0
    n_unjudged = 0
    for (pmid, stratum), res in zip(keys, results):
        if "error" in res or not res.get("tool_use"):
            n_err += 1
            continue
        raw = res["tool_use"]["input"].get("verdicts", [])
        # The tool payload sometimes arrives with the whole object serialised into
        # the `verdicts` field as a JSON string instead of as a list. Recover it
        # rather than losing the pass; drop only entries that are still not objects.
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                raw = parsed.get("verdicts", []) if isinstance(parsed, dict) else parsed
            except (ValueError, AttributeError):
                raw = []
        if not isinstance(raw, list):
            raw = []
        got = {_key(v["gene_target"]): v for v in raw
               if isinstance(v, dict) and v.get("gene_target") and v.get("verdict")}
        n_malformed += len(raw) - len(got)
        for c in groups[(pmid, stratum)]:
            v = got.get(_key(c["gene_target"]))
            if not v:
                n_unjudged += 1
                continue
            verdicts.append({
                "pmid": pmid,
                "stratum": stratum,
                "gene_target": c["gene_target"],
                "verdict": v["verdict"],
                "mechanism_from_body": v.get("mechanism_from_body", ""),
                "study_system": v.get("study_system", c["study_system"]),
                "evidence_sentence": v.get("evidence_sentence", ""),
            })
    # Repair pass: the first pass sometimes merges or renames a composite label
    # ("Hippo pathway" folded into "YAP1") and returns no verdict for it. Re-ask,
    # again over the complete body, naming only the labels still unjudged.
    judged = {(v["pmid"], v["stratum"], _key(v["gene_target"])) for v in verdicts}
    repair_keys, repair_reqs = [], []
    for pmid, stratum in keys:
        missing = [c for c in groups[(pmid, stratum)]
                   if (pmid, stratum, _key(c["gene_target"])) not in judged]
        if not missing:
            continue
        st = STRATA[stratum]
        repair_keys.append((pmid, stratum))
        repair_reqs.append({
            "prompt": (
                f"Disease: {st['disease']}\nManifestation: {st['manifestation']}\n\n"
                "Return one verdict for EACH of the following labels, using the label "
                "spelled EXACTLY as given. Do not merge, rename or omit any of them.\n"
                + "\n".join(f"- {c['gene_target']}: {c['mechanism_abstract']}" for c in missing)
                + f"\n\n=== COMPLETE ARTICLE TEXT ===\n{bodies[pmid]['body']}\n=== END ARTICLE ===\n\n"
                "Judge every label above against this article body."
            ),
            "system": VERIFY_SYSTEM,
            "tools": [VERIFY_TOOL],
            "tool_choice": {"type": "tool", "name": "verify_claims"},
            "max_tokens": 4000,
            "model": host.reasoning_model(),
        })
    n_repaired = 0
    if repair_reqs:
        print(f"  repair pass over {len(repair_reqs)} articles for {n_unjudged} unjudged claims")
        for (pmid, stratum), res in zip(repair_keys, host.llm(repair_reqs, max_concurrency=6)):
            if "error" in res or not res.get("tool_use"):
                continue
            raw = res["tool_use"]["input"].get("verdicts", [])
            if isinstance(raw, str):
                try:
                    parsed = json.loads(raw)
                    raw = parsed.get("verdicts", []) if isinstance(parsed, dict) else parsed
                except (ValueError, AttributeError):
                    raw = []
            if not isinstance(raw, list):
                raw = []
            got = {_key(v["gene_target"]): v for v in raw
                   if isinstance(v, dict) and v.get("gene_target") and v.get("verdict")}
            for c in groups[(pmid, stratum)]:
                k = (pmid, stratum, _key(c["gene_target"]))
                if k in judged:
                    continue
                v = got.get(_key(c["gene_target"]))
                if not v:
                    continue
                judged.add(k)
                n_repaired += 1
                verdicts.append({
                    "pmid": pmid,
                    "stratum": stratum,
                    "gene_target": c["gene_target"],
                    "verdict": v["verdict"],
                    "mechanism_from_body": v.get("mechanism_from_body", ""),
                    "study_system": v.get("study_system", c["study_system"]),
                    "evidence_sentence": v.get("evidence_sentence", ""),
                    "repair_pass": True,
                })
    still = n_unjudged - n_repaired
    print(f"  {len(verdicts)} verdicts; {n_err} verification passes failed; "
          f"{n_malformed} malformed verdict entries dropped; "
          f"{n_repaired} recovered by the repair pass; "
          f"{still} claims left with full text held but no verdict")
    return _dump(verdicts, os.path.join(work, "verdicts.json"))


# ---------------------------------------------------------------------------
# Aggregation -> the deliverable tables
# ---------------------------------------------------------------------------

TIER_SUPPORTED = "full text - supported"
TIER_PARTIAL = "full text - partial"
TIER_ABSTRACT = "abstract only"
TIER_RANK = {TIER_SUPPORTED: 3, TIER_PARTIAL: 2, TIER_ABSTRACT: 1}


def _label_in_body(label, constituents, body):
    """Does any token of this label literally occur in the extracted body text?

    The connector's PMC extraction drops italic markup, and journals italicise gene
    symbols, so a symbol can vanish from the body entirely ("the <i>FAT2</i> gene"
    arrives as "thegene"). A `not_supported` verdict returned against a body in which
    the symbol never appears is an artefact of that loss, not a reading of the paper.
    """
    toks = [t for t in re.split(r"[^A-Za-z0-9]+", label) if len(t) > 2]
    toks += [t for t in (constituents or []) if len(t) > 2]
    if not toks:
        return True
    return any(re.search(r"\b" + re.escape(t) + r"\b", body, re.I) for t in toks)


def _phase1b_index():
    """(disease, manifestation) -> set of loose keys for labels AND constituent genes."""
    idx = defaultdict(set)
    labels = defaultdict(set)
    with open(PHASE1B) as fh:
        for r in csv.DictReader(fh):
            k = (r["disease"], r["manifestation"])
            idx[k].add(_key(r["gene_target"]))
            labels[k].add(r["gene_target"])
            for g in (r.get("constituent_genes") or "").replace("|", ";").split(";"):
                if g.strip():
                    idx[k].add(_key(g))
    return idx, labels


def stage_aggregate(work, outdir=DATA):
    searches = _load(os.path.join(work, "search.json"), [])
    meta = _load(os.path.join(work, "metadata.json"), {})
    claims = _load(os.path.join(work, "claims.json"), [])
    bodies = _load(os.path.join(work, "fulltext.json"), {})
    verdicts = _load(os.path.join(work, "verdicts.json"), [])

    # Curation: label normalisation, scope drops and paper-level caveats, all held
    # in a file so each decision stays auditable and reversible.
    cur = _load(os.path.join(DATA, "phase7-fallback-curation.json"), {}) or {}
    drop = {(d["stratum"], _key(d["gene_target"])): d["reason"] for d in cur.get("drop_rows", [])}
    rename = {(d["stratum"], _key(d["from"])): d for d in cur.get("rename_labels", [])}
    pflag = {f["pmid"]: f for f in cur.get("paper_flags", [])}

    # --- query bank table ----------------------------------------------------
    qpath = os.path.join(outdir, "phase7-fallback-queries.csv")
    claim_pmids = defaultdict(set)
    for c in claims:
        claim_pmids[c["stratum"]].add(c["pmid"])
    with open(qpath, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["disease", "manifestation", "query_id", "query", "rationale", "sort",
                    "date_from", "max_results", "n_hits_total", "n_returned",
                    "n_papers_with_claim", "query_translation"])
        for s in searches:
            n_claim = len(set(s["pmids"]) & claim_pmids.get(s["stratum"], set()))
            w.writerow([s["disease"], s["manifestation"], s["query_id"], s["query"], s["rationale"],
                        s["sort"], s["date_from"], s["max_results"], s["n_hits_total"],
                        s["n_returned"], n_claim, s["query_translation"]])

    vmap = {(v["pmid"], v["stratum"], _key(v["gene_target"])): v for v in verdicts}
    p1b_idx, _ = _phase1b_index()

    rows = {}
    n_contradicted = 0
    n_dropped = 0
    n_unverified = 0
    n_markup_loss = 0
    n_symbol_absent = 0
    for c in claims:
        stratum = c["stratum"]
        ren = rename.get((stratum, _key(c["gene_target"])))
        label = ren["to"] if ren else c["gene_target"]
        k = (stratum, _key(label))
        if (stratum, _key(label)) in drop or (stratum, _key(c["gene_target"])) in drop:
            n_dropped += 1
            continue
        v = vmap.get((c["pmid"], stratum, _key(c["gene_target"])))
        has_body = c["pmid"] in bodies
        if has_body and v is None:
            n_unverified += 1
            continue  # body held but the verifier returned no verdict: not countable
        r = rows.setdefault(k, {
            "pmids": [], "access": [], "tiers": [], "mechanisms": [], "systems": [],
            "label": label, "label_type": "", "constituents": set(), "notes": set(),
            "caveats": set(),
            "n_fulltext_supported": 0, "n_fulltext_partial": 0, "n_fulltext_not_supported": 0,
            "n_papers_fulltext_read": 0, "n_papers_abstract_only": 0,
        })
        if ren:
            r["label_type"] = ren.get("label_type") or r["label_type"] or c["label_type"]
            for gname in ren.get("constituent_genes") or []:
                r["constituents"].add(gname)
            if ren.get("note"):
                r["notes"].add(ren["note"])
        else:
            r["label_type"] = r["label_type"] or c["label_type"]
        for gname in c.get("constituent_genes") or []:
            if gname.strip() and not ren:
                r["constituents"].add(gname.strip())
        symbol_in_body = True
        if has_body:
            symbol_in_body = _label_in_body(
                c["gene_target"],
                (ren.get("constituent_genes") if ren else None) or c.get("constituent_genes"),
                bodies[c["pmid"]]["body"])
        if v and v["verdict"] == "not_supported":
            if not symbol_in_body:
                # Markup loss, not a contradiction: hold the claim at the abstract tier.
                n_markup_loss += 1
                r["caveats"].add(
                    "full text retrieved but the gene symbol does not occur in the "
                    "extracted body (italic markup lost); claim held at the abstract tier")
                r["pmids"].append(c["pmid"])
                r["access"].append("abstract_only")
                r["n_papers_abstract_only"] += 1
                r["mechanisms"].append(c["mechanism_abstract"])
                r["systems"].append(c["study_system"])
                r["tiers"].append(TIER_ABSTRACT)
                continue
            n_contradicted += 1
            r["n_fulltext_not_supported"] += 1
            r["n_papers_fulltext_read"] += 1
            continue
        if has_body and v and not symbol_in_body:
            n_symbol_absent += 1
            r["caveats"].add(
                "verdict rests on the body naming the entity differently; the label's "
                "own symbol does not occur literally in the extracted text")
        r["pmids"].append(c["pmid"])
        if has_body and v:
            tier = TIER_SUPPORTED if v["verdict"] == "supported" else TIER_PARTIAL
            r["access"].append("full_text")
            r["n_papers_fulltext_read"] += 1
            if v["verdict"] == "supported":
                r["n_fulltext_supported"] += 1
            else:
                r["n_fulltext_partial"] += 1
            r["mechanisms"].append(v["mechanism_from_body"])
            r["systems"].append(v["study_system"])
        else:
            tier = TIER_ABSTRACT
            r["access"].append("abstract_only")
            r["n_papers_abstract_only"] += 1
            r["mechanisms"].append(c["mechanism_abstract"])
            r["systems"].append(c["study_system"])
        r["tiers"].append(tier)

    cpath = os.path.join(outdir, "phase7-fallback-candidates.csv")
    cols = ["gene_target", "constituent_genes", "label_type", "disease", "manifestation",
            "n_supporting_papers", "evidence_tier", "n_fulltext_supported", "n_fulltext_partial",
            "n_fulltext_not_supported", "n_papers_fulltext_read", "n_papers_abstract_only",
            "mechanism", "study_system", "supporting_pmids", "access", "paper_access",
            "novel_vs_phase1b", "novelty_basis", "scope_flag", "scope_flag_detail",
            "expression_evidence", "dataset_lost", "curation_note", "fulltext_caveat",
            "source_phase"]
    out_rows = []
    for (stratum, _kk), r in rows.items():
        if not r["pmids"]:
            continue  # every paper behind this label was contradicted by its own body
        st = STRATA[stratum]
        held = p1b_idx[(st["disease"], st["manifestation"])]
        best = max(r["tiers"], key=lambda t: TIER_RANK[t])
        order = sorted(range(len(r["pmids"])), key=lambda i: (-TIER_RANK[r["tiers"][i]], r["pmids"][i]))
        pm = [r["pmids"][i] for i in order]
        acc = [r["access"][i] for i in order]
        consts = sorted(r["constituents"])
        if _key(r["label"]) in held:
            basis, novel = "exact_label_in_phase1b", False
        elif consts and all(_key(gname) in held for gname in consts):
            basis, novel = "constituents_all_in_phase1b", False
        elif consts and any(_key(gname) in held for gname in consts):
            basis, novel = "composite_label_partly_held_by_phase1b", True
        else:
            basis, novel = "not_in_phase1b", True
        flags = [pflag[p] for p in pm if p in pflag]
        all_flagged = len(flags) == len(pm) and bool(flags)
        out_rows.append({
            "gene_target": r["label"],
            "constituent_genes": ";".join(consts),
            "label_type": r["label_type"],
            "disease": st["disease"],
            "manifestation": st["manifestation"],
            "n_supporting_papers": len(pm),
            "evidence_tier": best,
            "n_fulltext_supported": r["n_fulltext_supported"],
            "n_fulltext_partial": r["n_fulltext_partial"],
            "n_fulltext_not_supported": r["n_fulltext_not_supported"],
            "n_papers_fulltext_read": r["n_papers_fulltext_read"],
            "n_papers_abstract_only": r["n_papers_abstract_only"],
            "mechanism": r["mechanisms"][order[0]],
            "study_system": r["systems"][order[0]],
            "supporting_pmids": ";".join(pm),
            "access": ";".join(acc),
            "paper_access": ";".join("%s:%s" % (p, a) for p, a in zip(pm, acc)),
            "novel_vs_phase1b": str(novel),
            "novelty_basis": basis,
            "scope_flag": flags[0]["flag"] if all_flagged else "",
            "scope_flag_detail": flags[0]["detail"] if all_flagged else "",
            "expression_evidence": "no expression contrast found",
            "dataset_lost": st["dataset_lost"],
            "curation_note": " | ".join(sorted(r["notes"])),
            "fulltext_caveat": " | ".join(sorted(r["caveats"])),
            "source_phase": "phase7-fallback",
        })
    out_rows.sort(key=lambda r: (r["disease"], r["manifestation"],
                                 -TIER_RANK[r["evidence_tier"]], -r["n_supporting_papers"],
                                 r["gene_target"]))
    with open(cpath, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(out_rows)

    # --- integrity assertions over what was just written ---------------------
    with open(cpath) as fh:
        back = list(csv.DictReader(fh))
    live_pmids = set(meta)
    for r in back:
        assert r["evidence_tier"] in TIER_RANK, r["evidence_tier"]
        assert r["supporting_pmids"], "candidate with no PMID: %s" % r["gene_target"]
        for p in r["supporting_pmids"].split(";"):
            assert p in live_pmids, "PMID %s not in a retrieved connector response" % p
        assert r["disease"] in {"NF1", "NF2-SWN", "SWN"}
        assert r["manifestation"] in {s["manifestation"] for s in STRATA.values()}
        assert "exists" not in r["expression_evidence"]
        if r["evidence_tier"] != TIER_ABSTRACT:
            assert "full_text" in r["access"], r["gene_target"]
    print("  wrote %d candidate rows -> %s" % (len(back), cpath))
    print("  wrote %d query rows -> %s" % (len(searches), qpath))
    print("  claims dropped on scope grounds (curation): %d" % n_dropped)
    print("  claims contradicted by their own full text: %d" % n_contradicted)
    print("  claims with full text held but no verdict returned: %d" % n_unverified)
    print("  not_supported verdicts voided by markup loss (held at abstract tier): %d" % n_markup_loss)
    print("  verdicts kept but flagged, label symbol absent from the body: %d" % n_symbol_absent)
    novel = sum(1 for r in back if r["novel_vs_phase1b"] == "True")
    print("  novel vs Phase 1b: %d of %d rows" % (novel, len(back)))
    return cpath, qpath


# ---------------------------------------------------------------------------

# --- post-curation -----------------------------------------------------------
# Corrections ratified after the pipeline ran. They are applied as their own
# stage, reading the same curation file the aggregate stage reads, so they are
# reproducible from the record rather than hand-edited into the CSV. The stage
# is idempotent and needs no work/ cache, so it can be re-run on the committed
# table without re-fetching 279 papers and re-rolling every model verdict.

# Kara, 2026-11-17. A paper that does not establish germline NF disease is kept
# and penalised rather than excluded -- but only where germline status is
# UNSTATED. Material established as sporadic stays excluded under the standing
# rule in the Disease and Manifestation Labeling Standard. The magnitude is a
# judgement call, not a measurement, and lives here so it is visible and
# changeable in one place rather than buried per row.
GERMLINE_UNESTABLISHED_WEIGHT = 0.5
GERMLINE_FLAG = "germline NF attribution not established"


def stage_postcurate(outdir=DATA):
    """Apply ratified post-hoc corrections to the committed candidate table."""
    path = os.path.join(outdir, "phase7-fallback-candidates.csv")
    cur = _load(os.path.join(DATA, "phase7-fallback-curation.json"), {}) or {}
    relabels = {(d["disease"], d["from_manifestation"], _key(d["gene_target"])): d
                for d in cur.get("manifestation_relabels", [])}

    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
        fields = list(rows[0].keys()) if rows else []

    for col in ("germline_attribution_weight", "postcuration_note"):
        if col not in fields:
            fields.append(col)

    n_relabelled = n_penalised = 0
    for r in rows:
        key = (r["disease"], r["manifestation"], _key(r["gene_target"]))
        if key in relabels:
            d = relabels[key]
            r["manifestation"] = d["to_manifestation"]
            r["postcuration_note"] = d["reason"]
            n_relabelled += 1
        else:
            r.setdefault("postcuration_note", r.get("postcuration_note") or "")

        if (r.get("scope_flag") or "").strip() == GERMLINE_FLAG:
            r["germline_attribution_weight"] = GERMLINE_UNESTABLISHED_WEIGHT
            n_penalised += 1
        else:
            r["germline_attribution_weight"] = 1.0

    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print("  rows relabelled: %d" % n_relabelled)
    print("  rows carrying the germline penalty (%.2f): %d"
          % (GERMLINE_UNESTABLISHED_WEIGHT, n_penalised))
    return {"relabelled": n_relabelled, "penalised": n_penalised}


STAGES = ["search", "metadata", "screen", "fulltext", "verify", "aggregate", "postcurate"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stage", nargs="?", default="all", choices=STAGES + ["all"])
    ap.add_argument("--workdir", default=os.path.join(REPO, "phase-7", "work"))
    ap.add_argument("--outdir", default=DATA)
    args = ap.parse_args(argv)
    host = globals().get("HOST")
    os.makedirs(args.workdir, exist_ok=True)
    todo = STAGES if args.stage == "all" else [args.stage]
    for s in todo:
        print(f"[{s}]")
        if s == "aggregate":
            stage_aggregate(args.workdir, args.outdir)
        elif s == "postcurate":
            stage_postcurate(args.outdir)
        else:
            if host is None:
                raise SystemExit(
                    f"stage '{s}' needs the host object (MCP connector / host.llm). "
                    "Run it from the repl kernel with init_globals={'HOST': host}."
                )
            globals()[f"stage_{s}"](host, args.workdir)


if __name__ == "__main__":
    main()
