#!/usr/bin/env python3
"""Phase 5, DisMech pass: per-stratum disease mechanism context and a
cross-disease screen for the same mechanism in other rare diseases.

Pinned to a DisMech release (see dismech_client.PINNED_RELEASE), because `main`
is pushed daily and carries more disorder YAMLs than the latest release.

Two honest limits recorded in the outputs rather than papered over:
  * DisMech annotates driver genes only, roughly one gene per disorder, so
    gene-level overlap with a 1,930-gene candidate list is expected to be a
    handful of rows. The per-candidate evidence in Phase 5 comes from Monarch;
    DisMech supplies mechanism context for the stratum.
  * Several strata share one entry, one maps only approximately, and one has no
    entry of its own. Each row carries `entry_role` saying which case it is.

Usage:
  python phase5_dismech.py --builddir build/phase5 --datadir <phase>/data
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
import zipfile
from pathlib import Path

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dismech_client import DisMech  # noqa: E402

# (disease, manifestation) -> [(entry, entry_role)]
#   manifestation        : an entry for this manifestation itself
#   disease              : the disease entry, for mechanism not specific to one tumour
#   shared_unsubtyped    : one entry serving several manifestations (Neurofibroma)
#   approximate          : nearest available entry, not manifestation-specific
#   cross_disease_borrow : node from a DIFFERENT disease's entry; never direct support
STRATUM_ENTRIES = {
    ("NF1", "Malignant peripheral nerve sheath tumor (MPNST)"): [
        ("Malignant_Peripheral_Nerve_Sheath_Tumor", "manifestation"),
        ("Neurofibromatosis_Type_1", "disease")],
    ("NF1", "Plexiform neurofibroma"): [
        ("Neurofibroma", "shared_unsubtyped"), ("Neurofibromatosis_Type_1", "disease")],
    ("NF1", "Cutaneous neurofibroma"): [
        ("Neurofibroma", "shared_unsubtyped"), ("Neurofibromatosis_Type_1", "disease")],
    ("NF1", "ANNUBP / atypical neurofibroma"): [
        ("Neurofibroma", "shared_unsubtyped"), ("Neurofibromatosis_Type_1", "disease")],
    ("NF1", "Optic pathway glioma"): [
        ("Pilocytic_Astrocytoma", "approximate"), ("Neurofibromatosis_Type_1", "disease")],
    ("NF1", "Bone defects"): [("Neurofibromatosis_Type_1", "disease")],
    ("NF2-SWN", "Vestibular schwannoma"): [("Acoustic_Neuroma", "manifestation")],
    ("NF2-SWN", "Non-vestibular schwannoma"): [("Schwannoma", "manifestation")],
    ("NF2-SWN", "Pain"): [("Schwannomatosis", "cross_disease_borrow")],
}


def norm(curie: str | None) -> str | None:
    """DisMech writes hgnc:7765, Monarch writes HGNC:7765."""
    if not curie or ":" not in curie:
        return curie
    pre, local = curie.split(":", 1)
    return f"{pre.upper()}:{local}"


def node_rows(entry: str, doc: dict) -> list[dict]:
    rows = []
    for node in doc.get("pathophysiology") or []:
        ev = node.get("evidence") or []
        rows.append({
            "entry": entry,
            "node": node.get("name"),
            "conforms_to": node.get("conforms_to"),
            "description": node.get("description"),
            "go_terms": "|".join(sorted({(b.get("term") or {}).get("id", "")
                                         for b in node.get("biological_processes") or []} - {""})),
            "go_labels": "|".join((b.get("term") or {}).get("label", "")
                                  for b in node.get("biological_processes") or []),
            "go_modifiers": "|".join(b.get("modifier") or "" for b in node.get("biological_processes") or []),
            "genes": "|".join(sorted({norm((g.get("term") or {}).get("id"))
                                      for g in node.get("genes") or [] if (g.get("term") or {}).get("id")})),
            "gene_labels": "|".join(sorted({(g.get("term") or {}).get("label", "")
                                            for g in node.get("genes") or []} - {""})),
            "downstream": "|".join(d.get("target", "") for d in node.get("downstream") or []),
            "n_evidence": len(ev),
            "evidence_refs": "|".join(e.get("reference", "") for e in ev),
            "evidence_snippet": (ev[0].get("snippet") if ev else None),
        })
    return rows


def genetic_rows(entry: str, doc: dict) -> list[dict]:
    rows = []
    for g in doc.get("genetic") or []:
        term = (g.get("gene_term") or {}).get("term") or {}
        ev = g.get("evidence") or []
        rows.append({"entry": entry, "gene_curie": norm(term.get("id")), "gene_label": term.get("label"),
                     "association": g.get("association"),
                     "relationship_type": g.get("relationship_type"),
                     "n_evidence": len(ev),
                     "evidence_refs": "|".join(e.get("reference", "") for e in ev)})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--builddir", default="build/phase5")
    ap.add_argument("--datadir", default="phase-5-mechanistic-validation/data")
    args = ap.parse_args()
    build, data = Path(args.builddir), Path(args.datadir)
    data.mkdir(parents=True, exist_ok=True)

    dm = DisMech(cache=build)
    print("DisMech release", dm.tag, flush=True)
    mondo_idx = dm.mondo_index()

    entries = sorted({e for v in STRATUM_ENTRIES.values() for e, _ in v})
    docs = {e: dm.disorder(e) for e in entries}
    print("entries fetched:", len(docs), flush=True)

    # 1. mechanism nodes, with the stratum mapping attached
    nodes = pd.DataFrame([r for e, d in docs.items() for r in node_rows(e, d)])
    smap = pd.DataFrame([{"disease": dis, "manifestation": man, "entry": e, "entry_role": role}
                         for (dis, man), v in STRATUM_ENTRIES.items() for e, role in v])
    mech = smap.merge(nodes, on="entry", how="left")
    mech.to_csv(data / "phase5-dismech-mechanisms.csv", index=False)

    gen = pd.DataFrame([r for e, d in docs.items() for r in genetic_rows(e, d)])
    gen.to_csv(data / "phase5-dismech-genetic.csv", index=False)

    # 2. gene-level overlap with the candidate list, per stratum
    dossier = pd.read_csv(build / "phase4-target-dossier.csv")
    ident = pd.read_csv(build / "phase4-identifiers.csv")[["gene_symbol", "resolved_symbol"]]
    dismech_genes = collections.defaultdict(set)   # entry -> {gene label upper}
    for e, d in docs.items():
        for node in d.get("pathophysiology") or []:
            for g in node.get("genes") or []:
                lab = (g.get("term") or {}).get("label")
                if lab:
                    dismech_genes[e].add(lab.upper())
        for g in d.get("genetic") or []:
            lab = ((g.get("gene_term") or {}).get("term") or {}).get("label")
            if lab:
                dismech_genes[e].add(lab.upper())
    hits = []
    for (dis, man), v in STRATUM_ENTRIES.items():
        sub = dossier[(dossier.disease == dis) & (dossier.manifestation == man)]
        for e, role in v:
            for sym in sorted(set(sub.gene_symbol.dropna())):
                if sym.upper() in dismech_genes[e]:
                    hits.append({"disease": dis, "manifestation": man, "gene_symbol": sym,
                                 "entry": e, "entry_role": role})
    pd.DataFrame(hits).to_csv(data / "phase5-dismech-gene-overlap.csv", index=False)

    # 3. cross-disease screen: which other disorders carry the same GO processes
    dis_go, go_dis = {}, collections.defaultdict(set)
    with zipfile.ZipFile(dm.asset("kb.zip")) as z:
        names = [n for n in z.namelist() if "/disorders/" in n and n.endswith(".yaml")]
        for n in names:
            try:
                d = yaml.safe_load(z.read(n))
            except yaml.YAMLError:
                continue
            if not isinstance(d, dict):
                continue
            label = (d.get("disease_term") or {}).get("term", {}).get("label") or d.get("name")
            gos = {(b.get("term") or {}).get("id")
                   for p in (d.get("pathophysiology") or [])
                   for b in (p.get("biological_processes") or [])
                   if (b.get("term") or {}).get("id")}
            dis_go[label] = gos
            for g in gos:
                go_dis[g].add(label)
    print(f"indexed {len(dis_go)} disorders, {len(go_dis)} GO process terms", flush=True)

    own = {(d.get("disease_term") or {}).get("term", {}).get("label") or d.get("name")
           for d in docs.values()}
    cross = []
    for _, r in mech.dropna(subset=["node"]).iterrows():
        terms = [t for t in str(r["go_terms"]).split("|") if t]
        if not terms:
            continue
        shared = collections.Counter()
        for t in terms:
            for other in go_dis.get(t, set()):
                if other not in own:
                    shared[other] += 1
        for other, c in shared.most_common():
            cross.append({"disease": r["disease"], "manifestation": r["manifestation"],
                          "entry": r["entry"], "entry_role": r["entry_role"], "node": r["node"],
                          "n_node_go_terms": len(terms), "other_disorder": other,
                          "n_shared_go_terms": c,
                          "shared_go_terms": "|".join(sorted(set(terms) & dis_go.get(other, set())))})
    cross_df = pd.DataFrame(cross).sort_values(
        ["disease", "manifestation", "node", "n_shared_go_terms"], ascending=[True, True, True, False])
    cross_df.to_csv(data / "phase5-cross-disease-mechanisms.csv.gz", index=False)

    json.dump({"dismech_release": dm.tag,
               "dismech_release_published": dm.release.get("published_at"),
               "entries_fetched": entries,
               "strata_mapped": len(STRATUM_ENTRIES),
               "mondo_mapped_entries": len(mondo_idx),
               "n_mechanism_nodes": int(nodes.shape[0]),
               "n_genetic_rows": int(gen.shape[0]),
               "n_gene_overlap_rows": len(hits),
               "n_disorders_indexed": len(dis_go),
               "n_go_process_terms": len(go_dis),
               "n_cross_disease_rows": int(cross_df.shape[0])},
              open(build / "phase5-dismech-summary.json", "w"), indent=2)
    print("mechanism nodes:", len(nodes), "| gene overlap rows:", len(hits),
          "| cross-disease rows:", len(cross_df), flush=True)


if __name__ == "__main__":
    main()
