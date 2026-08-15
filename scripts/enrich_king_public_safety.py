#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"

KCSO_SOURCE = "https://data.kingcounty.gov/resource/4kmt-kfqf.json"
KCSO_SOURCE_PAGE = "https://data.kingcounty.gov/Law-Enforcement-Safety/KCSO-Offense-Reports-2020-to-Present/4kmt-kfqf"
KCSO_DISTRICT_LAYER = "https://services.arcgis.com/Ej0PsM5Aw677QF1W/ArcGIS/rest/services/PATROL_DISTRICTS_AREA_746/FeatureServer/0"
KCSO_DISTRICT_PAGE = "https://www.arcgis.com/home/item.html?id=4eb36844125d4e53a6144474a88042ea"
SPD_SOURCE = "https://data.seattle.gov/resource/tazs-3rd5.json"
SPD_SOURCE_PAGE = "https://data.seattle.gov/Public-Safety/SPD-Crime-Data-2008-Present/tazs-3rd5"
SPD_MCPP_GEOJSON = "https://data.seattle.gov/resource/ru88-fbhk.geojson"
SPD_MCPP_PAGE = "https://data.seattle.gov/Public-Safety/Seattle-Police-Department-Micro-Community-Policing/ru88-fbhk"

KCSO_CITIES = {
    "BEAUX ARTS", "BURIEN", "CARNATION", "COVINGTON", "KENMORE",
    "MAPLE VALLEY", "NEWCASTLE", "NORTH BEND", "SAMMAMISH", "SEATAC",
    "SHORELINE", "SKYKOMISH", "WOODINVILLE",
}
KCSO_UNINCORPORATED_LABELS = {"KING COUNTY", "VASHON"}

PUBLIC_SAFETY_KEYS = [
    "public_safety_12mo_offenses", "public_safety_scope",
    "public_safety_period_start", "public_safety_period_end",
    "public_safety_source", "public_safety_area", "public_safety_boundary_source",
]
RETRYABLE_HTTP = {429, 500, 502, 503, 504}


def fetch_json(url: str, params: dict[str, str] | None = None, timeout: int = 60,
               attempts: int = 5) -> Any:
    """Fetch public JSON with bounded retry/backoff for transient source failures."""
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            if r.status_code in RETRYABLE_HTTP and attempt < attempts - 1:
                time.sleep(min(8, 2 ** attempt))
                continue
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            if attempt >= attempts - 1:
                raise
            time.sleep(min(8, 2 ** attempt))
    if last_error:
        raise last_error
    raise RuntimeError(f"Unable to fetch JSON from {url}")


def fetch_grouped_counts(start: date, field: str) -> dict[str, int]:
    params = {
        "$select": f"upper({field}) as area,count(*) as offenses",
        "$where": f"incident_datetime >= '{start.isoformat()}T00:00:00.000' and {field} is not null",
        "$group": f"upper({field})",
        "$limit": "1000",
    }
    rows = fetch_json(KCSO_SOURCE, params=params)
    out: dict[str, int] = {}
    for row in rows:
        area = str(row.get("area") or "").strip().upper()
        # In the offense feed most patrol districts are published as "District F6"
        # while the official patrol-district GIS layer stores the same code as "F6".
        # Normalize only that literal prefix so the two official sources join cleanly;
        # values such as MT10 are intentionally left unchanged.
        if field == "district" and area.startswith("DISTRICT "):
            area = area[len("DISTRICT "):].strip()
        try:
            n = int(row.get("offenses") or 0)
        except (TypeError, ValueError):
            continue
        if area:
            out[area] = out.get(area, 0) + n
    return out


def fetch_kcso_counts(start: date) -> dict[str, int]:
    return fetch_grouped_counts(start, "city")


def fetch_kcso_district_counts(start: date) -> dict[str, int]:
    return fetch_grouped_counts(start, "district")


def fetch_kcso_district_features() -> list[dict[str, Any]]:
    params = {
        "f": "geojson",
        "where": "1=1",
        "outFields": "PatDist,CityName,Juris",
        "outSR": "4326",
        "returnGeometry": "true",
        "resultRecordCount": "2000",
    }
    payload = fetch_json(f"{KCSO_DISTRICT_LAYER}/query", params=params)
    return list(payload.get("features") or [])


def fetch_spd_neighborhood_counts(start: date) -> dict[str, int]:
    params = {
        "$select": "upper(neighborhood) as neighborhood,count(*) as offenses",
        "$where": f"offense_date >= '{start.isoformat()}T00:00:00.000' and neighborhood is not null",
        "$group": "upper(neighborhood)",
        "$limit": "1000",
    }
    rows = fetch_json(SPD_SOURCE, params=params)
    out: dict[str, int] = {}
    for row in rows:
        area = str(row.get("neighborhood") or "").strip().upper()
        try:
            n = int(row.get("offenses") or 0)
        except (TypeError, ValueError):
            continue
        if area:
            out[area] = n
    return out


def fetch_spd_mcpp_features() -> list[dict[str, Any]]:
    payload = fetch_json(SPD_MCPP_GEOJSON, params={"$limit": "5000"})
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


def find_kcso_district(features: list[dict[str, Any]], lon: float, lat: float) -> str:
    for feature in features:
        if feature_contains(feature, lon, lat):
            props = feature.get("properties") or {}
            return str(props.get("PatDist") or "").strip().upper()
    return ""


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


def set_metric(p: dict[str, Any], offenses: int, area: str, scope: str,
               start: date, today: date, source: str,
               boundary_source: str | None = None) -> None:
    p["public_safety_12mo_offenses"] = offenses
    p["public_safety_area"] = area
    p["public_safety_scope"] = scope
    p["public_safety_period_start"] = start.isoformat()
    p["public_safety_period_end"] = today.isoformat()
    p["public_safety_source"] = source
    if boundary_source:
        p["public_safety_boundary_source"] = boundary_source
    else:
        p.pop("public_safety_boundary_source", None)


def main() -> None:
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    today = date.today()
    start = today - timedelta(days=365)

    kcso_counts = fetch_kcso_counts(start)
    kcso_district_counts = fetch_kcso_district_counts(start)
    kcso_district_features = fetch_kcso_district_features()
    spd_counts = fetch_spd_neighborhood_counts(start)
    spd_features = fetch_spd_mcpp_features()

    kcso_city_filled = 0
    kcso_district_filled = 0
    kcso_district_unmapped = 0
    seattle_filled = 0
    seattle_unmapped = 0
    cleared = 0

    for p in doc.get("properties", []):
        if p.get("state") != "WA" or p.get("county") != "King":
            continue

        city = str(p.get("city") or "").strip().upper()
        if city in KCSO_CITIES and city in kcso_counts:
            set_metric(
                p, kcso_counts[city], city,
                "KCSO finalized offense reports in the named contract city; trailing 365 days; raw report count, not a population-adjusted crime rate",
                start, today, KCSO_SOURCE_PAGE,
            )
            kcso_city_filled += 1
            continue

        if city in KCSO_UNINCORPORATED_LABELS:
            try:
                lat = float(p.get("latitude"))
                lon = float(p.get("longitude"))
            except (TypeError, ValueError):
                if clear_metric(p):
                    cleared += 1
                kcso_district_unmapped += 1
                continue
            district = find_kcso_district(kcso_district_features, lon, lat)
            if district and district in kcso_district_counts:
                set_metric(
                    p, kcso_district_counts[district], district,
                    "KCSO finalized offense reports in the official patrol district containing the parcel; trailing 365 days; raw report count, not a population-adjusted crime rate",
                    start, today, KCSO_SOURCE_PAGE, KCSO_DISTRICT_PAGE,
                )
                kcso_district_filled += 1
            else:
                if clear_metric(p):
                    cleared += 1
                kcso_district_unmapped += 1
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
                set_metric(
                    p, spd_counts[area], area,
                    "SPD finalized/UCR-approved offense rows in the official MCPP neighborhood; trailing 365 days; raw offense count, not a population-adjusted crime rate",
                    start, today, SPD_SOURCE_PAGE, SPD_MCPP_PAGE,
                )
                seattle_filled += 1
            else:
                if clear_metric(p):
                    cleared += 1
                seattle_unmapped += 1
            continue

        if clear_metric(p):
            cleared += 1

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(
        "King County public-safety enrichment: "
        f"KCSO contract-city {kcso_city_filled}; KCSO district {kcso_district_filled}; "
        f"KCSO district unmapped {kcso_district_unmapped}; Seattle SPD {seattle_filled}; "
        f"Seattle unmapped {seattle_unmapped}; stale values cleared {cleared}"
    )
    print("Independent city police jurisdictions remain blank pending official integrated sources.")


if __name__ == "__main__":
    main()
