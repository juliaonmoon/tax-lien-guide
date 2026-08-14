#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
STATUS = ROOT / "data" / "refresh-status.json"
UA = "TaxLienGuideBot/2.0 (public neighborhood research; no access-control bypass)"
ADDRESS_API = "https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services/ADDRESS_POINT_642/FeatureServer/0/query"
PARCEL_ADDRESS_API = "https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services/PARCEL_ADDRESS_PUB_AREA_3069/FeatureServer/0/query"
PARCEL_GEOM_API = "https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services/PARCEL_AREA_439/FeatureServer/0/query"
CR_API = "https://api.censusreporter.org/1.0/data/show"
TABLES = "B19013,B25064,B25002,B25003"


def get_json(url, params=None, timeout=45):
    r = requests.get(url, params=params or {}, headers={"User-Agent": UA, "Accept": "application/json"}, timeout=timeout)
    r.raise_for_status()
    return r.json()


def num(v):
    try:
        x = float(v)
        return None if x < 0 else x
    except Exception:
        return None


def arcgis_map(url, parcels, fields):
    out = {}
    for i in range(0, len(parcels), 80):
        chunk = parcels[i:i+80]
        where = "PIN IN (" + ",".join("'%s'" % p for p in chunk) + ")"
        try:
            data = get_json(url, {
                "f": "json", "where": where, "outFields": fields,
                "returnGeometry": "false", "orderByFields": "PIN"
            })
        except Exception:
            continue
        for feature in data.get("features", []):
            a = feature.get("attributes", {})
            pin = str(a.get("PIN") or "").strip()
            if pin and pin not in out:
                out[pin] = a
    return out


def area_map(parcels):
    out = {}
    fields = "PIN,ADDR_FULL,ZIP5,CTYNAME,POSTALCTYNAME,LAT,LON,PRIM_ADDR,PRIM_ADDR_FILTER"
    for i in range(0, len(parcels), 80):
        chunk = parcels[i:i+80]
        where = "PIN IN (" + ",".join("'%s'" % p for p in chunk) + ")"
        try:
            data = get_json(ADDRESS_API, {
                "f": "json", "where": where, "outFields": fields,
                "returnGeometry": "false", "orderByFields": "PIN,PRIM_ADDR DESC"
            })
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


def parcel_geometry_map(parcels):
    out = {}
    for i in range(0, len(parcels), 80):
        chunk = parcels[i:i+80]
        where = "PIN IN (" + ",".join("'%s'" % p for p in chunk) + ")"
        try:
            data = get_json(PARCEL_GEOM_API, {
                "f": "json", "where": where, "outFields": "PIN",
                "returnGeometry": "true", "returnCentroid": "true", "outSR": 4326
            })
        except Exception:
            continue
        for feature in data.get("features", []):
            pin = str((feature.get("attributes") or {}).get("PIN") or "").strip()
            if pin and pin not in out:
                out[pin] = {"geometry": feature.get("geometry"), "centroid": feature.get("centroid")}
    return out


def spatial_address(parcel_geometry):
    if not parcel_geometry:
        return {}
    try:
        data = get_json(ADDRESS_API, {
            "f": "json",
            "where": "1=1",
            "geometry": json.dumps(parcel_geometry),
            "geometryType": "esriGeometryPolygon",
            "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "PIN,ADDR_FULL,ZIP5,CTYNAME,POSTALCTYNAME,LAT,LON,PRIM_ADDR,PRIM_ADDR_FILTER",
            "returnGeometry": "false",
            "orderByFields": "PRIM_ADDR DESC",
            "resultRecordCount": 10,
        })
    except Exception:
        return {}
    features = data.get("features", [])
    if not features:
        return {}
    return features[0].get("attributes", {}) or {}


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
            return num(g.get(table, {}).get("estimate", {}).get(col))
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
    parcels = [str(p["parcel_id"]) for p in wa]
    amap = area_map(parcels)
    pfields = "PIN,ADDR_FULL,ZIP5,CTYNAME,POSTALCTYNAME,LAT,LON,APPRLNDVAL,APPR_IMPR,TAX_LNDVAL,TAX_IMPR,PROPTYPE,PREUSE_DESC,KCA_ZONING,KCA_ACRES,LEGALDESC"
    pmap = arcgis_map(PARCEL_ADDRESS_API, parcels, pfields)
    gmap = parcel_geometry_map(parcels)
    cache = {}
    parcel_count = spatial_address_count = 0

    for p in wa:
        pin = str(p.get("parcel_id"))
        a = amap.get(pin) or {}
        pi = pmap.get(pin) or {}
        pg = gmap.get(pin) or {}
        if pi:
            parcel_count += 1

        # If the PIN-based address join misses, use an official address point that
        # spatially intersects the parcel polygon. This avoids assigning a nearby
        # street address unless King County's own GIS places that point in the parcel.
        if not (a.get("ADDR_FULL") or pi.get("ADDR_FULL")) and pg.get("geometry"):
            spatial = spatial_address(pg.get("geometry"))
            if spatial.get("ADDR_FULL"):
                a = spatial
                spatial_address_count += 1

        city = str(a.get("POSTALCTYNAME") or a.get("CTYNAME") or pi.get("POSTALCTYNAME") or pi.get("CTYNAME") or "").strip()
        zip5 = str(a.get("ZIP5") or pi.get("ZIP5") or p.get("zip") or "").strip()[:5]
        lat = num(a.get("LAT")) or num(pi.get("LAT"))
        lon = num(a.get("LON")) or num(pi.get("LON"))
        centroid = pg.get("centroid") or {}
        if lat is None:
            lat = num(centroid.get("y"))
        if lon is None:
            lon = num(centroid.get("x"))
        addr = str(a.get("ADDR_FULL") or pi.get("ADDR_FULL") or "").strip()

        p["city"] = city or p.get("city")
        p["zip"] = zip5 or p.get("zip")
        p["latitude"] = lat if lat is not None else p.get("latitude")
        p["longitude"] = lon if lon is not None else p.get("longitude")
        if addr:
            suffix = ", ".join(x for x in [city, "WA", zip5] if x)
            p["address"] = f"{addr}, {suffix}" if suffix else addr
            p["address_status"] = "Official situs address"
        else:
            p["address"] = None
            p["address_status"] = "No assigned situs address found in King County GIS"
        p["area_source"] = "King County GIS"
        p["area_source_url"] = "https://www5.kingcounty.gov/SDC?Layer=address_point"

        # Prefer current appraised values; fall back to taxable values when appraised fields are blank.
        appr_land = num(pi.get("APPRLNDVAL"))
        appr_impr = num(pi.get("APPR_IMPR"))
        tax_land = num(pi.get("TAX_LNDVAL"))
        tax_impr = num(pi.get("TAX_IMPR"))
        land = appr_land if appr_land is not None else tax_land
        impr = appr_impr if appr_impr is not None else tax_impr
        if land is not None:
            p["land_value"] = land
        if impr is not None:
            p["improvement_value"] = impr
        if (land or 0) + (impr or 0) > 0:
            p["assessed_value"] = (land or 0) + (impr or 0)
            p["market_value"] = p["assessed_value"]
            p["value_basis"] = "King County appraised value" if (appr_land is not None or appr_impr is not None) else "King County taxable value fallback"

        if pi.get("PREUSE_DESC"):
            p["property_type"] = pi.get("PREUSE_DESC")
        elif pi.get("PROPTYPE") and not p.get("property_type"):
            p["property_type"] = pi.get("PROPTYPE")
        if pi.get("LEGALDESC") and not p.get("legal_description"):
            p["legal_description"] = pi.get("LEGALDESC")
        if pi.get("KCA_ZONING"):
            p["zoning"] = pi.get("KCA_ZONING")
        acres = num(pi.get("KCA_ACRES"))
        if acres is not None:
            p["acres"] = acres
        p["parcel_enrichment_source"] = "King County Parcels with Address, Property and Ownership Information"

        m = metrics(zip5, cache)
        if m:
            p.update(m)

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    if STATUS.exists():
        st = json.loads(STATUS.read_text(encoding="utf-8"))
        total = len(wa)
        counts = {
            "address": sum(bool(p.get("address")) for p in wa),
            "city_zip": sum(bool(p.get("city") and p.get("zip")) for p in wa),
            "coordinates": sum(p.get("latitude") is not None and p.get("longitude") is not None for p in wa),
            "value": sum(p.get("assessed_value") not in (None, "") for p in wa),
            "property_type": sum(bool(p.get("property_type")) for p in wa),
            "legal": sum(bool(p.get("legal_description")) for p in wa),
            "neighborhood": sum(p.get("neighborhood_value_score") is not None for p in wa),
        }
        summary = (
            f"King County verified fill: parcel-layer {parcel_count}/{total}; address {counts['address']}/{total} "
            f"(+{spatial_address_count} recovered spatially); city+ZIP {counts['city_zip']}/{total}; "
            f"coordinates {counts['coordinates']}/{total}; assessed value {counts['value']}/{total}; "
            f"property type {counts['property_type']}/{total}; legal {counts['legal']}/{total}; "
            f"neighborhood metrics {counts['neighborhood']}/{total}."
        )
        st.setdefault("notes", []).append(summary)
        for h in st.get("source_health", []):
            if h.get("state") == "WA" and h.get("county") == "King":
                h["note"] = summary
        STATUS.write_text(json.dumps(st, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
