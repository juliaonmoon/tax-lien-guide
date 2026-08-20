#!/usr/bin/env python3
"""Refresh Dubuque County, Iowa 2026 property-level tax-sale liens.

The official publication is a two-column newspaper-style PDF. Plain text
extraction interleaves columns and can attach the wrong parcel to a numbered
sale item. This collector therefore uses the PDF word geometry instead:

* the REAL ESTATE section must contain item numbers 1..576 exactly;
* the real-estate pages must contain exactly 576 ten-digit parcel tokens;
* visual reading order must reproduce the official 1..576 item sequence after
  removing at most one duplicate extraction artifact;
* parcel-by-order assignments are cross-checked against hundreds of local
  same-column item/parcel anchors before anything is published.

The source contains taxpayer names. This collector never stores, aggregates, or
emits them. It also excludes the separate mobile-home section and never labels
the published delinquent amount as an opening/minimum bid.
"""

from __future__ import annotations

import io
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import pdfplumber
import requests

ROOT = Path(__file__).resolve().parents[1]
DETAILS = ROOT / "data" / "tax-lien-properties.json"
PROFILE_ID = "IA-Dubuque-2026"
SOURCE_PAGE = "https://dubuquecountyiowa.gov/248/Treasurer"
SOURCE_PDF = "https://dubuquecountyiowa.gov/DocumentCenter/View/8222/2026-Publication-Report-5-26-2026-PDF"
AUCTION_URL = "https://www.iowataxauction.com/"
UA = "TaxLienGuideBot/2.9 (public tax-lien research; no access-control bypass)"

REAL_ESTATE_ITEM_COUNT = 576
ITEM_WORD_RE = re.compile(r"^(\d{1,3})\)$")
PARCEL_WORD_RE = re.compile(r"^\d{10}$")
MONEY_WORD_RE = re.compile(r"^\$?([\d,]+\.\d{2})$")


def fetch_pdf() -> bytes:
    response = requests.get(
        SOURCE_PDF,
        headers={"User-Agent": UA, "Accept": "application/pdf,*/*"},
        timeout=90,
    )
    response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        raise RuntimeError("Dubuque County publication did not return a PDF")
    return response.content


def _column(x: float) -> int:
    # The official 2026 publication has two newspaper columns. The item-number
    # x clusters are near 50 and 300 points, so 250 is a wide blank gutter.
    return 0 if x < 250 else 1


def _center_y(word: dict) -> float:
    return (float(word["top"]) + float(word["bottom"])) / 2


def _reading_key(page_no: int, word: dict) -> tuple[int, int, float, float]:
    return (page_no, _column(float(word["x0"])), float(word["top"]), float(word["x0"]))


def _money_value(word: dict) -> float | None:
    match = MONEY_WORD_RE.match(str(word.get("text", "")).strip())
    if not match:
        return None
    return round(float(match.group(1).replace(",", "")), 2)


def _select_item_tokens(items: list[dict]) -> dict[int, dict]:
    by_number: dict[int, list[dict]] = defaultdict(list)
    for item in items:
        by_number[int(item["number"])].append(item)

    expected = set(range(1, REAL_ESTATE_ITEM_COUNT + 1))
    if set(by_number) != expected:
        missing = sorted(expected - set(by_number))
        extra = sorted(set(by_number) - expected)
        raise RuntimeError(
            f"Dubuque geometry item set mismatch: missing={missing[:20]} extra={extra[:20]}"
        )

    duplicate_groups = {number: tokens for number, tokens in by_number.items() if len(tokens) != 1}
    if not duplicate_groups:
        selected = {number: tokens[0] for number, tokens in by_number.items()}
        ordered = [item["number"] for item in sorted(selected.values(), key=lambda w: _reading_key(w["page_no"], w))]
        if ordered != list(range(1, REAL_ESTATE_ITEM_COUNT + 1)):
            raise RuntimeError("Dubuque item geometry does not reproduce the official 1..576 reading order")
        return selected

    # The current official PDF has one duplicated extraction token. Do not guess
    # which occurrence is spurious: try each occurrence and accept only the one
    # whose visual reading order is exactly 1..576.
    if len(duplicate_groups) != 1:
        raise RuntimeError(f"Dubuque geometry has unexpected duplicate item groups: {len(duplicate_groups)}")
    duplicate_number, duplicate_tokens = next(iter(duplicate_groups.items()))
    if len(duplicate_tokens) != 2:
        raise RuntimeError("Dubuque geometry duplicate item count changed; refusing to infer")

    viable: list[dict[int, dict]] = []
    for chosen in duplicate_tokens:
        selected = {
            number: (chosen if number == duplicate_number else tokens[0])
            for number, tokens in by_number.items()
        }
        ordered = [item["number"] for item in sorted(selected.values(), key=lambda w: _reading_key(w["page_no"], w))]
        if ordered == list(range(1, REAL_ESTATE_ITEM_COUNT + 1)):
            viable.append(selected)
    if len(viable) != 1:
        raise RuntimeError(
            f"Dubuque duplicate item artifact could not be resolved uniquely from official visual order; viable={len(viable)}"
        )
    return viable[0]


def _amount_for_item(item: dict, page_monies: list[dict]) -> float | None:
    ix = float(item["x0"])
    iy = _center_y(item)
    item_col = _column(ix)

    # Amounts are printed on the numbered sale row. Prefer an exact same-row
    # token in the same newspaper column. If pdfplumber splits a dollar token in
    # an unusual row, leave the amount blank rather than borrowing another row.
    candidates = []
    for money in page_monies:
        mx = float(money["x0"])
        if mx <= ix:
            continue
        if item_col == 0 and mx >= 350:
            continue
        if item_col == 1 and mx < 350:
            continue
        if abs(_center_y(money) - iy) <= 3.2:
            value = _money_value(money)
            if value is not None:
                candidates.append((mx - ix, value))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][1]


def parse_geometry(raw: bytes, verified: str) -> list[dict]:
    all_items: list[dict] = []
    all_parcels: list[dict] = []
    monies_by_page: dict[int, list[dict]] = defaultdict(list)
    parcels_by_page: dict[int, list[dict]] = defaultdict(list)
    real_pages: set[int] = set()

    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
            page_items: list[dict] = []
            page_parcels: list[dict] = []
            for word in words:
                text = str(word.get("text", "")).strip()
                item_match = ITEM_WORD_RE.match(text)
                if item_match:
                    number = int(item_match.group(1))
                    if 1 <= number <= REAL_ESTATE_ITEM_COUNT:
                        item = dict(word)
                        item["number"] = number
                        item["page_no"] = page_no
                        page_items.append(item)
                if PARCEL_WORD_RE.match(text):
                    parcel = dict(word)
                    parcel["page_no"] = page_no
                    page_parcels.append(parcel)
                if MONEY_WORD_RE.match(text):
                    money = dict(word)
                    money["page_no"] = page_no
                    monies_by_page[page_no].append(money)

            if page_items:
                real_pages.add(page_no)
                all_items.extend(page_items)
                all_parcels.extend(page_parcels)
                parcels_by_page[page_no].extend(page_parcels)

    if not real_pages:
        raise RuntimeError("Dubuque geometry found no real-estate item pages")
    # Mobile-home pages follow the real-estate section and intentionally are not
    # included because they contain no 1..576 item tokens.
    if len(all_parcels) != REAL_ESTATE_ITEM_COUNT:
        raise RuntimeError(
            f"Dubuque REAL ESTATE pages contain {len(all_parcels)} parcel tokens; expected exactly {REAL_ESTATE_ITEM_COUNT}"
        )

    selected_items = _select_item_tokens(all_items)
    ordered_parcels = sorted(all_parcels, key=lambda w: _reading_key(w["page_no"], w))
    parcel_ids = [str(parcel["text"]).strip() for parcel in ordered_parcels]
    if len(set(parcel_ids)) != REAL_ESTATE_ITEM_COUNT:
        raise RuntimeError("Dubuque REAL ESTATE geometry contains duplicate parcel IDs; refusing to infer")

    # Assign the nth parcel in validated visual reading order to official item n.
    # Then independently check the assignment wherever the local page geometry
    # exposes a parcel directly above the numbered item. The current source gives
    # hundreds of such anchors; a mismatch means the sequence assumption is wrong.
    assigned = {number: ordered_parcels[number - 1] for number in range(1, REAL_ESTATE_ITEM_COUNT + 1)}
    anchors = 0
    mismatches = 0
    for number, item in selected_items.items():
        same_page = parcels_by_page[item["page_no"]]
        ix = float(item["x0"])
        local = [
            parcel for parcel in same_page
            if _column(float(parcel["x0"])) == _column(ix)
            and float(parcel["bottom"]) <= float(item["top"]) + 1
            and 0 <= float(item["top"]) - float(parcel["bottom"]) <= 45
        ]
        if not local:
            continue
        nearest = min(local, key=lambda parcel: float(item["top"]) - float(parcel["bottom"]))
        anchors += 1
        if str(nearest["text"]).strip() != str(assigned[number]["text"]).strip():
            mismatches += 1
    if anchors < 560 or mismatches:
        raise RuntimeError(
            f"Dubuque parcel/item order validation failed: anchors={anchors}, mismatches={mismatches}"
        )

    rows: list[dict] = []
    for number in range(1, REAL_ESTATE_ITEM_COUNT + 1):
        item = selected_items[number]
        parcel_id = str(assigned[number]["text"]).strip()
        amount = _amount_for_item(item, monies_by_page[item["page_no"]])
        rows.append(
            {
                "record_id": f"IA-Dubuque-2026-{number}",
                "profile_id": PROFILE_ID,
                "state": "IA",
                "state_name": "Iowa",
                "county": "Dubuque",
                "parcel_id": parcel_id,
                "sale_item_number": str(number),
                # Free-text legal lines are intentionally omitted by this repair
                # until they can be separated from taxpayer text with the same
                # level of certainty as parcel IDs.
                "legal_description": None,
                "auction_date": "2026-06-15",
                "sale_date": "2026-06-15",
                "auction_time": "09:00 CT",
                "auction_format": "Online; Dubuque County directs bidders to Iowa Tax Auction",
                "auction_location": "Online; administered by Dubuque County Treasurer",
                "auction_url": AUCTION_URL,
                "official_source_url": SOURCE_PDF,
                "direct_listing_url": SOURCE_PDF,
                "minimum_bid": None,
                "opening_bid": None,
                "delinquent_tax_amount": amount,
                "sale_status": "Official 2026 publication snapshot; June 15 annual sale has passed and current parcel/certificate status must be reconfirmed",
                "lien_type": "Iowa tax sale certificate / property-tax lien",
                "sale_type": "tax_lien",
                "maximum_statutory_return": "2% per month redemption interest under Iowa tax-sale redemption law",
                "winning_rate_mechanism": "Iowa tax-sale percentage-interest bidding; verify Dubuque County purchaser terms for the specific sale",
                "redemption_period": "Certificate/redemption process is governed by Iowa Code Chapters 446 and 447; deed is a separate later stage after statutory notice and redemption requirements",
                "important_rules": "Published delinquent tax due is not labeled as an opening/minimum bid and is not presented as one. Taxpayer names from the source are intentionally not collected. A tax-sale certificate is distinct from a later tax deed.",
                "data_source": "Dubuque County Treasurer official 2026 delinquent-tax publication",
                "last_verified": verified,
                "source_mode": "official_2026_publication_geometry",
            }
        )

    if len(rows) != REAL_ESTATE_ITEM_COUNT:
        raise RuntimeError(f"Dubuque geometry produced {len(rows)} rows; expected 576")
    if [int(row["sale_item_number"]) for row in rows] != list(range(1, REAL_ESTATE_ITEM_COUNT + 1)):
        raise RuntimeError("Dubuque geometry output is not the complete item set 1..576")
    if any(any("owner" in str(key).lower() or "taxpayer" in str(key).lower() for key in row) for row in rows):
        raise RuntimeError("Dubuque output contains a restricted owner/taxpayer-name field")
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
        "county": "Dubuque",
        "auction_date": "2026-06-15",
        "sale_date": "2026-06-15",
        "auction_time": "09:00 CT",
        "auction_format": "Online",
        "auction_location": "Online; administered by Dubuque County Treasurer",
        "auction_url": AUCTION_URL,
        "direct_listing_url": SOURCE_PDF,
        "official_source_url": SOURCE_PDF,
        "lien_type": "Iowa tax sale certificate / property-tax lien",
        "sale_type": "tax_lien",
        "maximum_statutory_return": "2% per month redemption interest under Iowa tax-sale redemption law",
        "important_rules": "Official parcel-level delinquent-tax publication snapshot parsed from validated PDF geometry. Published delinquent amount is not represented as an opening bid. Taxpayer names in the source are intentionally not collected. Mobile homes are excluded.",
        "data_source": "Dubuque County Treasurer official 2026 delinquent-tax publication",
        "last_verified": date.today().isoformat(),
        "source_mode": "official_2026_publication_geometry",
        "county_information_url": SOURCE_PAGE,
    }
    doc["properties"] = [row for row in doc.get("properties", []) if row.get("profile_id") != PROFILE_ID] + rows
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    DETAILS.write_text(json.dumps(doc, separators=(",", ":")), encoding="utf-8")


def main() -> None:
    try:
        rows = parse_geometry(fetch_pdf(), date.today().isoformat())
    except (requests.RequestException, RuntimeError) as exc:
        prior = existing_rows()
        if not prior:
            raise
        print(
            f"Dubuque County IA: source unavailable/unparseable; preserved {len(prior)} previously verified rows. Reason: {exc}"
        )
        return
    update_details(rows)
    with_amount = sum(1 for row in rows if row.get("delinquent_tax_amount") is not None)
    print(
        f"Dubuque County IA: loaded {len(rows)} official real-estate tax-lien rows from validated PDF geometry; "
        f"{with_amount} rows include a safely matched published delinquent amount; taxpayer names intentionally omitted"
    )


if __name__ == "__main__":
    main()
