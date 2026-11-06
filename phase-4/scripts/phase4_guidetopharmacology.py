#!/usr/bin/env python3
"""Phase 4: expert-curated selectivity from the IUPHAR/BPS Guide to Pharmacology.

Syntax verified against https://www.guidetopharmacology.org/webServices.jsp
on 2026-11-04. Two things changed since the project plan was written and
both are handled here:

  - The REST API is no longer open. Every request needs an API key, issued
    to registered users on request, passed in the GTP-API-Key header. A
    request without it returns HTTP 401. The key is read from the
    GTP_API_KEY environment variable and is never written to any output.
  - The documented rate limit is about 60 requests per minute, so the
    script paces itself rather than firing as fast as it can.

Selectivity is read from the interaction records: for a candidate target
this script records every ligand interaction with its affinity type and
value, and then, for each of those ligands, how many other human targets
the database records it acting on at comparable affinity. A ligand that
hits one target at pKi 8 and nothing else above pKi 6 is selective; one
that hits fifteen is not.

Output:
  phase-4/data/phase4-gtop-interactions.csv.gz
  phase-4/data/phase4-gtop-selectivity.csv
  phase-4/data/phase4-gtop-provenance.json

Run from the repo root, with the key in the environment:
  GTP_API_KEY=... python phase-4/scripts/phase4_guidetopharmacology.py
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import pandas as pd
import requests

BASE = "https://www.guidetopharmacology.org/services"
# Documented limit is ~60 requests per minute.
MIN_INTERVAL_S = 1.05
# The key is read from the environment. GTPAPIKEY is the name the credential
# is stored under in this project; the underscored form is accepted too.
ENV_NAMES = ("GTPAPIKEY", "GTP_API_KEY")


class RateLimited:
    """Paced client. A transport error is retried, not raised: an 85-minute
    run must not die on one read timeout near the end."""

    def __init__(self, key: str) -> None:
        self.session = requests.Session()
        self.session.headers.update({"GTP-API-Key": key})
        self.last = 0.0
        self.failures: list = []

    def get(self, path: str, params: dict | None = None, retries: int = 4):
        last_error = None
        for attempt in range(retries):
            wait = MIN_INTERVAL_S - (time.time() - self.last)
            if wait > 0:
                time.sleep(wait)
            try:
                response = self.session.get(
                    f"{BASE}/{path}", params=params or {}, timeout=60
                )
                self.last = time.time()
                if response.status_code == 200:
                    return response.json()
                if response.status_code == 401:
                    raise SystemExit(
                        "Guide to Pharmacology returned 401. The API key is missing or "
                        "invalid; keys are issued to registered users on request."
                    )
                if response.status_code == 404:
                    return None
                last_error = f"HTTP {response.status_code}"
            except SystemExit:
                raise
            except Exception as exc:  # noqa: BLE001
                self.last = time.time()
                last_error = f"{type(exc).__name__}"
            time.sleep(3 * (attempt + 1))
        self.failures.append({"path": path, "params": params, "error": last_error})
        return None


def affinity_value(record: dict) -> float:
    """Interaction records carry affinity as a median string that can be a
    range ('7.5' or '6.9 - 7.2'); take the midpoint of whatever is given."""
    raw = record.get("affinity") or record.get("affinityHigh") or ""
    parts = [p.strip() for p in str(raw).replace("–", "-").split("-") if p.strip()]
    values = []
    for part in parts:
        try:
            values.append(float(part))
        except ValueError:
            continue
    return sum(values) / len(values) if values else float("nan")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument(
        "--comparable-window",
        type=float,
        default=1.0,
        help="log units below a ligand's best affinity still counted as comparable",
    )
    parser.add_argument(
        "--min-affinity",
        type=float,
        default=6.0,
        help="only profile ligands reaching this affinity (6.0 = 1 uM) at a candidate target",
    )
    parser.add_argument("--max-ligands", type=int, default=2000)
    parser.add_argument(
        "--refresh", action="store_true", help="ignore the cache and re-query every symbol"
    )
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    data = root / "phase-4/data"

    key = next(
        (os.environ[name].strip() for name in ENV_NAMES if os.environ.get(name, "").strip()), ""
    )
    if not key:
        raise SystemExit(
            f"No API key found in any of {', '.join(ENV_NAMES)}. Register at "
            "guidetopharmacology.org, request an API key, and put it in the environment "
            "before running this script."
        )
    api = RateLimited(key)

    identifiers = pd.read_csv(data / "phase4-identifiers.csv")
    terms = sorted(
        identifiers.loc[identifiers["query_term"].notna(), "query_term"].replace("", pd.NA).dropna().unique()
    )

    # The symbol pass is about 2,500 paced requests, so it is checkpointed to
    # a JSON-lines cache after every symbol. Re-running resumes instead of
    # starting over.
    cache_path = data / "phase4-gtop-cache.jsonl"
    done: set = set()
    cached_rows: list = []
    cached_unmatched: list = []
    if cache_path.exists() and not args.refresh:
        with cache_path.open() as handle:
            for line in handle:
                if not line.strip():
                    continue
                entry = json.loads(line)
                done.add(entry["symbol"])
                cached_rows.extend(entry.get("rows", []))
                if not entry.get("rows"):
                    cached_unmatched.append(entry["symbol"])
        print(f"resuming: {len(done)} symbols already cached", flush=True)

    rows, matched, unmatched = list(cached_rows), {}, list(cached_unmatched)
    for row in cached_rows:
        matched[row["gene_symbol"]] = row["gtop_target_id"]

    handle = cache_path.open("a")
    for n, symbol in enumerate(terms, start=1):
        if symbol in done:
            continue
        symbol_rows: list = []
        hits = api.get("targets", {"geneSymbol": symbol})
        for hit in hits or []:
            target_id = hit.get("targetId")
            matched[symbol] = target_id
            interactions = api.get(
                f"targets/{target_id}/interactions", {"species": "Human"}
            )
            for inter in interactions or []:
                symbol_rows.append(
                    {
                        "gene_symbol": symbol,
                        "gtop_target_id": target_id,
                        "gtop_target_name": hit.get("name", ""),
                        "gtop_target_type": hit.get("type", ""),
                        "ligand_id": inter.get("ligandId"),
                        "ligand_name": inter.get("ligandName", ""),
                        "ligand_type": inter.get("ligandType", ""),
                        "approved_ligand": inter.get("approved"),
                        "interaction_type": inter.get("type", ""),
                        "action": inter.get("action", ""),
                        "affinity_type": inter.get("affinityParameter", ""),
                        "affinity_median": inter.get("affinity", ""),
                        "affinity_value": affinity_value(inter),
                        "primary_target": inter.get("primaryTarget"),
                        "species": inter.get("targetSpecies", ""),
                        "refs": "; ".join(str(r) for r in (inter.get("refIds") or [])),
                    }
                )
        rows.extend(symbol_rows)
        if not symbol_rows:
            unmatched.append(symbol)
        handle.write(json.dumps({"symbol": symbol, "rows": symbol_rows}) + "\n")
        handle.flush()
        if n % 100 == 0:
            print(f"  {n}/{len(terms)} symbols, {len(rows)} interactions", flush=True)
    handle.close()

    inter_frame = pd.DataFrame(rows)
    inter_frame.to_csv(data / "phase4-gtop-interactions.csv.gz", index=False, compression="gzip")

    # Selectivity needs the ligand's WHOLE target profile, not just the part
    # of it that happens to fall inside this project's target list. Counting
    # breadth within the queried set alone would make every ligand look
    # selective, so each prioritisation-relevant ligand is queried again from
    # the ligand side to get all the targets the database records for it.
    ligand_profiles, capped = {}, False
    if len(inter_frame):
        potent = inter_frame.dropna(subset=["affinity_value"])
        potent = potent[potent["affinity_value"] >= args.min_affinity]
        ligand_ids = sorted({int(x) for x in potent["ligand_id"].dropna().unique()})
        if len(ligand_ids) > args.max_ligands:
            capped = True
            ranked = (
                potent.groupby("ligand_id")["affinity_value"].max().sort_values(ascending=False)
            )
            ligand_ids = [int(x) for x in ranked.head(args.max_ligands).index]
        print(f"ligand profile pass: {len(ligand_ids)} ligands", flush=True)
        for n, ligand_id in enumerate(ligand_ids, start=1):
            records = api.get(f"ligands/{ligand_id}/interactions", {"species": "Human"})
            rows_for_ligand = []
            for record in records or []:
                value = affinity_value(record)
                if value == value:  # not NaN
                    rows_for_ligand.append((record.get("targetId"), value))
            if rows_for_ligand:
                best = max(v for _, v in rows_for_ligand)
                within = {
                    t for t, v in rows_for_ligand if v >= best - args.comparable_window
                }
                ligand_profiles[ligand_id] = {
                    "ligand_best_affinity_any_target": best,
                    "n_targets_total": len({t for t, _ in rows_for_ligand}),
                    "n_targets_within_window": len(within),
                }
            if n % 100 == 0:
                print(f"  {n}/{len(ligand_ids)} ligand profiles", flush=True)

    if len(inter_frame):
        valid = inter_frame.dropna(subset=["affinity_value"])
        selectivity = valid.groupby(
            ["gene_symbol", "ligand_id", "ligand_name"], as_index=False
        ).agg(
            affinity_at_target=("affinity_value", "max"),
            affinity_type=("affinity_type", "first"),
            gtop_target_id=("gtop_target_id", "first"),
        )
        profile = pd.DataFrame.from_dict(ligand_profiles, orient="index")
        if len(profile):
            profile.index.name = "ligand_id"
            selectivity = selectivity.merge(profile.reset_index(), on="ligand_id", how="left")
        else:
            for col in (
                "ligand_best_affinity_any_target",
                "n_targets_total",
                "n_targets_within_window",
            ):
                selectivity[col] = pd.NA
        selectivity["is_primary_target_for_ligand"] = (
            selectivity["affinity_at_target"]
            >= selectivity["ligand_best_affinity_any_target"] - 1e-9
        )
        selectivity["selectivity_profiled"] = selectivity["n_targets_total"].notna()
    else:
        selectivity = pd.DataFrame()
    selectivity.to_csv(data / "phase4-gtop-selectivity.csv", index=False)

    provenance = {
        "base_url": BASE,
        "auth": "GTP-API-Key request header (key read from GTP_API_KEY, never recorded here)",
        "docs_verified": "https://www.guidetopharmacology.org/webServices.jsp on 2026-11-04",
        "rate_limit_respected_s": MIN_INTERVAL_S,
        "comparable_window_log_units": args.comparable_window,
        "selectivity_method": (
            "Ligands reaching affinity >= "
            f"{args.min_affinity} at a candidate target were queried again from the ligand "
            "side, so n_targets_total and n_targets_within_window count every human target "
            "the database records for that ligand, not only the ones in this project's list."
        ),
        "ligands_profiled": len(ligand_profiles),
        "ligand_pass_capped": capped,
        "failed_requests": len(api.failures),
        "failed_request_sample": api.failures[:10],
        "coverage_caveat": (
            "A failed request is not an empty result: the symbols and ligands it covered are "
            "unassessed, not free of interactions."
        )
        if api.failures
        else "every request returned a response",
        "symbols_queried": len(terms),
        "symbols_with_a_gtop_target": len(matched),
        "symbols_without_a_gtop_target": len(unmatched),
        "interaction_rows": int(len(inter_frame)),
        "distinct_ligands": int(inter_frame["ligand_id"].nunique()) if len(inter_frame) else 0,
    }
    (data / "phase4-gtop-provenance.json").write_text(json.dumps(provenance, indent=2))
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()
