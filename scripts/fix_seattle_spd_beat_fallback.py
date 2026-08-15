#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"

SPD_SOURCE = "https://data.seattle.gov/resource/tazs-3rd5.json"
SPD_SOURCE_PAGE = "https://data.seattle.gov/Public-Safety/SPD-Crime-Data-2008-Present/tazs-3rd5"
SPD_BEATS_LAYER = "https://services.arcgis.com/ZOyb2t4B0UYuYNYH/arcgis/rest/services/Current_Beats/FeatureServer/0"
SPD_BEATS_PAGE = "https://data.seattle.gov/dataset/Seattle-Police-Department-Beats-Web-Mercator-/vhna-33bt"


def fetch_spd_beat_counts(start: date) -> dict[str, int]:
    params = {
        "$select": "upper(beat) as beat,count(*) as offenses",
        "$where": f"offense_date >= '{start.isoformat()}T00:00:00.000' and beat is not null",
        "$group": "upper(beat)",
        "$limit": "1000",
    }
    r = requests.get(SPD_SOURCE, params=params, timeout=60)
    r.raise_for_status()
    out: dict[str, int] = {}
    for row in r.json():
        beat = str(row.get("beat") or "").strip().upper()
        try:
            offenses = int(row.get("offenses") or 0)
        except (TypeError, ValueError):
            continue
        if beat:
            out[beat] = offenses
    return out


def fetch_spd_beat_features() -> list[dict[str, Any]]:
    params = {
        "f": "geojson",
        "where": "1=1",
        "outFields": "beat,first_precinct,sector",
        "outSR": "4326",
        "returnGeometry": "true",
        "resultRecordCount": "2000",
    }
    r = requests.get(f"{SPD_BEATS_LAYER}/query", params=params, timeout=60)
    r.raise_for_status()
    payload = r.json()
    return list(payload.get("features") or [])


def point_in_ring(lon: float, lat: float, ring: list[list[float]]) -> bool:
    inside = False
    if len(ring) < 3:
        return False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        crosses = ((yi > lat) != (yj > lat)) and (
            lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-15) + xi
        )
        if crosses:
            inside = not inside
        j = i
    return inside


def point_in_polygon(lon: float, lat: float, polygon: list[list[list[float]]]) -> bool:
    if not polygon or not point_in_ring(lon, lat, polygon[0]):
        return False
    return not any(point_in_ring(lon, lat, hole) for hole in polygon[1:])


def feature_contains(feature: dict[str, Any], lon: float, lat: float) -> bool:
    geom = feature.get("geometry") or {}
    coords = geom.get("coordinates") or []
    if geom.get("type") == "Polygon":
        return point_in_polygon(lon, lat, coords)
    if geom.get("type") == "MultiPolygon":
        return any(point_in_polygon(lon, lat, poly) for poly in coords)
    return False


def find_spd_beat(features: list[dict[str, Any]], lon: float, lat: float) -> tuple[str, str, str]:
    for feature in features:
        if feature_contains(feature, lon, lat):
            props = feature.get("properties") or {}
            return (
                str(props.get("beat") or "").strip().upper(),
                str(props.get("first_precinct") or "").strip().upper(),
                str(props.get("sector") or "").strip().upper(),
            )
    return "", "", ""


def main() -> None:
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    today = date.today()
    start = today - timedelta(days=365)
    beat_counts = fetch_spd_beat_counts(start)
    beat_features = fetch_spd_beat_features()

    filled = 0
    outside_or_unmapped = 0
    already_filled = 0

    for p in doc.get("properties", []):
        if p.get("state") != "WA" or p.get("county") != "King":
            continue
        if str(p.get("city") or "").strip().upper() != "SEATTLE":
            continue
        if p.get("public_safety_12mo_offenses") not in (None, ""):
            already_filled += 1
            continue

        try:
            lat = float(p.get("latitude"))
            lon = float(p.get("longitude"))
        except (TypeError, ValueError):
            outside_or_unmapped += 1
            continue

        beat, precinct, sector = find_spd_beat(beat_features, lon, lat)
        if not beat or beat not in beat_counts:
            outside_or_unmapped += 1
            continue

        p["public_safety_12mo_offenses"] = beat_counts[beat]
        p["public_safety_area"] = beat
        p["public_safety_scope"] = (
            "SPD finalized/UCR-approved offense rows in the official current police beat containing the parcel; "
            "trailing 365 days; raw offense count, not a population-adjusted crime rate"
        )
        p["public_safety_period_start"] = start.isoformat()
        p["public_safety_period_end"] = today.isoformat()
        p["public_safety_source"] = SPD_SOURCE_PAGE
        p["public_safety_boundary_source"] = SPD_BEATS_PAGE
        if precinct:
            p["public_safety_precinct"] = precinct
        if sector:
            p["public_safety_sector"] = sector
        filled += 1

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(
        "Seattle SPD beat fallback: "
        f"already MCPP-enriched {already_filled}; beat fallback filled {filled}; "
        f"outside/unmapped {outside_or_unmapped}"
    )


if __name__ == "__main__":
    main()
