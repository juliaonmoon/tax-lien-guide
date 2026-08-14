#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
STATUS = ROOT / "data" / "refresh-status.json"

# These two parcels are present on King County's official 2026 foreclosure list,
# but currently do not resolve through the public King County GIS parcel/address
# services used by this project. Independent public property-record pages identify
# both parcels as residential parcels in Federal Way, WA 98023.
#
# We only recover fields explicitly supported by those sources. We do NOT infer an
# exact street address, coordinates, assessed value, legal description, or tax data.
FALLBACKS = {
    "2188201795": {
        "city": "FEDERAL WAY",
        "zip": "98023",
        "property_type": "Residential",
        "zoning": "RS15.0",
        "lot_sqft": 3000,
        "source_url": "https://www.crexi.com/property-records/218820-1795-FEDERAL-WAY-WA-98023/600491f0be3acd1b9265aaa2658bf47f695dfc49",
    },
    "2188201800": {
        "city": "FEDERAL WAY",
        "zip": "98023",
        "property_type": "Residential",
        "zoning": "RS15.0",
        "lot_sqft": 6000,
        "source_url": "https://www.crexi.com/property-records/218820-1800-FEDERAL-WAY-WA-98023/13e3c712d0f370ecd453b6a242712f47eda0cf36",
    },
}


def main():
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    rows = [
        p for p in doc.get("properties", [])
        if p.get("state") == "WA" and p.get("county") == "King"
    ]
    changed = 0
    recovered = {"city_zip": 0, "property_type": 0, "zoning": 0, "lot_sqft": 0}

    for p in rows:
        pin = str(p.get("parcel_id") or "")
        fb = FALLBACKS.get(pin)
        if not fb:
            continue

        before_city_zip = bool(p.get("city") and p.get("zip"))
        before_type = bool(p.get("property_type"))
        before_zoning = bool(p.get("zoning"))
        before_lot = p.get("lot_sqft") not in (None, "")
        row_changed = False

        if not p.get("city"):
            p["city"] = fb["city"]
            row_changed = True
        if not p.get("zip"):
            p["zip"] = fb["zip"]
            row_changed = True
        if not p.get("property_type"):
            p["property_type"] = fb["property_type"]
            row_changed = True
        if not p.get("zoning"):
            p["zoning"] = fb["zoning"]
            row_changed = True
        if p.get("lot_sqft") in (None, ""):
            p["lot_sqft"] = fb["lot_sqft"]
            row_changed = True

        if row_changed:
            p["orphan_fallback_source"] = "Public property-record fallback; King County GIS join unavailable"
            p["orphan_fallback_source_url"] = fb["source_url"]
            p["orphan_fallback_scope"] = "city, ZIP, property type, zoning, lot size only"
            changed += 1

        if not before_city_zip and p.get("city") and p.get("zip"):
            recovered["city_zip"] += 1
        if not before_type and p.get("property_type"):
            recovered["property_type"] += 1
        if not before_zoning and p.get("zoning"):
            recovered["zoning"] += 1
        if not before_lot and p.get("lot_sqft") not in (None, ""):
            recovered["lot_sqft"] += 1

    if changed:
        PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    summary = (
        f"King County orphan public fallback changed {changed}/{len(rows)} rows; "
        f"recovered city+ZIP {recovered['city_zip']}, property type {recovered['property_type']}, "
        f"zoning {recovered['zoning']}, lot size {recovered['lot_sqft']}. "
        "No street address, coordinates, value, legal or tax fields were inferred."
    )
    print(summary)

    if STATUS.exists():
        st = json.loads(STATUS.read_text(encoding="utf-8"))
        st.setdefault("notes", []).append(summary)
        for h in st.get("source_health", []):
            if h.get("state") == "WA" and h.get("county") == "King":
                h["note"] = (str(h.get("note") or "") + " " + summary).strip()
        STATUS.write_text(json.dumps(st, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
