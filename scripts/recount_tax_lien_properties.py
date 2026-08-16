#!/usr/bin/env python3
"""Recompute tax-lien detail counts after all append/enrichment steps.

Compact property rows may omit state/county because those values live in the
referenced profile. Resolve both forms so the published counts reflect the
actual multi-state, multi-county dataset instead of only rows that repeat the
profile metadata inline.

Also update refresh-status with explicit deed, lien, and combined coverage.
The existing top-level refresh-status counters historically described only
``properties.json``; keeping separate counters avoids silently presenting that
small deed/foreclosure slice as the coverage of the whole website.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DETAILS = ROOT / "data" / "tax-lien-properties.json"
DEEDS = ROOT / "data" / "properties.json"
STATUS = ROOT / "data" / "refresh-status.json"


def resolved(row: dict, profiles: dict) -> dict:
    profile = profiles.get(row.get("profile_id"), {})
    return {
        "state": row.get("state") or profile.get("state"),
        "county": row.get("county") or profile.get("county"),
        "auction_date": row.get("auction_date") or row.get("sale_date") or profile.get("auction_date") or profile.get("sale_date"),
    }


def jurisdiction_sets(rows: list[dict]) -> tuple[set[str], set[tuple[str, str]]]:
    states = {r.get("state") for r in rows if r.get("state")}
    counties = {(r.get("state"), r.get("county")) for r in rows if r.get("state") and r.get("county")}
    return states, counties


def main() -> None:
    doc = json.loads(DETAILS.read_text(encoding="utf-8"))
    props = doc.get("properties", [])
    profiles = doc.get("profiles", {})
    resolved_rows = [resolved(p, profiles) for p in props]

    lien_states, lien_counties = jurisdiction_sets(resolved_rows)

    doc["counts"] = {
        "total_records": len(props),
        "states": len(lien_states),
        "counties": len(lien_counties),
        "with_parcel_id": sum(bool(p.get("parcel_id")) for p in props),
        "with_address": sum(bool(p.get("property_address") or p.get("address")) for p in props),
        "with_auction_date": sum(bool(r["auction_date"]) for r in resolved_rows),
        "with_minimum_bid": sum(p.get("minimum_bid") is not None for p in props),
        "with_assessed_value": sum((p.get("assessed_value") is not None or p.get("market_value") is not None) for p in props),
        "with_research_priority": sum(bool(p.get("research_priority")) for p in props),
    }
    DETAILS.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    if STATUS.exists() and DEEDS.exists():
        deed_doc = json.loads(DEEDS.read_text(encoding="utf-8"))
        deed_rows = deed_doc.get("properties", [])
        deed_states, deed_counties = jurisdiction_sets(deed_rows)

        status = json.loads(STATUS.read_text(encoding="utf-8"))
        status["coverage_counts"] = {
            "tax_deed_foreclosure": {
                "records": len(deed_rows),
                "states": len(deed_states),
                "counties": len(deed_counties),
            },
            "tax_lien": {
                "records": len(props),
                "states": len(lien_states),
                "counties": len(lien_counties),
            },
            "combined": {
                "records": len(deed_rows) + len(props),
                "states": len(deed_states | lien_states),
                "counties": len(deed_counties | lien_counties),
            },
        }
        STATUS.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(doc["counts"], indent=2))


if __name__ == "__main__":
    main()
