#!/usr/bin/env python3
"""Refresh Michigan's statewide tax-foreclosure "Surplus Properties" list.

Source: tax-sale.info's "Surplus Properties" page
(https://www.tax-sale.info/surplus -> /listings/surplus), the official
online-auction platform used by the Michigan Department of Treasury and
dozens of Michigan counties. Surplus properties are individual parcels that
went through a county's regular tax-foreclosure auction, received no
successful bid, and are now being reoffered first-come-first-served to
qualified buyers -- a rolling, always-current inventory (unlike the
platform's per-county live auction catalogs, which are single scheduled
events that expire within hours/days). No login, CAPTCHA, or
access-control workaround is used; the listing page and each parcel's
public detail page are both served without authentication.

Owner names are intentionally never collected in bulk (repo-wide privacy
convention, see STATUS.md / BUG-004 / BUG-005 in BUGS.md). This source does
not publish an owner name anywhere on the parcel detail page at all -- the
only place the word "owner" appears is generic policy text such as "Can
Only Be Sold To Adjacent Owner" -- so there is nothing to filter out.
"""
from __future__ import annotations

import html as html_module
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"

LISTING_URL = "https://www.tax-sale.info/listings/surplus"
LOT_URL = "https://www.tax-sale.info/lot/show/id/{lot_id}"
INFO_URL = "https://www.tax-sale.info/surplus"
UA = "TaxLienGuideBot/1.0 (public-record research; no access-control bypass)"

TITLE_RE = re.compile(r"Lot\s+(\d+):\s*(.+?)\s+Surplus\s+\d{4}", re.I)
MIN_ROWS = 5  # observed 24 on 2026-08-20; a rolling, irregularly-updated list


def fetch(url: str, timeout: int = 30) -> str:
    response = requests.get(url, headers={"User-Agent": UA, "Accept": "text/html"}, timeout=timeout)
    response.raise_for_status()
    return response.text


def extract_lot_ids(listing_html: str) -> list[str]:
    return sorted(set(re.findall(r"/lot/show/id/(\d+)", listing_html)), key=int)


def _field(raw_html: str, label: str) -> str | None:
    m = re.search(re.escape(label) + r"(.*?)</li>", raw_html, re.S)
    if not m:
        return None
    value = re.sub(r"<[^>]+>", " ", m.group(1))
    value = html_module.unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def _money(text: str | None) -> float | None:
    if not text or text.strip().upper() == "TBA":
        return None
    m = re.search(r"[\d,]+(?:\.\d{1,2})?", text)
    if not m:
        return None
    return round(float(m.group().replace(",", "")), 2)


def parse_lot_detail(raw_html: str, lot_id: str, verified: str) -> dict | None:
    title_match = TITLE_RE.search(raw_html)
    if not title_match:
        return None
    lot_number, county = title_match.group(1), title_match.group(2).strip()

    parcel_id = _field(raw_html, "Parcel ID:")
    if not parcel_id:
        return None

    # The human-readable listing description sits in its own heading, not
    # behind a labelled <li> -- pull it from the "Parcel Information:" repeat
    # section instead, which is consistently <h*>{description}</h*>
    # immediately followed by "Parcel ID:".
    desc_match = re.search(r"Parcel Information:(.*?)Parcel ID:", raw_html, re.S)
    listing_description = None
    if desc_match:
        text = re.sub(r"<[^>]+>", " ", desc_match.group(1))
        text = html_module.unescape(text)
        listing_description = re.sub(r"\s+", " ", text).strip() or None

    return {
        "state": "MI",
        "state_name": "Michigan",
        "county": county,
        "case_number": None,
        "parcel_id": parcel_id,
        "owner": None,
        "legal_description": _field(raw_html, "Legal Description:"),
        "sale_date": None,
        "available_date": None,
        "sale_status": "Surplus -- unsold at the county tax-foreclosure auction; available first-come-first-served to qualified buyers",
        "opening_bid": _money(_field(raw_html, "Minimum Bid:")),
        "opening_bid_note": "TBA -- not yet published by the county" if _field(raw_html, "Minimum Bid:") == "TBA" else None,
        "current_tax_due": _money(_field(raw_html, "Current Tax:")),
        "assessed_value": _money(_field(raw_html, "SEV:")),
        "assessed_value_basis": "Michigan State Equalized Value (SEV) -- approximately 50% of the assessor's determined value; may be several years stale per the source's own disclaimer",
        "market_value": None,
        "address": _field(raw_html, "Address:"),
        "city": None,
        "zip": None,
        "listing_description": listing_description,
        "official_url": LOT_URL.format(lot_id=lot_id),
        "source_document": INFO_URL,
        "auction_url": INFO_URL,
        "title_review_status": "not_reviewed",
        "data_completeness": "statewide surplus-property listing (base fields; no per-county enrichment)",
        "source_lot_id": lot_id,
        "source_lot_number": lot_number,
        "last_verified": verified,
    }


def score(row: dict) -> dict:
    points, reasons = 40, []
    if row.get("opening_bid"):
        points += 15
        reasons.append("official minimum bid/purchase price captured")
    else:
        reasons.append("purchase price not yet published (TBA)")
    if row.get("assessed_value"):
        points += 10
        reasons.append("State Equalized Value captured")
    if row.get("address"):
        points += 5
        reasons.append("address captured")
    if row.get("legal_description"):
        points += 5
        reasons.append("legal description captured")
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
    return [p for p in doc.get("properties", []) if p.get("state") == "MI"]


def merge_state_rows(existing_properties: list[dict], new_rows: list[dict], state: str) -> list[dict]:
    """Replace only `state`'s rows, leaving every other row untouched.

    Safe to key by state alone here -- this is the only collector that
    writes MI rows into data/properties.json (unlike FL, see BUG-007 in
    BUGS.md for what a state-only merge risks when more than one collector
    shares a state code).
    """
    kept = [p for p in existing_properties if p.get("state") != state]
    return kept + new_rows


def fetch_all_lots() -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    lot_ids = extract_lot_ids(fetch(LISTING_URL))
    if not lot_ids:
        raise RuntimeError("Michigan surplus-properties listing page returned no lot links")

    rows: list[dict] = []
    for lot_id in lot_ids:
        try:
            detail_html = fetch(LOT_URL.format(lot_id=lot_id))
        except requests.RequestException:
            continue
        row = parse_lot_detail(detail_html, lot_id, now)
        if row:
            rows.append(row)
        time.sleep(0.2)

    if len(rows) < max(1, len(lot_ids) // 2):
        raise RuntimeError(f"Michigan surplus parser only parsed {len(rows)}/{len(lot_ids)} listed lots; page structure may have changed")
    if len(rows) < MIN_ROWS:
        raise RuntimeError(f"Michigan surplus parser found only {len(rows)} rows; expected at least {MIN_ROWS}")
    return rows


def main() -> None:
    try:
        rows = fetch_all_lots()
    except (requests.RequestException, RuntimeError) as exc:
        prior = existing_rows()
        if not prior:
            raise
        print(f"Michigan surplus properties: official listing unavailable/unparseable; preserved {len(prior)} previously verified rows. Reason: {exc}")
        return

    for row in rows:
        row["research_priority"] = score(row)
    rows.sort(key=lambda r: (r["county"], r["parcel_id"]))

    payload = json.loads(PROPS.read_text(encoding="utf-8")) if PROPS.exists() else {"properties": []}
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()
    payload["properties"] = merge_state_rows(payload.get("properties", []), rows, "MI")
    PROPS.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    counties = sorted({r["county"] for r in rows})
    print(f"Michigan surplus properties: loaded {len(rows)} parcels across {len(counties)} counties ({', '.join(counties)}); owner names intentionally omitted")


if __name__ == "__main__":
    main()
