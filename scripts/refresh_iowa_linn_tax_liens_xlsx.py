#!/usr/bin/env python3
"""Prefer Linn County's official XLSX publication; fall back to the vetted PDF parser."""
from __future__ import annotations

import io
import re
from datetime import date

import requests
from openpyxl import load_workbook

import refresh_iowa_linn_tax_liens as pdf_linn

SOURCE_XLSX = pdf_linn.SOURCE_XLSX
UA = pdf_linn.UA
PARCEL_RE = re.compile(r"^\d{15}$")


def _text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def fetch_xlsx() -> bytes:
    response = requests.get(
        SOURCE_XLSX,
        headers={"User-Agent": UA, "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*"},
        timeout=90,
    )
    response.raise_for_status()
    if not response.content.startswith(b"PK"):
        raise RuntimeError("Linn County publication did not return an XLSX workbook")
    return response.content


def _find_header(rows: list[list[str]]) -> tuple[int, dict[str, int]]:
    for idx, row in enumerate(rows[:80]):
        lowered = [cell.lower() for cell in row]
        columns: dict[str, int] = {}
        for col, cell in enumerate(lowered):
            if not cell:
                continue
            if "parcel" in cell and "parcel" not in columns:
                columns["parcel"] = col
            if ("legal" in cell or "description" in cell) and "legal" not in columns:
                columns["legal"] = col
            if (cell in {"item", "item #", "item no", "number", "no."} or "item number" in cell) and "item" not in columns:
                columns["item"] = col
            if any(token in cell for token in ("total", "amount due", "tax sale amount", "delinquent amount")):
                columns["amount"] = col
        if "parcel" in columns and "amount" in columns:
            return idx, columns
    raise RuntimeError("Linn County XLSX headers were not recognized safely")


def _parcel(value) -> str | None:
    text = _text(value).replace("-", "").replace(" ", "")
    if PARCEL_RE.fullmatch(text):
        return text
    if text.isdigit() and 13 <= len(text) <= 14:
        candidate = text.zfill(15)
        if PARCEL_RE.fullmatch(candidate):
            return candidate
    return None


def parse_xlsx(raw: bytes, verified: str) -> list[dict]:
    wb = load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
    output: list[dict] = []
    seen: set[int] = set()
    public_bidder = False

    for ws in wb.worksheets:
        values = [[_text(cell) for cell in row] for row in ws.iter_rows(values_only=True)]
        try:
            header_idx, cols = _find_header(values)
        except RuntimeError:
            continue

        for row in values[header_idx + 1 :]:
            joined = " ".join(cell for cell in row if cell).lower()
            if "public bidder real estate" in joined:
                public_bidder = True
                continue
            if "mobile home" in joined and ("offer" in joined or "sale" in joined):
                break

            parcel = _parcel(row[cols["parcel"]] if cols["parcel"] < len(row) else "")
            if not parcel:
                continue

            item = None
            if "item" in cols and cols["item"] < len(row):
                m = re.search(r"\d{1,4}", row[cols["item"]])
                if m:
                    item = int(m.group())
            if item is None:
                for cell in row[:3]:
                    m = re.fullmatch(r"(\d{1,4})\.?", cell)
                    if m:
                        item = int(m.group(1))
                        break
            if item is None or not (1 <= item <= 1568) or item in seen:
                continue

            amount_text = row[cols["amount"]] if cols["amount"] < len(row) else ""
            amount_match = re.search(r"-?\$?([\d,]+(?:\.\d{1,2})?)", amount_text)
            if not amount_match:
                continue
            amount = round(float(amount_match.group(1).replace(",", "")), 2)
            if amount < 0:
                continue

            legal = None
            if "legal" in cols and cols["legal"] < len(row):
                legal = re.sub(r"\s+", " ", row[cols["legal"]]).strip() or None

            sale_class = "Public bidder tax sale" if public_bidder else "Regular tax sale"
            redemption = (
                "90-day notice of right of redemption may be issued after 9 months from sale"
                if public_bidder
                else "90-day notice of right of redemption may be issued after 1 year 9 months from sale"
            )
            output.append({
                "record_id": f"IA-Linn-2026-{item}",
                "profile_id": pdf_linn.PROFILE_ID,
                "state": "IA",
                "state_name": "Iowa",
                "county": "Linn",
                "parcel_id": parcel,
                "sale_item_number": str(item),
                "legal_description": legal,
                "auction_date": "2026-06-15",
                "sale_date": "2026-06-15",
                "auction_time": "09:00 CT",
                "auction_format": "Online; percentage-interest bid down with random selection among tied lowest bidders",
                "auction_location": "Online through Iowa Tax Auction; administered by Linn County Treasurer",
                "auction_url": pdf_linn.SOURCE_PAGE,
                "official_source_url": SOURCE_XLSX,
                "direct_listing_url": pdf_linn.SOURCE_PAGE,
                "minimum_bid": None,
                "opening_bid": None,
                "delinquent_tax_amount": amount,
                "sale_status": f"Official 2026 publication snapshot — {sale_class}; sale date has passed and current parcel status must be reconfirmed",
                "lien_type": "Iowa tax sale certificate / property-tax lien",
                "sale_type": "tax_lien",
                "maximum_statutory_return": "2% per month redemption interest; fractions of a month count as a whole month",
                "winning_rate_mechanism": "Parcels are offered at 100%; bidders bid their percentage interest down in whole percentages from 99% to 1%; tied lowest bids are resolved by random selection",
                "redemption_period": redemption,
                "important_rules": "The county publication is a pre-sale delinquent-tax snapshot and may include parcels paid or withheld after publication. A Tax Sale Certificate of Purchase does not convey title; a later Treasurer's Deed process is separate.",
                "data_source": "Linn County Treasurer official 2026 tax-sale publication (Excel)",
                "last_verified": verified,
                "source_mode": "official_2026_publication_snapshot_xlsx",
                "data_completeness": {"published_fields": 8, "tracked_fields": 19, "percent": 42},
                "research_priority": {
                    "score": 42,
                    "label": "Low research priority",
                    "reasons": ["Official parcel ID is published", "Official delinquent-tax amount is published", "The 2026 sale date is confirmed but has passed"],
                    "disclaimer": "Research-priority ranking only; not a buy recommendation.",
                },
            })
            seen.add(item)

    output.sort(key=lambda row: int(row["sale_item_number"]))
    if len(output) < 1500:
        raise RuntimeError(f"Linn County XLSX parser found only {len(output)} rows; using PDF fallback")
    if any(int(row["sale_item_number"]) > 1568 for row in output):
        raise RuntimeError("Linn County XLSX parser crossed into the mobile-home section")
    return output


def main() -> None:
    try:
        rows = parse_xlsx(fetch_xlsx(), date.today().isoformat())
    except (requests.RequestException, RuntimeError, ValueError) as exc:
        print(f"Linn County IA: Excel-first refresh unavailable/unrecognized; falling back to vetted PDF parser. Reason: {exc}")
        pdf_linn.main()
        return
    pdf_linn.update_details(rows)
    print(f"Linn County IA: loaded {len(rows)} official XLSX real-estate tax-lien rows; owner names intentionally omitted")


if __name__ == "__main__":
    main()
