#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Colfax County"
EVENT_ID = "NE-ColfaxCounty-2026-market-event"

ROW = r'''{state:'Nebraska — Colfax County',product:'Tax lien / certificate of tax sale',schedule:'Colfax County Treasurer published its 2026 County Tax Sale for <span class="schedule-date">March 2, 2026</span> at 9:00 a.m. at the County Courthouse. The 2026 sale has passed. Do not present a later Colfax County sale date, time, venue, or delinquent-tax list as confirmed until the Treasurer publishes the current information.',availability:'2026 public tax-lien/certificate sale passed — no current parcel inventory is asserted here. The Treasurer states that after the public sale closes, delinquent taxes may be offered under Private Tax Sale; do not infer that any specific parcel or certificate is currently available and verify current availability directly with the Treasurer.',maxReturn:'14%/yr published certificate interest',interest:'The Colfax County Treasurer FAQ states a 14% interest rate for tax-sale certificates. Nebraska redemption law applies the rate specified in Neb. Rev. Stat. § 45-104.01, which currently provides 14% per annum for delinquent taxes or special assessments owing to Nebraska political subdivisions. Verify current law and current county guidance before bidding.',bid:'https://colfaxcountyne.gov/treasurer-office/public-tax-sale-information/',canadian:'The published county information requires a separate completed registration for each company and a registration fee, but it does not establish a simple foreign-bidder rule. Do not assume Canadian eligibility; confirm current taxpayer-identification, registration, payment, and certificate requirements directly with the Colfax County Treasurer.',itin:'The published county information does not establish that an ITIN or foreign-tax form is accepted. Confirm current taxpayer-identification requirements directly with the Colfax County Treasurer before relying on an ITIN.',online:'NO for the published 2026 procedure — Colfax County states that the tax sale is held at the County Courthouse and uses a randomly drawn bidder order with one choice per bidder per round. Nebraska Taxes Online provides the public delinquent-tax sale list; it is not asserted here as an online auction platform. Reconfirm the method for every later sale.',otc:'The Treasurer states that when the public sale closes, delinquent taxes are offered under Private Tax Sale. This is not a claim that any particular parcel or certificate is currently available; verify current inventory and purchase procedure directly with the Colfax County Treasurer.',deed:'A tax-sale certificate is not immediate ownership or possession. The Treasurer explicitly says certificate purchasers are purchasing delinquent taxes, not the property. The county describes a three-year redemption period and a later foreclosure process if a certificate remains unredeemed; verify current statutes, notices, timing, title issues, and legal requirements before relying on any foreclosure or deed outcome.',special:'This row covers the Colfax County Treasurer delinquent-real-property tax-lien/certificate process, not an immediate tax-deed or sheriff-foreclosure auction. The county publishes its delinquent-tax sale list through Nebraska Taxes Online and warns investors that purchasing a certificate means purchasing delinquent taxes, not the property. Market-level only: do not bulk republish owner/taxpayer names and do not fabricate parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, foreclosure outcomes, or deed outcomes. Official Public Tax Sale Information page: https://colfaxcountyne.gov/treasurer-office/public-tax-sale-information/ . Nebraska statutes: https://nebraskalegislature.gov/laws/statutes.php?statute=45-104.01 and https://nebraskalegislature.gov/laws/statutes.php?statute=77-1824 .',source:'https://colfaxcountyne.gov/treasurer-office/public-tax-sale-information/'}'''

EVENT = {
    "record_id": EVENT_ID,
    "record_type": "market_event",
    "state": "NE",
    "state_name": "Nebraska",
    "county": "Colfax County",
    "sale_type": "tax_lien",
    "product_type": "County Tax Sale / certificate of tax sale",
    "auction_date": "2026-03-02",
    "sale_date": "2026-03-02",
    "auction_time": "09:00 CT",
    "auction_format": "In-person county tax sale at the County Courthouse; randomly drawn bidder order with one choice per bidder per round",
    "sale_status": "Colfax County's officially published 2026 County Tax Sale occurred March 2, 2026. Historical market-level event only; no current parcel or certificate inventory is asserted.",
    "official_source_url": "https://colfaxcountyne.gov/treasurer-office/public-tax-sale-information/",
    "important_rules": "Market-level calendar event only. This is Colfax County's delinquent-real-property tax-lien/certificate process, not an immediate tax-deed, sheriff-foreclosure sale, or immediate property ownership. No owner/taxpayer names, parcel inventory, opening/minimum bids, amounts due, property characteristics, or bidder-eligibility claims are republished or inferred here.",
    "data_source": "Colfax County Treasurer official Public Tax Sale Information page; Nebraska redemption statutes",
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
        raise SystemExit("Found Colfax marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Colfax marker but could not locate row end")
    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Colfax repair outside rows array")
    return row_start, row_end


def ensure_index_row():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Colfax County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Colfax County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Colfax County tax-lien market")


def ensure_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    properties = payload.setdefault("properties", [])
    matches = [i for i, item in enumerate(properties) if item.get("record_id") == EVENT_ID]
    if len(matches) > 1:
        raise SystemExit("Refusing to repair duplicate Colfax County market events automatically")
    if matches:
        idx = matches[0]
        if properties[idx] == EVENT:
            print("Colfax County calendar event already canonical")
            return
        properties[idx] = EVENT
        print("Restored canonical Colfax County calendar event")
    else:
        properties.append(EVENT)
        print("Added Colfax County calendar event")
    payload["updated_at"] = "2026-09-03T22:20:00Z"
    EVENTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ensure_index_row()
    ensure_calendar_event()


if __name__ == "__main__":
    main()
