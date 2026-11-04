"""Helpers for the monthly NF literature update.

Retrieval ladder, preprint detection and the two prompt builders used by the
Phase 1b protocol. Everything else (merge rules, table schema) is in SKILL.md.
"""

import json
import re
import time
import urllib.parse
import urllib.request

EPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
EPMC_FULLTEXT = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&rettype=xml&id={pmcid}"
PREPRINT_DOI_PREFIXES = ("10.1101", "10.21203", "10.20944", "10.31219", "10.64898", "10.26434", "10.48550")

NF_MANIFESTATIONS = (
    "Bone defects", "Cardiovascular issues", "Cognition / Behavioral / Learning", "Sleep",
    "Cutaneous neurofibroma", "Ependymoma", "Gastrointestinal stromal tumor (GIST)",
    "Hematologic malignancies", "High grade glioma",
    "Malignant peripheral nerve sheath tumor (MPNST)", "Meningioma", "Optic pathway glioma",
    "Non-optic LGG", "Pain", "Plexiform neurofibroma", "ANNUBP / atypical neurofibroma",
    "Pulmonary disease", "Non-vestibular schwannoma", "Vestibular schwannoma", "Other",
)


def nf_manifestations():
    """The fixed vocabulary, as a list. Apply verbatim; never invent a term."""
    return list(NF_MANIFESTATIONS)


def epmc_record(pmid, timeout=40):
    """Europe PMC core record for one PMID: pmcid, open-access and author-manuscript flags."""
    url = EPMC_SEARCH + "?" + urllib.parse.urlencode(
        {"query": "EXT_ID:%s" % pmid, "resultType": "core", "format": "json"})
    try:
        hits = json.load(urllib.request.urlopen(url, timeout=timeout))["resultList"]["result"]
    except Exception as exc:
        return {"pmid": str(pmid), "error": repr(exc)[:120]}
    if not hits:
        return {"pmid": str(pmid), "found": False}
    r = hits[0]
    return {"pmid": str(pmid), "found": True, "pmcid": r.get("pmcid"), "doi": r.get("doi"),
            "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title"),
            "year": r.get("pubYear"), "is_open_access": r.get("isOpenAccess"),
            "in_epmc": r.get("inEPMC"), "author_manuscript": r.get("authMan"),
            "pub_types": (r.get("pubTypeList") or {}).get("pubType")}


def fetch_fulltext(pmcid, timeout=45, min_sections=3):
    """Full article body via the retrieval ladder, references stripped.

    Tries Europe PMC fullTextXML, then NCBI efetch against the same PMC id, which
    returns NIH author manuscripts that Europe PMC refuses. Open-access status does
    NOT predict which works, so always try both before calling a paper unreachable.
    Returns {text, route, n_sections} or {text: None, route: None} on failure.
    """
    pid = str(pmcid)
    attempts = (("europepmc", EPMC_FULLTEXT.format(pmcid=pid)),
                ("efetch", EFETCH.format(pmcid=pid.replace("PMC", ""))))
    for route, url in attempts:
        try:
            body = urllib.request.urlopen(url, timeout=timeout).read().decode("utf-8", "replace")
        except Exception:
            time.sleep(0.3)
            continue
        if body.count("<sec") >= min_sections and len(body) > 8000:
            return {"text": strip_references(body), "route": route,
                    "n_sections": body.count("<sec")}
    return {"text": None, "route": None, "n_sections": 0}


def strip_references(xml):
    """Drop the back matter so cited titles cannot be read as claims of this paper."""
    return re.sub(r"<back>.*?</back>", "", xml, flags=re.S)


def is_preprint(doi=None, journal=None):
    """Flag preprints by DOI prefix, then journal string. Detection is imperfect:
    a preprint on an unusual server can go unflagged, so record the method used."""
    d = (doi or "").strip().lower()
    for prefix in PREPRINT_DOI_PREFIXES:
        if d.startswith(prefix + "/"):
            return True
    j = (journal or "").strip().lower()
    return bool(re.search(r"rxiv|research square|res sq|preprint", j))


def extraction_prompt(title, abstract, manifestations=None):
    """Prompt for abstract-level claim extraction. Pair with EXTRACTION_SYSTEM in SKILL.md."""
    if manifestations is None:
        manifestations = NF_MANIFESTATIONS
    return EXTRACTION_TEMPLATE.format(manif="; ".join(manifestations),
                                      title=title, abstract=(abstract or "")[:6000])


def verdict_prompt(claims, body, manifestations=None):
    """Prompt for judging extracted claims against a complete article body.

    claims: iterable of (gene_target, disease, manifestation) tuples from ONE paper.
    """
    if manifestations is None:
        manifestations = NF_MANIFESTATIONS
    listed = "\n".join("- %s | %s | %s" % (g, d, m) for g, d, m in claims)
    return VERDICT_TEMPLATE.format(claims=listed, manif="; ".join(manifestations),
                                   body=(body or "")[:260000])


EXTRACTION_TEMPLATE = """Abstract below. Extract every gene/protein/molecular target that the abstract presents as a disease driver, disease modifier, or therapeutic target in neurofibromatosis.

Rules:
- Use the official human HGNC gene symbol where one exists. For a protein family or complex with no single symbol, use the common name (e.g. "MEK1/2", "PRC2", "Hippo/YAP-TEAD").
- Do NOT extract: the disease gene itself when merely used to define the cohort (e.g. "NF1 patients"); cell-type markers; assay reagents; genes mentioned only as background citation.
- disease: exactly one of "NF1", "NF2-SWN", "SWN", or "Not specified". Use NF2-SWN only for NF2-related disease or NF2/merlin-driven tumours; use SWN only for schwannomatosis (SMARCB1/LZTR1/22q, non-NF2).
- manifestations: choose from this fixed list, verbatim, one or more: {manif}
  Use "Other" only if the phenotype studied is not on the list. Use only what the abstract actually studies.
- role: one of "driver", "modifier", "therapeutic target", "biomarker".
- mechanism: <= 25 words, stated in the abstract.
- evidence: one of "human tissue", "clinical trial", "mouse model", "cell line", "computational", "review".
- If the paper is a review, still extract the targets it highlights, with evidence "review".

Return JSON: {{"targets":[{{"gene":"","disease":"","manifestations":[],"role":"","mechanism":"","evidence":""}}]}}
Empty list if nothing qualifies.

TITLE: {title}
ABSTRACT: {abstract}"""

VERDICT_TEMPLATE = """Article full text (JATS XML, references removed) follows. Judge each claim below against the WHOLE article, not against its abstract.

Claims, one per line, as gene_target | disease | manifestation:
{claims}

For each claim return one object:
- verdict: "supported" if the article itself presents this gene as a driver, modifier or therapeutic target for that disease and manifestation; "partially_supported" if it supports the target but for a different manifestation, a different disease, or only indirectly; "not_supported" if the article does not support it or contradicts it.
- mechanism_from_fulltext: <= 25 words, as the body states it. Empty string if the body states none.
- manifestation_in_fulltext: the manifestation the body actually studies, verbatim from this list: {manif}. Comma-separate if several.
- study_system: one of "clinical trial", "human tissue", "mouse model", "cell line", "computational", "review".
- evidence_note: <= 20 words on what the article actually shows. Empty string if nothing to add.

Judge only what this article demonstrates or explicitly asserts. A cited result from another paper is not this paper's support.

Return JSON: {{"judgements":[{{"gene_target":"","manifestation":"","verdict":"","mechanism_from_fulltext":"","manifestation_in_fulltext":"","study_system":"","evidence_note":""}}]}}

FULL TEXT:
{body}"""
