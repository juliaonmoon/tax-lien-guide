#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
STATUS = ROOT / "data" / "refresh-status.json"
UA = "TaxLienGuideBot/2.1 (public parcel research; no access-control bypass)"
ADDRESS_API = "https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services/ADDRESS_POINT_642/FeatureServer/0/query"
PARCEL_API = "https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services/PARCEL_ADDRESS_PUB_AREA_3069/FeatureServer/0/query"


def coord(v):
    try:
        return float(v)
    except Exception:
        return None


def query(url, parcels):
    out = {}
    for i in range(0, len(parcels), 80):
        chunk = parcels[i:i + 80]
        where = "PIN IN (" + ",".join("'%s'" % p for p in chunk) + ")"
        try:
            r = requests.get(url, params={
                "f": "json",
                "where": where,
                "outFields": "PIN,LAT,LON,PRIM_ADDR,PRIM_ADDR_FILTER",
                "returnGeometry": "false",
                "orderByFields": "PIN,PRIM_ADDR DESC",
            }, headers={"User-Agent": UA, "Accept": "application/json"}, timeout=45)
            r.raise_for_status()
            data = r.json()
        except Exception:
            continue
        for feature in data.get("features", []):
            a = feature.get("attributes", {})
            pin = str(a.get("PIN") or "").strip()
            if not pin:
                continue
            current = out.get(pin)
            primary = a.get("PRIM_ADDR") in (1, "1") or str(a.get("PRIM_ADDR_FILTER") or "").lower().startswith("primary")
            if current and not primary:
                continue
            out[pin] = a
    return out


def main():
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    props = doc.get("properties", [])
    wa = [p for p in props if p.get("state") == "WA" and p.get("county") == "King" and p.get("parcel_id")]
    parcels = [str(p["parcel_id"]) for p in wa]

    addr = query(ADDRESS_API, parcels)
    parcel = query(PARCEL_API, parcels)

    for p in wa:
        pin = str(p.get("parcel_id"))
        a = addr.get(pin) or {}
        pi = parcel.get(pin) or {}
        lat = coord(a.get("LAT"))
        lon = coord(a.get("LON"))
        if lat is None:
            lat = coord(pi.get("LAT"))
        if lon is None:
            lon = coord(pi.get("LON"))
        if lat is not None:
            p["latitude"] = lat
        if lon is not None:
            p["longitude"] = lon

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    if STATUS.exists():
        st = json.loads(STATUS.read_text(encoding="utf-8"))
        count = sum(p.get("latitude") is not None and p.get("longitude") is not None for p in wa)
        note = f"King County coordinate repair: {count}/{len(wa)} parcels now have latitude+longitude."
        st.setdefault("notes", []).append(note)
        for h in st.get("source_health", []):
            if h.get("state") == "WA" and h.get("county") == "King":
                old = h.get("note") or ""
                h["note"] = old + " " + note
        STATUS.write_text(json.dumps(st, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
