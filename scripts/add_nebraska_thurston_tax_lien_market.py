#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Thurston County"
EVENT_ID = "NE-ThurstonCounty-2026-market-event"

ROW = r'''{state:'Nebraska — Thurston County',product:'Tax lien / tax sale certificate',schedule:'Thurston County states its 2026 County Tax Sale was held <span class="schedule-date">March 2, 2026</span> at 9:00 a.m. at the county courthouse in Pender. The Treasurer also states the public sale is held the first Monday in March each year at 9:00 a.m. Verify future dates directly with the Treasurer.',availability:'2026 public sale passed. The Treasurer states delinquent taxes remaining after the public sale may be offered under Private Tax Sale, but no particular parcel or certificate is asserted as currently available here; verify current availability and procedure directly with the Treasurer and current official delinquent-tax list.',maxReturn:'14%/yr stated certificate interest',interest:'The Thurston County Treasurer states the tax-sale certificate interest rate is 14% and the redemption time is three years. Verify current county guidance and Nebraska law before relying on any return or redemption timeline.',bid:'https://thurstoncountyne.gov/treasurer-office/public-tax-sale-information/',canadian:'The official county page does not establish a simple foreign-bidder rule. Do not assume Canadian eligibility; confirm current registration, identification, taxpayer-information, payment, and certificate requirements directly with the Thurston County Treasurer.',itin:'The official county page does not state that an ITIN or foreign-tax form is accepted for bidder registration. Confirm current taxpayer-identification requirements directly with the Treasurer rather than inferring eligibility.',online:'NO for the published public-sale procedure — Thurston County states the public tax sale is held in person at the courthouse in Pender. The delinquent-tax list is published online, but that is not an online-auction claim.',otc:'The Treasurer states delinquent taxes remaining after the public sale are offered under Private Tax Sale. This is not a claim that any particular parcel or certificate is currently available; verify current inventory and purchase procedure directly with the Treasurer.',deed:'A tax-sale certificate is not immediate property ownership. Thurston County expressly states that the purchaser is buying delinquent taxes, not the property; the county describes a three-year redemption period before a certificate holder may begin foreclosure.',special:'MARKET-LEVEL ONLY. This row covers Thurston County\'s delinquent-real-property tax-lien/certificate process, not an immediate tax-deed, sheriff sale, or mortgage-foreclosure transfer. The official Treasurer page publishes the March 2, 2026 sale date, in-person courthouse procedure, public delinquent-tax-list link, 14% interest statement, three-year redemption statement, and explicit warning that certificate purchasers buy delinquent taxes rather than the property. Do not bulk republish owner/taxpayer names and do not fabricate parcel availability, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, foreclosure outcomes, or deed outcomes. Official source: https://thurstoncountyne.gov/treasurer-office/public-tax-sale-information/ .',source:'https://thurstoncountyne.gov/treasurer-office/public-tax-sale-information/'}'''

EVENT = {
    "record_id": EVENT_ID,
    "record_type": "market_event",
    "state": "NE",
    "state_name": "Nebraska",
    "county": "Thurston County",
    "sale_type": "tax_lien",
    "product_type": "Public tax sale / tax sale certificate",
    "auction_date": "2026-03-02",
    "sale_date": "2026-03-02",
    "auction_time": "09:00 CT",
    "auction_format": "In-person public tax sale at the Thurston County Courthouse in Pender; round-robin bidder procedure",
    "sale_status": "Thurston County's officially published 2026 public tax sale occurred March 2, 2026. Historical market-level event only; no current parcel inventory is asserted. The county says remaining delinquent taxes may move to Private Tax Sale after the public sale, subject to current official availability and procedure.",
    "official_source_url": "https://thurstoncountyne.gov/treasurer-office/public-tax-sale-information/",
    "secondary_official_source_url": "https://thurstoncountyne.gov/treasurer-office/real-estate-taxes/",
    "important_rules": "Market-level calendar event only. Thurston County states certificate purchasers buy delinquent taxes, not the property; this is a tax-lien/certificate sale, not an immediate property transfer. No owner names, parcel inventory, opening/minimum bids, or bidder-eligibility claims are republished or inferred here.",
    "data_source": "Thurston County Treasurer official Public Tax Sale Information and Real Estate Taxes pages",
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
    endings = [p for token in ("},\n", "}\n,", "}\n];") if (p := text.find(token, marker_pos, rows_end + 3)) >= 0]
    if row_start < rows_start or not endings:
        raise SystemExit("Thurston row boundaries are invalid")
    return row_start, min(endings) + 1


def ensure_index_row():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Thurston County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Thurston County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Thurston County tax-lien market")


def ensure_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    properties = payload.setdefault("properties", [])
    matches = [i for i, item in enumerate(properties) if item.get("record_id") == EVENT_ID]
    if len(matches) > 1:
        raise SystemExit("Refusing to repair duplicate Thurston County market events automatically")
    if matches:
        idx = matches[0]
        if properties[idx] == EVENT:
            print("Thurston County calendar event already canonical")
            return
        properties[idx] = EVENT
        print("Restored canonical Thurston County calendar event")
    else:
        properties.append(EVENT)
        print("Added Thurston County calendar event")
    payload["updated_at"] = "2026-09-03T19:11:00Z"
    EVENTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ensure_index_row()
    ensure_calendar_event()


if __name__ == "__main__":
    main()
