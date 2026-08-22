#!/usr/bin/env python3
"""Refresh Des Moines County, Iowa 2026 property-level tax-sale liens.

Source: official Des Moines County Treasurer 2026 Notice of Tax Sale PDF.
The publication mixes real property and mobile homes. Real-property parcel IDs use
Des Moines County's hyphenated 00-00-000-000 format; the mobile-home section starts
at item 724 and uses title/VIN-like identifiers instead. This collector therefore:

* keeps only rows with the official hyphenated real-property parcel format;
* requires all emitted sale item numbers to be <= 723;
* never stores owner/taxpayer names from the source;
* keeps the published Total Due as delinquent_tax_amount only, never as an
  opening/minimum bid; and
* preserves previously verified rows if the official PDF is temporarily unavailable.
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
PROFILE_ID = "IA-Des-Moines-2026"
SOURCE_PAGE = "https://www.desmoinescounty.iowa.gov/treasurer/tax_department/"
SOURCE_PDF = "https://desmoinescounty.iowa.gov/files/treasurer/tax_sale_delq_list_40918.pdf"
TERMS_PDF = "https://desmoinescounty.iowa.gov/files/treasurer/2023_tax_sale_rules_ad_regulations_45457.pdf"
AUCTION_URL = "https://www.iowataxauction.com/"
UA = "TaxLienGuideBot/3.0 (public tax-lien research; no access-control bypass)"

REAL_ESTATE_LAST_ITEM = 723
MIN_EXPECTED_REAL_ESTATE_ROWS = 600
PARCEL_RE = re.compile(r"^\d{2}-\d{2}-\d{3}-\d{3}$")
ITEM_RE = re.compile(r"^\*?(\d{1,3})$")
MONEY_RE = re.compile(r"^\$?([\d,]+\.\d{2})$")


def fetch_pdf() -> bytes:
    response = requests.get(
        SOURCE_PDF,
        headers={"User-Agent": UA, "Accept": "application/pdf,*/*"},
        timeout=90,
    )
    response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        raise RuntimeError("Des Moines County publication did not return a PDF")
    return response.content


def _center_y(word: dict) -> float:
    return (float(word["top"]) + float(word["bottom"])) / 2


def _group_lines(words: list[dict], tolerance: float = 2.8) -> list[list[dict]]:
    ordered = sorted(words, key=lambda w: (float(w["top"]), float(w["x0"])))
    lines: list[list[dict]] = []
    for word in ordered:
        y = _center_y(word)
        if not lines:
            lines.append([word])
            continue
        current_y = sum(_center_y(w) for w in lines[-1]) / len(lines[-1])
        if abs(y - current_y) <= tolerance:
            lines[-1].append(word)
            lines[-1].sort(key=lambda w: float(w["x0"]))
        else:
            lines.append([word])
    return lines


def _item_token(line: list[dict]) -> tuple[int, bool] | None:
    for word in line[:5]:
        text = str(word.get("text", "")).strip()
        match = ITEM_RE.match(text)
        if match:
            item = int(match.group(1))
            if 1 <= item <= REAL_ESTATE_LAST_ITEM:
                return item, text.startswith("*")
    return None


def _find_preceding_item(lines: list[list[dict]], line_index: int) -> tuple[int, bool] | None:
    candidates: list[tuple[int, bool]] = []
    for prior_index in range(max(0, line_index - 3), line_index + 1):
        candidate = _item_token(lines[prior_index])
        if candidate:
            candidates.append(candidate)
    unique: list[tuple[int, bool]] = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    return unique[-1] if len(unique) == 1 else None


def _amount_after_parcel(line: list[dict], parcel_word: dict) -> float | None:
    parcel_x = float(parcel_word["x0"])
    candidates: list[tuple[float, float]] = []
    for word in line:
        if float(word["x0"]) <= parcel_x:
            continue
        text = str(word.get("text", "")).strip()
        match = MONEY_RE.match(text)
        if not match:
            continue
        value = round(float(match.group(1).replace(",", "")), 2)
        candidates.append((float(word["x0"]), value))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][1]


def parse_pdf(raw: bytes, verified: str) -> list[dict]:
    parsed: dict[int, dict] = {}
    seen_parcels: set[str] = set()

    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            lines = _group_lines(page.extract_words(use_text_flow=False, keep_blank_chars=False))
            for line_index, line in enumerate(lines):
                parcel_words = [
                    word for word in line
                    if PARCEL_RE.match(str(word.get("text", "")).strip())
                ]
                if len(parcel_words) != 1:
                    continue
                parcel_word = parcel_words[0]
                parcel_id = str(parcel_word["text"]).strip()
                item_info = _find_preceding_item(lines, line_index)
                if item_info is None:
                    continue
                item_number, public_bidder = item_info
                if item_number > REAL_ESTATE_LAST_ITEM:
                    continue
                if item_number in parsed:
                    existing = parsed[item_number]
                    if existing["parcel_id"] != parcel_id:
                        raise RuntimeError(
                            f"Des Moines item {item_number} mapped to conflicting parcels "
                            f"{existing['parcel_id']} and {parcel_id}"
                        )
                    continue
                if parcel_id in seen_parcels:
                    raise RuntimeError(f"Des Moines parcel {parcel_id} appeared more than once")
                seen_parcels.add(parcel_id)
                amount = _amount_after_parcel(line, parcel_word)
                parsed[item_number] = {
                    "record_id": f"IA-Des-Moines-2026-{item_number}",
                    "profile_id": PROFILE_ID,
                    "state": "IA",
                    "state_name": "Iowa",
                    "county": "Des Moines",
                    "parcel_id": parcel_id,
                    "sale_item_number": str(item_number),
                    "legal_description": None,
                    "auction_date": "2026-06-15",
                    "sale_date": "2026-06-15",
                    "auction_time": "09:00 CT",
                    "auction_format": "Online bidding through Iowa Tax Auction",
                    "auction_location": "Online; administered by Des Moines County Treasurer",
                    "auction_url": AUCTION_URL,
                    "official_source_url": SOURCE_PDF,
                    "direct_listing_url": SOURCE_PDF,
                    "minimum_bid": None,
                    "opening_bid": None,
                    "delinquent_tax_amount": amount,
                    "public_bidder": public_bidder,
                    "sale_status": "Official 2026 publication snapshot; June 15 annual sale has passed and current parcel/certificate status must be reconfirmed",
                    "lien_type": "Iowa tax sale certificate / property-tax lien",
                    "sale_type": "tax_lien",
                    "maximum_statutory_return": "2% per month redemption interest under Iowa tax-sale redemption law",
                    "winning_rate_mechanism": "Percentage-interest bid-down from a 100% undivided interest; lowest percentage wins, ties resolved by random selection under county terms",
                    "redemption_period": "Governed by Iowa Code Chapters 446 and 447; any deed is a separate later stage after statutory notice and redemption requirements",
                    "important_rules": "Published Total Due is a delinquent-tax amount, not an opening/minimum bid. Owner names from the official publication are intentionally not collected. Mobile homes are excluded from this real-property feed.",
                    "data_source": "Des Moines County Treasurer official 2026 Notice of Tax Sale",
                    "last_verified": verified,
                    "source_mode": "official_2026_publication_geometry",
                }

    rows = [parsed[item] for item in sorted(parsed)]
    if len(rows) < MIN_EXPECTED_REAL_ESTATE_ROWS:
        raise RuntimeError(
            f"Des Moines County parser recovered only {len(rows)} real-property rows; "
            f"expected at least {MIN_EXPECTED_REAL_ESTATE_ROWS}"
        )
    if any(int(row["sale_item_number"]) > REAL_ESTATE_LAST_ITEM for row in rows):
        raise RuntimeError("Des Moines County output crossed into the mobile-home section")
    if any(not PARCEL_RE.match(row["parcel_id"]) for row in rows):
        raise RuntimeError("Des Moines County output contains a non-real-property parcel identifier")
    if any(any("owner" in str(key).lower() or "taxpayer" in str(key).lower() for key in row) for row in rows):
        raise RuntimeError("Des Moines County output contains a restricted owner/taxpayer-name field")
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
        "county": "Des Moines",
        "auction_date": "2026-06-15",
        "sale_date": "2026-06-15",
        "auction_time": "09:00 CT",
        "auction_format": "Online bidding through Iowa Tax Auction",
        "auction_location": "Online; administered by Des Moines County Treasurer",
        "auction_url": AUCTION_URL,
        "direct_listing_url": SOURCE_PDF,
        "official_source_url": SOURCE_PDF,
        "county_information_url": SOURCE_PAGE,
        "rules_url": TERMS_PDF,
        "lien_type": "Iowa tax sale certificate / property-tax lien",
        "sale_type": "tax_lien",
        "maximum_statutory_return": "2% per month redemption interest under Iowa tax-sale redemption law",
        "important_rules": "Official 2026 real-property publication snapshot. Published Total Due is not represented as an opening bid. Owner names in the source are intentionally not collected. Mobile homes are excluded.",
        "data_source": "Des Moines County Treasurer official 2026 Notice of Tax Sale",
        "last_verified": date.today().isoformat(),
        "source_mode": "official_2026_publication_geometry",
    }
    doc["properties"] = [
        row for row in doc.get("properties", []) if row.get("profile_id") != PROFILE_ID
    ] + rows
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    DETAILS.write_text(json.dumps(doc, separators=(",", ":")), encoding="utf-8")


def main() -> None:
    try:
        rows = parse_pdf(fetch_pdf(), date.today().isoformat())
    except (requests.RequestException, RuntimeError) as exc:
        prior = existing_rows()
        if not prior:
            raise
        print(
            f"Des Moines County IA: source unavailable/unparseable; preserved {len(prior)} previously verified rows. Reason: {exc}"
        )
        return
    update_details(rows)
    with_amount = sum(1 for row in rows if row.get("delinquent_tax_amount") is not None)
    print(
        f"Des Moines County IA: published {len(rows)} real-property tax-lien rows; "
        f"{with_amount} include the county-published delinquent Total Due."
    )


if __name__ == "__main__":
    main()
