#!/usr/bin/env python3
"""Refresh Dubuque County, Iowa 2026 property-level tax-sale liens.

Uses the Dubuque County Treasurer's official 2026 delinquent-tax PDF. The source
contains taxpayer names, but this collector deliberately does not store,
aggregate, or emit them. It retains only numbered real-estate sale items,
official parcel IDs, legal descriptions, and the county-published delinquent
amount. Mobile-home items are excluded.

The publication's PDF text order is not stable across extractors. To avoid
associating a parcel from one visual column with an item from another, this
collector extracts the official PDF several independent ways and only accepts
an item when at least two strategies agree on parcel ID and delinquent amount.
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
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DETAILS = ROOT / "data" / "tax-lien-properties.json"
PROFILE_ID = "IA-Dubuque-2026"
SOURCE_PAGE = "https://dubuquecountyiowa.gov/248/Treasurer"
SOURCE_PDF = "https://dubuquecountyiowa.gov/DocumentCenter/View/8222/2026-Publication-Report-5-26-2026-PDF"
AUCTION_URL = "https://www.iowataxauction.com/"
UA = "TaxLienGuideBot/2.8 (public tax-lien research; no access-control bypass)"

ITEM_RE = re.compile(r"(?<!\d)(\d{1,3})\s*\)\s*(.*)$")
PARCEL_RE = re.compile(r"\b(\d{10})\b")
MONEY_RE = re.compile(r"\$\s*([\d,]+(?:\.\d{2})?)")
REAL_ESTATE_ITEM_COUNT = 576


def _item_match(line: str) -> re.Match[str] | None:
    return ITEM_RE.search(line)


def _sale_item_match(line: str) -> re.Match[str] | None:
    """Return a real sale-row marker, not an incidental numbered text token.

    The official publication places the delinquent dollar amount on the sale
    item's numbered line. Diagnostics against the live county PDF show many
    additional N) tokens in legal/notice text; treating those as item boundaries
    breaks parcel association. Requiring both structures is a fail-closed way to
    distinguish actual sale rows without reading or storing taxpayer names.
    """
    match = _item_match(line)
    if not match or not MONEY_RE.search(line):
        return None
    item_number = int(match.group(1))
    if not 1 <= item_number <= REAL_ESTATE_ITEM_COUNT:
        return None
    return match


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


def _split_lines(text: str) -> list[str]:
    text = re.sub(r"(?<!\n)(?=(?:\d{1,3})\s*\)\s)", "\n", text)
    return [line.rstrip() for line in text.splitlines() if line.strip()]


def _crop_columns(page, count: int) -> str:
    """Extract visual columns independently to avoid cross-column line joins."""
    width = float(page.width)
    parts: list[str] = []
    for col in range(count):
        x0 = width * col / count
        x1 = width * (col + 1) / count
        if col:
            x0 += 1
        if col < count - 1:
            x1 -= 1
        cropped = page.crop((x0, 0, x1, page.height))
        parts.append(cropped.extract_text(layout=False) or "")
    return "\n".join(parts)


def extract_line_strategies(raw: bytes) -> dict[str, list[str]]:
    strategies: dict[str, list[str]] = {}

    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        strategies["pdfplumber"] = _split_lines(
            "\n".join(page.extract_text(layout=False) or "" for page in pdf.pages)
        )
        strategies["pdfplumber_layout"] = _split_lines(
            "\n".join(page.extract_text(layout=True) or "" for page in pdf.pages)
        )
        strategies["two_columns"] = _split_lines(
            "\n".join(_crop_columns(page, 2) for page in pdf.pages)
        )
        strategies["three_columns"] = _split_lines(
            "\n".join(_crop_columns(page, 3) for page in pdf.pages)
        )

    reader = PdfReader(io.BytesIO(raw))
    strategies["pypdf"] = _split_lines(
        "\n".join(page.extract_text() or "" for page in reader.pages)
    )
    return strategies


def _nearest_parcel(lines: list[str], item_index: int) -> str | None:
    for idx in range(item_index - 1, max(-1, item_index - 8), -1):
        # Only another actual sale row is a hard item boundary. Incidental N)
        # tokens in notice/legal text must not block the parcel search.
        if _sale_item_match(lines[idx]):
            break
        matches = PARCEL_RE.findall(lines[idx])
        if matches:
            return matches[-1]
    return None


def _candidate_row(lines: list[str], i: int, match: re.Match[str], verified: str) -> dict | None:
    item_number = int(match.group(1))
    if not 1 <= item_number <= REAL_ESTATE_ITEM_COUNT:
        return None

    parcel_id = _nearest_parcel(lines, i)
    if not parcel_id:
        return None

    parts = [match.group(2).strip()]
    amount = None
    for j in range(i, min(len(lines), i + 7)):
        current = lines[j]
        money = MONEY_RE.search(current)
        if money:
            amount = round(float(money.group(1).replace(",", "")), 2)
            if j > i:
                before = current[: money.start()].strip(" .")
                if before:
                    parts.append(before)
            break
        if j > i:
            if _sale_item_match(current) or PARCEL_RE.search(current):
                break
            cleaned = current.strip(" .")
            if cleaned:
                parts.append(cleaned)
    if amount is None:
        return None

    legal = " ".join(part for part in parts if part)
    legal = re.sub(r"\.{2,}", " ", legal)
    legal = re.sub(r"\s+", " ", legal).strip(" ;")
    return {
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
    }


def _strategy_candidates(lines: list[str], verified: str) -> dict[int, dict]:
    found: dict[int, list[dict]] = defaultdict(list)
    for i, line in enumerate(lines):
        match = _sale_item_match(line)
        if not match:
            continue
        candidate = _candidate_row(lines, i, match, verified)
        if candidate:
            found[int(candidate["sale_item_number"])].append(candidate)

    result: dict[int, dict] = {}
    for item, candidates in found.items():
        unique = {}
        for row in candidates:
            key = (row["parcel_id"], row["delinquent_tax_amount"])
            unique.setdefault(key, row)
        if len(unique) == 1:
            result[item] = next(iter(unique.values()))
    return result


def parse_real_estate_rows(strategies: dict[str, list[str]], verified: str) -> list[dict]:
    parsed = {name: _strategy_candidates(lines, verified) for name, lines in strategies.items()}
    rows: list[dict] = []
    used_parcels: dict[str, int] = {}
    unresolved: list[int] = []

    for item in range(1, REAL_ESTATE_ITEM_COUNT + 1):
        candidates: list[dict] = [items[item] for items in parsed.values() if item in items]
        votes = Counter((row["parcel_id"], row["delinquent_tax_amount"]) for row in candidates)
        if not votes:
            unresolved.append(item)
            continue
        ranked = votes.most_common()
        winner_key, winner_votes = ranked[0]
        runner_votes = ranked[1][1] if len(ranked) > 1 else 0
        if winner_votes < 2 or winner_votes <= runner_votes:
            unresolved.append(item)
            continue

        matching = [row for row in candidates if (row["parcel_id"], row["delinquent_tax_amount"]) == winner_key]
        chosen = max(matching, key=lambda row: len(row.get("legal_description") or ""))
        parcel_id = chosen["parcel_id"]
        prior_item = used_parcels.get(parcel_id)
        if prior_item is not None and prior_item != item:
            raise RuntimeError(
                f"Dubuque County corroborated extraction reused parcel {parcel_id} for items {prior_item} and {item}"
            )
        used_parcels[parcel_id] = item
        rows.append(chosen)

    if unresolved or len(rows) != REAL_ESTATE_ITEM_COUNT:
        preview = ", ".join(map(str, unresolved[:30])) or "none"
        coverage = ", ".join(f"{name}:{len(items)}" for name, items in parsed.items())
        raise RuntimeError(
            "Dubuque County parser did not obtain corroborated mappings for the complete official REAL ESTATE section: "
            f"loaded {len(rows)}/{REAL_ESTATE_ITEM_COUNT}; unresolved items [{preview}]; strategy coverage [{coverage}]"
        )

    rows.sort(key=lambda row: int(row["sale_item_number"]))
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
        raw = fetch_pdf()
        rows = parse_real_estate_rows(extract_line_strategies(raw), date.today().isoformat())
    except (requests.RequestException, RuntimeError) as exc:
        prior = existing_rows()
        if not prior:
            raise
        print(f"Dubuque County IA: source unavailable/unparseable; preserved {len(prior)} previously verified rows. Reason: {exc}")
        return
    update_details(rows)
    print(f"Dubuque County IA: loaded {len(rows)} corroborated official real-estate tax-lien rows; taxpayer names intentionally omitted")


if __name__ == "__main__":
    main()
