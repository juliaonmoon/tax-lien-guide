#!/usr/bin/env python3
"""Refresh Woodbury County, Iowa 2026 property-level tax-sale liens.

Uses Woodbury County Treasurer's official 2026 delinquent-tax publication.
The publication includes owner names, but this collector deliberately does not
store, aggregate, or emit them. It retains only the numbered sale item, official
12-digit parcel ID, and the two county-published dollar amounts. Mobile-home
items are excluded because they do not use the 12-digit real-estate parcel IDs.
"""

from __future__ import annotations

import io
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

import pdfplumber
import requests

ROOT = Path(__file__).resolve().parents[1]
DETAILS = ROOT / "data" / "tax-lien-properties.json"
PROFILE_ID = "IA-Woodbury-2026"
SOURCE_PAGE = "https://www.woodburycountyiowa.gov/treasurer/tax_sale/"
SOURCE_PDF = "https://www.woodburycountyiowa.gov/files/treasurer/delinquent_tax_listing_2026_50422.pdf"
RULES = "https://www.woodburycountyiowa.gov/files/treasurer/woodbury_county_terms_conditions_55199.pdf"
UA = "TaxLienGuideBot/2.5 (public tax-lien research; no access-control bypass)"

ITEM_AND_PARCEL = re.compile(r"^\s*(\d{1,4})\*?\s+.*?\b(\d{12})\b")
MONEY = re.compile(r"(?<!\d)(\d[\d,]*\.\d{2})(?!\d)")


def fetch_pdf() -> bytes:
    response = requests.get(
        SOURCE_PDF,
        headers={"User-Agent": UA, "Accept": "application/pdf,*/*"},
        timeout=90,
    )
    response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        raise RuntimeError("Woodbury County publication did not return a PDF")
    return response.content


def extract_text(raw: bytes) -> str:
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        return "\n".join(page.extract_text(layout=False) or "" for page in pdf.pages)


def _published_amounts(line: str) -> tuple[float, float] | None:
    """Return (publication amount, sale amount) without reading owner text.

    The official sheet has two terminal monetary columns. PDF extraction can
    reverse their visual order on a few rows, while the 2026 sale amount is the
    publication amount plus the county's $20 certificate fee. Use that invariant
    to normalize the pair instead of depending on column extraction order.
    """
    values = [round(float(raw.replace(",", "")), 2) for raw in MONEY.findall(line)]
    if len(values) < 2:
        return None
    a, b = values[-2], values[-1]
    low, high = sorted((a, b))
    if abs((high - low) - 20.0) > 0.02:
        return None
    return low, high


def parse_real_estate_rows(text: str, verified: str) -> list[dict]:
    rows: list[dict] = []
    seen_items: set[int] = set()
    seen_parcels: set[str] = set()

    # pdfplumber occasionally joins the final row of one page to the first row
    # of the next. Split again at a numbered item followed by district text so
    # both official records remain visible to the parser.
    normalized = re.sub(r"\s+(?=(?:\d{1,4})\*?\s+\d{4}\s+-\s+)", "\n", text)

    for line in normalized.splitlines():
        match = ITEM_AND_PARCEL.match(line)
        if not match:
            continue
        item_number = int(match.group(1))
        parcel_id = match.group(2)
        # The official 2026 PDF switches to mobile homes after real-estate item
        # 1569. Requiring a 12-digit parcel ID is an independent safety guard.
        if not (1 <= item_number <= 1569):
            continue
        if item_number in seen_items or parcel_id in seen_parcels:
            continue
        amounts = _published_amounts(line)
        if amounts is None:
            continue
        publication_amount, sale_amount = amounts
        seen_items.add(item_number)
        seen_parcels.add(parcel_id)
        rows.append({
            "record_id": f"IA-Woodbury-2026-{item_number}",
            "profile_id": PROFILE_ID,
            "state": "IA",
            "state_name": "Iowa",
            "county": "Woodbury",
            "parcel_id": parcel_id,
            "sale_item_number": str(item_number),
            "auction_date": "2026-06-15",
            "sale_date": "2026-06-15",
            "auction_time": "09:00 CT",
            "auction_format": "Online through GovEase; bidders bid percentage interest down from 100%",
            "auction_location": "Online; administered by Woodbury County Treasurer",
            "auction_url": SOURCE_PAGE,
            "official_source_url": SOURCE_PDF,
            "direct_listing_url": SOURCE_PDF,
            "minimum_bid": None,
            "opening_bid": None,
            "delinquent_tax_amount": publication_amount,
            "certificate_purchase_amount": sale_amount,
            "sale_status": "Official 2026 publication snapshot; June 15 annual sale has passed and current parcel/certificate status must be reconfirmed",
            "lien_type": "Iowa tax sale certificate / property-tax lien",
            "sale_type": "tax_lien",
            "maximum_statutory_return": "2% per month redemption interest; fractions of a month count as a whole month",
            "winning_rate_mechanism": "Delinquent taxes are offered beginning at 100% undivided interest; bidders bid percentage interest down from 99% to 1%; tied lowest bids use random selection",
            "redemption_period": "Regular tax sale: 90-day notice of right of redemption may be issued after 1 year 9 months; public-bidder certificates may use a shorter statutory timetable",
            "important_rules": "The published Sale Amount is the county-published certificate purchase amount, not a dollar opening bid. A Tax Sale Certificate of Purchase does not convey title; a later Treasurer's Deed process is separate. The publication can include parcels paid or withheld before sale.",
            "data_source": "Woodbury County Treasurer official 2026 delinquent-tax publication",
            "last_verified": verified,
            "source_mode": "official_2026_publication_snapshot",
            "data_completeness": {"published_fields": 6, "tracked_fields": 19, "percent": 32},
            "research_priority": {
                "score": 32,
                "label": "Low research priority",
                "reasons": [
                    "Official parcel ID is published",
                    "Official delinquent/publication amount is published",
                    "Official certificate purchase amount is published",
                    "The 2026 annual sale date is confirmed but has passed",
                ],
                "disclaimer": "Research-priority ranking only; not a buy recommendation.",
            },
        })

    rows.sort(key=lambda row: int(row["sale_item_number"]))
    if len(rows) < 1500:
        raise RuntimeError(f"Woodbury County parser found only {len(rows)} real-estate rows; expected at least 1500")
    if any(int(row["sale_item_number"]) > 1569 for row in rows):
        raise RuntimeError("Woodbury County parser crossed into the mobile-home section")
    if any(any("owner" in str(key).lower() for key in row) for row in rows):
        raise RuntimeError("Woodbury County output contains a restricted owner-name field")
    return rows


def existing_rows() -> list[dict]:
    if not DETAILS.exists():
        return []
    doc = json.loads(DETAILS.read_text(encoding="utf-8"))
    return [row for row in doc.get("properties", []) if row.get("profile_id") == PROFILE_ID]


def update_details(rows: list[dict]) -> None:
    doc = json.loads(DETAILS.read_text(encoding="utf-8"))
    profiles = doc.setdefault("profiles", {})
    profiles[PROFILE_ID] = {
        "state": "IA",
        "state_name": "Iowa",
        "county": "Woodbury",
        "auction_date": "2026-06-15",
        "sale_date": "2026-06-15",
        "auction_time": "09:00 CT",
        "auction_format": "Online through GovEase; percentage-interest bid down",
        "auction_location": "Online; administered by Woodbury County Treasurer",
        "auction_url": SOURCE_PAGE,
        "direct_listing_url": SOURCE_PDF,
        "official_source_url": SOURCE_PDF,
        "lien_type": "Iowa tax sale certificate / property-tax lien",
        "sale_type": "tax_lien",
        "maximum_statutory_return": "2% per month redemption interest; fractions of a month count as a whole month",
        "winning_rate_mechanism": "Woodbury County 2026 terms: percentage-interest bid down from 99% to 1%; tied lowest bids use random selection",
        "important_rules": "Official parcel-level publication snapshot. Certificate purchase does not convey title; Treasurer's Deed is a separate later process. Owner names in the source are intentionally not collected.",
        "data_source": "Woodbury County Treasurer official 2026 delinquent-tax publication",
        "last_verified": date.today().isoformat(),
        "source_mode": "official_2026_publication_snapshot",
        "county_information_url": SOURCE_PAGE,
        "procedures_url": RULES,
    }
    doc["properties"] = [row for row in doc.get("properties", []) if row.get("profile_id") != PROFILE_ID] + rows
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    full = [{**profiles.get(row.get("profile_id"), {}), **row} for row in doc["properties"]]
    doc["counts"] = {
        "total_records": len(full),
        "states": len({row.get("state") for row in full if row.get("state")}),
        "counties": len({(row.get("state"), row.get("county")) for row in full if row.get("state") and row.get("county")}),
        "with_parcel_id": sum(bool(row.get("parcel_id")) for row in full),
        "with_address": sum(bool(row.get("property_address")) for row in full),
        "with_auction_date": sum(bool(row.get("auction_date")) for row in full),
        "with_minimum_bid": sum(row.get("minimum_bid") is not None for row in full),
        "with_assessed_value": sum((row.get("assessed_value") is not None or row.get("market_value") is not None) for row in full),
        "with_research_priority": sum(bool(row.get("research_priority")) for row in full),
    }
    DETAILS.write_text(json.dumps(doc, separators=(",", ":")), encoding="utf-8")


def main() -> None:
    try:
        rows = parse_real_estate_rows(extract_text(fetch_pdf()), date.today().isoformat())
    except (requests.RequestException, RuntimeError) as exc:
        prior = existing_rows()
        if not prior:
            raise
        print(f"Woodbury County IA: live official publication unavailable/unparseable; preserved {len(prior)} previously verified rows. Reason: {exc}")
        return
    update_details(rows)
    print(f"Woodbury County IA: loaded {len(rows)} official real-estate tax-lien rows; owner names intentionally omitted")


if __name__ == "__main__":
    main()
