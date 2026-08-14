#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
STATUS = ROOT / "data" / "refresh-status.json"
API = "https://services.arcgis.com/jsIt88o09Q0r1j8h/arcgis/rest/services/Current_Parcels/FeatureServer/0/query"
UA = "TaxLienGuideBot/2.3 (public WA parcel research; explicit non-owner fields only)"

# Washington State Parcels Project / WaTech. We intentionally request only
# parcel/location/land-use/value fields and never owner/taxpayer names or addresses.
FIELDS = "ORIG_PARCEL_ID,SITUS_ADDRESS,SUB_ADDRESS,SITUS_CITY_NM,SITUS_ZIP_NR,LANDUSE_CD,ORIG_LANDUSE_CD,VALUE_LAND,VALUE_BLDG,DATA_LINK"


def clean(v):
    return str(v or "").strip()


def num(v):
    try:
        return float(v)
    except Exception:
        return None


def fetch_parcel(pin: str):
    r = requests.get(
        API,
        params={
            "f": "json",
            "where": f"FIPS_NR='033' AND ORIG_PARCEL_ID='{pin}'",
            "outFields": FIELDS,
            "returnGeometry": "true",
            "returnCentroid": "true",
            "outSR": 4326,
            "resultRecordCount": 2,
        },
        headers={"User-Agent": UA, "Accept": "application/json"},
        timeout=30,
    )
    r.raise_for_status()
    features = r.json().get("features", [])
    return features[0] if len(features) == 1 else None


def main():
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    wa = [p for p in doc.get("properties", []) if p.get("state") == "WA" and p.get("county") == "King"]
    targets = [p for p in wa if p.get("parcel_id") and (
        p.get("latitude") is None or p.get("longitude") is None or p.get("assessed_value") in (None, "")
    )]
    matched = changed = value_recovered = coord_recovered = address_recovered = 0

    for p in targets:
        pin = clean(p.get("parcel_id"))
        try:
            f = fetch_parcel(pin)
        except Exception:
            continue
        if not f:
            continue
        matched += 1
        a = f.get("attributes") or {}
        before = json.dumps(p, sort_keys=True, default=str)

        # Location fields: fill only blanks, never overwrite a more current county result.
        situs = clean(a.get("SITUS_ADDRESS"))
        sub = clean(a.get("SUB_ADDRESS"))
        city = clean(a.get("SITUS_CITY_NM"))
        zip5 = clean(a.get("SITUS_ZIP_NR"))[:5]
        if not p.get("address") and situs:
            full = " ".join(x for x in [situs, sub] if x)
            suffix = ", ".join(x for x in [city, "WA", zip5] if x)
            p["address"] = f"{full}, {suffix}" if suffix else full
            p["address_status"] = "WA State Parcels Project situs address"
            address_recovered += 1
        if not p.get("city") and city:
            p["city"] = city
        if not p.get("zip") and zip5:
            p["zip"] = zip5

        # Values are market land/building values in the statewide parcel schema.
        lv = num(a.get("VALUE_LAND"))
        bv = num(a.get("VALUE_BLDG"))
        total = (lv or 0) + (bv or 0)
        if p.get("assessed_value") in (None, "") and total > 0:
            p["land_value"] = lv or 0
            p["improvement_value"] = bv or 0
            p["assessed_value"] = total
            p["market_value"] = total
            p["value_basis"] = "Washington State Parcels Project market land + building value (2026 snapshot)"
            value_recovered += 1

        # Prefer centroid returned by ArcGIS; fall back to geometry ring average only if necessary.
        if p.get("latitude") is None or p.get("longitude") is None:
            c = f.get("centroid") or {}
            lat, lon = num(c.get("y")), num(c.get("x"))
            if lat is None or lon is None:
                geom = f.get("geometry") or {}
                rings = geom.get("rings") or []
                pts = [pt for ring in rings for pt in ring if isinstance(pt, list) and len(pt) >= 2]
                if pts:
                    lon = sum(float(pt[0]) for pt in pts) / len(pts)
                    lat = sum(float(pt[1]) for pt in pts) / len(pts)
            if lat is not None and lon is not None:
                p["latitude"] = lat
                p["longitude"] = lon
                p["coordinate_source"] = "Washington State Parcels Project parcel geometry"
                coord_recovered += 1

        p["state_parcel_source"] = "Washington State Parcels Project (WaTech / county-sourced)"
        if a.get("DATA_LINK"):
            p["state_parcel_data_link"] = a.get("DATA_LINK")
        if a.get("LANDUSE_CD") and not p.get("state_landuse_code"):
            p["state_landuse_code"] = a.get("LANDUSE_CD")
        if a.get("ORIG_LANDUSE_CD") and not p.get("county_landuse_code"):
            p["county_landuse_code"] = a.get("ORIG_LANDUSE_CD")

        if json.dumps(p, sort_keys=True, default=str) != before:
            changed += 1

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    note = (
        f"WA State Parcels fallback: targeted {len(targets)} King County gap rows; matched {matched}; "
        f"changed {changed}; recovered value {value_recovered}, coordinates {coord_recovered}, address {address_recovered}."
    )
    if STATUS.exists():
        st = json.loads(STATUS.read_text(encoding="utf-8"))
        st.setdefault("notes", []).append(note)
        for h in st.get("source_health", []):
            if h.get("state") == "WA" and h.get("county") == "King":
                h["note"] = ((h.get("note") or "") + " " + note).strip()
        STATUS.write_text(json.dumps(st, indent=2), encoding="utf-8")
    print(note)


if __name__ == "__main__":
    main()
