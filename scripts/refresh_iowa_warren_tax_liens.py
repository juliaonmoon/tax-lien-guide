#!/usr/bin/env python3
"""Refresh Warren County, Iowa 2026 property-level tax-sale liens.

Uses the Warren County Treasurer's official 2026 delinquent-tax publication.
The source includes taxpayer names; this collector intentionally discards them
and emits only numbered real-estate items, official parcel IDs, legal
descriptions, and county-published delinquent amounts. Mobile-home items are
excluded and published delinquent amounts are never labeled as opening bids.
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
PROFILE_ID = "IA-Warren-2026"
SOURCE_PAGE = "https://www.warrencountyia.gov/government/county-government/treasurer/tax-sale/"
SOURCE_PDF = "https://www.warrencountyia.gov/wp-content/uploads/2026/06/2026-Tax-Sale-Publication-List.pdf"
RULES = "https://www.warrencountyia.gov/wp-content/uploads/2026/05/2026-Online-Tax-Sale-Terms-1.pdf"
AUCTION_URL = "https://www.govease.com/"
UA = "TaxLienGuideBot/2.7 (public tax-lien research; no access-control bypass)"

# The official publication lists real-estate items 1-426 first. Item 427 is
# the first mobile-home item; Warren's 2026 terms explicitly state real estate
# is offered first and mobile homes last. Real-estate parcel IDs are 11 digits.
REAL_ESTATE_ITEM_COUNT = 426
ITEM_RE = re.compile(r"^\s*(\d{1,3})\)\s*(.*)$")
PARCEL_RE = re.compile(r"\b(\d{11})\b")
MONEY_RE = re.compile(r"\$\s*([\d,]+(?:\.\d{2})?)")
DISTRICT_RE = re.compile(r"^\s*\d{5}\s+-\s+")


def fetch_pdf() -> bytes:
    response = requests.get(
        SOURCE_PDF,
        headers={"User-Agent": UA, "Accept": "application/pdf,*/*"},
        timeout=90,
    )
    response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        raise RuntimeError("Warren County publication did not return a PDF")
    return response.content


def extract_lines(raw: bytes) -> list[str]:
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        text = "\n".join(page.extract_text(layout=False) or "" for page in pdf.pages)
    # Page extraction can glue the next taxpayer/parcel line to the prior
    # amount. Split before an 11-digit parcel token when it follows other text.
    text = re.sub(r"(?<=\d\.\d{2})(?=[A-Z*].*?\b\d{11}\b)", "\n", text)
    return text.splitlines()


def _nearest_parcel(lines: list[str], item_index: int) -> tuple[str | None, bool]:
    """Return only the official parcel token plus public-bidder marker.

    Warren marks public-bidder source rows with a leading asterisk on the
    taxpayer/parcel line. The surrounding taxpayer text is never retained.
    """
    for idx in range(item_index - 1, max(-1, item_index - 5), -1):
        matches = PARCEL_RE.findall(lines[idx])
        if matches:
            return matches[-1], lines[idx].lstrip().startswith("*")
        if DISTRICT_RE.match(lines[idx]):
            break
    return None, False


def parse_real_estate_rows(lines: list[str], verified: str) -> list[dict]:
    rows: list[dict] = []
    seen_items: set[int] = set()
    seen_parcels: set[str] = set()

    for i, line in enumerate(lines):
        match = ITEM_RE.match(line)
        if not match:
            continue
        item_number = int(match.group(1))
        if not 1 <= item_number <= REAL_ESTATE_ITEM_COUNT:
            continue

        parcel_id, public_bidder = _nearest_parcel(lines, i)
        if not parcel_id or item_number in seen_items or parcel_id in seen_parcels:
            continue

        description_parts = [match.group(2).strip()]
        amount = None
        for j in range(i, min(len(lines), i + 10)):
            current = line if j == i else lines[j]
            money = MONEY_RE.search(current)
            if money:
                amount = round(float(money.group(1).replace(",", "")), 2)
                if j > i:
                    before = current[: money.start()].strip(" .")
                    if before:
                        description_parts.append(before)
                break
            if j > i:
                if ITEM_RE.match(current) or DISTRICT_RE.match(current):
                    break
                # A new real-estate parcel token means the next owner/parcel
                # block started before an amount was found.
                if PARCEL_RE.search(current):
                    break
                cleaned = current.strip(" .")
                if cleaned:
                    description_parts.append(cleaned)
        if amount is None:
            continue

        legal = " ".join(part for part in description_parts if part)
        legal = re.sub(r"\.{2,}", " ", legal)
        legal = re.sub(r"\s+", " ", legal).strip(" ;") or None
        sale_class = "Public bidder tax sale" if public_bidder else "Regular tax sale"
        redemption = (
            "90-day notice of right of redemption may be served after 9 months from sale"
            if public_bidder
            else "90-day notice of right of redemption may be served after 1 year 9 months from sale"
        )
        rows.append({
            "record_id": f"IA-Warren-2026-{item_number}",
            "profile_id": PROFILE_ID,
            "state": "IA",
            "state_name": "Iowa",
            "county": "Warren",
            "parcel_id": parcel_id,
            "sale_item_number": str(item_number),
            "legal_description": legal,
            "auction_date": "2026-06-15",
            "sale_date": "2026-06-15",
            "auction_time": "08:30 CT",
            "auction_format": "Online through GovEase; percentage-interest bid down",
            "auction_location": "Online; administered by Warren County Treasurer",
            "auction_url": AUCTION_URL,
            "official_source_url": SOURCE_PDF,
            "direct_listing_url": SOURCE_PDF,
            "minimum_bid": None,
            "opening_bid": None,
            "delinquent_tax_amount": amount,
            "sale_status": f"Official 2026 publication snapshot — {sale_class}; sale date has passed and current certificate status must be reconfirmed",
            "lien_type": "Iowa tax sale certificate / property-tax lien",
            "sale_type": "tax_lien",
            "maximum_statutory_return": "2% per month redemption interest; fractions of a month count as a whole month",
            "winning_rate_mechanism": "Items begin at 100% undivided interest; bidders bid the percentage interest down in whole points from 99% to 1%",
            "redemption_period": redemption,
            "important_rules": "A Tax Sale Certificate of Purchase does not convey title. Published delinquent tax due is a pre-sale snapshot and is not represented as an opening/minimum bid. A later tax-sale deed requires the separate statutory notice/redemption process.",
            "data_source": "Warren County Treasurer official 2026 delinquent-tax publication",
            "last_verified": verified,
            "source_mode": "official_2026_publication_snapshot",
        })
        seen_items.add(item_number)
        seen_parcels.add(parcel_id)

    rows.sort(key=lambda row: int(row["sale_item_number"]))
    expected_items = set(range(1, REAL_ESTATE_ITEM_COUNT + 1))
    actual_items = {int(row["sale_item_number"]) for row in rows}
    if actual_items != expected_items or len(rows) != REAL_ESTATE_ITEM_COUNT:
        missing = sorted(expected_items - actual_items)
        extra = sorted(actual_items - expected_items)
        raise RuntimeError(
            "Warren County parser did not recover the complete official real-estate section: "
            f"loaded {len(rows)}/{REAL_ESTATE_ITEM_COUNT}; missing {missing[:20]}; extra {extra[:20]}"
        )
    if any(any("owner" in str(key).lower() or "taxpayer" in str(key).lower() for key in row) for row in rows):
        raise RuntimeError("Warren County output contains a restricted owner/taxpayer-name field")
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
        "state": "IA", "state_name": "Iowa", "county": "Warren",
        "auction_date": "2026-06-15", "sale_date": "2026-06-15", "auction_time": "08:30 CT",
        "auction_format": "Online through GovEase; percentage-interest bid down",
        "auction_location": "Online; administered by Warren County Treasurer",
        "auction_url": AUCTION_URL, "direct_listing_url": SOURCE_PDF, "official_source_url": SOURCE_PDF,
        "lien_type": "Iowa tax sale certificate / property-tax lien", "sale_type": "tax_lien",
        "maximum_statutory_return": "2% per month redemption interest; fractions of a month count as a whole month",
        "winning_rate_mechanism": "Warren County 2026 terms: 100% interest offered first; percentage interest bid down from 99% to 1%",
        "important_rules": "Official parcel-level delinquent-tax publication snapshot. Taxpayer names in the source are intentionally not collected. Real-estate items 1-426 are retained; mobile-home items 427+ are excluded. Certificate purchase is not title ownership.",
        "data_source": "Warren County Treasurer official 2026 delinquent-tax publication",
        "last_verified": date.today().isoformat(), "source_mode": "official_2026_publication_snapshot",
        "county_information_url": SOURCE_PAGE, "procedures_url": RULES,
    }
    doc["properties"] = [row for row in doc.get("properties", []) if row.get("profile_id") != PROFILE_ID] + rows
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    DETAILS.write_text(json.dumps(doc, separators=(",", ":")), encoding="utf-8")


def main() -> None:
    try:
        rows = parse_real_estate_rows(extract_lines(fetch_pdf()), date.today().isoformat())
    except (requests.RequestException, RuntimeError) as exc:
        prior = existing_rows()
        if not prior:
            raise
        print(f"Warren County IA: source unavailable/unparseable; preserved {len(prior)} prior verified rows. Reason: {exc}")
        return
    update_details(rows)
    print(f"Warren County IA: loaded {len(rows)} official real-estate tax-lien rows; taxpayer names intentionally omitted")


if __name__ == "__main__":
    main()
