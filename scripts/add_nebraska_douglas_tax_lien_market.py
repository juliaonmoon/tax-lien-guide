#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Douglas County"
EVENT_ID = "NE-DouglasCounty-2026-market-event"
SOURCE = "https://treasurer.douglascounty-ne.gov/public-tax-sale/"

ROW = r'''{state:'Nebraska — Douglas County',product:'Tax lien / certificate of tax sale',schedule:'Douglas County\'s published 2026 delinquent-tax notice scheduled its public tax-lien sale for <span class="schedule-date">March 2, 2026</span>, with online bids accepted from February 5 through March 2, 2026. That sale has passed. Nebraska law generally requires the delinquent-real-property list before the first Monday of March, but do not present a later Douglas County sale as confirmed until the Treasurer publishes the current notice.',availability:'2026 annual tax-lien sale passed — no current parcel inventory is asserted here. Use the Douglas County Treasurer\'s current Public Tax Sale page and legal advertisement for any later sale.',maxReturn:'14%/yr current statutory interest',interest:'Neb. Rev. Stat. § 45-104.01 currently sets 14% annual interest for delinquent taxes or special assessments owed to Nebraska political subdivisions, and § 77-1824 applies that rate to redemption from a tax sale. Verify current law and the county notice before bidding.',bid:'https://treasurer.douglascounty-ne.gov/public-tax-sale/',canadian:'The public 2026 notice requires online registration but does not establish a simple foreign-bidder rule. Do not assume Canadian eligibility; confirm current taxpayer-identification, registration, deposit, payment, and certificate requirements directly with the Douglas County Treasurer.',itin:'The public legal notice does not establish that an ITIN or foreign-tax form is accepted. Confirm current taxpayer-identification requirements directly with the Douglas County Treasurer before relying on an ITIN.',online:'YES for the published 2026 sale — the County Treasurer\'s legal notice stated that the sale would take place online at douglas.nebraskataxsale.com. Reconfirm the platform and method for each later sale.',otc:'Do not infer current private-sale, over-the-counter, or county-held certificate inventory from the completed 2026 public sale. Confirm any post-sale availability directly with the Treasurer under the current Nebraska statutes and county procedures.',deed:'A tax-sale certificate is not immediate ownership or possession. Nebraska law provides a redemption process and separate statutory requirements before a certificate holder may seek a tax deed or foreclosure; do not describe the annual tax-lien sale as a tax-deed auction.',special:'This row covers the Douglas County Treasurer delinquent-real-property tax-lien/certificate sale, not sheriff foreclosure or a tax-deed auction. The February 5, 2026 legal notice states that listed liens were subject to sale for delinquent taxes and special assessments and that the March 2 sale was for taxes, special assessments, interest, and costs. Market-level only: do not bulk republish owner/taxpayer names and do not fabricate parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, or deed outcomes. Official Treasurer page: https://treasurer.douglascounty-ne.gov/public-tax-sale/ . Public 2026 legal notice: https://www.omahadailyrecord.com/sites/default/files/DELINQUENT%20TAX%20DOUGLAS%20COUNTY%202025%20p%201.pdf . Nebraska statutes: https://nebraskalegislature.gov/laws/statutes.php?statute=77-1802 and https://nebraskalegislature.gov/laws/statutes.php?statute=77-1824 .',source:'https://treasurer.douglascounty-ne.gov/public-tax-sale/'}'''

EVENT = {
    "record_id": EVENT_ID,
    "record_type": "market_event",
    "state": "NE",
    "state_name": "Nebraska",
    "county": "Douglas County",
    "sale_type": "tax_lien",
    "product_type": "Public tax sale / certificate of tax sale",
    "auction_date": "2026-03-02",
    "sale_date": "2026-03-02",
    "auction_time": "Online bidding through March 2, 2026",
    "auction_format": "Online public tax-lien sale; the published 2026 notice accepted online bids from February 5 through March 2, 2026",
    "sale_status": "Douglas County's officially published 2026 annual tax-lien sale has passed. Historical market-level event only; no current parcel or certificate inventory is asserted here.",
    "official_source_url": SOURCE,
    "important_rules": "Market-level calendar event only. This is the Douglas County Treasurer delinquent-real-property tax-lien/certificate sale, not a sheriff foreclosure, tax-deed auction, or immediate ownership transfer. No owner/taxpayer names, parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, or deed outcomes are republished or inferred here.",
    "data_source": "Douglas County Treasurer official Public Tax Sale page and published 2026 delinquent-tax notice",
    "last_verified": "2026-09-03",
    "market_level_only": True,
}


def find_rows_bounds(text: str):
    rows_start = text.find("const rows=[")
    if rows_start < 0:
        raise SystemExit("Could not find rows array")
    rows_end = text.find("\n];", rows_start)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")
    return rows_start, rows_end


def find_row_bounds(text: str):
    rows_start, rows_end = find_rows_bounds(text)
    marker_pos = text.find(MARKER, rows_start, rows_end)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", rows_start, marker_pos + 1)
    if row_start < rows_start:
        raise SystemExit("Found Douglas marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Douglas marker but could not locate row end")
    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Douglas repair outside rows array")
    return row_start, row_end


def ensure_index_row():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Douglas County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Douglas County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Douglas County tax-lien market")


def ensure_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    properties = payload.setdefault("properties", [])
    matches = [i for i, item in enumerate(properties) if item.get("record_id") == EVENT_ID]
    if len(matches) > 1:
        raise SystemExit("Refusing to repair duplicate Douglas County market events automatically")
    if matches:
        idx = matches[0]
        if properties[idx] == EVENT:
            print("Douglas County calendar event already canonical")
            return
        properties[idx] = EVENT
        print("Restored canonical Douglas County calendar event")
    else:
        properties.append(EVENT)
        print("Added Douglas County calendar event")
    payload["updated_at"] = "2026-09-04T00:30:00Z"
    EVENTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ensure_index_row()
    ensure_calendar_event()


if __name__ == "__main__":
    main()
