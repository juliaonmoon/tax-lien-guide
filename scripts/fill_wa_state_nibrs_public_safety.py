#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
SOURCE_API = "https://data.wa.gov/resource/vvfu-ry7f.json"
SOURCE_PAGE = "https://data.wa.gov/Public-Safety/Washington-State-Uniform-Crime-Reporting-National-/vvfu-ry7f"
YEAR = "2024"  # latest year currently published by WA OFM/SAC
RETRYABLE_HTTP = {429, 500, 502, 503, 504}

# Only use this statewide official annual dataset as a fallback where a more
# local official source has not already populated the parcel.
CITY_ALIASES = {
    "KENT": ("KENT",),
    "RENTON": ("RENTON",),
    "AUBURN": ("AUBURN",),
    "FEDERAL WAY": ("FEDERAL WAY",),
    "DES MOINES": ("DES MOINES",),
    "SEATTLE": ("SEATTLE",),
    "LAKE FOREST PARK": ("LAKE FOREST PARK",),
    "REDMOND": ("REDMOND",),
    "TUKWILA": ("TUKWILA",),
    "ISSAQUAH": ("ISSAQUAH",),
    "KIRKLAND": ("KIRKLAND",),
    "SNOQUALMIE": ("SNOQUALMIE",),
}


def fetch_json(url: str, params: dict[str, str], attempts: int = 5) -> Any:
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            r = requests.get(url, params=params, timeout=60)
            if r.status_code in RETRYABLE_HTTP and attempt < attempts - 1:
                time.sleep(min(8, 2 ** attempt))
                continue
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as exc:
            last = exc
            if attempt >= attempts - 1:
                raise
            time.sleep(min(8, 2 ** attempt))
    if last:
        raise last
    raise RuntimeError("state NIBRS fetch failed")


def parse_number(v: Any) -> float | None:
    if v in (None, ""):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def normalized(s: Any) -> str:
    return " ".join(str(s or "").upper().split())


def choose_row(rows: list[dict[str, Any]], aliases: tuple[str, ...]) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for row in rows:
        loc = normalized(row.get("location"))
        if any(alias in loc for alias in aliases):
            candidates.append(row)
    if not candidates:
        return None
    # Prefer rows explicitly identifying a police department/department, then
    # the row with the largest reported population. This guards against a city
    # token appearing in a different agency name while avoiding invented joins.
    candidates.sort(
        key=lambda r: (
            "POLICE" in normalized(r.get("location")) or "DEPARTMENT" in normalized(r.get("location")),
            parse_number(r.get("population")) or 0,
        ),
        reverse=True,
    )
    return candidates[0]


def main() -> None:
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    params = {
        "$limit": "5000",
        "$where": f"indexyear='{YEAR}' and upper(county)='KING'",
    }
    rows = fetch_json(SOURCE_API, params)
    if not isinstance(rows, list) or not rows:
        raise SystemExit("WA OFM/SAC NIBRS query returned no 2024 King County rows; preserving blanks")

    selected = {city: choose_row(rows, aliases) for city, aliases in CITY_ALIASES.items()}
    filled = 0
    unresolved: dict[str, int] = {}

    for p in doc.get("properties", []):
        if p.get("state") != "WA" or p.get("county") != "King":
            continue
        if p.get("public_safety_12mo_offenses") not in (None, ""):
            continue
        city = normalized(p.get("city"))
        row = selected.get(city)
        if not row:
            unresolved[city or "UNCLASSIFIED"] = unresolved.get(city or "UNCLASSIFIED", 0) + 1
            continue
        total = parse_number(row.get("total"))
        if total is None:
            unresolved[city or "UNCLASSIFIED"] = unresolved.get(city or "UNCLASSIFIED", 0) + 1
            continue

        p["public_safety_12mo_offenses"] = int(total) if total.is_integer() else total
        p["public_safety_area"] = str(row.get("location") or city).strip()
        p["public_safety_scope"] = (
            f"Washington OFM/SAC NIBRS annual reported-crime total for the reporting law-enforcement agency, calendar {YEAR}; "
            "citywide agency fallback, not a parcel/neighborhood crime rate and not directly comparable to KCSO/SPD trailing-365-day metrics"
        )
        p["public_safety_period_start"] = f"{YEAR}-01-01"
        p["public_safety_period_end"] = f"{YEAR}-12-31"
        p["public_safety_source"] = SOURCE_PAGE
        p.pop("public_safety_boundary_source", None)
        rate = parse_number(row.get("rate"))
        if rate is not None:
            p["public_safety_rate_published"] = rate
        filled += 1

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"WA OFM/SAC NIBRS citywide fallback filled {filled} King County parcels")
    if unresolved:
        print("Still unresolved by city:", dict(sorted(unresolved.items())))


if __name__ == "__main__":
    main()
