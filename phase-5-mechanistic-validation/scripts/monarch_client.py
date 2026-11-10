"""Minimal client for the Monarch Initiative v3 REST API (Phase 5).

API host : https://api-v3.monarchinitiative.org   (the pre-2024 Biolink API at
           api.monarchinitiative.org is retired; api-v2 does not exist)
Docs     : https://api-v3.monarchinitiative.org/v3/docs  (OpenAPI: /openapi.json)
Auth     : none. Plain GETs, JSON responses.
Sandbox  : the host must be on the network allowlist
           (request_network_access(domain="api-v3.monarchinitiative.org")).

Every call records the KG release so Phase 5 output can cite a version.
"""
from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://api-v3.monarchinitiative.org/v3/api"
PAGE = 500  # hard maximum the API accepts for `limit`
HUMAN = "NCBITaxon:9606"


class Monarch:
    def __init__(self, base: str = BASE, timeout: int = 60):
        self.base, self.timeout = base, timeout
        self.s = requests.Session()
        self.s.headers.update({"Accept": "application/json"})
        self.s.mount(
            "https://",
            HTTPAdapter(max_retries=Retry(total=4, backoff_factor=1.0,
                                          status_forcelist=[429, 500, 502, 503, 504],
                                          allowed_methods=["GET"])),
        )

    def _get(self, path: str, **params) -> dict:
        r = self.s.get(f"{self.base}{path}", params=params, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def _paged(self, path: str, **params) -> list[dict]:
        """Walk every page. The API caps `limit` at 500 (per its own openapi.json)
        and silently returns a truncated page above that, so anything that can
        exceed 500 edges must page rather than ask for more."""
        items: list[dict] = []
        offset = 0
        while True:
            r = self._get(path, limit=PAGE, offset=offset, **params)
            batch = r.get("items", [])
            items.extend(batch)
            total = r.get("total", len(items))
            offset += PAGE
            if not batch or offset >= total:
                return items

    # --- provenance -------------------------------------------------------
    def version(self) -> dict:
        """KG release date + API version — cite this with any Phase 5 result."""
        return self._get("/version")

    def sources(self) -> dict:
        """Per-source ingest versions behind the current KG release."""
        return self._get("/sources/versions")

    # --- term grounding ---------------------------------------------------
    def search(self, q: str, category: str | None = None, limit: int = 10, **kw) -> list[dict]:
        return self._get("/search", q=q, category=category, limit=limit, **kw)["items"]

    def resolve_disease(self, label: str) -> list[tuple[str, str]]:
        """Label -> candidate Mondo CURIEs. Review the list; do not auto-take [0]."""
        return [(i["id"], i["name"]) for i in self.search(label, "biolink:Disease")]

    def resolve_gene(self, symbol: str) -> tuple[str, str] | None:
        """HGNC symbol -> ('HGNC:nnnn', symbol), exact human match only."""
        for i in self.search(symbol, "biolink:Gene", limit=20, in_taxon=HUMAN):
            if i["id"].startswith("HGNC:") and i["name"].upper() == symbol.upper():
                return i["id"], i["name"]
        return None

    def mappings(self, curie: str, limit: int = 50) -> list[tuple[str, str]]:
        """Cross-references (OMIM, Orphanet, MeSH, UMLS, ...) for a Mondo term."""
        return [(m["object_id"], m["predicate_id"])
                for m in self._get("/mappings", entity_id=curie, limit=limit)["items"]]

    # --- associations -----------------------------------------------------
    def associations(self, *, subject=None, object=None, category=None,
                     limit: int = 100, **kw) -> dict:
        """Raw /association call. Pass Biolink CURIEs; returns {total, items, ...}."""
        return self._get("/association", subject=subject, object=object,
                         category=category, limit=limit, **kw)

    def gene_diseases(self, gene_curie: str) -> list[dict]:
        """Diseases this gene is asserted to cause (ground-truth check)."""
        items = self._paged("/association", subject=gene_curie,
                            category="biolink:CausalGeneToDiseaseAssociation")
        return [{"disease": a["object"], "label": a["object_label"],
                 "predicate": a["predicate"],
                 "source": a.get("primary_knowledge_source")} for a in items]

    def disease_genes(self, mondo_curie: str) -> list[dict]:
        items = self._paged("/association", object=mondo_curie,
                            category="biolink:CausalGeneToDiseaseAssociation")
        return [{"gene": a["subject"], "label": a["subject_label"],
                 "source": a.get("primary_knowledge_source")} for a in items]

    def gene_phenotypes(self, gene_curie: str) -> list[dict]:
        items = self._paged("/association", subject=gene_curie,
                            category="biolink:GeneToPhenotypicFeatureAssociation")
        return [{"hpo": a["object"], "label": a["object_label"],
                 "source": a.get("primary_knowledge_source")} for a in items]

    def disease_phenotypes(self, mondo_curie: str) -> list[dict]:
        """HPO profile of a disease — the hook for manifestation labelling."""
        items = self._paged(f"/entity/{mondo_curie}/biolink:DiseaseToPhenotypicFeatureAssociation")
        return [{"hpo": a["object"], "label": a["object_label"],
                 "source": a.get("primary_knowledge_source")} for a in items]


# Mondo terms for the project's three disease labels, verified against the live API.
NF_DISEASES = {
    "NF1": "MONDO:0018975",      # neurofibromatosis type 1
    "NF2-SWN": "MONDO:0007039",  # NF2-related schwannomatosis
    "SWN": "MONDO:0008075",      # schwannomatosis (grouping term)
}

# MONDO:0008075 is a grouping class: in KG 2026-10-07 its only causal-gene edge is
# NF2. The molecularly defined SWN subtypes carry SMARCB1/LZTR1 and must be queried
# separately or the SWN ground-truth check misses them.
SWN_SUBTYPES = {
    "SWN-SMARCB1": "MONDO:0024517",  # SMARCB1-related schwannomatosis
    "SWN-LZTR1": "MONDO:0014299",    # LZTR1-related schwannomatosis
    "SWN-22q": "MONDO:1030016",      # 22q-related schwannomatosis
}

if __name__ == "__main__":
    m = Monarch()
    v = m.version()
    print(f"KG {v['monarch_kg_version']} / API {v['monarch_api_version']}")
    for label, curie in NF_DISEASES.items():
        genes = m.disease_genes(curie)
        print(f"{label:12} {curie:16} causal genes={sorted({g['label'] for g in genes})} "
              f"phenotypes={len(m.disease_phenotypes(curie))}")
    for label, curie in SWN_SUBTYPES.items():
        genes = m.disease_genes(curie)
        print(f"{label:12} {curie:16} causal genes={sorted({g['label'] for g in genes})} "
              f"phenotypes={len(m.disease_phenotypes(curie))}")
    nf1 = m.resolve_gene("NF1")
    print("resolve_gene('NF1') ->", nf1)
    print("NF1 gene->disease:", [(d['label'], d['source']) for d in m.gene_diseases(nf1[0])])
