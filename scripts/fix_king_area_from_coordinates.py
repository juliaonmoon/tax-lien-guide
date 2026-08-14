#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
STATUS = ROOT / "data" / "refresh-status.json"
UA = "TaxLienGuideBot/2.4 (public parcel research; official King County GIS)"
# King County migrated its GIS Open Data APIs to ArcGIS Online. Use the
# current hosted feature service rather than the deprecated gisdata.kingcounty.gov MapServer.
CITY_API = "https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services/CITY_KC_AREA_446/FeatureServer/0/query"
# Keep ZIP best-effort only until the migrated King County ZIP polygon service is identified.
ZIP_API = None


def spatial_lookup(url: str | None, lon: float, lat: float, out_fields: str) -> dict:
    if not url:
        return {}
    try:
        r = requests.get(url, params={
            "f": "json",
            "where": "1=1",
            "geometry": f"{lon},{lat}",
            "geometryType": "esriGeometryPoint",
            "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": out_fields,
            "returnGeometry": "false",
            "resultRecordCount": 1,
        }, headers={"User-Agent": UA, "Accept": "application/json"}, timeout=30)
        r.raise_for_status()
        doc = r.json()
        feats = doc.get("features", [])
        return (feats[0].get("attributes") or {}) if feats else {}
    except Exception:
        return {}


def main():
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    wa = [p for p in doc.get("properties", []) if p.get("state") == "WA" and p.get("county") == "King"]
    zip_fixed = city_fixed = rows_changed = 0

    for p in wa:
        if p.get("latitude") is None or p.get("longitude") is None:
            continue
        need_zip = not str(p.get("zip") or "").strip()
        need_city = not str(p.get("city") or "").strip()
        if not (need_zip or need_city):
            continue
        lat, lon = float(p["latitude"]), float(p["longitude"])
        changed = False
        if need_zip:
            z = spatial_lookup(ZIP_API, lon, lat, "ZIPCODE,ZIP")
            zip5 = str(z.get("ZIPCODE") or z.get("ZIP") or "").strip()[:5]
            if len(zip5) == 5:
                p["zip"] = zip5
                p["zip_source"] = "King County ZIP code polygon"
                zip_fixed += 1
                changed = True
        if need_city:
            # Migrated CITY_KC schema preserves CITYNAME; request all fields as a
            # fallback so a future schema alias does not silently zero out results.
            c = spatial_lookup(CITY_API, lon, lat, "*")
            city = str(c.get("CITYNAME") or c.get("NAME") or c.get("JURIS") or "").strip()
            if city:
                p["city"] = city
                p["city_source"] = "King County ArcGIS Online city/unincorporated polygon"
                city_fixed += 1
                changed = True
        if changed:
            rows_changed += 1

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    if STATUS.exists():
        st = json.loads(STATUS.read_text(encoding="utf-8"))
        complete = sum(bool(str(p.get("city") or "").strip()) and bool(str(p.get("zip") or "").strip()) for p in wa)
        note = (f"King County coordinate-to-area repair changed {rows_changed}/{len(wa)} rows; "
                f"recovered {city_fixed} city/jurisdiction values and {zip_fixed} ZIP codes. "
                f"Current city+ZIP fill: {complete}/{len(wa)}.")
        st.setdefault("notes", []).append(note)
        for h in st.get("source_health", []):
            if h.get("state") == "WA" and h.get("county") == "King":
                h["note"] = ((h.get("note") or "") + " " + note).strip()
        STATUS.write_text(json.dumps(st, indent=2), encoding="utf-8")
    print(note if STATUS.exists() else f"Changed {rows_changed} rows")


if __name__ == "__main__":
    main()
