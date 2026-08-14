#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
STATUS = ROOT / "data" / "refresh-status.json"
UA = "TaxLienGuideBot/1.6 (public neighborhood research; no access-control bypass)"
ADDRESS_API = "https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services/ADDRESS_POINT_642/FeatureServer/0/query"
ACS_VARS = "NAME,B19013_001E,B25064_001E,B25002_001E,B25002_003E,B25003_001E,B25003_003E"


def get_json(url, params, timeout=45):
    r = requests.get(url, params=params, headers={"User-Agent": UA, "Accept": "application/json"}, timeout=timeout)
    r.raise_for_status()
    return r.json()


def num(v):
    try:
        x = float(v)
        return None if x < 0 else x
    except Exception:
        return None


def area_map(parcels):
    out = {}
    fields = "PIN,ZIP5,CTYNAME,POSTALCTYNAME,LAT,LON,PRIM_ADDR,PRIM_ADDR_FILTER"
    for i in range(0, len(parcels), 80):
        chunk = parcels[i:i+80]
        where = "PIN IN (" + ",".join("'%s'" % p for p in chunk) + ")"
        data = get_json(ADDRESS_API, {
            "f": "json", "where": where, "outFields": fields,
            "returnGeometry": "false", "orderByFields": "PIN,PRIM_ADDR DESC"
        })
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


def acs_zip(zip5, year):
    if not zip5 or len(zip5) != 5:
        return None
    try:
        rows = get_json(
            f"https://api.census.gov/data/{year}/acs/acs5",
            {"get": ACS_VARS, "for": f"zip code tabulation area:{zip5}"}
        )
    except Exception:
        return None
    if not isinstance(rows, list) or len(rows) < 2:
        return None
    d = dict(zip(rows[0], rows[1]))
    income = num(d.get("B19013_001E"))
    rent = num(d.get("B25064_001E"))
    housing = num(d.get("B25002_001E"))
    vacant = num(d.get("B25002_003E"))
    occupied = num(d.get("B25003_001E"))
    renter = num(d.get("B25003_003E"))
    return {
        "median_household_income": income,
        "median_gross_rent": rent,
        "vacancy_proxy_pct": round(vacant / housing * 100, 1) if housing else None,
        "renter_share_pct": round(renter / occupied * 100, 1) if occupied else None,
    }


def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


def metrics(zip5, cache):
    if not zip5:
        return {}
    if zip5 in cache:
        return cache[zip5]
    cur = acs_zip(zip5, 2024)
    old = acs_zip(zip5, 2022)
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
        reasons.append(f"2022–2024 median-rent change {trend:+.1f}%")

    score = int(round(clamp(score)))
    result = {
        **cur,
        "rent_trend_2022_2024_pct": trend,
        "rent_to_income_pct": affordability,
        "rentability_score": score,
        "neighborhood_value_score": score,
        "neighborhood_value_label": "Strong" if score >= 70 else "Moderate" if score >= 50 else "Weak",
        "neighborhood_metric_level": "ZIP/ZCTA proxy",
        "neighborhood_metric_year": "2024 ACS 5-year; trend vs 2022",
        "neighborhood_reasons": reasons,
    }
    cache[zip5] = result
    return result


def main():
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    props = doc.get("properties", [])
    wa = [p for p in props if p.get("state") == "WA" and p.get("county") == "King" and p.get("parcel_id")]
    amap = area_map([str(p["parcel_id"]) for p in wa])
    cache = {}
    area_count = metric_count = 0

    for p in wa:
        a = amap.get(str(p.get("parcel_id")))
        if not a:
            continue
        city = str(a.get("POSTALCTYNAME") or a.get("CTYNAME") or "").strip()
        zip5 = str(a.get("ZIP5") or "").strip()
        p["city"] = city or None
        p["zip"] = zip5 or None
        p["latitude"] = num(a.get("LAT"))
        p["longitude"] = num(a.get("LON"))
        p["area_source"] = "King County GIS Addresses in King County"
        p["area_source_url"] = "https://www5.kingcounty.gov/SDC?Layer=address_point"
        area_count += 1
        m = metrics(zip5, cache)
        if m:
            p.update(m)
            metric_count += 1

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    if STATUS.exists():
        st = json.loads(STATUS.read_text(encoding="utf-8"))
        st.setdefault("notes", []).append(
            f"King County area enrichment matched {area_count}/{len(wa)} parcels; ZIP-level neighborhood metrics matched {metric_count}/{len(wa)}."
        )
        for h in st.get("source_health", []):
            if h.get("state") == "WA" and h.get("county") == "King":
                h["note"] = (h.get("note") or "") + f"; area {area_count}/{len(wa)}, neighborhood metrics {metric_count}/{len(wa)}"
        STATUS.write_text(json.dumps(st, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
