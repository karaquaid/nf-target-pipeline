"""Phase 2 ingestion: fetch, assemble and test one launch-set dataset at a time.

Implements phase-2/docs/phase2-pipeline-spec.md. For each dataset this script resolves the
sample membership and contrast arms from the committed tables, downloads the archive files
into build/phase2/<accession>/ (outside the repo), writes the sample table, hands the
normalization and differential expression to phase-2/scripts/phase2_de.R, and appends one
row to the ingestion manifest.

Nothing here decides biology. Membership comes from phase2-sample-overrides.csv (GEO) and
phase2-non-geo-samples.csv (ArrayExpress), arms from their de_arm column, the reference arm
and effect type from the decisions block of phase2-review-diagnosis.json, and which datasets
produce a ranking at all from the pipeline_role column of phase2-launchset-readiness.csv.
A dataset whose inputs disagree with those files is reported, never patched in passing.

Usage, from the repo root:
    python phase-2/scripts/phase2_ingest.py --accession GSE163071
    python phase-2/scripts/phase2_ingest.py --all --skip-existing
    python phase-2/scripts/phase2_ingest.py --accession GSE41747 --combat batch
Options:
    --no-download   use files already in build/phase2/<accession>/
    --dry-run       resolve the design and write the sample table, skip R
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import os
import subprocess
import sys
import tarfile
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "phase-2" / "data"
READINESS = DATA / "phase2-launchset-readiness.csv"
OVERRIDES = DATA / "phase2-sample-overrides.csv"
NON_GEO = DATA / "phase2-non-geo-samples.csv"
DIAGNOSIS = DATA / "phase2-review-diagnosis.json"
PHASE1A_SAMPLES = ROOT / "phase-1a" / "data" / "phase1a-samples.csv"
MANIFEST = DATA / "phase2-ingestion-manifest.csv"
ENSEMBL_RELEASE = "113"   # pinned by ratified call 3; rebuild maps with phase2_build_idmap.py
TX2GENE = DATA / f"ensembl-{ENSEMBL_RELEASE}-tx2gene.tsv.gz"
GENE2SYMBOL = DATA / f"ensembl-{ENSEMBL_RELEASE}-gene2symbol.tsv.gz"
PLATFORM_CACHE = ROOT / "build" / "phase2" / "_platforms"
BUILD = ROOT / "build" / "phase2"
R_WORKER = ROOT / "phase-2" / "scripts" / "phase2_de.R"

GEO_FTP = "https://ftp.ncbi.nlm.nih.gov/geo"
GEO_ACC = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"
BIOSTUDIES_FILES = "https://www.ebi.ac.uk/biostudies/api/v1/studies/{acc}/files"
# www.ebi.ac.uk/biostudies/files/<acc>/<name> returns 404; the FIRE path serves the bytes.
BIOSTUDIES_FIRE = "https://ftp.ebi.ac.uk/biostudies/fire/{stem}/{tail}/{acc}/Files/{name}"
HREF = re.compile(r'<a href="([^"/][^"]*)">')

# Which engine each dataset goes through. Ratified 2026-10-19, panel route 2026-10-20;
# see the Phase 2 section of docs/project-plan.md for why each was chosen.
ENGINE_BY_ASSAY = {
    "expression_array": "limma_trend",
    "bulk_rnaseq": "deseq2",
    "single_cell_rnaseq": "pseudobulk_limma_trend",
}
PANEL_ENGINE = "nanostring_housekeeping_limma"
PROCESSED_ENGINE = "author_matrix_limma_trend"

# Arms are recorded per sample for most datasets. Where they are not, the contrast is the
# Phase 1a case/control split and these labels name the two sides.
LABEL_ARMS = {"nf_case_tumor": "nf_case", "nf_case_nontumor": "nf_case",
              "control_matched_adjacent_normal": "control", "control_unaffected_donor_normal": "control",
              "control_isogenic_engineered": "control", "treated_or_perturbed": "treated"}


def truthy(series):
    return series.astype(str).str.lower().eq("true")


def stem(accession: str) -> str:
    kind, digits = re.match(r"([A-Z]+)(\d+)", accession).groups()
    return f"{kind}{digits[:-3]}nnn" if len(digits) > 3 else f"{kind}nnn"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def gsm_keys(accession: str, cache_dir: Path) -> pd.DataFrame:
    """Per-sample title and description from the series SOFT header.

    Submitters routinely name the columns of a deposited matrix by an internal id that
    appears only in Sample_description (GSE163071's matrix is keyed on Lb3303 and the like),
    so the sample table carries that field as a third matching key.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = cache_dir / f"{accession}_gsm_soft.txt"
    if not cache.exists():
        time.sleep(0.34)
        r = requests.get(GEO_ACC, params={"acc": accession, "targ": "gsm", "form": "text", "view": "brief"},
                         timeout=600)
        r.raise_for_status()
        cache.write_text(r.text)
    rows, current = [], {}
    for line in cache.read_text().splitlines():
        if line.startswith("^SAMPLE"):
            if current:
                rows.append(current)
            current = {"sample_id": line.split("=", 1)[1].strip(), "soft_title": "", "description": ""}
        elif line.startswith("!Sample_title") and current:
            current["soft_title"] = line.split("=", 1)[1].strip()
        elif line.startswith("!Sample_description") and current and not current["description"]:
            current["description"] = line.split("=", 1)[1].strip()
    if current:
        rows.append(current)
    return pd.DataFrame(rows)


class Dataset:
    """Everything the pipeline knows about one launch-set dataset, from the committed files."""

    def __init__(self, accession: str):
        readiness = pd.read_csv(READINESS)
        row = readiness[readiness.accession == accession]
        if row.empty:
            raise SystemExit(f"{accession} is not in the launch set ({READINESS.name})")
        self.row = row.iloc[0]
        self.accession = accession
        self.source = self.row.source
        self.decision = json.loads(DIAGNOSIS.read_text())["decisions"].get(accession, {})
        self.dir = BUILD / accession
        self.samples = self._samples()
        if self.source != "ArrayExpress":
            keys = gsm_keys(accession, self.dir)
            self.samples = self.samples.merge(keys, on="sample_id", how="left")
            self.samples[["soft_title", "description"]] = self.samples[["soft_title", "description"]].fillna("")
        self._apply_patient_rule()
        self.engine = self._engine()

    # ---- design -------------------------------------------------------------
    def _samples(self) -> pd.DataFrame:
        if self.source == "ArrayExpress":
            non_geo = pd.read_csv(NON_GEO, keep_default_na=False)
            mine = non_geo[(non_geo.series == self.accession) & truthy(non_geo.use_in_phase2)]
            if mine.empty:
                raise SystemExit(f"{self.accession}: no usable rows in {NON_GEO.name}")
            return pd.DataFrame({
                "sample_id": mine.sample_name.astype(str) + "|" + mine.channel.astype(str),
                "title": mine.sample_name, "file": mine.array_data_file, "channel": mine.channel,
                "de_role": mine.de_role, "de_arm": mine.de_arm,
                "patient_id": mine.get("patient_id", ""), "batch": mine.get("hybridization", ""),
            })
        overrides = pd.read_csv(OVERRIDES, keep_default_na=False)
        mine = overrides[(overrides.series == self.accession) & truthy(overrides.use_in_phase2)]
        if not mine.empty:
            arms = mine.de_arm.replace("", pd.NA)
            if arms.isna().all():
                raise SystemExit(f"{self.accession}: override rows carry no de_arm; run the backfill first")
            return pd.DataFrame({"sample_id": mine.sample_id, "title": mine.title,
                                 "file": "", "channel": "",
                                 "de_role": mine.de_role, "de_arm": arms,
                                 "patient_id": "", "batch": ""})
        # No overrides: the frozen Phase 1a labels stand, and the arm is the case/control split.
        phase1a = pd.read_csv(PHASE1A_SAMPLES)
        mine = phase1a[(phase1a.series == self.accession) & truthy(phase1a.in_scope_sample)
                       & (phase1a.organism == "Homo sapiens")]
        if mine.empty:
            raise SystemExit(f"{self.accession}: no in-scope human samples in {PHASE1A_SAMPLES.name}")
        arms = mine.label.map(LABEL_ARMS)
        if arms.isna().any():
            raise SystemExit(f"{self.accession}: labels with no arm mapping: "
                             f"{sorted(set(mine.label[arms.isna()]))}")
        return pd.DataFrame({"sample_id": mine.gsm, "title": mine.title, "file": "", "channel": "",
                             "de_role": mine.label, "de_arm": arms.values,
                             "patient_id": "", "batch": ""})

    def _apply_patient_rule(self) -> None:
        """Pseudobulk is per patient (spec call 6), so the rule for recovering the patient
        from a sample title is declared per dataset in the decisions block, never inferred."""
        rule = self.decision.get("patient_rule")
        if not rule:
            return
        titles = self.samples.get("title", pd.Series("", index=self.samples.index)).astype(str)
        if "soft_title" in self.samples.columns:
            titles = titles.where(titles.str.len() > 0, self.samples.soft_title.astype(str))
        extracted = titles.str.extract(rule, expand=False)
        if extracted.isna().any():
            raise SystemExit(f"{self.accession}: patient_rule {rule!r} did not match "
                             f"{int(extracted.isna().sum())} of {len(extracted)} titles, e.g. "
                             f"{titles[extracted.isna()].head(3).tolist()}")
        self.samples["patient_id"] = extracted.values

    def _engine(self) -> str:
        if bool(self.row.get("targeted_panel", False)):
            return PANEL_ENGINE
        if self.row.data_availability == "processed_matrix_only":
            return ("pseudobulk_author_matrix" if self.row.assay_class == "single_cell_rnaseq"
                    else PROCESSED_ENGINE)
        if self.source == "ArrayExpress":
            return "two_colour_limma"
        engine = ENGINE_BY_ASSAY.get(self.row.assay_class)
        if engine is None:
            raise SystemExit(f"{self.accession}: no engine for assay_class {self.row.assay_class!r}")
        return engine

    @property
    def reference_arm(self) -> str:
        """The arm every other arm is compared against.

        A control arm is the reference wherever one exists. Otherwise the baseline is a
        scientific choice, not something to infer from arm sizes, so it must be declared as
        reference_arm in the decisions block; the pipeline refuses to guess.
        """
        controls = self.samples.loc[self.samples.de_role.astype(str).str.startswith("control"), "de_arm"]
        if len(controls):
            return controls.iloc[0]
        declared = self.decision.get("reference_arm")
        if not declared:
            raise SystemExit(
                f"{self.accession}: no control arm and no reference_arm in the decisions block. "
                f"Add one for this dataset (arms present: {sorted(self.samples.de_arm.unique())}); "
                f"the baseline of a between-state contrast is a curation decision, not a default")
        if declared not in set(self.samples.de_arm):
            raise SystemExit(f"{self.accession}: declared reference_arm {declared!r} is not among the arms "
                             f"{sorted(self.samples.de_arm.unique())}")
        return declared

    @property
    def effect_type(self) -> str:
        return ("disease_vs_normal"
                if self.samples.de_role.astype(str).str.startswith("control").any()
                else "between_state")

    @property
    def gene_space(self) -> str:
        return "panel:770" if self.engine == PANEL_ENGINE else "transcriptome"

    @property
    def produces_ranking(self) -> bool:
        return self.row.pipeline_role == "ranked"

    # ---- fetch --------------------------------------------------------------
    def download(self) -> list[dict]:
        self.dir.mkdir(parents=True, exist_ok=True)
        files = self._fetch_arrayexpress() if self.source == "ArrayExpress" else self._fetch_geo()
        if not files:
            raise SystemExit(f"{self.accession}: no files downloaded; the raw-file check said they resolve, "
                             f"so investigate before proceeding")
        for tar in [f for f in self.dir.glob("*_RAW.tar")]:
            with tarfile.open(tar) as t:
                t.extractall(self.dir / "raw", filter="data")
        return files

    def _get(self, url: str, dest: Path) -> dict:
        if dest.exists():
            return {"name": dest.name, "bytes": dest.stat().st_size, "sha256": sha256(dest), "url": url,
                    "reused": True}
        time.sleep(0.34)
        with requests.get(url, stream=True, timeout=600) as r:
            r.raise_for_status()
            with dest.open("wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
        return {"name": dest.name, "bytes": dest.stat().st_size, "sha256": sha256(dest), "url": url,
                "reused": False}

    def _fetch_geo(self) -> list[dict]:
        base = f"{GEO_FTP}/series/{stem(self.accession)}/{self.accession}/suppl/"
        listing = requests.get(base, timeout=120)
        listing.raise_for_status()
        names = [n for n in HREF.findall(listing.text) if not n.endswith("/") and "://" not in n]
        return [self._get(base + n, self.dir / n) for n in names if n != "filelist.txt"]

    def _fetch_arrayexpress(self) -> list[dict]:
        items = requests.get(BIOSTUDIES_FILES.format(acc=self.accession), timeout=120).json()["items"]
        wanted = set(self.samples.file) | {f"{self.accession}.sdrf.txt", f"{self.accession}.idf.txt"}
        kind, digits = re.match(r"([A-Z]+)-([A-Z]+)-(\d+)", self.accession).groups()[:2], self.accession.split("-")[-1]
        prefix = "-".join(self.accession.split("-")[:2]) + "-"
        out = []
        for item in items:
            name = item.get("path", "")
            if name not in wanted:
                continue
            url = BIOSTUDIES_FIRE.format(stem=prefix, tail=digits, acc=self.accession, name=name)
            out.append(self._get(url, self.dir / name))
        return out


def id_kind(ids: pd.Series) -> str:
    """What the rows of a result file are keyed on. Decided from the ids themselves,
    because the same assay class appears with different identifier spaces."""
    sample = ids.astype(str).head(200)
    if sample.str.startswith("ENST").mean() > 0.5:
        return "ensembl_transcript"
    if sample.str.startswith("ENSG").mean() > 0.5:
        return "ensembl_gene"
    if (sample.str.contains("_at$|_x_at$|_s_at$", regex=True) | sample.str.startswith(("TC", "PSR", "JUC"))).mean() > 0.5:
        return "affy_probe"
    return "symbol"


def platform_table(gpl: str) -> pd.DataFrame:
    """The GEO platform annotation table, cached. Array probe ids are platform-specific,
    so Ensembl cannot map them; the archive's own table is the authority."""
    PLATFORM_CACHE.mkdir(parents=True, exist_ok=True)
    cache = PLATFORM_CACHE / f"{gpl}.tsv.gz"
    if not cache.exists():
        time.sleep(0.34)
        r = requests.get(GEO_ACC, params={"acc": gpl, "targ": "self", "form": "text", "view": "data"},
                         timeout=900)
        r.raise_for_status()
        lines = r.text.splitlines()
        start = next(i for i, line in enumerate(lines) if line.startswith("ID\t"))
        import gzip as _gzip
        with _gzip.open(cache, "wt") as fh:
            fh.write("\n".join(lines[start:]))
    table = pd.read_csv(cache, sep="\t", dtype=str, low_memory=False)
    symbol_cols = [c for c in table.columns
                   if c.lower() in ("gene symbol", "gene_symbol", "symbol", "gene")]
    if symbol_cols:
        out = table[["ID", symbol_cols[0]]].rename(columns={symbol_cols[0]: "gene_symbol"})
    elif "gene_assignment" in [c.lower() for c in table.columns]:
        col = [c for c in table.columns if c.lower() == "gene_assignment"][0]
        # gene_assignment packs several "accession // symbol // description" records per probe.
        out = pd.DataFrame({"ID": table["ID"],
                            "gene_symbol": table[col].fillna("").str.split("//").str[1].str.strip()})
    else:
        raise SystemExit(f"{gpl}: no gene symbol column in the platform table "
                         f"(columns: {list(table.columns)[:12]})")
    out = out.rename(columns={"ID": "source_id"})
    out["gene_symbol"] = out.gene_symbol.fillna("").replace({"---": "", "nan": ""})
    return out[out.source_id.notna()]


def map_identifiers(ds: Dataset, de_path: Path) -> dict:
    """Add gene_symbol and source_id to a ranked list, per ratified call 3.

    The original id is never discarded, and rows that do not map keep an empty symbol and
    are counted in the manifest rather than dropped: Phase 3 needs to know how much of a
    dataset's ranking is addressable by symbol.
    """
    de = pd.read_csv(de_path)
    de = de.rename(columns={"gene_symbol": "source_id"}) if "source_id" not in de.columns else de
    kind = id_kind(de.source_id)
    if kind == "symbol":
        de["gene_symbol"] = de.source_id
        mapped_from = "already HGNC symbols as deposited"
    elif kind in ("ensembl_transcript", "ensembl_gene"):
        table = pd.read_csv(TX2GENE if kind == "ensembl_transcript" else GENE2SYMBOL, sep="\t", dtype=str)
        key = "transcript_id" if kind == "ensembl_transcript" else "gene_id"
        lookup = dict(zip(table[key], table.gene_symbol.fillna("")))
        stripped = de.source_id.astype(str).str.replace(r"\.\d+$", "", regex=True)
        de["gene_symbol"] = stripped.map(lookup).fillna("")
        mapped_from = f"Ensembl release {ENSEMBL_RELEASE} ({key})"
    else:
        gpl = str(ds.row.platforms).split(";")[0]
        lookup = platform_table(gpl)
        de = de.merge(lookup.drop_duplicates("source_id"), on="source_id", how="left")
        de["gene_symbol"] = de.gene_symbol.fillna("")
        mapped_from = f"GEO platform table {gpl}"
    columns = ["gene_symbol", "source_id"] + [c for c in de.columns if c not in ("gene_symbol", "source_id")]
    de[columns].to_csv(de_path, index=False)
    mapped = int((de.gene_symbol.astype(str).str.len() > 0).sum())
    print(f"  identifiers: {kind}, {mapped} of {len(de)} rows carry a symbol via {mapped_from}")
    return {"id_kind": kind, "id_map_source": mapped_from,
            "rows_total": len(de), "rows_with_symbol": mapped,
            "symbols_distinct": int(de.loc[de.gene_symbol.astype(str).str.len() > 0, "gene_symbol"].nunique())}


def write_sample_table(ds: Dataset) -> Path:
    out = ds.dir / f"{ds.accession}_samples.csv"
    table = ds.samples.copy()
    table.insert(0, "accession", ds.accession)
    table["is_reference_arm"] = table.de_arm == ds.reference_arm
    table.to_csv(out, index=False)
    return out


def run_r(ds: Dataset, sample_table: Path, combat: str | None, rscript: str = "Rscript",
          rlibs: str = "") -> Path:
    de_path = ds.dir / f"{ds.accession}_de.csv"
    cmd = [rscript, str(R_WORKER), "--accession", ds.accession, "--engine", ds.engine,
           "--indir", str(ds.dir), "--samples", str(sample_table), "--reference", ds.reference_arm,
           "--out", str(de_path)]
    if combat:
        cmd += ["--combat", combat]
    print("  " + " ".join(cmd[:6]) + " ...")
    env = dict(os.environ)
    if rlibs:
        env["R_LIBS_USER"] = rlibs
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    sys.stdout.write(result.stdout[-4000:])
    if result.returncode != 0:
        sys.stderr.write(result.stderr[-4000:])
        raise SystemExit(f"{ds.accession}: {R_WORKER.name} failed with exit {result.returncode}")
    return de_path


def append_manifest(ds: Dataset, files: list[dict], de_path: Path | None, combat: str | None, notes: str,
                    mapping: dict | None = None) -> None:
    arms = ds.samples.de_arm.value_counts().to_dict()
    row = {
        "accession": ds.accession, "source": ds.source, "assay_class": ds.row.assay_class,
        "engine": ds.engine, "pipeline_role": ds.row.pipeline_role,
        "reference_arm": ds.reference_arm, "effect_type": ds.effect_type, "gene_space": ds.gene_space,
        "n_samples": len(ds.samples), "n_per_arm": ";".join(f"{k}:{v}" for k, v in arms.items()),
        "combat_covariate": combat or "",
        "combat_status": ("applied" if combat else "not applied: no populated covariate requested"),
        "raw_files": ";".join(f["name"] for f in files),
        "raw_bytes": sum(f["bytes"] for f in files),
        "raw_sha256": ";".join(f"{f['name']}={f['sha256'][:16]}" for f in files),
        "de_file": de_path.name if de_path else "",
        "normalization": ("author-provided, not reproduced" if ds.engine == PROCESSED_ENGINE
                          else "computed by phase2_de.R"),
        "id_kind": (mapping or {}).get("id_kind", ""),
        "id_map_source": (mapping or {}).get("id_map_source", ""),
        "rows_total": (mapping or {}).get("rows_total", ""),
        "rows_with_symbol": (mapping or {}).get("rows_with_symbol", ""),
        "symbols_distinct": (mapping or {}).get("symbols_distinct", ""),
        "notes": notes, "run_date": time.strftime("%Y-%m-%d"),
    }
    frame = pd.DataFrame([row])
    if MANIFEST.exists():
        prior = pd.read_csv(MANIFEST)
        prior = prior[prior.accession != ds.accession]
        frame = pd.concat([prior, frame], ignore_index=True).sort_values("accession")
    frame.to_csv(MANIFEST, index=False)


def remap(accession: str) -> None:
    """Rows written before the mapping step carry no symbol; this refreshes them in place."""
    ds = Dataset(accession)
    de_path = ds.dir / f"{ds.accession}_de.csv"
    if not de_path.exists():
        print(f"[{accession}] no {de_path.name} on disk, nothing to remap")
        return
    mapping = map_identifiers(ds, de_path)
    files = [{"name": p.name, "bytes": p.stat().st_size, "sha256": sha256(p), "url": "local", "reused": True}
             for p in sorted(ds.dir.glob("*")) if p.is_file() and p.suffix != ".csv"]
    append_manifest(ds, files, de_path, None,
                    "" if ds.produces_ranking else f"no ranking by ruling: {ds.row.blocker}", mapping)
    print(f"  manifest row refreshed for {accession}")


def ingest(accession: str, download: bool, dry_run: bool, combat: str | None,
           rscript: str = "Rscript", rlibs: str = "") -> None:
    ds = Dataset(accession)
    print(f"[{accession}] engine={ds.engine} role={ds.row.pipeline_role} "
          f"arms={ds.samples.de_arm.value_counts().to_dict()} reference={ds.reference_arm} "
          f"effect={ds.effect_type}")
    files = ds.download() if download else [
        {"name": p.name, "bytes": p.stat().st_size, "sha256": sha256(p), "url": "local", "reused": True}
        for p in sorted(ds.dir.glob("*")) if p.is_file() and p.suffix != ".csv"]
    sample_table = write_sample_table(ds)
    if dry_run:
        print(f"  dry run: wrote {sample_table.relative_to(ROOT)}, skipped R")
        return
    de_path = run_r(ds, sample_table, combat, rscript, rlibs) if ds.produces_ranking else None
    mapping = map_identifiers(ds, de_path) if de_path else {}
    notes = ("" if ds.produces_ranking else
             f"no ranking by ruling: {ds.row.blocker}. Ingested for coverage and Phase 7")
    append_manifest(ds, files, de_path, combat, notes, mapping)
    print(f"  manifest row written for {accession}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--accession")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--no-download", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--combat", help="column of the sample table to correct on (within dataset only)")
    ap.add_argument("--rscript", default="Rscript",
                    help="Rscript to use; point this at the env holding limma, DESeq2, edgeR and sva")
    ap.add_argument("--rlibs", default=os.environ.get("R_LIBS_USER", ""),
                    help="extra R library path (absolute) holding packages installed outside conda, "
                         "e.g. affy CDF packages; passed to the worker as R_LIBS_USER")
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--remap-only", action="store_true",
                    help="re-apply identifier mapping to an existing <acc>_de.csv and refresh the "
                         "manifest row, without re-fetching or re-testing")
    args = ap.parse_args()

    if args.all:
        targets = pd.read_csv(READINESS).accession.tolist()
    elif args.accession:
        targets = [args.accession]
    else:
        raise SystemExit("pass --accession <id> or --all")

    done = set()
    if args.skip_existing and MANIFEST.exists():
        done = set(pd.read_csv(MANIFEST).accession)
    for accession in targets:
        if accession in done:
            print(f"[{accession}] already in the manifest, skipping")
            continue
        if args.remap_only:
            remap(accession)
            continue
        ingest(accession, download=not args.no_download, dry_run=args.dry_run, combat=args.combat,
               rscript=args.rscript, rlibs=args.rlibs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
