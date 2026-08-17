#!/usr/bin/env python3
"""Restore missing King County enrichment from a recent verified repository snapshot.

This is a regression guard, not a substitute for live enrichment. It activates only
when the current King County slice has suffered a severe field-coverage collapse and
only fills currently blank enrichment fields from a recent committed snapshot that
passes strict coverage checks. Current nonblank values, sale status, bids, tax status,
and owner data are never overwritten.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"

SAFE_FIELDS = {
    "address", "city", "zip", "latitude", "longitude",
    "assessed_value", "market_value", "land_value", "improvement_value", "value_basis",
    "property_type", "legal_description", "zoning", "acres",
    "address_status", "address_basis", "coordinate_source", "coordinate_basis",
    "city_source", "zip_source", "area_source", "area_source_url",
    "parcel_enrichment_source", "condo_parent_parcel", "property_type_basis",
    "median_household_income", "median_gross_rent", "vacancy_proxy_pct", "renter_share_pct",
    "acs_release_year", "rent_trend_pct", "rent_trend_period", "rent_to_income_pct",
    "rentability_score", "neighborhood_value_score", "neighborhood_value_label",
    "neighborhood_metric_level", "neighborhood_metric_year", "neighborhood_reasons",
    "public_safety_12mo_offenses", "public_safety_area", "public_safety_scope",
    "public_safety_period_start", "public_safety_period_end", "public_safety_source",
    "public_safety_boundary_source", "public_safety_precinct", "public_safety_sector",
    "public_safety_rate_published",
}


def king_rows(doc: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        p for p in doc.get("properties", [])
        if p.get("state") == "WA" and p.get("county") == "King" and p.get("parcel_id")
    ]


def coverage(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "count": len(rows),
        "city_zip": sum(bool(p.get("city") and p.get("zip")) for p in rows),
        "coordinates": sum(p.get("latitude") is not None and p.get("longitude") is not None for p in rows),
        "assessed_value": sum(p.get("assessed_value") not in (None, "") for p in rows),
        "property_type": sum(bool(p.get("property_type")) for p in rows),
        "neighborhood": sum(p.get("neighborhood_value_score") is not None for p in rows),
        "public_safety": sum(p.get("public_safety_12mo_offenses") not in (None, "") for p in rows),
    }


def severe_regression(c: dict[str, int]) -> bool:
    if c["count"] < 100:
        return True
    return any(c[k] < 100 for k in ("city_zip", "coordinates", "assessed_value", "property_type", "neighborhood"))


def verified_candidate(c: dict[str, int]) -> bool:
    return (
        c["count"] >= 140
        and c["city_zip"] >= 140
        and c["coordinates"] >= 140
        and c["assessed_value"] >= 140
        and c["property_type"] >= 140
        and c["neighborhood"] >= 140
        and c["public_safety"] >= 140
    )


def git_output(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL)


def find_verified_snapshot() -> tuple[str, dict[str, Any], dict[str, int]] | None:
    try:
        commits = git_output("rev-list", "--max-count=40", "HEAD", "--", "data/properties.json").splitlines()
    except Exception:
        return None
    for sha in commits[1:]:  # skip current HEAD; we need an earlier committed state
        try:
            raw = git_output("show", f"{sha}:data/properties.json")
            doc = json.loads(raw)
        except Exception:
            continue
        c = coverage(king_rows(doc))
        if verified_candidate(c):
            return sha, doc, c
    return None


def blank(v: Any) -> bool:
    return v is None or v == "" or v == []


def main() -> None:
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    current = king_rows(doc)
    before = coverage(current)
    if not severe_regression(before):
        print("King County historical restore: current enrichment coverage is not severely regressed; no restore needed.", before)
        return

    found = find_verified_snapshot()
    if not found:
        print("King County historical restore: severe regression detected but no recent snapshot passed strict verification; leaving data unchanged.", before)
        return

    sha, old_doc, old_cov = found
    old_by_pin = {str(p.get("parcel_id")): p for p in king_rows(old_doc)}
    fields_filled = 0
    rows_changed = 0
    for p in current:
        prior = old_by_pin.get(str(p.get("parcel_id")))
        if not prior:
            continue
        changed = False
        for field in SAFE_FIELDS:
            if blank(p.get(field)) and not blank(prior.get(field)):
                p[field] = prior[field]
                fields_filled += 1
                changed = True
        if changed:
            rows_changed += 1

    if rows_changed:
        PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    after = coverage(current)
    print(
        f"King County historical restore: used {sha[:12]} (coverage {old_cov}); "
        f"changed {rows_changed} rows / filled {fields_filled} missing enrichment fields; "
        f"coverage before {before}; after {after}."
    )


if __name__ == "__main__":
    main()
