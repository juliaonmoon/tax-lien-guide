#!/usr/bin/env python3
"""Refresh public Florida tax-deed / lands-available property rows.

The sale inventory comes from county clerks. Parcel attributes come from the
Florida Department of Revenue statewide cadastral FeatureServer. No login,
CAPTCHA, or access-control workaround is used. A dated official-page snapshot
keeps the last verified Putnam inventory available when that small county host
is temporarily unreachable from GitHub Actions.
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
STATUS = ROOT / "data" / "refresh-status.json"
REGISTRY = ROOT / "data" / "county-sources.json"
PUTNAM_SNAPSHOT = ROOT / "data" / "florida-putnam-verified-snapshot.json"

PUTNAM_URL = "https://apps.putnam-fl.com/coc/taxdeeds/public/public_LAFT.php"
ESCAMBIA_URL = "https://public.escambiaclerk.com/taxsale/landsavailable.asp"
CADASTRAL = "https://services9.arcgis.com/Gh9awoU677aKree0/ArcGIS/rest/services/Florida_Statewide_Cadastral/FeatureServer/0/query"
UA = "TaxLienGuideBot/1.6 (public-record research; no access-control bypass)"

DOR_USE = {
    "0000": "Vacant residential",
    "0001": "Single-family residential",
    "0002": "Mobile home",
    "0003": "Multi-family residential",
    "0004": "Condominium",
    "0005": "Cooperative",
    "0010": "Vacant commercial",
    "0011": "Store / retail",
    "0040": "Vacant industrial",
    "0050": "Improved agricultural",
    "0099": "Acreage / non-agricultural",
}


def fetch(url: str, params: dict | None = None, timeout: int = 35) -> str:
    if params:
        url += ("&" if "?" in url else "?") + urlencode(params)
    req = Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/json"})
    with urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", "replace")


def visible_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(?:script|style).*?>.*?</(?:script|style)>", " ", raw)
    raw = re.sub(r"(?i)<(?:br\s*/?|/p|/div|/tr|/td|hr)[^>]*>", "\n", raw)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"[ \t]+", " ", html.unescape(raw)).replace("\r", "")


def money(value: str) -> float | None:
    try:
        return float(re.sub(r"[^0-9.-]", "", value))
    except (TypeError, ValueError):
        return None


def putnam_live() -> list[list]:
    text = visible_text(fetch(PUTNAM_URL))
    matches = list(re.finditer(r"T\.D\.\s*(\d{4}-\d+)\s+([^\n]+)", text, re.I))
    records = []
    for index, match in enumerate(matches):
        block = text[match.end(): matches[index + 1].start() if index + 1 < len(matches) else len(text)]
        parcel = re.search(r"Parcel Number\s+([0-9-]{18,30})", block, re.I)
        auction = re.search(r"Auction date:\s*(\d{2}/\d{2}/\d{4})", block, re.I)
        available = re.search(r"Available for Purchase:\s*(\d{2}/\d{2}/\d{4})", block, re.I)
        price = re.search(r"Estimated Purchase Price:\s*(\$[\d,]+(?:\.\d{2})?)", block, re.I)
        if not (parcel and auction and available and price):
            continue
        legal_match = re.search(r"TDA Certification\s+(.+?)\s+Parcel Number", block, re.I | re.S)
        legal = re.sub(r"\s+", " ", legal_match.group(1)).strip() if legal_match else None
        records.append([match.group(1), match.group(2).strip(), parcel.group(1), legal,
                        auction.group(1), available.group(1), money(price.group(1))])
    if len(records) < 10:
        raise RuntimeError(f"Putnam parser found only {len(records)} records")
    return records


def putnam_snapshot() -> tuple[list[list], str]:
    payload = json.loads(PUTNAM_SNAPSHOT.read_text(encoding="utf-8"))
    return payload["records"], payload["verified_at"]


def base_row(county: str, case: str, owner: str | None, parcel: str,
             legal: str | None, sale_date: str, available_date: str | None,
             opening_bid: float | None, source_url: str) -> dict:
    return {
        "state": "FL", "state_name": "Florida", "county": county,
        "case_number": case, "parcel_id": parcel, "owner": owner,
        "legal_description": legal, "sale_date": sale_date,
        "available_date": available_date, "sale_status": "Lands available",
        "opening_bid": opening_bid,
        "opening_bid_note": None if opening_bid is not None else "Request a current purchase quote from the Clerk",
        "address": None, "city": None, "zip": None,
        "assessed_value": None, "market_value": None, "land_value": None,
        "property_type": None, "acreage": None, "living_area_sqft": None,
        "year_built": None, "homestead_value": None,
        "official_url": source_url, "source_document": source_url,
        "auction_url": source_url, "title_review_status": "not_reviewed",
        "data_completeness": "county lands-available list + FDOR cadastral enrichment",
        "appraisal_source": "Florida DOR statewide cadastral / county property appraiser",
        "appraisal_year": 2025,
    }


def escambia_live() -> list[dict]:
    text = visible_text(fetch(ESCAMBIA_URL))
    pattern = re.compile(
        r"(\d{4}-\d+)\s+(\d{6,12})\s+(\d{4,8})\s+([0-9A-Z]{12,24})\s+"
        r"(\d{1,2}/\d{1,2}/\d{4})\s+\*{0,2}(\$[\d,]+(?:\.\d{2})?)\s+(.+?)(?=\n\s*\d{4}-\d+|$)",
        re.I | re.S,
    )
    rows = []
    for m in pattern.finditer(text):
        row = base_row("Escambia", m.group(1), None, m.group(4),
                       re.sub(r"\s+", " ", m.group(7)).strip(), m.group(5), None,
                       money(m.group(6)), ESCAMBIA_URL)
        row["account_number"] = m.group(2)
        row["certificate_number"] = m.group(3)
        row["property_viewer_url"] = f"https://www.escpa.org/cama/Detail_a.aspx?a={m.group(2)}"
        rows.append(row)
    return rows


def cadastral_enrich(rows: list[dict]) -> tuple[int, str]:
    by_parcel = {row["parcel_id"]: row for row in rows}
    matched = 0
    fields = ("PARCEL_ID,ASMNT_YR,DOR_UC,JV,AV_SD,AV_NSD,JV_HMSTD,AV_HMSTD,"
              "LND_VAL,LND_SQFOOT,TOT_LVG_AR,NO_BULDNG,ACT_YR_BLT,PHY_ADDR1,"
              "PHY_ADDR2,PHY_CITY,PHY_ZIPCD,S_LEGAL,OWN_NAME")
    parcels = list(by_parcel)
    errors = []
    for start in range(0, len(parcels), 18):
        chunk = parcels[start:start + 18]
        quoted = ",".join("'" + p.replace("'", "''") + "'" for p in chunk)
        try:
            payload = json.loads(fetch(CADASTRAL, {
                "where": f"PARCEL_ID IN ({quoted})", "outFields": fields,
                "returnGeometry": "false", "f": "json",
            }, timeout=60))
            if payload.get("error"):
                raise RuntimeError(str(payload["error"]))
        except Exception as exc:
            errors.append(type(exc).__name__)
            continue
        for feature in payload.get("features", []):
            a = feature.get("attributes", {})
            row = by_parcel.get(str(a.get("PARCEL_ID") or "").strip())
            if not row:
                continue
            matched += 1
            addr = " ".join(str(a.get(k) or "").strip() for k in ("PHY_ADDR1", "PHY_ADDR2")).strip()
            assessed = max(float(a.get("AV_SD") or 0), float(a.get("AV_NSD") or 0)) or None
            row.update({
                "address": addr or None,
                "city": str(a.get("PHY_CITY") or "").strip() or None,
                "zip": str(int(a["PHY_ZIPCD"])).zfill(5) if a.get("PHY_ZIPCD") else None,
                "assessed_value": assessed,
                "market_value": float(a.get("JV") or 0) or None,
                "land_value": float(a.get("LND_VAL") or 0) or None,
                "property_type": DOR_USE.get(str(a.get("DOR_UC") or "").zfill(4), f"DOR use {a.get('DOR_UC')}") if a.get("DOR_UC") is not None else None,
                "acreage": round(float(a.get("LND_SQFOOT") or 0) / 43560, 3) if a.get("LND_SQFOOT") else None,
                "living_area_sqft": float(a.get("TOT_LVG_AR") or 0) or None,
                "building_count": int(a.get("NO_BULDNG") or 0) or None,
                "year_built": int(a.get("ACT_YR_BLT") or 0) or None,
                "homestead_value": float(a.get("JV_HMSTD") or 0) or None,
                "assessed_homestead_value": float(a.get("AV_HMSTD") or 0) or None,
                "appraisal_year": int(a.get("ASMNT_YR") or 2025),
            })
            if not row.get("legal_description") and a.get("S_LEGAL"):
                row["legal_description"] = str(a["S_LEGAL"]).strip()
            if not row.get("owner") and a.get("OWN_NAME"):
                row["owner"] = str(a["OWN_NAME"]).strip()
            if not row.get("address") and row.get("property_type", "").lower().startswith("vacant"):
                row["address_note"] = "No situs address published — vacant land"
            if not row.get("living_area_sqft") and row.get("property_type", "").lower().startswith("vacant"):
                row["improvement_note"] = "Vacant land — no building area or year built published"
            if row["county"] == "Putnam":
                row["property_viewer_url"] = "https://pamap.putnam-fl.gov/PropertyAppraiserPublicMap/?find=" + quote(row["parcel_id"])
    note = f"FDOR cadastral matched {matched}/{len(rows)} Florida parcels"
    if errors:
        note += f"; {len(errors)} batch error(s): {', '.join(errors)}"
    return matched, note


def score(row: dict) -> dict:
    points, reasons = 45, []
    value = row.get("assessed_value") or row.get("market_value")
    bid = row.get("opening_bid")
    if value and bid:
        ratio = bid / value
        row["bid_to_assessed_ratio"] = round(ratio, 4)
        if ratio <= .10:
            points += 20; reasons.append("opening bid <=10% of assessed value")
        elif ratio <= .25:
            points += 10; reasons.append("opening bid <=25% of assessed value")
        elif ratio >= .70:
            points -= 20; reasons.append("opening bid >=70% of assessed value")
    if row.get("address"):
        points += 5; reasons.append("physical address captured")
    if value:
        points += 5; reasons.append("official appraisal value captured")
    if row.get("property_type"):
        points += 5; reasons.append("property use captured")
    if not row.get("title_review_status") or row.get("title_review_status") == "not_reviewed":
        points -= 10; reasons.append("title and surviving liens not reviewed")
    points = max(0, min(100, points))
    return {"score": points, "label": "High research priority" if points >= 70 else "Medium research priority" if points >= 45 else "Low research priority", "reasons": reasons}


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    health = []
    try:
        records = putnam_live()
        putnam_note = f"Live official list parsed: {len(records)} lands-available parcels"
        putnam_ok = True
    except Exception as exc:
        records, verified = putnam_snapshot()
        putnam_note = f"Official host unavailable ({type(exc).__name__}); preserved {len(records)} parcels from verified {verified} snapshot"
        putnam_ok = False
    florida = [base_row("Putnam", *record, PUTNAM_URL) for record in records]
    try:
        escambia = escambia_live()
        escambia_note = f"Live official list parsed: {len(escambia)} lands-available parcels"
        escambia_ok = True
    except Exception as exc:
        # Verified directly on the official Clerk page on 2026-08-15. Keep the
        # row during Cloudflare/automation blocks; a later successful live
        # parse replaces it rather than accumulating stale rows.
        row = base_row(
            "Escambia", "0226-64", None, "211N301302000000",
            "BEG AT INTER OF W LI OF PALAFOX H/W AND N LI OF S1/2 OF SW1/4 OF NE1/4 SELY ALG H/W 406 FT WLY PARL TO N LI OF S1/2 OF SW1/4 OF NE1/4 TO E LI OF FRISCO RR R/W NLY ALG RR R/W TO N LI OF S1/2 OF SW1/4 OF NE1/4 E ALG SAID N LI TO POB OR 5347 P 1182",
            "03/04/2026", None, 3371.77, ESCAMBIA_URL,
        )
        row["account_number"] = "110553000"
        row["certificate_number"] = "06325"
        row["property_viewer_url"] = "https://www.escpa.org/cama/Detail_a.aspx?a=110553000"
        escambia = [row]
        escambia_note = f"Official host blocked automation ({type(exc).__name__}); preserved 1 parcel from verified 2026-08-15 official-page snapshot"
        escambia_ok = False
    florida.extend(escambia)
    _, enrich_note = cadastral_enrich(florida)
    for row in florida:
        row["research_priority"] = score(row)

    payload = json.loads(PROPS.read_text(encoding="utf-8"))
    existing = [p for p in payload.get("properties", []) if p.get("state") != "FL"]
    payload["updated_at"] = now
    # Preserve the existing collector order so a Florida refresh does not
    # create a huge unrelated diff for Washington, Texas, and Arizona rows.
    florida.sort(key=lambda p: (p.get("county") or "", p.get("parcel_id") or ""))
    payload["properties"] = existing + florida
    PROPS.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    counties = [c for c in registry.get("counties", []) if not (c.get("state") == "FL" and c.get("county") in {"Putnam", "Escambia"})]
    counties.extend([
        {"state": "FL", "state_name": "Florida", "county": "Putnam", "source_url": PUTNAM_URL, "auction_url": PUTNAM_URL, "coverage": "lands_available_property_feed"},
        {"state": "FL", "state_name": "Florida", "county": "Escambia", "source_url": ESCAMBIA_URL, "auction_url": "https://www.escambia.realtaxdeed.com/", "coverage": "lands_available_property_feed"},
    ])
    registry["updated_at"] = now
    registry["counties"] = counties
    REGISTRY.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    status = json.loads(STATUS.read_text(encoding="utf-8"))
    source_health = [h for h in status.get("source_health", []) if not (h.get("state") == "FL" and h.get("county") in {"Putnam", "Escambia"})]
    source_health.extend([
        {"state": "FL", "county": "Putnam", "source_url": PUTNAM_URL, "checked_at": now, "ok": putnam_ok, "note": putnam_note + "; " + enrich_note},
        {"state": "FL", "county": "Escambia", "source_url": ESCAMBIA_URL, "checked_at": now, "ok": escambia_ok, "note": escambia_note + "; " + enrich_note},
    ])
    status.update({
        "updated_at": now, "property_count": len(payload["properties"]),
        "states_tracked": len({c.get("state") for c in counties}),
        "counties_tracked": len(counties), "official_sources_registered": len(counties),
        "source_health": source_health,
    })
    notes = [n for n in status.get("notes", []) if not n.startswith("Florida property expansion:")]
    notes.append(f"Florida property expansion: {len(florida)} individual lands-available tax-deed parcels across Putnam and Escambia; {enrich_note}.")
    status["notes"] = notes
    STATUS.write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(f"Published {len(florida)} Florida tax-deed properties. {enrich_note}. {putnam_note}. {escambia_note}.")


if __name__ == "__main__":
    main()
