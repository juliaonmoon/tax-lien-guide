#!/usr/bin/env python3
"""Refresh Oklahoma County, OK's official county-owned resale property list.

Source: the Treasurer's own "ACTIVE RESALE ACCOUNTS" / county-owned parcel
list (docs.oklahomacounty.org/treasurer/CountyOwnedList.asp) -- parcels that
received no bidder at the annual June resale auction and are now owned by
the county, available for direct purchase (or, occasionally, scheduled for
a future public resale). No login, CAPTCHA, or access-control workaround is
used; a plain HTTP fetch without a browser-like User-Agent previously
appeared blocked, which turned out to be ordinary bot-UA filtering.

Owner names are intentionally never collected in bulk (repo-wide privacy
convention, see STATUS.md / BUG-004 / BUG-005 in BUGS.md). This source's own
table does not publish owner names at all -- only parcel number, scheduled
sale date (if any), bid amounts, and a city-only placeholder address -- so
there is nothing to filter out at this stage. A separate per-parcel Assessor
detail page *does* carry current and historical owner/grantor/grantee names
and is deliberately not fetched by this collector; enriching from it safely
(legal description, land value, land size -- never the owner/deed-history
sections) is a documented follow-up, not done here.
"""
from __future__ import annotations

import html as html_module
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"

SOURCE_URL = "https://docs.oklahomacounty.org/treasurer/CountyOwnedList.asp"
UA = "TaxLienGuideBot/1.0 (public-record research; no access-control bypass)"

PARCEL_RE = re.compile(r"^\d{4}-\d{2}-\d{3}-\d{4}$")
MIN_ROWS = 150  # observed 196 on 2026-08-19; leaves room for daily fluctuation


def fetch_html() -> str:
    response = requests.get(SOURCE_URL, headers={"User-Agent": UA, "Accept": "text/html"}, timeout=30)
    response.raise_for_status()
    return response.text


def _text(cell_html: str) -> str:
    cell_html = re.sub(r"<[^>]+>", " ", cell_html)
    return re.sub(r"\s+", " ", html_module.unescape(cell_html)).strip()


def _href(cell_html: str) -> str | None:
    m = re.search(r'href="([^"]+)"', cell_html)
    return m.group(1) if m else None


def _money(text: str) -> float | None:
    m = re.search(r"-?[\d,]+(?:\.\d{1,2})?", text)
    if not m:
        return None
    return round(float(m.group().replace(",", "")), 2)


def parse_county_owned_list(raw_html: str, verified: str) -> list[dict]:
    output: list[dict] = []
    seen: set[str] = set()

    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", raw_html, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(cells) != 7:
            continue

        parcel_no = _text(cells[1])
        if not PARCEL_RE.fullmatch(parcel_no) or parcel_no in seen:
            continue
        seen.add(parcel_no)

        suggested_bid = _money(_text(cells[5]))
        if suggested_bid is None:
            continue
        initial_bid = _money(_text(cells[4]))

        scheduled_raw = _text(cells[3])
        sale_date = None
        sale_status = (
            "County-owned; available for direct purchase from the Treasurer "
            "(not yet scheduled for a public resale)"
        )
        if scheduled_raw.upper() != "N/A":
            m = re.match(r"(\d{1,2}/\d{1,2}/\d{4})", scheduled_raw)
            if m:
                sale_date = m.group(1)
                sale_status = "County-owned; scheduled for a public resale"

        # This column is "Physical Address Per Assessor/Legal Description".
        # In practice it is almost always a "0 UNKNOWN <CITY>" placeholder
        # (no situs address on file, typically vacant/unaddressed remnant
        # parcels) -- treat that pattern as city-only, never a real address.
        addr_legal = _text(cells[6])
        city = None
        address = None
        m = re.match(r"^0\s+UNKNOWN\s+(.+)$", addr_legal, re.I)
        if m:
            city = m.group(1).strip().title()
        elif addr_legal:
            address = addr_legal

        output.append({
            "state": "OK",
            "state_name": "Oklahoma",
            "county": "Oklahoma",
            "case_number": None,
            "parcel_id": parcel_no,
            "owner": None,
            "legal_description": None,
            "sale_date": sale_date,
            "available_date": None,
            "sale_status": sale_status,
            "opening_bid": suggested_bid,
            "opening_bid_note": None,
            "county_initial_bid_amount": initial_bid,
            "address": address,
            "city": city,
            "zip": None,
            "assessed_value": None,
            "market_value": None,
            "land_value": None,
            "property_type": None,
            "acreage": None,
            "living_area_sqft": None,
            "year_built": None,
            "official_url": SOURCE_URL,
            "source_document": SOURCE_URL,
            "parcel_map_url": _href(cells[2]),
            "assessor_detail_url": _href(cells[6]),
            "auction_url": None,
            "title_review_status": "not_reviewed",
            "data_completeness": "county-owned resale list (base fields only; per-parcel Assessor enrichment not yet added)",
            "last_verified": verified,
        })

    if len(output) < MIN_ROWS:
        raise RuntimeError(f"Oklahoma County parser found only {len(output)} rows; expected at least {MIN_ROWS}")
    return output


def score(row: dict) -> dict:
    points, reasons = 40, []
    if row.get("opening_bid"):
        points += 15
        reasons.append("official suggested purchase price captured")
    else:
        reasons.append("purchase price not published")
    if row.get("sale_date"):
        points += 10
        reasons.append("formally scheduled for a public resale")
    else:
        reasons.append("available for direct purchase; not yet scheduled for a public resale")
    if row.get("city"):
        points += 5
        reasons.append("city captured")
    else:
        reasons.append("no city/address published")
    reasons.append("legal description and assessed value not yet enriched")
    points = max(0, min(100, points))
    label = "High research priority" if points >= 70 else "Medium research priority" if points >= 45 else "Low research priority"
    return {"score": points, "label": label, "reasons": reasons, "disclaimer": "Research-priority ranking only; not a buy recommendation."}


def existing_rows() -> list[dict]:
    if not PROPS.exists():
        return []
    try:
        doc = json.loads(PROPS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [p for p in doc.get("properties", []) if p.get("state") == "OK" and p.get("county") == "Oklahoma"]


def merge_state_county_rows(existing_properties: list[dict], new_rows: list[dict], state: str, county: str) -> list[dict]:
    """Replace only (state, county)'s rows, leaving every other row untouched.

    Deliberately scoped by (state, county), not state alone -- a state-wide
    merge would silently clobber other counties sharing the same state code
    (see BUG-001/BUG-002 in BUGS.md for what that failure mode looks like).
    """
    kept = [p for p in existing_properties if not (p.get("state") == state and p.get("county") == county)]
    return kept + new_rows


def main() -> None:
    now = datetime.now(timezone.utc).isoformat()
    try:
        rows = parse_county_owned_list(fetch_html(), now)
    except (requests.RequestException, RuntimeError) as exc:
        prior = existing_rows()
        if not prior:
            raise
        print(f"Oklahoma County OK: official list unavailable/unparseable; preserved {len(prior)} previously verified rows. Reason: {exc}")
        return

    for row in rows:
        row["research_priority"] = score(row)
    rows.sort(key=lambda r: r["parcel_id"])

    payload = json.loads(PROPS.read_text(encoding="utf-8")) if PROPS.exists() else {"properties": []}
    payload["updated_at"] = now
    payload["properties"] = merge_state_county_rows(payload.get("properties", []), rows, "OK", "Oklahoma")
    PROPS.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Oklahoma County OK: loaded {len(rows)} official county-owned resale parcels; owner names intentionally omitted")


if __name__ == "__main__":
    main()
