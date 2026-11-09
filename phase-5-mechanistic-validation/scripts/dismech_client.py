"""Access to DisMech (Monarch's Disorder Mechanisms KB) for Phase 5.

THERE IS NO DisMech REST API. DisMech is a curated YAML knowledge base in
github.com/monarch-initiative/dismech (BSD-3), rendered as a static site at
dismech.monarchinitiative.org. Programmatic access is therefore:

  * one disorder          -> GitHub contents API, kb/disorders/<Entry>.yaml
  * whole KB / graph      -> GitHub *release* assets (versioned, ~weekly):
      mondo_emc.tsv        Mondo CURIE -> DisMech page + definition + PMIDs (~6 MB)
      kb.zip               every disorder YAML (~64 MB) - use for mechanism indexing
      dismech_nodes.jsonl  Biolink-typed KGX nodes (~9 MB)
      dismech_edges.jsonl  KGX edges (~220 MB)
      dismech_sepio.jsonl  per-edge evidence sidecar, joins on edge id (~330 MB)

DisMech is NOT in the Monarch KG: /v3/api/association?primary_knowledge_source=
infores:dismech returns 0 in KG 2026-10-07. Monarch and DisMech are two separate
integrations that happen to share Mondo CURIEs as the join key.

Hosts used: api.github.com only (allowlisted). GITHUB_TOKEN is optional but
raises the rate limit from 60 to 5000 requests/hour.
"""
from __future__ import annotations

import csv
import io
import os
import zipfile
from pathlib import Path

import requests
import yaml

REPO = "monarch-initiative/dismech"
# Pin a release: `main` is pushed daily and carries ~200 more disorder YAMLs than
# the latest release, so figures computed off `main` drift day to day.
PINNED_RELEASE = "v0.1.46"  # published 2026-10-29
API = f"https://api.github.com/repos/{REPO}"
CACHE = Path(__file__).resolve().parents[1] / "data"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"Accept": "application/vnd.github+json"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        s.headers["Authorization"] = f"Bearer {tok}"
    return s


class DisMech:
    def __init__(self, release: str | None = PINNED_RELEASE, cache: Path = CACHE):
        """release: a release tag. Pass None for whatever is latest, but then
        record the tag that comes back - the KB changes weekly."""
        self.s = _session()
        self.cache = cache
        self.cache.mkdir(parents=True, exist_ok=True)
        r = self.s.get(f"{API}/releases/tags/{release}" if release else f"{API}/releases/latest",
                       timeout=60)
        r.raise_for_status()
        self.release = r.json()
        self.tag = self.release["tag_name"]
        self._assets = {a["name"]: a for a in self.release["assets"]}

    # --- release assets ---------------------------------------------------
    def asset(self, name: str) -> Path:
        """Download a release asset once into the cache; return its path."""
        dest = self.cache / f"dismech-{self.tag}-{name}"
        if not dest.exists():
            a = self._assets[name]
            r = self.s.get(a["url"], headers={"Accept": "application/octet-stream"},
                           timeout=900, stream=True)
            r.raise_for_status()
            with open(dest, "wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
        return dest

    def mondo_index(self) -> dict[str, dict]:
        """Mondo CURIE -> {label, dismech_url, definition, pmids}. The join key
        between Phase 5's Mondo terms and DisMech entries."""
        with open(self.asset("mondo_emc.tsv"), newline="") as fh:
            return {r["mondo_id"]: r for r in csv.DictReader(fh, delimiter="\t")}

    # --- single disorder --------------------------------------------------
    def disorder(self, entry: str) -> dict:
        """Fetch kb/disorders/<entry>.yaml (entry = 'Neurofibromatosis_Type_1')."""
        r = self.s.get(f"{API}/contents/kb/disorders/{entry}.yaml",
                       headers={"Accept": "application/vnd.github.raw"}, timeout=90)
        r.raise_for_status()
        return yaml.safe_load(r.text)

    def entry_name(self, mondo_curie: str, index: dict | None = None) -> str | None:
        idx = index if index is not None else self.mondo_index()
        row = idx.get(mondo_curie)
        return row["dismech_url"].rsplit("/", 1)[-1][:-5] if row else None

    # --- cross-disease mechanism matching ---------------------------------
    def mechanism_index(self) -> tuple[dict[str, set], dict[str, set]]:
        """Parse every disorder YAML in kb.zip once (~2.5 min, 3.8k files).

        Returns (disorder -> set of GO process CURIEs on its pathophysiology
        nodes, GO CURIE -> set of disorders). Sharing GO terms is a screen, not
        a verdict: judging whether two diseases share a mechanism still needs
        the node descriptions and their quoted evidence.
        """
        import collections
        dis_go, go_dis = {}, collections.defaultdict(set)
        with zipfile.ZipFile(self.asset("kb.zip")) as z:
            for n in z.namelist():
                if "/disorders/" not in n or not n.endswith(".yaml"):
                    continue
                try:
                    d = yaml.safe_load(z.read(n))
                except yaml.YAMLError:
                    continue
                if not isinstance(d, dict):
                    continue
                label = (d.get("disease_term") or {}).get("term", {}).get("label") or d.get("name")
                gos = {
                    (b.get("term") or {}).get("id")
                    for p in (d.get("pathophysiology") or [])
                    for b in (p.get("biological_processes") or [])
                    if (b.get("term") or {}).get("id")
                }
                dis_go[label] = gos
                for g in gos:
                    go_dis[g].add(label)
        return dis_go, dict(go_dis)


# DisMech coverage of the project's disease labels, checked against v0.1.46.
# NF2-related schwannomatosis has NO DisMech entry: MONDO:0007039 is absent from
# mondo_emc.tsv and no NF2 disorder YAML exists; it is mentioned only inside the
# Neurofibromatosis.yaml grouping entry. Its tumour manifestations are covered.
DISMECH_ENTRIES = {
    "NF1": ("MONDO:0018975", "Neurofibromatosis_Type_1"),
    "NF2-SWN": ("MONDO:0007039", None),
    "SWN": ("MONDO:0008075", "Schwannomatosis"),
}
# The Schwannomatosis entry is the SWN evidence source that Monarch lacks: it
# carries "SMARCB1 SWI/SNF Chromatin-Remodeling Dysfunction" and "LZTR1-CUL3
# Substrate Adaptor Dysfunction" pathophysiology nodes plus a CAUSATIVE genetic
# section for both genes. Gene CURIEs are lowercase here ("hgnc:11103") and
# uppercase in Monarch ("HGNC:11103"); normalise case before joining.
MANIFESTATION_ENTRIES = {
    "Vestibular schwannoma": "MONDO:0001569",   # acoustic neuroma
    "Non-vestibular schwannoma": "MONDO:0002546",
    "MPNST": "MONDO:0017827",
    "Cutaneous/Plexiform neurofibroma": "MONDO:0016755",  # neurofibroma (not subtyped)
    "Meningioma": "MONDO:0016642",
    "Ependymoma": "MONDO:0016698",
    "Optic pathway glioma": "MONDO:0016691",    # pilocytic astrocytoma (not OPG-specific)
}

if __name__ == "__main__":
    dm = DisMech()
    print("release:", dm.tag, "| assets:", len(dm._assets))
    idx = dm.mondo_index()
    print("mondo-mapped entries:", len(idx))
    for label, (curie, _) in DISMECH_ENTRIES.items():
        print(f"  {label:10} {curie:16} -> {dm.entry_name(curie, idx) or 'ABSENT'}")
    for label, curie in MANIFESTATION_ENTRIES.items():
        print(f"  {label:34} {curie:16} -> {dm.entry_name(curie, idx) or 'ABSENT'}")
    d = dm.disorder("Neurofibromatosis_Type_1")
    print("\nNF1 entry sections:", list(d))
    print("pathophysiology nodes:", [p["name"] for p in d["pathophysiology"]])
