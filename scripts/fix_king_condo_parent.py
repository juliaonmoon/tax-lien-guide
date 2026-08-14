#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
STATUS = ROOT / "data" / "refresh-status.json"
UA = "TaxLienGuideBot/2.3 (public parcel research; no access-control bypass)"
ADDRESS_API = "https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services/ADDRESS_POINT_642/FeatureServer/0/query"
PARCEL_API = "https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services/PARCEL_ADDRESS_PUB_AREA_3069/FeatureServer/0/query"
PARCEL_GEOM_API = "https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services/PARCEL_AREA_439/FeatureServer/0/query"
CR_API = "https://api.censusreporter.org/1.0/data/show"
TABLES = "B19013,B25064,B25002,B25003"


def get_json(url, params=None, timeout=45):
    r = requests.get(url, params=params or {}, headers={"User-Agent": UA, "Accept": "application/json"}, timeout=timeout)
    r.raise_for_status()
    return r.json()


def coord(v):
    try:
        return float(v)
    except Exception:
        return None


def nonneg(v):
    try:
        x = float(v)
        return None if x < 0 else x
    except Exception:
        return None


def parent_pin(pin):
    pin = str(pin or "").strip()
    if len(pin) != 10 or not pin.isdigit() or pin.endswith("0000"):
        return None
    return pin[:6] + "0000"


def query(url, pins, fields, geometry=False):
    out = {}
    pins = sorted(set(p for p in pins if p))
    for i in range(0, len(pins), 80):
        chunk = pins[i:i + 80]
        where = "PIN IN (" + ",".join("'%s'" % p for p in chunk) + ")"
        params = {
            "f": "json",
            "where": where,
            "outFields": fields,
            "returnGeometry": "true" if geometry else "false",
            "outSR": 4326,
        }
        if geometry:
            params["returnCentroid"] = "true"
        try:
            data = get_json(url, params)
        except Exception:
            continue
        for feature in data.get("features", []):
            attrs = feature.get("attributes", {}) or {}
            pin = str(attrs.get("PIN") or "").strip()
            if not pin:
                continue
            out[pin] = {"attributes": attrs, "geometry": feature.get("geometry"), "centroid": feature.get("centroid")}
    return out


def cr_zip(zip5, year):
    if not zip5 or len(zip5) != 5:
        return None
    geoid = f"86000US{zip5}"
    release = f"acs{year}_5yr"
    try:
        doc = get_json(f"{CR_API}/{release}", {"table_ids": TABLES, "geo_ids": geoid})
        g = doc.get("data", {}).get(geoid, {})
        if not g:
            return None
        def est(table, col):
            return nonneg(g.get(table, {}).get("estimate", {}).get(col))
        income = est("B19013", "B19013001")
        rent = est("B25064", "B25064001")
        housing = est("B25002", "B25002001")
        vacant = est("B25002", "B25002003")
        occupied = est("B25003", "B25003001")
        renter = est("B25003", "B25003003")
        return {
            "median_household_income": income,
            "median_gross_rent": rent,
            "vacancy_proxy_pct": round(vacant / housing * 100, 1) if housing else None,
            "renter_share_pct": round(renter / occupied * 100, 1) if occupied else None,
            "acs_release_year": year,
        }
    except Exception:
        return None


def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


def metrics(zip5, cache):
    if not zip5:
        return {}
    if zip5 in cache:
        return cache[zip5]
    cur = cr_zip(zip5, 2024)
    old = cr_zip(zip5, 2022) if cur else None
    cur_year, old_year = 2024, 2022
    if not cur:
        cur = cr_zip(zip5, 2023)
        old = cr_zip(zip5, 2021) if cur else None
        cur_year, old_year = 2023, 2021
    if not cur:
        cache[zip5] = {}
        return {}
    renter = cur.get("renter_share_pct")
    vacancy = cur.get("vacancy_proxy_pct")
    income = cur.get("median_household_income")
    rent = cur.get("median_gross_rent")
    old_rent = old.get("median_gross_rent") if old else None
    trend = round((rent / old_rent - 1) * 100, 1) if rent and old_rent else None
    affordability = round(rent * 12 / income * 100, 1) if rent and income else None
    score = 50.0
    reasons = []
    if renter is not None:
        score += clamp((renter - 30) * 0.7, -10, 15)
        reasons.append(f"{renter:.1f}% renter share")
    if vacancy is not None:
        score += clamp((7 - vacancy) * 2.2, -15, 15)
        reasons.append(f"{vacancy:.1f}% housing vacancy proxy")
    if affordability is not None:
        if affordability <= 25:
            score += 8
        elif affordability <= 35:
            score += 3
        elif affordability > 45:
            score -= 8
        reasons.append(f"median rent ≈ {affordability:.1f}% of median income")
    if trend is not None:
        score += clamp(trend * 0.45, -8, 8)
        reasons.append(f"{old_year}–{cur_year} median-rent change {trend:+.1f}%")
    score = int(round(clamp(score)))
    result = {
        **cur,
        "rent_trend_pct": trend,
        "rent_trend_period": f"{old_year}-{cur_year}" if trend is not None else None,
        "rent_to_income_pct": affordability,
        "rentability_score": score,
        "neighborhood_value_score": score,
        "neighborhood_value_label": "Strong" if score >= 70 else "Moderate" if score >= 50 else "Weak",
        "neighborhood_metric_level": "ZIP/ZCTA proxy",
        "neighborhood_metric_year": f"{cur_year} ACS 5-year via Census Reporter",
        "neighborhood_reasons": reasons,
    }
    cache[zip5] = result
    return result


def main():
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    props = doc.get("properties", [])
    wa = [p for p in props if p.get("state") == "WA" and p.get("county") == "King" and p.get("parcel_id")]
    mapping = {str(p["parcel_id"]): parent_pin(p["parcel_id"]) for p in wa}
    parents = [x for x in mapping.values() if x]

    afields = "PIN,ADDR_FULL,ZIP5,CTYNAME,POSTALCTYNAME,LAT,LON,PRIM_ADDR,PRIM_ADDR_FILTER"
    pfields = "PIN,ADDR_FULL,ZIP5,CTYNAME,POSTALCTYNAME,LAT,LON,PROPTYPE,PREUSE_DESC,KCA_ZONING,KCA_ACRES"
    amap = query(ADDRESS_API, parents, afields)
    pmap = query(PARCEL_API, parents, pfields)
    gmap = query(PARCEL_GEOM_API, parents, "PIN", geometry=True)

    recovered = address_recovered = area_recovered = coord_recovered = type_recovered = 0
    cache = {}
    for p in wa:
        pin = str(p.get("parcel_id"))
        parent = mapping.get(pin)
        if not parent:
            continue
        a = (amap.get(parent) or {}).get("attributes", {})
        pi = (pmap.get(parent) or {}).get("attributes", {})
        pg = gmap.get(parent) or {}
        if not (a or pi or pg):
            continue

        changed = False
        city = str(a.get("POSTALCTYNAME") or a.get("CTYNAME") or pi.get("POSTALCTYNAME") or pi.get("CTYNAME") or "").strip()
        zip5 = str(a.get("ZIP5") or pi.get("ZIP5") or "").strip()[:5]
        addr = str(a.get("ADDR_FULL") or pi.get("ADDR_FULL") or "").strip()

        if not p.get("city") and city:
            p["city"] = city
            changed = True
        if not p.get("zip") and zip5:
            p["zip"] = zip5
            changed = True
        if changed and p.get("city") and p.get("zip"):
            area_recovered += 1

        if not p.get("address") and addr:
            suffix = ", ".join(x for x in [city, "WA", zip5] if x)
            p["address"] = f"{addr}, {suffix}" if suffix else addr
            p["address_status"] = "Condo unit mapped to official condo-complex situs address"
            p["address_basis"] = f"King County condo-complex parent parcel {parent}"
            address_recovered += 1
            changed = True

        if p.get("latitude") is None or p.get("longitude") is None:
            lat = coord(a.get("LAT"))
            lon = coord(a.get("LON"))
            source = "King County condo-complex address point"
            if lat is None or lon is None:
                lat = coord(pi.get("LAT"))
                lon = coord(pi.get("LON"))
                source = "King County condo-complex parcel-address layer"
            if lat is None or lon is None:
                centroid = pg.get("centroid") or {}
                lat = coord(centroid.get("y"))
                lon = coord(centroid.get("x"))
                source = "King County condo-complex parcel centroid"
            if lat is not None and lon is not None:
                p["latitude"] = lat
                p["longitude"] = lon
                p["coordinate_source"] = source
                p["coordinate_basis"] = f"parent parcel {parent}"
                coord_recovered += 1
                changed = True

        if not p.get("property_type"):
            pt = pi.get("PREUSE_DESC") or pi.get("PROPTYPE")
            if pt:
                p["property_type"] = str(pt)
                p["property_type_basis"] = f"King County condo-complex parent parcel {parent}; unit-specific type unavailable in public parcel layer"
                type_recovered += 1
                changed = True

        if p.get("zip") and p.get("neighborhood_value_score") is None:
            m = metrics(str(p.get("zip"))[:5], cache)
            if m:
                p.update(m)
                changed = True

        if changed:
            p["condo_parent_parcel"] = parent
            recovered += 1

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    if STATUS.exists():
        st = json.loads(STATUS.read_text(encoding="utf-8"))
        counts = {
            "address": sum(bool(p.get("address")) for p in wa),
            "city_zip": sum(bool(p.get("city") and p.get("zip")) for p in wa),
            "coordinates": sum(p.get("latitude") is not None and p.get("longitude") is not None for p in wa),
            "property_type": sum(bool(p.get("property_type")) for p in wa),
            "neighborhood": sum(p.get("neighborhood_value_score") is not None for p in wa),
        }
        note = (
            f"King County condo-parent fallback changed {recovered}/{len(wa)} rows; "
            f"recovered address {address_recovered}, city/ZIP {area_recovered}, coordinates {coord_recovered}, property type {type_recovered}. "
            f"Current fill: address {counts['address']}/{len(wa)}, city+ZIP {counts['city_zip']}/{len(wa)}, "
            f"coordinates {counts['coordinates']}/{len(wa)}, property type {counts['property_type']}/{len(wa)}, "
            f"neighborhood metrics {counts['neighborhood']}/{len(wa)}."
        )
        st.setdefault("notes", []).append(note)
        for h in st.get("source_health", []):
            if h.get("state") == "WA" and h.get("county") == "King":
                h["note"] = (h.get("note") or "") + " " + note
        STATUS.write_text(json.dumps(st, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
