#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Arizona — Pima County"
EVENT_ID = "AZ-PimaCounty-2026-market-event"
SOURCE = "https://www.to.pima.gov/taxLienSale/"

ROW = r'''{state:'Arizona — Pima County',product:'Tax lien / Certificate of Purchase',schedule:'Pima County held its 2026 annual online tax-lien auction on February 26, 2026. The Treasurer states that New Assignments (over-the-counter liens) opened April 1, 2026 and remain open through December 15, 2026. Verify live inventory through the Treasurer/RealAuction before purchase.',availability:'New Assignments open April 1–December 15, 2026 — live inventory requires Treasurer/RealAuction access',maxReturn:'16%/yr max',interest:'The annual auction starts interest-rate bidding at 16% and bids decrease in 1% increments; a 0% bid is acceptable. The actual certificate rate can therefore be lower than the statutory ceiling.',bid:'https://www.to.pima.gov/taxLienSale/',canadian:'The Treasurer requires prospective investors to register through RealAuction. The public county page does not state a simple foreign-bidder eligibility rule; confirm taxpayer-identification, registration, and payment requirements directly with the Treasurer before participating.',itin:'Not stated as a simple rule on the public Pima County tax-lien page. Confirm acceptable taxpayer-identification documentation directly with the Treasurer/RealAuction.',online:'YES — Pima County states the annual tax-lien auction is hosted online by RealAuction.',otc:'YES — New Assignments (over-the-counter liens) may be purchased online through RealAuction from April 1 through December 15. Current inventory changes and is available after registration, so this guide does not fabricate or mirror an unverified parcel list.',deed:'You are not purchasing property. Pima County explicitly describes the purchase as a tax lien / Certificate of Purchase against the property; any later foreclosure of the right to redeem is a separate judicial process.',special:'Market-level summary only, based on the current official Pima County Treasurer tax-lien page. Do not bulk aggregate owner/taxpayer names. Do not fabricate parcel inventory, purchase amounts, opening/minimum bids, or availability. The Treasurer states that amounts in the annual sale notice include base tax, accrued interest, penalties, and applicable fees; verify the amount due for any specific certificate directly with the official system.',source:'https://www.to.pima.gov/taxLienSale/'}'''

EVENT = {
    "record_id": EVENT_ID,
    "record_type": "market_event",
    "state": "AZ",
    "state_name": "Arizona",
    "county": "Pima County",
    "sale_type": "tax_lien",
    "product_type": "Tax lien / Certificate of Purchase",
    "auction_date": "2026-02-26",
    "sale_date": "2026-02-26",
    "auction_time": "Online batches closed from 8:00 AM through 12:00 PM MST; auxiliary session 1:00 PM–3:00 PM MST",
    "auction_format": "Online annual tax-lien sale hosted by RealAuction; interest-rate bidding started at 16% and decreased in 1% increments, with 0% bids accepted",
    "sale_status": "The 2026 annual auction has passed. Pima County states New Assignments (over-the-counter liens) are available April 1 through December 15, 2026; live inventory must be checked through the Treasurer/RealAuction and is not mirrored here.",
    "official_source_url": SOURCE,
    "important_rules": "Market-level calendar event only; no parcel inventory is republished or inferred. A Certificate of Purchase is a tax lien against property, not a purchase of the property or an immediate deed/ownership right. Do not bulk republish owner/taxpayer names and do not fabricate parcel inventory, purchase amounts, opening/minimum bids, current availability, bidder eligibility, redemption outcomes, or later foreclosure outcomes.",
    "data_source": "Pima County Treasurer official Tax Lien Sale Information and 2026 Tax Lien Sale materials",
    "last_verified": "2026-09-04",
    "market_level_only": True,
}


def rows_array_bounds(text: str):
    rows_start = text.find("const rows=[")
    if rows_start < 0:
        raise SystemExit("Could not find rows array")
    rows_end = text.find("\n];", rows_start)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")
    return rows_start, rows_end


def find_row_bounds(text: str):
    rows_start, rows_end = rows_array_bounds(text)
    marker_pos = text.find(MARKER, rows_start, rows_end)
    if marker_pos < 0:
        return None

    row_start = text.rfind("{state:", rows_start, marker_pos + 1)
    if row_start < rows_start:
        raise SystemExit("Found Pima County marker but could not locate row start inside rows array")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + len("\n];"))
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Pima County marker but could not locate row end inside rows array")

    row_end = min(endings)
    if row_end >= rows_end + len("\n];"):
        raise SystemExit("Refusing Pima County repair outside rows array")
    return row_start, row_end + 1


def add_pima():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        row_start, row_end = bounds
        existing = text[row_start:row_end]
        if existing == ROW:
            print("Arizona Pima County canonical row already present")
            return
        INDEX.write_text(text[:row_start] + ROW + text[row_end:], encoding="utf-8")
        print("Restored canonical Arizona Pima County tax-lien market row")
        return

    _, end = rows_array_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Arizona Pima County tax-lien market")


def ensure_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    properties = payload.setdefault("properties", [])
    matches = [i for i, item in enumerate(properties) if item.get("record_id") == EVENT_ID]
    if len(matches) > 1:
        raise SystemExit("Refusing to repair duplicate Pima County market events automatically")
    if matches:
        idx = matches[0]
        if properties[idx] == EVENT:
            print("Pima County calendar event already canonical")
            return
        properties[idx] = EVENT
        print("Restored canonical Pima County calendar event")
    else:
        properties.append(EVENT)
        print("Added Pima County calendar event")
    payload["updated_at"] = "2026-09-04T03:40:00Z"
    EVENTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    add_pima()
    ensure_calendar_event()


if __name__ == "__main__":
    main()
