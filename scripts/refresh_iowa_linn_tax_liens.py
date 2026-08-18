#!/usr/bin/env python3
"""Refresh Linn County, Iowa 2026 property-level tax-sale liens.

Uses the county Treasurer's official 2026 tax-sale publication. Owner/taxpayer
names are intentionally not collected. Mobile-home items are excluded so every
emitted row is a real-estate parcel tax-lien item.
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
PROFILE_ID = "IA-Linn-2026"
SOURCE_PAGE = "https://www.linncountyiowa.gov/208/Property-Tax-Forms"
SOURCE_PDF = "https://www.linncountyiowa.gov/DocumentCenter/View/28483/2026-Tax-Publication-List-PDF"
SOURCE_XLSX = "https://www.linncountyiowa.gov/DocumentCenter/View/28482/2026-Tax-Publication-List-Excel"
RULES = "https://www.linncountyiowa.gov/DocumentCenter/View/28470/2026-Tax-Sale-Rules"
UA = "TaxLienGuideBot/2.4 (public tax-lien research; no access-control bypass)"
ITEM = re.compile(r"^\s*(\d{1,4})\.\s+.*?\s+(\d{15})\s*$")
MONEY = re.compile(r"\$([\d,]+\.\d{2})")


def fetch_pdf() -> bytes:
    response = requests.get(SOURCE_PDF, headers={"User-Agent": UA, "Accept": "application/pdf,*/*"}, timeout=90)
    response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        raise RuntimeError("Linn County publication did not return a PDF")
    return response.content


def extract_text(raw: bytes) -> str:
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        return "\n".join(page.extract_text(layout=False) or "" for page in pdf.pages)


def parse_real_estate_rows(text: str, verified: str) -> list[dict]:
    # The official publication numbers real-estate items 1..1568. Mobile homes
    # begin at item 1569 and use non-parcel identifiers, so both boundaries are
    # enforced rather than relying on taxpayer names or page positions.
    lines = [line.rstrip() for line in text.splitlines()]
    rows: list[dict] = []
    seen: set[int] = set()
    public_bidder = False
    i = 0

    while i < len(lines):
        line = lines[i]
        if "Public Bidder Real Estate" in line:
            public_bidder = True
            i += 1
            continue
        if "mobile homes" in line.lower() and "offer for sale" in line.lower():
            break

        match = ITEM.match(line)
        if not match:
            i += 1
            continue
        item_number = int(match.group(1))
        parcel = match.group(2)
        if not (1 <= item_number <= 1568) or item_number in seen:
            i += 1
            continue

        description_parts: list[str] = []
        published_total = None
        end = i
        for j in range(i + 1, min(i + 18, len(lines))):
            candidate = lines[j].strip()
            if ITEM.match(candidate) or re.match(r"^\d{5}\s+-\s+", candidate):
                break
            if "Public Bidder Real Estate" in candidate:
                break
            amounts = MONEY.findall(candidate)
            cleaned = MONEY.sub("", candidate).replace(".", " ").strip()
            if cleaned:
                description_parts.append(cleaned)
            if amounts:
                published_total = round(float(amounts[-1].replace(",", "")), 2)
                end = j
                break
            end = j

        if published_total is None:
            i += 1
            continue
        seen.add(item_number)
        legal = re.sub(r"\s+", " ", " ".join(description_parts)).strip() or None
        sale_class = "Public bidder tax sale" if public_bidder else "Regular tax sale"
        redemption = (
            "90-day notice of right of redemption may be issued after 9 months from sale"
            if public_bidder else
            "90-day notice of right of redemption may be issued after 1 year 9 months from sale"
        )
        rows.append({
            "record_id": f"IA-Linn-2026-{item_number}",
            "profile_id": PROFILE_ID,
            "state": "IA",
            "state_name": "Iowa",
            "county": "Linn",
            "parcel_id": parcel,
            "sale_item_number": str(item_number),
            "legal_description": legal,
            "auction_date": "2026-06-15",
            "sale_date": "2026-06-15",
            "auction_time": "09:00 CT",
            "auction_format": "Online; percentage-interest bid down with random selection among tied lowest bidders",
            "auction_location": "Online through Iowa Tax Auction; administered by Linn County Treasurer",
            "auction_url": SOURCE_PAGE,
            "official_source_url": SOURCE_PDF,
            "direct_listing_url": SOURCE_PAGE,
            "minimum_bid": None,
            "opening_bid": None,
            "delinquent_tax_amount": published_total,
            "sale_status": f"Official 2026 publication snapshot — {sale_class}; sale date has passed and current parcel status must be reconfirmed",
            "lien_type": "Iowa tax sale certificate / property-tax lien",
            "sale_type": "tax_lien",
            "maximum_statutory_return": "2% per month redemption interest; fractions of a month count as a whole month",
            "winning_rate_mechanism": "Parcels are offered at 100%; bidders bid their percentage interest down in whole percentages from 99% to 1%; tied lowest bids are resolved by random selection",
            "redemption_period": redemption,
            "important_rules": "The county publication is a pre-sale delinquent-tax snapshot and may include parcels paid or withheld after publication. A Tax Sale Certificate of Purchase does not convey title; a later Treasurer's Deed process is separate.",
            "data_source": "Linn County Treasurer official 2026 tax-sale publication",
            "last_verified": verified,
            "source_mode": "official_2026_publication_snapshot",
            "data_completeness": {"published_fields": 8, "tracked_fields": 19, "percent": 42},
            "research_priority": {
                "score": 42,
                "label": "Low research priority",
                "reasons": ["Official parcel ID is published", "Official legal description is published", "County publishes the delinquent-tax amount", "The 2026 sale date is confirmed but has passed"],
                "disclaimer": "Research-priority ranking only; not a buy recommendation.",
            },
        })
        i = max(i + 1, end + 1)

    rows.sort(key=lambda row: int(row["sale_item_number"]))
    if len(rows) < 1500:
        raise RuntimeError(f"Linn County parser found only {len(rows)} real-estate rows; expected at least 1500")
    if any(int(row["sale_item_number"]) > 1568 for row in rows):
        raise RuntimeError("Linn County parser crossed into the mobile-home section")
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
        "state": "IA", "state_name": "Iowa", "county": "Linn",
        "auction_date": "2026-06-15", "sale_date": "2026-06-15", "auction_time": "09:00 CT",
        "auction_format": "Online; percentage-interest bid down with random selection among tied lowest bidders",
        "auction_location": "Online through Iowa Tax Auction; administered by Linn County Treasurer",
        "auction_url": SOURCE_PAGE, "direct_listing_url": SOURCE_PAGE, "official_source_url": SOURCE_PDF,
        "machine_readable_source_url": SOURCE_XLSX,
        "lien_type": "Iowa tax sale certificate / property-tax lien", "sale_type": "tax_lien",
        "maximum_statutory_return": "2% per month redemption interest; fractions of a month count as a whole month",
        "winning_rate_mechanism": "Linn County 2026 terms: percentage-interest bid down from 99% to 1%; tied lowest bids use random selection",
        "important_rules": "The official publication is a pre-sale snapshot and may include parcels paid or withheld before sale. Certificate purchase is not immediate ownership; Treasurer's Deed is a separate later process.",
        "data_source": "Linn County Treasurer official 2026 tax-sale publication",
        "last_verified": date.today().isoformat(), "source_mode": "official_2026_publication_snapshot",
        "county_information_url": SOURCE_PAGE, "procedures_url": RULES,
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
        print(f"Linn County IA: live official publication unavailable/unparseable; preserved {len(prior)} previously verified rows. Reason: {exc}")
        return
    update_details(rows)
    print(f"Linn County IA: loaded {len(rows)} official real-estate tax-lien rows; owner names intentionally omitted")


if __name__ == "__main__":
    main()
