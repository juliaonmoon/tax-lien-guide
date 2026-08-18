#!/usr/bin/env python3
"""Enrich Indiana tax-lien records with official assessed values.

Source: Indiana Gateway for Government Units (gateway.ifionline.org), the
official state platform where county assessors/auditors submit compliance-
checked property data to the Department of Local Government Finance (DLGF).
No login, CAPTCHA, or access-control workaround is used -- the "Real
Property" download is a public form on an official .gov-partnered state
portal.

The downloaded file is a fixed-width "PARCEL" record file. Field byte
positions come directly from the authoritative regulation defining this
format, 50 IAC 26-20-4 ("REAL PROPERTY PARCEL DATA FILE"), not guessed.
Matching against our existing tax-lien records is done by parcel number
with all non-digit characters stripped (Indiana's fixed-width file stores
the 18-digit state parcel number with no punctuation; our records store it
in the conventional dashed/dotted display format, e.g.
"02-12-13-404-011.000-074"). Verified against 5 known Allen County parcels
before this script was written: 5/5 matched with plausible real addresses
and assessed values.

This script only *adds* fields to existing verified records -- it never
creates, removes, or re-derives a record_id, and never touches a county's
records if that county's download fails (see `enrich_county`'s
try/except in `main`).
"""
from __future__ import annotations

import io
import json
import re
import zipfile
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DETAILS = ROOT / "data" / "tax-lien-properties.json"
GATEWAY_URL = "https://gateway.ifionline.org/public/download.aspx"
UA = "TaxLienGuideBot/1.0 (public tax-lien research; no access-control bypass)"

# Dataset/year selections on the Gateway download form.
REAL_PROPERTY_DATASET = "5"
PAY_YEAR = "2025"  # "2025 pay 2026" -- most recent submitted assessment year.

# County name -> Gateway's county code (from the DropDownList3 <option> values).
COUNTY_CODES = {
    "Allen": "02",
    "Grant": "27",
    "Tippecanoe": "79",
    "Wabash": "85",
}

# Fixed-width byte positions for the PARCEL record, per 50 IAC 26-20-4.
# (start, end) are 1-indexed inclusive per the regulation; sliced as [start-1:end].
FIELDS = {
    "parcel_number": (1, 25),
    "property_street_address": (94, 153),
    "property_city": (154, 183),
    "property_zip": (184, 193),
    "av_total_land_and_improvements": (493, 504),
    "legal_description": (750, 1249),
    "current_av_total_land_and_improvements": (1275, 1286),
}


def clean(value: str) -> str | None:
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def parse_av(raw: str) -> float | None:
    raw = raw.strip()
    if not raw or not re.fullmatch(r"-?\d+", raw):
        return None
    value = int(raw)
    return float(value) if value > 0 else None


def slice_field(line: str, name: str) -> str:
    start, end = FIELDS[name]
    return line[start - 1:end]


def download_real_property_file(county_code: str) -> bytes:
    session = requests.Session()
    session.headers.update({"User-Agent": UA})
    page = session.get(GATEWAY_URL, timeout=30)
    page.raise_for_status()
    soup = BeautifulSoup(page.text, "html.parser")

    def hidden(field_id: str) -> str:
        el = soup.find(id=field_id)
        return el.get("value", "") if el else ""

    payload = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": hidden("__VIEWSTATE"),
        "__VIEWSTATEGENERATOR": hidden("__VIEWSTATEGENERATOR"),
        "__EVENTVALIDATION": hidden("__EVENTVALIDATION"),
        "ctl00$ContentPlaceHolder1$DropDownList1": REAL_PROPERTY_DATASET,
        "ctl00$ContentPlaceHolder1$DropDownList2": PAY_YEAR,
        "ctl00$ContentPlaceHolder1$DropDownList3": county_code,
        "ctl00$ContentPlaceHolder1$button2": "Download",
    }
    if not payload["__VIEWSTATE"] or not payload["__EVENTVALIDATION"]:
        raise RuntimeError("Gateway download form is missing expected ASP.NET postback fields")

    response = session.post(GATEWAY_URL, data=payload, timeout=90)
    response.raise_for_status()
    if "zip" not in (response.headers.get("content-type") or "").lower() and not response.content.startswith(b"PK"):
        raise RuntimeError(f"Gateway did not return a zip file (content-type={response.headers.get('content-type')})")
    return response.content


def parse_real_property_records(zip_bytes: bytes) -> dict[str, dict]:
    archive = zipfile.ZipFile(io.BytesIO(zip_bytes))
    names = [n for n in archive.namelist() if n.upper().endswith(".TXT")]
    if not names:
        raise RuntimeError("Real Property zip did not contain a .txt data file")
    text = archive.read(names[0]).decode("latin-1")

    records: dict[str, dict] = {}
    for line in text.split("\n"):
        if not line or line.startswith("PARCEL"):
            continue  # skip blank lines and the header record
        parcel_digits = slice_field(line, "parcel_number").strip()
        if not re.fullmatch(r"\d{10,25}", parcel_digits):
            continue
        current_av = parse_av(slice_field(line, "current_av_total_land_and_improvements"))
        certified_av = parse_av(slice_field(line, "av_total_land_and_improvements"))
        records[parcel_digits] = {
            "assessed_value": certified_av,
            "market_value": current_av if current_av is not None else certified_av,
            "property_address": clean(slice_field(line, "property_street_address")),
            "city": clean(slice_field(line, "property_city")),
            "zip": clean(slice_field(line, "property_zip")),
            "legal_description": clean(slice_field(line, "legal_description")),
        }
    return records


def enrich_county(county: str) -> tuple[dict[str, dict], str]:
    zip_bytes = download_real_property_file(COUNTY_CODES[county])
    records = parse_real_property_records(zip_bytes)
    return records, f"Downloaded and parsed {len(records)} {county} County parcel records from Indiana Gateway"


def apply_enrichment(rows: list[dict], by_parcel: dict[str, dict]) -> int:
    matched = 0
    for row in rows:
        parcel_id = row.get("parcel_id")
        if not parcel_id:
            continue
        digits = re.sub(r"[^0-9]", "", parcel_id)
        record = by_parcel.get(digits)
        if not record:
            continue
        matched += 1
        for key in ("assessed_value", "market_value", "property_address", "city", "zip", "legal_description"):
            if row.get(key) in (None, "") and record.get(key) is not None:
                row[key] = record[key]
        if row.get("address") in (None, "") and record.get("property_address"):
            row["address"] = record["property_address"]
    return matched


def main() -> int:
    doc = json.loads(DETAILS.read_text(encoding="utf-8"))
    verified = date.today().isoformat()
    notes = []
    total_matched = 0

    for county in COUNTY_CODES:
        profile_id = f"IN-{county}-2026"
        county_rows = [p for p in doc["properties"] if p.get("profile_id") == profile_id]
        if not county_rows:
            continue
        try:
            by_parcel, note = enrich_county(county)
        except Exception as exc:  # a failed county enrichment must not touch its rows
            print(f"{county} County: enrichment FAILED, rows left unchanged ({exc})")
            continue
        matched = apply_enrichment(county_rows, by_parcel)
        total_matched += matched
        notes.append(f"{note}; matched {matched}/{len(county_rows)} rows")
        print(f"{county} County: matched {matched}/{len(county_rows)} rows")

    all_rows = doc["properties"]
    doc["counts"]["with_assessed_value"] = sum(
        (p.get("assessed_value") is not None or p.get("market_value") is not None) for p in all_rows
    )
    doc["counts"]["with_address"] = sum(bool(p.get("property_address") or p.get("address")) for p in all_rows)
    doc.setdefault("enrichment_health", []).insert(0, {
        "source": "Indiana Gateway for Government Units -- Real Property assessment data",
        "url": GATEWAY_URL,
        "checked_at": verified,
        "notes": notes,
        "total_matched": total_matched,
    })
    doc["enrichment_health"] = doc["enrichment_health"][:5]  # keep a short recent history, not unbounded growth

    DETAILS.write_text(json.dumps(doc, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Enrichment complete: {total_matched} Indiana tax-lien records matched to official assessed values")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
