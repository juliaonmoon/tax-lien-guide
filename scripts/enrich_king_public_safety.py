#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
SOURCE = "https://data.kingcounty.gov/resource/4kmt-kfqf.json"
SOURCE_PAGE = "https://data.kingcounty.gov/Law-Enforcement-Safety/KCSO-Offense-Reports-2020-to-Present/4kmt-kfqf"

# King County Sheriff's Office contract-city jurisdictions listed on the County's
# official crime-data page. Independent city police jurisdictions are deliberately
# excluded so this does not masquerade as a countywide comparable crime rate.
KCSO_CITIES = {
    "BURIEN", "CARNATION", "COVINGTON", "KENMORE", "MAPLE VALLEY",
    "NEWCASTLE", "NORTH BEND", "SAMMAMISH", "SEATAC", "SHORELINE",
    "SKYKOMISH", "WOODINVILLE",
}


def fetch_counts(start: date) -> dict[str, int]:
    params = {
        "$select": "upper(city) as city,count(*) as offenses",
        "$where": f"incident_datetime >= '{start.isoformat()}T00:00:00.000'",
        "$group": "upper(city)",
        "$limit": "500",
    }
    r = requests.get(SOURCE, params=params, timeout=45)
    r.raise_for_status()
    out: dict[str, int] = {}
    for row in r.json():
        city = str(row.get("city") or "").strip().upper()
        try:
            n = int(row.get("offenses") or 0)
        except (TypeError, ValueError):
            continue
        if city:
            out[city] = n
    return out


def main() -> None:
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    today = date.today()
    start = today - timedelta(days=365)
    counts = fetch_counts(start)

    filled = 0
    cleared = 0
    for p in doc.get("properties", []):
        if p.get("state") != "WA" or p.get("county") != "King":
            continue
        city = str(p.get("city") or "").strip().upper()
        if city in KCSO_CITIES and city in counts:
            p["public_safety_12mo_offenses"] = counts[city]
            p["public_safety_scope"] = "KCSO finalized offense reports in the named contract city; trailing 365 days; raw report count, not a population-adjusted crime rate"
            p["public_safety_period_start"] = start.isoformat()
            p["public_safety_period_end"] = today.isoformat()
            p["public_safety_source"] = SOURCE_PAGE
            filled += 1
        else:
            # Remove stale KCSO-derived values if a parcel is no longer mapped to a
            # covered contract city. Never fill independent police jurisdictions.
            keys = [
                "public_safety_12mo_offenses", "public_safety_scope",
                "public_safety_period_start", "public_safety_period_end",
                "public_safety_source",
            ]
            if any(k in p for k in keys):
                cleared += 1
                for k in keys:
                    p.pop(k, None)

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"King County public-safety enrichment: {filled} parcels filled; {cleared} stale values cleared")
    print("Independent city police jurisdictions remain blank by design.")


if __name__ == "__main__":
    main()
