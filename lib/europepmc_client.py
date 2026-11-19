#!/usr/bin/env python3
"""Europe PMC JATS retrieval - the ruled-on full-text route for verification.

Why this exists
---------------
Phase 7 measured the PubMed MCP connector's PMC text extraction deleting
italicised text from article bodies. Journals italicise gene symbols, so
`the <italic>FAT2</italic> gene` arrived as `thegene` and the symbol vanished.
53 of 59 sampled papers carried the signature, the claim's own label was absent
from the retrieved body in 39 of 155 claims, and self-disagreement ran 23.1%
where the label was missing against 8.6% where it was present - the damage
degrades judgement rather than merely hiding text.

Kara ruled on 2026-11-17: verification reads Europe PMC JATS; the PubMed
connector keeps search and metadata. This module is that path.

The safety property
-------------------
`jats_to_text` is *provably* symbol-preserving: `missing_inline_strings()`
re-reads the rendered text and returns every inline-markup string (italic,
bold, sup, sub, sc, monospace) that failed to survive. A caller can assert it is
empty. This is what the symbol-presence guard could not give - that guard only
voided false negatives, and could never catch the positive-verdict-on-a-deleted-
symbol case that PMID 39367156 / RNF213 demonstrated.

Routes, in order
----------------
1. Europe PMC  `{EPMC}/{PMCID}/fullTextXML`
2. NCBI efetch `efetch.fcgi?db=pmc&id={numeric}`

Open-access status does not predict which route works: a paper closed at the
publisher often has a free author manuscript that only efetch serves. This
mirrors litmonitor/monitor.py, which has carried the same two-route logic since
Phase 1b; that module is left untouched here rather than refactored, because it
backs a scheduled agent.

Usage
-----
    from europepmc_client import get_fulltext
    doc = get_fulltext(pmid="39367156")
    doc["text"]            # rendered body, symbols intact
    doc["sections"]        # [(heading, text), ...]
    doc["route"]           # 'europepmc' | 'efetch' | None
    doc["symbol_check"]    # [] when nothing was dropped

    python europepmc_client.py --pmid 39367156 --grep RNF213
    python europepmc_client.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.parse
import urllib.request
from xml.etree import ElementTree as ET

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CACHE = os.environ.get("EPMC_CACHE", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  "..", "build", "epmc-cache"))
UA = "nf-target-pipeline"

# Inline markup whose text content must survive rendering. This is the exact
# failure mode being defended against: the connector dropped <italic> content.
INLINE_TAGS = ("italic", "bold", "sup", "sub", "sc", "monospace", "underline")

# Removed wholesale: numbered citations inline as "disease1-3" and corrupt the
# text a reader is asked to judge; back matter is references and funding.
# Tables are KEPT: they carry results a verifier needs. Only citation noise and
# back matter go. An earlier draft dropped table-wrap and lost an italicised gene
# symbol (BMPR1B) that appeared only in a table - the self-check caught it.
DROP_TAGS = ("xref", "ref-list", "back", "fn-group", "author-notes")

BLOCK_TAGS = ("p", "title", "sec", "abstract", "caption", "list-item", "td", "th")


def _get(url: str, timeout: int = 45) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return fh.read().decode("utf-8", "replace")


def _cache_path(key: str) -> str:
    os.makedirs(CACHE, exist_ok=True)
    return os.path.join(CACHE, re.sub(r"[^A-Za-z0-9_.-]", "_", key) + ".xml")


def epmc_record(pmid: str) -> dict:
    """PMID -> {pmcid, doi, is_open_access, author_manuscript, journal, title}."""
    url = EPMC + "/search?" + urllib.parse.urlencode(
        {"query": "EXT_ID:%s" % pmid, "resultType": "core", "format": "json"})
    try:
        hits = json.loads(_get(url))["resultList"]["result"]
    except Exception:
        return {}
    if not hits:
        return {}
    r = hits[0]
    return {"pmcid": r.get("pmcid"), "doi": r.get("doi"),
            "is_open_access": r.get("isOpenAccess"), "author_manuscript": r.get("authMan"),
            "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title"),
            "title": r.get("title")}


def fetch_jats(pmcid: str, use_cache: bool = True) -> dict:
    """Return {'xml': str|None, 'route': str|None, 'error': str|None}."""
    pid = str(pmcid)
    cp = _cache_path(pid)
    if use_cache and os.path.exists(cp):
        with open(cp, encoding="utf-8") as fh:
            blob = fh.read()
        route, _, xml = blob.partition("\n")
        return {"xml": xml, "route": route or "cache", "error": None}

    errors = []
    for route, url in (("europepmc", "%s/%s/fullTextXML" % (EPMC, pid)),
                       ("efetch", "%s/efetch.fcgi?db=pmc&rettype=xml&id=%s"
                        % (EUTILS, pid.replace("PMC", "")))):
        try:
            xml = _get(url)
        except Exception as exc:
            errors.append("%s: %s" % (route, type(exc).__name__))
            time.sleep(0.3)
            continue
        # A body, not a stub or an error page. Deliberately not litmonitor's
        # "3+ <sec> and >8000 chars": that rejects short but complete papers.
        if "<body" in xml and len(xml) > 2000:
            if use_cache:
                with open(cp, "w", encoding="utf-8") as fh:
                    fh.write(route + "\n" + xml)
            return {"xml": xml, "route": route, "error": None}
        errors.append("%s: no <body> (%d chars)" % (route, len(xml)))
        time.sleep(0.3)
    return {"xml": None, "route": None, "error": "; ".join(errors)}


def _strip(root: ET.Element) -> None:
    for tag in DROP_TAGS:
        for parent in root.iter():
            for child in list(parent):
                if child.tag == tag:
                    # Keep the tail so surrounding words stay separated.
                    tail = child.tail or ""
                    parent.remove(child)
                    if tail.strip():
                        prev = list(parent)
                        if prev:
                            prev[-1].tail = (prev[-1].tail or "") + tail
                        else:
                            parent.text = (parent.text or "") + tail


def _render(el: ET.Element) -> str:
    """Depth-first render. Inline markup contributes its text; block elements
    are separated by newlines so sentences never run together."""
    out = []

    def walk(node: ET.Element) -> None:
        if node.tag in BLOCK_TAGS:
            out.append("\n")
        if node.text:
            out.append(node.text)
        for child in node:
            walk(child)
            if child.tail:
                out.append(child.tail)
        if node.tag in BLOCK_TAGS:
            out.append("\n")

    walk(el)
    text = "".join(out)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def missing_inline_strings(xml: str, text: str) -> list:
    """Inline-markup strings that did NOT survive rendering. Should be empty.

    Stripped regions (citations, reference lists) are removed first, so the
    check measures what SHOULD have survived rather than flagging journal names
    in a bibliography we deliberately discard.
    """
    root = ET.fromstring(xml)
    _strip(root)
    body = root.find(".//body")
    if body is None:
        return []
    missing = []
    for tag in INLINE_TAGS:
        for el in body.findall(".//%s" % tag):
            s = "".join(el.itertext()).strip()
            if s and s not in text:
                missing.append({"tag": tag, "string": s[:60]})
    return missing


def jats_to_text(xml: str) -> dict:
    root = ET.fromstring(xml)
    _strip(root)
    body = root.find(".//body")
    sections = []
    if body is not None:
        for sec in body.findall("./sec"):
            t = sec.find("./title")
            sections.append(((t.text or "").strip() if t is not None else "",
                             _render(sec)))
    abstract_el = root.find(".//abstract")
    return {
        "abstract": _render(abstract_el) if abstract_el is not None else "",
        "text": _render(body) if body is not None else "",
        "sections": sections,
    }


def get_fulltext(pmid: str = None, pmcid: str = None, use_cache: bool = True) -> dict:
    """One call: resolve, fetch, render, and self-check symbol preservation."""
    rec = {}
    if pmcid is None:
        if pmid is None:
            raise ValueError("need pmid or pmcid")
        rec = epmc_record(str(pmid))
        pmcid = rec.get("pmcid")
    out = {"pmid": pmid, "pmcid": pmcid, "record": rec, "route": None,
           "text": "", "sections": [], "abstract": "", "symbol_check": [],
           "error": None}
    if not pmcid:
        out["error"] = "no PMCID in Europe PMC"
        return out
    got = fetch_jats(pmcid, use_cache=use_cache)
    if not got["xml"]:
        out["error"] = got["error"]
        return out
    out["route"] = got["route"]
    parsed = jats_to_text(got["xml"])
    out.update(parsed)
    out["symbol_check"] = missing_inline_strings(got["xml"], parsed["text"])
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pmid")
    ap.add_argument("--pmcid")
    ap.add_argument("--grep", help="count occurrences of this string in the body")
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        # PMID 39367156 / RNF213 is the case that exposed the connector defect:
        # its connector-extracted body contained RNF213 zero times.
        doc = get_fulltext(pmid="39367156", use_cache=not args.no_cache)
        n = len(re.findall(r"RNF213", doc["text"]))
        print("route:", doc["route"], "| body chars:", len(doc["text"]))
        print("RNF213 occurrences:", n, "(connector-extracted body had 0)")
        print("inline strings dropped:", len(doc["symbol_check"]))
        assert n > 0, "RNF213 missing - the defect this module exists to fix"
        assert not doc["symbol_check"], doc["symbol_check"][:5]
        print("SELFTEST PASS")
        return

    doc = get_fulltext(pmid=args.pmid, pmcid=args.pmcid, use_cache=not args.no_cache)
    print(json.dumps({k: doc[k] for k in ("pmid", "pmcid", "route", "error")}, indent=1))
    print("body chars:", len(doc["text"]), "| sections:", len(doc["sections"]),
          "| inline dropped:", len(doc["symbol_check"]))
    if args.grep:
        print("%r occurrences: %d" % (args.grep, len(re.findall(re.escape(args.grep), doc["text"]))))


if __name__ == "__main__":
    main()
