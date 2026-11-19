#!/usr/bin/env python3
"""Phase 7 follow-up: how unstable is single-reader full-text verification?

Measurement only. Nothing in phase-1b/ is read for anything but input, and no Phase 1b
table is modified.

Two quantities, kept separate:

  A. Self-consistency - the same reader, the same retrieved body, the same prompt, run
     twice. The input is held fixed, so disagreement here is reader noise and nothing else.
  B. Reproduction of Phase 1b's recorded verdict - a fresh verdict against what Phase 1b
     wrote down. This conflates reader noise with every change in protocol and in retrieved
     text since Phase 1b ran, and must not be read as a pure measure of reader noise.

Claim unit: (gene_target, disease, manifestation, pmid), reconstructed from
phase-1b/data/phase1b-literature-targets.csv (supporting_pmids / paper_access /
n_papers_fulltext_read / verdicts_from_whole_body) and phase1b-references.csv.

Phase 1b stores verdict COUNTS per row, not a verdict per claim. A claim's recorded verdict
is recoverable only where a row's full-text verdicts are unanimous, their count equals
n_papers_fulltext_read, and all of them came from the whole-body pass. Those claims, and
only those, enter measurement B.

Sampling is a one-stage cluster sample: papers are shuffled with a fixed seed and walked in
order, and every full-text claim of a sampled paper is verified in one prompt - which is
exactly Phase 1b's prompt unit. Each claim therefore has the same inclusion probability, and
confidence intervals are reported both as Wilson intervals (claims treated as independent)
and as a bootstrap resampling whole papers, which respects the clustering.

Retrieval is the PubMed MCP connector, as Phase 7 used. Its PMC extraction drops italic
markup, and journals italicise gene symbols, so a symbol can be deleted from the retrieved
body outright. The markup guard voids any fresh `not_supported` verdict returned against a
body in which the claim's label never appears.

RUNTIME REQUIREMENTS
  * host.mcp (Claude Science `repl` kernel) for connector retrieval, or --retrieval epmc to
    use Europe PMC / NCBI efetch directly, which is what Phase 1b itself used.
  * host.llm (Claude Science python kernel) for the verification passes.
  The recorded run used: connector retrieval, model claude-sonnet-5, thinking disabled, two
  independent batched passes over identical prompts.

Outputs (phase-7/):
  data/phase7-verification-stability.csv
  data/phase7-verification-stability-summary.json
  docs/phase7-verification-stability.md  (written by hand from the JSON, not by this script)
"""

import argparse
import collections
import csv
import json
import math
import os
import re
import time
import urllib.request

import numpy as np

SEED = 20261117
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P1B = os.path.join(REPO, "phase-1b", "data")
OUT = os.path.join(REPO, "phase-7", "data")
PUBMED_MCP = "directory-f5d400df-ea7e-41b4-8fa7-34cfba605551"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
ADJUDICATE = ["36148553", "39367156"]

# -- Phase 1b verification protocol, copied verbatim from litmonitor/monitor.py -------------
MANIF = ["Bone defects", "Cardiovascular issues", "Cognition / Behavioral / Learning", "Sleep",
         "Cutaneous neurofibroma", "Ependymoma", "Gastrointestinal stromal tumor (GIST)",
         "Hematologic malignancies", "High grade glioma",
         "Malignant peripheral nerve sheath tumor (MPNST)", "Meningioma", "Optic pathway glioma",
         "Non-optic LGG", "Pain", "Plexiform neurofibroma", "ANNUBP / atypical neurofibroma",
         "Pulmonary disease", "Non-vestibular schwannoma", "Vestibular schwannoma", "Other"]
SYSTEMS = ["human tissue", "clinical trial", "mouse model", "cell line", "computational", "review"]
VERDICT_SYSTEM = ("You verify target claims against the complete body of a research article. You "
                  "output JSON only. You never credit a claim the article does not itself "
                  "demonstrate or explicitly assert.")


def verdict_prompt(claims, body):
    listed = "\n".join("- %s | %s | %s" % c for c in claims)
    return """Article full text (JATS XML, references removed) follows. Judge each claim against the WHOLE article, not its abstract.

Claims, as target | disease | manifestation:
{claims}

For each claim return one object:
- verdict: "supported" if this article presents the target as a driver, modifier or therapeutic target for that disease and manifestation; "partially_supported" if it supports the target but for a different manifestation or disease, or only indirectly; "not_supported" otherwise.
- mechanism_from_fulltext: <= 25 words as the body states it, else "".
- manifestation_in_fulltext: what the body studies, verbatim from: {manif}
- study_system: one of {systems}.

A cited result from another paper is not this paper's support.

Return JSON: {{"judgements":[{{"gene_target":"","manifestation":"","verdict":"","mechanism_from_fulltext":"","manifestation_in_fulltext":"","study_system":""}}]}}

FULL TEXT:
{body}""".format(claims=listed, manif="; ".join(MANIF),
                 systems=", ".join('"%s"' % s for s in SYSTEMS), body=(body or "")[:260000])


# -- population ----------------------------------------------------------------------------
def parse_access(s):
    d = {}
    for tok in (s or "").split(";"):
        tok = tok.strip()
        if tok:
            p, _, a = tok.partition(":")
            d[p.strip()] = a.strip()
    return d


def build_population():
    rows = list(csv.DictReader(open(os.path.join(P1B, "phase1b-literature-targets.csv"))))
    refs = {r["pmid"]: r for r in csv.DictReader(open(os.path.join(P1B, "phase1b-references.csv")))}
    population, paper_claims = [], collections.defaultdict(list)
    for i, r in enumerate(rows):
        acc = parse_access(r["paper_access"])
        ft = [p for p, a in acc.items() if a.startswith("full_text")]
        s, pa, ns = (int(r[k] or 0) for k in
                     ("n_fulltext_supported", "n_fulltext_partial", "n_fulltext_not_supported"))
        tot = s + pa + ns
        wb = int(r["verdicts_from_whole_body"] or 0)
        unanimous = tot > 0 and max(s, pa, ns) == tot and tot == len(ft)
        recorded = ("supported" if s == tot else "partially_supported" if pa == tot
                    else "not_supported") if unanimous else ""
        basis = "whole_body" if (unanimous and wb == tot) else (
            "mixed_pass" if unanimous else "not_determinable")
        for p in ft:
            c = dict(row_idx=i, gene_target=r["gene_target"], disease=r["disease"],
                     manifestation=r["manifestation"], pmid=p,
                     constituent_genes=r["constituent_genes"],
                     pmc=refs.get(p, {}).get("pmc", "").strip(),
                     phase1b_fulltext_source=refs.get(p, {}).get("fulltext_source", ""),
                     phase1b_verdict=recorded if basis == "whole_body" else "",
                     phase1b_verdict_basis=basis)
            population.append(c)
            paper_claims[p].append(c)
    return rows, population, paper_claims


# -- retrieval -----------------------------------------------------------------------------
def fetch_connector(host, pmcid):
    r = host.mcp(PUBMED_MCP, "get_full_text_article", pmc_ids=[pmcid])
    arts = r.get("articles") or []
    return (arts[0].get("full_text") or "") if arts else ""


def fetch_epmc(pmcid):
    """Phase 1b's own route: Europe PMC JATS, then NCBI efetch. Markup is preserved here."""
    pid = str(pmcid)
    for url in ("%s/%s/fullTextXML" % (EPMC, pid),
                "%s/efetch.fcgi?db=pmc&rettype=xml&id=%s" % (EUTILS, pid.replace("PMC", ""))):
        try:
            body = urllib.request.urlopen(url, timeout=60).read().decode("utf-8", "replace")
        except Exception:
            time.sleep(0.3)
            continue
        if body.count("<sec") >= 3 and len(body) > 8000:
            return re.sub(r"<back>.*?</back>", "", body, flags=re.S)
    return ""


# -- parsing, guard ------------------------------------------------------------------------
def parse_judgements(text):
    if not text:
        return []
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        try:
            return json.loads(m.group(0)).get("judgements") or []
        except Exception:
            pass
    objs = []
    for frag in re.findall(r"\{[^{}]*\"verdict\"[^{}]*\}", text, re.S):
        try:
            objs.append(json.loads(frag))
        except Exception:
            pass
    return objs


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def norm_verdict(v):
    v = norm(v)
    if v == "supported":
        return "supported"
    if v.startswith("partial"):
        return "partially_supported"
    if v.startswith("not"):
        return "not_supported"
    return "unparsed:" + (v[:20] or "empty")


def symbol_tokens(gene_target, constituent):
    toks = {p.strip() for p in re.split(r"[;,]", constituent or "") if p.strip()}
    base = re.sub(r"\(([^)]*)\)", r" \1 ", gene_target or "")
    for t in re.split(r"[\s/\\|]+", base):
        t = t.strip(" -")
        if len(t) >= 3:
            toks.add(t)
    return {t for t in toks if t}


def present(body, toks, lax=True):
    """Does the label appear at a word boundary? `lax` also accepts the digit-stripped base
    (YAP1 -> YAP), so the guard voids a verdict only when the label is genuinely absent."""
    low = body.lower()
    for t in toks:
        variants = {t}
        if lax:
            s = re.sub(r"\d+$", "", t)
            if len(s) >= 3:
                variants.add(s)
        for v in variants:
            if re.search(r"(?<![a-z0-9])" + re.escape(v.lower()) + r"(?![a-z0-9])", low):
                return True, v
    return False, ""


# Fingerprint of dropped italic markup: words fused across a deleted symbol ("thegene"),
# or a dangling hyphen where the symbol was ("-related schwannomatosis", "with-SWN").
MARKUP_PAT = re.compile(
    r"\b(the|a|an|with|in|of|and|that|this)(gene|genes|protein|mice|cells|expression|mutation|"
    r"mutations|knockdown|locus)\b|(?<=[\s(])-(related|SWN|deficient|null|mutant|positive|"
    r"negative)\b|\b(the|in|of|with|and)-")


def markup_signature(body):
    return len(MARKUP_PAT.findall(body))


# -- statistics ----------------------------------------------------------------------------
def wilson(k, n, z=1.96):
    if not n:
        return [float("nan"), float("nan")]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def cluster_boot(recs, flagfn, rng, B=10000):
    papers = sorted({r["pmid"] for r in recs})
    byp = {p: [r for r in recs if r["pmid"] == p] for p in papers}
    est = []
    for _ in range(B):
        num = den = 0
        for i in rng.choice(len(papers), size=len(papers), replace=True):
            for r in byp[papers[i]]:
                den += 1
                num += int(flagfn(r))
        if den:
            est.append(num / den)
    return [round(float(np.percentile(est, 2.5)), 4), round(float(np.percentile(est, 97.5)), 4)]


def binary(v):
    return "not_supported" if v == "not_supported" else "support"


# -- the two known contradictions ----------------------------------------------------------
def adjudicate(host, paper_claims, bodies, model, repeats=3):
    """Re-read the two Phase 7 contradictions, each three times against the connector body and
    three times against the clean Europe PMC JATS body Phase 1b itself read. The second route
    is the point: it shows whether a disagreement is judgement or deleted markup."""
    out = {}
    for pmid in ADJUDICATE:
        if pmid not in bodies:
            out[pmid] = {"error": "no connector body retrieved"}
            continue
        clean = fetch_epmc(paper_claims[pmid][0]["pmc"])
        claims = [(c["gene_target"], c["disease"], c["manifestation"]) for c in paper_claims[pmid]]
        reqs = []
        for body in (bodies[pmid], clean):
            for _ in range(repeats):
                reqs.append({"prompt": verdict_prompt(claims, body), "system": VERDICT_SYSTEM,
                             "model": model, "max_tokens": 8000, "thinking": {"type": "disabled"}})
        res = host.llm(reqs, max_concurrency=6)
        got = collections.defaultdict(list)
        for i, r in enumerate(res):
            route = "connector_body" if i < repeats else "clean_jats_europepmc"
            for j in parse_judgements(r.get("text", "")):
                got[(norm(j.get("gene_target")), route)].append(
                    (norm_verdict(j.get("verdict")), j.get("mechanism_from_fulltext", "")))
        out[pmid] = {
            "claims": claims,
            "phase1b_recorded": {c["gene_target"] + " | " + c["manifestation"]: c["phase1b_verdict"]
                                 for c in paper_claims[pmid]},
            "verdicts": {"%s|%s" % k: [v[0] for v in vals] for k, vals in got.items()},
            "label_occurrences": {
                "connector_body": {t: bodies[pmid].count(t)
                                   for c in paper_claims[pmid]
                                   for t in symbol_tokens(c["gene_target"], c["constituent_genes"])},
                "clean_jats": {t: clean.count(t)
                               for c in paper_claims[pmid]
                               for t in symbol_tokens(c["gene_target"], c["constituent_genes"])}}}
    return out


# -- run -----------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--papers", type=int, default=74,
                    help="papers to attempt, in seeded shuffle order (74 reproduces the run)")
    ap.add_argument("--retrieval", choices=["connector", "epmc"], default="connector")
    ap.add_argument("--cache", default=os.path.join(REPO, "phase-7", "work", "bodies"),
                    help="body cache; not committed")
    args = ap.parse_args()

    host = globals().get("host")  # provided by the Claude Science kernels
    if host is None:
        raise SystemExit("needs the Claude Science kernel: host.llm for verification, "
                         "host.mcp for connector retrieval")

    rows, population, paper_claims = build_population()
    papers = sorted(paper_claims)
    import random
    rnd = random.Random(SEED)
    order = papers[:]
    rnd.shuffle(order)
    attempted = [p for p in order if p not in ADJUDICATE][:args.papers]

    os.makedirs(args.cache, exist_ok=True)
    bodies, failures = {}, {}
    for p in attempted + ADJUDICATE:
        path = os.path.join(args.cache, p + ".txt")
        if os.path.exists(path):
            bodies[p] = open(path).read()
            continue
        pmcid = paper_claims[p][0]["pmc"]
        if not pmcid:
            failures[p] = "no_pmcid"
            continue
        try:
            body = fetch_connector(host, pmcid) if args.retrieval == "connector" else fetch_epmc(pmcid)
        except Exception as exc:
            failures[p] = ("err:" + str(exc))[:150]
            continue
        if len(body) < 4000:
            failures[p] = "short_body_%d" % len(body)
            continue
        open(path, "w").write(body)
        bodies[p] = body
    sample_papers = [p for p in attempted if p in bodies]

    model = host.reasoning_model()
    reqs = [{"prompt": verdict_prompt([(c["gene_target"], c["disease"], c["manifestation"])
                                       for c in paper_claims[p]], bodies[p]),
             "system": VERDICT_SYSTEM, "model": model, "max_tokens": 8000,
             "thinking": {"type": "disabled"}} for p in sample_papers]
    run1 = host.llm(reqs, max_concurrency=8)
    run2 = host.llm(reqs, max_concurrency=8)

    recs = []
    for pi, p in enumerate(sample_papers):
        judged = {}
        for ri, run in ((1, run1), (2, run2)):
            by = {}
            for j in parse_judgements(run[pi].get("text", "")):
                by[(norm(j.get("gene_target")), norm(j.get("manifestation")))] = j
                by.setdefault((norm(j.get("gene_target")),), j)
            for c in paper_claims[p]:
                j = by.get((norm(c["gene_target"]), norm(c["manifestation"]))) or \
                    by.get((norm(c["gene_target"]),))
                d = judged.setdefault((c["gene_target"], c["manifestation"]), {})
                d["run%d" % ri] = norm_verdict(j.get("verdict")) if j else "missing"
                d["run%d_mech" % ri] = (j or {}).get("mechanism_from_fulltext", "")
        sig = markup_signature(bodies[p])
        for c in paper_claims[p]:
            toks = symbol_tokens(c["gene_target"], c["constituent_genes"])
            ok_strict, _ = present(bodies[p], toks, lax=False)
            ok_lax, hit = present(bodies[p], toks, lax=True)
            r = dict(c, **judged[(c["gene_target"], c["manifestation"])])
            r.update(symbol_tokens_str=";".join(sorted(toks)), symbol_in_body=ok_strict,
                     symbol_in_body_lax=ok_lax, symbol_matched_lax=hit,
                     paper_markup_signature=sig, body_chars=len(bodies[p]))
            for ri in (1, 2):
                v = r["run%d" % ri]
                r["run%d_guard_voided" % ri] = (v == "not_supported" and not ok_lax)
                r["run%d_final" % ri] = ("voided_markup_guard" if r["run%d_guard_voided" % ri] else v)
            recs.append(r)

    adj = adjudicate(host, paper_claims, bodies, model)
    write_outputs(population, paper_claims, attempted, sample_papers, failures, recs, bodies,
                  model, adj)


def write_outputs(population, paper_claims, attempted, sample_papers, failures, recs, bodies,
                  model, adj):
    os.makedirs(OUT, exist_ok=True)
    fields = ["gene_target", "disease", "manifestation", "pmid", "pmc", "phase1b_verdict",
              "phase1b_verdict_basis", "phase1b_fulltext_source", "body_retrieved", "body_chars",
              "paper_markup_signature", "symbol_tokens", "symbol_in_body", "symbol_in_body_lax",
              "symbol_matched_lax", "run1_verdict", "run2_verdict", "run1_guard_voided",
              "run2_guard_voided", "run1_final", "run2_final", "runs_agree", "runs_agree_binary",
              "run1_agrees_phase1b", "run2_agrees_phase1b", "in_reproduction_population",
              "run1_mechanism", "run2_mechanism"]
    out_rows = []
    for r in sorted(recs, key=lambda r: (r["gene_target"], r["disease"], r["manifestation"], r["pmid"])):
        out_rows.append({
            "gene_target": r["gene_target"], "disease": r["disease"],
            "manifestation": r["manifestation"], "pmid": r["pmid"], "pmc": r["pmc"],
            "phase1b_verdict": r["phase1b_verdict"], "phase1b_verdict_basis": r["phase1b_verdict_basis"],
            "phase1b_fulltext_source": r["phase1b_fulltext_source"], "body_retrieved": True,
            "body_chars": r["body_chars"], "paper_markup_signature": r["paper_markup_signature"],
            "symbol_tokens": r["symbol_tokens_str"], "symbol_in_body": r["symbol_in_body"],
            "symbol_in_body_lax": r["symbol_in_body_lax"], "symbol_matched_lax": r["symbol_matched_lax"],
            "run1_verdict": r["run1"], "run2_verdict": r["run2"],
            "run1_guard_voided": r["run1_guard_voided"], "run2_guard_voided": r["run2_guard_voided"],
            "run1_final": r["run1_final"], "run2_final": r["run2_final"],
            "runs_agree": r["run1"] == r["run2"],
            "runs_agree_binary": binary(r["run1"]) == binary(r["run2"]),
            "run1_agrees_phase1b": (r["run1"] == r["phase1b_verdict"]) if r["phase1b_verdict"] else "",
            "run2_agrees_phase1b": (r["run2"] == r["phase1b_verdict"]) if r["phase1b_verdict"] else "",
            "in_reproduction_population": bool(r["phase1b_verdict"]),
            "run1_mechanism": (r.get("run1_mech") or "")[:300],
            "run2_mechanism": (r.get("run2_mech") or "")[:300]})
    for p in [q for q in attempted if q not in sample_papers]:
        for c in paper_claims[p]:
            row = {k: "" for k in fields}
            row.update(gene_target=c["gene_target"], disease=c["disease"],
                       manifestation=c["manifestation"], pmid=p, pmc=c["pmc"],
                       phase1b_verdict=c["phase1b_verdict"],
                       phase1b_verdict_basis=c["phase1b_verdict_basis"],
                       phase1b_fulltext_source=c["phase1b_fulltext_source"],
                       body_retrieved=False, body_chars=0, in_reproduction_population=False,
                       run1_verdict="no_body", run2_verdict="no_body",
                       run1_final="no_body", run2_final="no_body")
            out_rows.append(row)
    with open(os.path.join(OUT, "phase7-verification-stability.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)

    rng = np.random.default_rng(SEED)
    B = [r for r in recs if r["phase1b_verdict"]]
    a_k = sum(r["run1"] != r["run2"] for r in recs)
    b1 = sum(r["run1"] != r["phase1b_verdict"] for r in B)
    b2 = sum(r["run2"] != r["phase1b_verdict"] for r in B)
    summary = {
        "population": {"claim_pairs_total": len(population), "papers_total": len(paper_claims),
                       "claims_with_deterministic_phase1b_wholebody_verdict":
                           sum(1 for c in population if c["phase1b_verdict"])},
        "sampling": {"seed": SEED, "papers_attempted": len(attempted),
                     "papers_with_body_retrieved": len(sample_papers),
                     "retrieval_failures": failures, "claims_verified": len(recs),
                     "reproduction_subsample_n": len(B)},
        "method": {"model": model, "thinking": "disabled"},
        "self_consistency_run1_vs_run2": {
            "n": len(recs), "disagreements": a_k, "rate": round(a_k / len(recs), 4),
            "wilson95": wilson(a_k, len(recs)),
            "cluster_bootstrap95_by_paper": cluster_boot(recs, lambda r: r["run1"] != r["run2"], rng)},
        "reproduction_of_phase1b": {
            "n": len(B), "run1_disagreements": b1, "run1_rate": round(b1 / len(B), 4),
            "run1_wilson95": wilson(b1, len(B)),
            "run1_cluster_bootstrap95_by_paper":
                cluster_boot(B, lambda r: r["run1"] != r["phase1b_verdict"], rng),
            "run2_disagreements": b2, "run2_rate": round(b2 / len(B), 4),
            "run2_wilson95": wilson(b2, len(B))},
        "markup_guard": {
            "papers_with_markup_loss_signature":
                sum(1 for p in sample_papers if markup_signature(bodies[p]) > 0),
            "papers_sampled": len(sample_papers),
            "claims_label_absent_lax": sum(1 for r in recs if not r["symbol_in_body_lax"]),
            "voided_run1": sum(r["run1_guard_voided"] for r in recs),
            "voided_run2": sum(r["run2_guard_voided"] for r in recs)},
        "adjudications": adj}
    with open(os.path.join(OUT, "phase7-verification-stability-summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary["self_consistency_run1_vs_run2"], indent=1))
    print(json.dumps(summary["reproduction_of_phase1b"], indent=1))
    print(json.dumps(summary["markup_guard"], indent=1))


if __name__ == "__main__":
    main()
