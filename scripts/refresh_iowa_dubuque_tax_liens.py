#!/usr/bin/env python3
"""Refresh Dubuque County, Iowa 2026 property-level tax-sale liens.

Uses the Dubuque County Treasurer's official 2026 delinquent-tax PDF. The source
contains taxpayer names, but this collector deliberately does not store,
aggregate, or emit them. It retains only numbered real-estate sale items,
official parcel IDs, legal descriptions, and the county-published delinquent
amount. Mobile-home items are excluded.
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
PROFILE_ID = "IA-Dubuque-2026"
SOURCE_PAGE = "https://dubuquecountyiowa.gov/248/Treasurer"
SOURCE_PDF = "https://dubuquecountyiowa.gov/DocumentCenter/View/8222/2026-Publication-Report-5-26-2026-PDF"
AUCTION_URL = "https://www.iowataxauction.com/"
UA = "TaxLienGuideBot/2.6 (public tax-lien research; no access-control bypass)"

ITEM_RE = re.compile(r"^\s*(\d{1,3})\)\s*(.*)$")
PARCEL_RE = re.compile(r"\b(\d{10})\b")
MONEY_RE = re.compile(r"\$\s*([\d,]+(?:\.\d{2})?)")
REAL_ESTATE_ITEM_COUNT = 576


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


def extract_lines(raw: bytes) -> list[str]:
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        text = "\n".join(page.extract_text(layout=False) or "" for page in pdf.pages)
    # PDF extraction can join the final item of one page to the first owner line
    # of the next. Re-split before a numbered item token when needed.
    text = re.sub(r"(?<!\n)(?=(?:\d{1,3})\)\s)", "\n", text)
    return text.splitlines()


def _nearest_parcel(lines: list[str], item_index: int) -> str | None:
    # The parcel is printed with the taxpayer name immediately before each
    # numbered item; long taxpayer names can wrap, so inspect a small window but
    # retain only the parcel token, never the surrounding owner text.
    for idx in range(item_index - 1, max(-1, item_index - 5), -1):
        matches = PARCEL_RE.findall(lines[idx])
        if matches:
            return matches[-1]
    return None


def parse_real_estate_rows(lines: list[str], verified: str) -> list[dict]:
    rows: list[dict] = []
    seen_parcels: set[str] = set()
    expected_item = 1

    for i, line in enumerate(lines):
        match = ITEM_RE.match(line)
        if not match:
            continue
        item_number = int(match.group(1))
        # The official 2026 REAL ESTATE publication is one monotonic sequence
        # from 1 through 576; MOBILE HOMES begins at 577. pdfplumber can expose
        # stray line-start tokens that look like repeated item numbers inside
        # wrapped legal text. Accept only the next expected official item so a
        # noisy duplicate cannot poison the county-wide parse.
        if item_number != expected_item:
            continue
        parcel_id = _nearest_parcel(lines, i)
        if not parcel_id or parcel_id in seen_parcels:
            continue

        parts = [match.group(2).strip()]
        amount = None
        # Legal descriptions can wrap for several lines. Stop as soon as the
        # official dollar amount appears; this prevents the next taxpayer line
        # from entering the stored description.
        for j in range(i, min(len(lines), i + 7)):
            current = line if j == i else lines[j]
            money = MONEY_RE.search(current)
            if money:
                amount = round(float(money.group(1).replace(",", "")), 2)
                if j > i:
                    before = current[: money.start()].strip(" .")
                    if before:
                        parts.append(before)
                break
            if j > i:
                if ITEM_RE.match(current):
                    break
                # A 10-digit parcel token marks the next owner/parcel line.
                if PARCEL_RE.search(current):
                    break
                cleaned = current.strip(" .")
                if cleaned:
                    parts.append(cleaned)
        if amount is None:
            continue

        legal = " ".join(part for part in parts if part)
        legal = re.sub(r"\.{2,}", " ", legal)
        legal = re.sub(r"\s+", " ", legal).strip(" ;")
        seen_parcels.add(parcel_id)
        rows.append({
            "record_id": f"IA-Dubuque-2026-{item_number}",
            "profile_id": PROFILE_ID,
            "state": "IA",
            "state_name": "Iowa",
            "county": "Dubuque",
            "parcel_id": parcel_id,
            "sale_item_number": str(item_number),
            "legal_description": legal or None,
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
            "important_rules": "Published delinquent tax due is not labeled as an opening/minimum bid and is not presented as one. The county warns some published taxes may have been paid before publication. A tax-sale certificate is distinct from a later tax deed.",
            "data_source": "Dubuque County Treasurer official 2026 delinquent-tax publication",
            "last_verified": verified,
            "source_mode": "official_2026_publication_snapshot",
        })
        expected_item += 1
        if expected_item > REAL_ESTATE_ITEM_COUNT:
            break

    rows.sort(key=lambda row: int(row["sale_item_number"]))
    expected_items = set(range(1, REAL_ESTATE_ITEM_COUNT + 1))
    actual_items = {int(row["sale_item_number"]) for row in rows}
    missing_items = sorted(expected_items - actual_items)
    extra_items = sorted(actual_items - expected_items)
    if missing_items or extra_items or len(rows) != REAL_ESTATE_ITEM_COUNT:
        missing_preview = ", ".join(map(str, missing_items[:20])) or "none"
        extra_preview = ", ".join(map(str, extra_items[:20])) or "none"
        raise RuntimeError(
            "Dubuque County parser did not recover the complete official REAL ESTATE section: "
            f"loaded {len(rows)}/{REAL_ESTATE_ITEM_COUNT}; missing items [{missing_preview}]; "
            f"unexpected items [{extra_preview}]"
        )
    if any(any("owner" in str(key).lower() or "taxpayer" in str(key).lower() for key in row) for row in rows):
        raise RuntimeError("Dubuque County output contains a restricted owner/taxpayer-name field")
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
        "important_rules": "Official parcel-level delinquent-tax publication snapshot. Published delinquent amount is not represented as an opening bid. Taxpayer names in the source are intentionally not collected. Mobile homes are excluded.",
        "data_source": "Dubuque County Treasurer official 2026 delinquent-tax publication",
        "last_verified": date.today().isoformat(),
        "source_mode": "official_2026_publication_snapshot",
        "county_information_url": SOURCE_PAGE,
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
        print(f"Dubuque County IA: source unavailable/unparseable; preserved {len(prior)} previously verified rows. Reason: {exc}")
        return
    update_details(rows)
    print(f"Dubuque County IA: loaded {len(rows)} official real-estate tax-lien rows; taxpayer names intentionally omitted")


if __name__ == "__main__":
    main()
