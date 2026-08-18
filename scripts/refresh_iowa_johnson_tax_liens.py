#!/usr/bin/env python3
"""Refresh Johnson County, Iowa 2026 property-level tax-sale liens.

Uses only the county's public 2026 delinquent-tax publication. Owner/taxpayer
names printed in that publication are intentionally not collected. The parser
stops before the separate mobile-home section so every emitted record is a
real-estate parcel/certificate item.
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
PROFILE_ID = "IA-Johnson-2026"
SOURCE_PAGE = "https://johnsoncountyiowa.gov/treasurer/tax-sale-publication-lists"
SOURCE_PDF = "https://johnsoncountyiowa.gov/sites/default/files/2026-06/Gazette%20Proof%202026%20Johnson%20Co%20Delinquent%20Taxes.pdf"
PROCEDURES = "https://www.johnsoncountyiowa.gov/sites/default/files/2025-07/2026%20TAX%20SALE%20PROCEDURES.pdf"
UA = "TaxLienGuideBot/2.3 (public tax-lien research; no access-control bypass)"

PARCEL_AT_END = re.compile(r"\b(\d{10})\s*$")
ITEM_START = re.compile(r"^\s*(\d{1,4})\)\s*(.*)$")
MONEY = re.compile(r"\$([\d,]+\.\d{2})")


def fetch_pdf() -> bytes:
    response = requests.get(
        SOURCE_PDF,
        headers={"User-Agent": UA, "Accept": "application/pdf,*/*"},
        timeout=90,
    )
    response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        raise RuntimeError("Johnson County publication did not return a PDF")
    return response.content


def extract_text(raw: bytes) -> str:
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        return "\n".join(page.extract_text(layout=False) or "" for page in pdf.pages)


def _amount(value: str) -> float:
    return round(float(value.replace(",", "")), 2)


def parse_real_estate_rows(text: str, verified: str) -> list[dict]:
    """Parse only real-estate items, excluding the publication's mobile homes."""
    # The official publication labels a separate MOBILE HOMES section after
    # real-estate item 799. Do not collect VIN/title records from that section.
    real_estate_text = text.split("\nMOBILE HOMES", 1)[0]
    lines = [line.rstrip() for line in real_estate_text.splitlines()]
    rows: list[dict] = []
    seen_items: set[int] = set()
    public_bidder = False

    i = 0
    while i < len(lines):
        line = lines[i]
        if "PUBLIC BIDDER TAX SALE" in line:
            public_bidder = True
            i += 1
            continue

        parcel_match = PARCEL_AT_END.search(line)
        if not parcel_match:
            i += 1
            continue
        parcel = parcel_match.group(1)

        item_index = None
        item_number = None
        first_description = ""
        for j in range(i + 1, min(i + 5, len(lines))):
            item_match = ITEM_START.match(lines[j])
            if item_match:
                item_index = j
                item_number = int(item_match.group(1))
                first_description = item_match.group(2).strip()
                break
        if item_index is None or item_number is None or not (1 <= item_number <= 799):
            i += 1
            continue

        description_parts = [first_description] if first_description else []
        published_total = None
        end_index = item_index
        for k in range(item_index, min(item_index + 32, len(lines))):
            candidate = lines[k]
            if k > item_index:
                if PARCEL_AT_END.search(candidate) or ITEM_START.match(candidate):
                    break
                description_parts.append(candidate.strip())
            money_matches = MONEY.findall(candidate)
            if money_matches:
                published_total = _amount(money_matches[-1])
                # Remove the published dollar amount from the legal text.
                description_parts[-1] = MONEY.sub("", description_parts[-1]).strip()
                end_index = k
                break
            end_index = k

        if published_total is None or item_number in seen_items:
            i = max(i + 1, end_index + 1)
            continue
        seen_items.add(item_number)

        legal = " ".join(part for part in description_parts if part)
        legal = re.sub(r"\s+", " ", legal).strip() or None
        sale_class = "Public bidder tax sale" if public_bidder else "Regular tax sale"
        redemption = (
            "90-day notice of right of redemption may be issued after 9 months from sale"
            if public_bidder
            else "90-day notice of right of redemption may be issued after 1 year 9 months from sale"
        )
        rows.append({
            "record_id": f"IA-Johnson-2026-{item_number}",
            "profile_id": PROFILE_ID,
            "state": "IA",
            "state_name": "Iowa",
            "county": "Johnson",
            "parcel_id": parcel,
            "sale_item_number": str(item_number),
            "legal_description": legal,
            "auction_date": "2026-06-15",
            "sale_date": "2026-06-15",
            "auction_time": "08:00 CT",
            "auction_format": "In person; percentage-interest bid down with random selection among tied active bidders",
            "auction_location": "Johnson County Administration Building, Room 110, 913 S Dubuque St, Iowa City, IA 52240",
            "auction_url": SOURCE_PAGE,
            "official_source_url": SOURCE_PDF,
            "direct_listing_url": SOURCE_PAGE,
            # The publication calls this the total tax due, not a dollar opening bid.
            # Keep bid fields blank rather than relabeling it inaccurately.
            "minimum_bid": None,
            "opening_bid": None,
            "delinquent_tax_amount": published_total,
            "sale_status": f"Official 2026 publication snapshot — {sale_class}; sale date has passed and current parcel status must be reconfirmed",
            "lien_type": "Iowa tax sale certificate / property-tax lien",
            "sale_type": "tax_lien",
            "maximum_statutory_return": "2% per month redemption interest; fractions of a month count as a whole month",
            "winning_rate_mechanism": "Items are offered at 100%; active bidders bid the percentage interest in the parcel down in whole percentages from 99% to 1%, with random selection among remaining bidders",
            "redemption_period": redemption,
            "important_rules": (
                "The county publication warns that some listed taxes may have been paid after publication. "
                "A tax-sale certificate is not immediate ownership; consult current county records before relying on any listed item."
            ),
            "data_source": "Johnson County Treasurer official 2026 delinquent-tax publication PDF",
            "last_verified": verified,
            "source_mode": "official_2026_publication_snapshot",
            "data_completeness": {
                "published_fields": 8,
                "tracked_fields": 19,
                "percent": 42,
            },
            "research_priority": {
                "score": 42,
                "label": "Low research priority",
                "reasons": [
                    "Official parcel ID is published",
                    "Official legal description is published",
                    "County publishes the delinquent-tax amount",
                    "The 2026 sale date is confirmed but has passed",
                ],
                "disclaimer": "Research-priority ranking only; not a buy recommendation.",
            },
        })
        i = max(i + 1, end_index + 1)

    rows.sort(key=lambda row: int(row["sale_item_number"]))
    if len(rows) < 700:
        raise RuntimeError(f"Johnson County parser found only {len(rows)} real-estate rows; expected at least 700")
    if any(int(row["sale_item_number"]) > 799 for row in rows):
        raise RuntimeError("Johnson County parser crossed into the mobile-home section")
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
        "county": "Johnson",
        "auction_date": "2026-06-15",
        "sale_date": "2026-06-15",
        "auction_time": "08:00 CT",
        "auction_format": "In person; percentage-interest bid down with random selection among tied active bidders",
        "auction_location": "Johnson County Administration Building, Room 110, 913 S Dubuque St, Iowa City, IA 52240",
        "auction_url": SOURCE_PAGE,
        "direct_listing_url": SOURCE_PAGE,
        "official_source_url": SOURCE_PDF,
        "lien_type": "Iowa tax sale certificate / property-tax lien",
        "sale_type": "tax_lien",
        "maximum_statutory_return": "2% per month redemption interest; fractions of a month count as a whole month",
        "winning_rate_mechanism": "Johnson County 2026 procedure: percentage-interest bid down from 99% to 1%; random selection among remaining active bidders",
        "important_rules": "The list is a publication snapshot and may include parcels paid before sale. Certificate purchase is not immediate ownership.",
        "data_source": "Johnson County Treasurer official 2026 delinquent-tax publication PDF",
        "last_verified": date.today().isoformat(),
        "source_mode": "official_2026_publication_snapshot",
        "county_information_url": "https://www.johnsoncountyiowa.gov/treasurer/tax-sale-information",
        "procedures_url": PROCEDURES,
    }

    keep = [row for row in doc.get("properties", []) if row.get("profile_id") != PROFILE_ID]
    doc["properties"] = keep + rows
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()

    full_rows = [{**profiles.get(row.get("profile_id"), {}), **row} for row in doc["properties"]]
    doc["counts"] = {
        "total_records": len(full_rows),
        "states": len({row.get("state") for row in full_rows if row.get("state")}),
        "counties": len({(row.get("state"), row.get("county")) for row in full_rows if row.get("state") and row.get("county")}),
        "with_parcel_id": sum(bool(row.get("parcel_id")) for row in full_rows),
        "with_address": sum(bool(row.get("property_address")) for row in full_rows),
        "with_auction_date": sum(bool(row.get("auction_date")) for row in full_rows),
        "with_minimum_bid": sum(row.get("minimum_bid") is not None for row in full_rows),
        "with_assessed_value": sum((row.get("assessed_value") is not None or row.get("market_value") is not None) for row in full_rows),
        "with_research_priority": sum(bool(row.get("research_priority")) for row in full_rows),
    }
    DETAILS.write_text(json.dumps(doc, separators=(",", ":")), encoding="utf-8")


def main() -> None:
    try:
        rows = parse_real_estate_rows(extract_text(fetch_pdf()), date.today().isoformat())
    except (requests.RequestException, RuntimeError) as exc:
        prior = existing_rows()
        if not prior:
            raise
        print(
            f"Johnson County IA: live official publication unavailable/unparseable; preserved "
            f"{len(prior)} previously verified rows. Reason: {exc}"
        )
        return

    update_details(rows)
    print(f"Johnson County IA: loaded {len(rows)} official real-estate tax-lien rows; owner names intentionally omitted")


if __name__ == "__main__":
    main()
