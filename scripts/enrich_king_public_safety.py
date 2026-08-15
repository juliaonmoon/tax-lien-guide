#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"

KCSO_SOURCE = "https://data.kingcounty.gov/resource/4kmt-kfqf.json"
KCSO_SOURCE_PAGE = "https://data.kingcounty.gov/Law-Enforcement-Safety/KCSO-Offense-Reports-2020-to-Present/4kmt-kfqf"
SPD_SOURCE = "https://data.seattle.gov/resource/tazs-3rd5.json"
SPD_SOURCE_PAGE = "https://data.seattle.gov/Public-Safety/SPD-Crime-Data-2008-Present/tazs-3rd5"
SPD_MCPP_GEOJSON = "https://data.seattle.gov/resource/ru88-fbhk.geojson"
SPD_MCPP_PAGE = "https://data.seattle.gov/Public-Safety/Seattle-Police-Department-Micro-Community-Policing/ru88-fbhk"

# King County Sheriff's Office contract-city jurisdictions listed on the County's
# official crime-data page. Independent city police jurisdictions are deliberately
# excluded unless an official city dataset is explicitly integrated below.
KCSO_CITIES = {
    "BURIEN", "CARNATION", "COVINGTON", "KENMORE", "MAPLE VALLEY",
    "NEWCASTLE", "NORTH BEND", "SAMMAMISH", "SEATAC", "SHORELINE",
    "SKYKOMISH", "WOODINVILLE",
}

PUBLIC_SAFETY_KEYS = [
    "public_safety_12mo_offenses", "public_safety_scope",
    "public_safety_period_start", "public_safety_period_end",
    "public_safety_source", "public_safety_area",
]


def fetch_kcso_counts(start: date) -> dict[str, int]:
    params = {
        "$select": "upper(city) as city,count(*) as offenses",
        "$where": f"incident_datetime >= '{start.isoformat()}T00:00:00.000'",
        "$group": "upper(city)",
        "$limit": "500",
    }
    r = requests.get(KCSO_SOURCE, params=params, timeout=45)
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


def fetch_spd_neighborhood_counts(start: date) -> dict[str, int]:
    # SPD's dataset contains finalized/UCR-approved offense rows and is refreshed
    # daily. Group by the published MCPP neighborhood to avoid presenting a
    # citywide count as if it were local to a parcel.
    params = {
        "$select": "upper(neighborhood) as neighborhood,count(*) as offenses",
        "$where": (
            f"offense_date >= '{start.isoformat()}T00:00:00.000' "
            "and neighborhood is not null"
        ),
        "$group": "upper(neighborhood)",
        "$limit": "1000",
    }
    r = requests.get(SPD_SOURCE, params=params, timeout=60)
    r.raise_for_status()
    out: dict[str, int] = {}
    for row in r.json():
        area = str(row.get("neighborhood") or "").strip().upper()
        try:
            n = int(row.get("offenses") or 0)
        except (TypeError, ValueError):
            continue
        if area:
            out[area] = n
    return out


def fetch_spd_mcpp_features() -> list[dict[str, Any]]:
    r = requests.get(SPD_MCPP_GEOJSON, params={"$limit": "5000"}, timeout=60)
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
    # Holes in a GeoJSON polygon subtract from the exterior ring.
    return not any(point_in_ring(lon, lat, hole) for hole in polygon[1:])


def feature_contains(feature: dict[str, Any], lon: float, lat: float) -> bool:
    geom = feature.get("geometry") or {}
    coords = geom.get("coordinates") or []
    if geom.get("type") == "Polygon":
        return point_in_polygon(lon, lat, coords)
    if geom.get("type") == "MultiPolygon":
        return any(point_in_polygon(lon, lat, poly) for poly in coords)
    return False


def find_spd_neighborhood(features: list[dict[str, Any]], lon: float, lat: float) -> str:
    for feature in features:
        if feature_contains(feature, lon, lat):
            props = feature.get("properties") or {}
            return str(props.get("name") or "").strip().upper()
    return ""


def clear_metric(p: dict[str, Any]) -> bool:
    had = any(k in p for k in PUBLIC_SAFETY_KEYS)
    for k in PUBLIC_SAFETY_KEYS:
        p.pop(k, None)
    return had


def main() -> None:
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    today = date.today()
    start = today - timedelta(days=365)

    kcso_counts = fetch_kcso_counts(start)
    spd_counts = fetch_spd_neighborhood_counts(start)
    spd_features = fetch_spd_mcpp_features()

    kcso_filled = 0
    seattle_filled = 0
    seattle_unmapped = 0
    cleared = 0

    for p in doc.get("properties", []):
        if p.get("state") != "WA" or p.get("county") != "King":
            continue

        city = str(p.get("city") or "").strip().upper()
        if city in KCSO_CITIES and city in kcso_counts:
            p["public_safety_12mo_offenses"] = kcso_counts[city]
            p["public_safety_area"] = city
            p["public_safety_scope"] = (
                "KCSO finalized offense reports in the named contract city; "
                "trailing 365 days; raw report count, not a population-adjusted crime rate"
            )
            p["public_safety_period_start"] = start.isoformat()
            p["public_safety_period_end"] = today.isoformat()
            p["public_safety_source"] = KCSO_SOURCE_PAGE
            kcso_filled += 1
            continue

        if city == "SEATTLE":
            try:
                lat = float(p.get("latitude"))
                lon = float(p.get("longitude"))
            except (TypeError, ValueError):
                if clear_metric(p):
                    cleared += 1
                seattle_unmapped += 1
                continue

            area = find_spd_neighborhood(spd_features, lon, lat)
            if area and area in spd_counts:
                p["public_safety_12mo_offenses"] = spd_counts[area]
                p["public_safety_area"] = area
                p["public_safety_scope"] = (
                    "SPD finalized/UCR-approved offense rows in the official MCPP neighborhood; "
                    "trailing 365 days; raw offense count, not a population-adjusted crime rate"
                )
                p["public_safety_period_start"] = start.isoformat()
                p["public_safety_period_end"] = today.isoformat()
                p["public_safety_source"] = SPD_SOURCE_PAGE
                p["public_safety_boundary_source"] = SPD_MCPP_PAGE
                seattle_filled += 1
            else:
                if clear_metric(p):
                    cleared += 1
                p.pop("public_safety_boundary_source", None)
                seattle_unmapped += 1
            continue

        # Other independent city police jurisdictions remain blank until an
        # official, refreshable source is deliberately integrated for that city.
        if clear_metric(p):
            cleared += 1
        p.pop("public_safety_boundary_source", None)

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(
        "King County public-safety enrichment: "
        f"KCSO {kcso_filled}; Seattle SPD {seattle_filled}; "
        f"Seattle unmapped {seattle_unmapped}; stale values cleared {cleared}"
    )
    print("Other independent city police jurisdictions remain blank pending official integrated sources.")


if __name__ == "__main__":
    main()
