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

The 2026 PDF has rows that sometimes wrap the district label. We therefore parse
with two independent strategies: direct text rows and word geometry. Conflicting
item/parcel mappings fail closed rather than guessing.
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
UA = "TaxLienGuideBot/3.1 (public tax-lien research; no access-control bypass)"

REAL_ESTATE_LAST_ITEM = 723
MIN_EXPECTED_REAL_ESTATE_ROWS = 600
PARCEL_RE = re.compile(r"^\d{2}-\d{2}-\d{3}-\d{3}$")
ITEM_RE = re.compile(r"^\*?(\d{1,3})$")
MONEY_RE = re.compile(r"^\$?([\d,]+\.\d{2})$")
TEXT_ROW_RE = re.compile(
    r"^\s*(\*?\d{1,3})\s+.+?\s(\d{2}-\d{2}-\d{3}-\d{3})\s+([\d,]+\.\d{2})(?:\s|$)"
)


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


def _money_value(text: str) -> float | None:
    match = MONEY_RE.match(text.strip())
    if not match:
        return None
    return round(float(match.group(1).replace(",", "")), 2)


def _parse_text_rows(page) -> dict[int, tuple[str, float | None, bool]]:
    """Parse rows that remain intact in pdfplumber's text extraction."""
    out: dict[int, tuple[str, float | None, bool]] = {}
    text = page.extract_text(x_tolerance=1.5, y_tolerance=3) or ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        match = TEXT_ROW_RE.match(line)
        if not match:
            continue
        item_token, parcel_id, amount_token = match.groups()
        item_number = int(item_token.lstrip("*"))
        if not (1 <= item_number <= REAL_ESTATE_LAST_ITEM):
            continue
        amount = _money_value(amount_token)
        out[item_number] = (parcel_id, amount, item_token.startswith("*"))
    return out


def _geometry_candidates(page) -> dict[int, tuple[str, float | None, bool]]:
    """Recover wrapped rows by associating parcel tokens with the item-number column."""
    words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    item_words: list[dict] = []
    parcel_words: list[dict] = []
    money_words: list[dict] = []

    for word in words:
        text = str(word.get("text", "")).strip()
        item_match = ITEM_RE.match(text)
        if item_match and 1 <= int(item_match.group(1)) <= REAL_ESTATE_LAST_ITEM:
            if float(word["x0"]) < 55:
                tagged = dict(word)
                tagged["item_number"] = int(item_match.group(1))
                tagged["public_bidder"] = text.startswith("*")
                item_words.append(tagged)
        if PARCEL_RE.match(text):
            parcel_words.append(dict(word))
        if MONEY_RE.match(text):
            money_words.append(dict(word))

    out: dict[int, tuple[str, float | None, bool]] = {}
    for parcel in parcel_words:
        py = _center_y(parcel)
        px = float(parcel["x0"])
        candidates = []
        for item in item_words:
            iy = _center_y(item)
            vertical = py - iy
            if -2.5 <= vertical <= 34:
                candidates.append((abs(vertical), float(item["x0"]), item))
        if not candidates:
            continue
        candidates.sort(key=lambda candidate: (candidate[0], candidate[1]))
        best_distance = candidates[0][0]
        tied = [candidate for candidate in candidates if abs(candidate[0] - best_distance) < 0.6]
        if len(tied) != 1:
            continue
        item = tied[0][2]
        item_number = int(item["item_number"])

        amount_candidates = []
        for money in money_words:
            if float(money["x0"]) <= px:
                continue
            dy = abs(_center_y(money) - py)
            if dy <= 3.5:
                value = _money_value(str(money.get("text", "")))
                if value is not None:
                    amount_candidates.append((float(money["x0"]) - px, value))
        amount_candidates.sort()
        amount = amount_candidates[0][1] if amount_candidates else None
        value = (str(parcel["text"]).strip(), amount, bool(item["public_bidder"]))
        existing = out.get(item_number)
        if existing and existing[0] != value[0]:
            raise RuntimeError(
                f"Des Moines geometry mapped item {item_number} to conflicting parcels {existing[0]} and {value[0]}"
            )
        out[item_number] = value
    return out


def _merge_mapping(
    merged: dict[int, tuple[str, float | None, bool]],
    incoming: dict[int, tuple[str, float | None, bool]],
    source_name: str,
) -> None:
    for item_number, value in incoming.items():
        existing = merged.get(item_number)
        if existing is None:
            merged[item_number] = value
            continue
        if existing[0] != value[0]:
            raise RuntimeError(
                f"Des Moines item {item_number} conflicts across parsers: {existing[0]} vs {value[0]} ({source_name})"
            )
        if existing[1] is not None and value[1] is not None and existing[1] != value[1]:
            raise RuntimeError(
                f"Des Moines item {item_number} has conflicting published amounts {existing[1]} and {value[1]}"
            )
        merged[item_number] = (
            existing[0],
            existing[1] if existing[1] is not None else value[1],
            existing[2] or value[2],
        )


def parse_pdf(raw: bytes, verified: str) -> list[dict]:
    mapping: dict[int, tuple[str, float | None, bool]] = {}

    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        text_hits = 0
        geometry_hits = 0
        for page in pdf.pages:
            text_rows = _parse_text_rows(page)
            geometry_rows = _geometry_candidates(page)
            text_hits += len(text_rows)
            geometry_hits += len(geometry_rows)
            _merge_mapping(mapping, text_rows, "text")
            _merge_mapping(mapping, geometry_rows, "geometry")

    if len(mapping) < MIN_EXPECTED_REAL_ESTATE_ROWS:
        raise RuntimeError(
            f"Des Moines County parser recovered only {len(mapping)} real-property rows "
            f"(text={text_hits}, geometry={geometry_hits}); expected at least {MIN_EXPECTED_REAL_ESTATE_ROWS}"
        )

    parcel_ids = [value[0] for value in mapping.values()]
    if len(parcel_ids) != len(set(parcel_ids)):
        raise RuntimeError("Des Moines County output contains duplicate real-property parcel IDs")

    rows: list[dict] = []
    for item_number in sorted(mapping):
        parcel_id, amount, public_bidder = mapping[item_number]
        rows.append(
            {
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
                "source_mode": "official_2026_publication_text_plus_geometry",
            }
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
        "source_mode": "official_2026_publication_text_plus_geometry",
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
