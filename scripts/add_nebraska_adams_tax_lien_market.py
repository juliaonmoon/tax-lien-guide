#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Adams County"
EVENT_ID = "NE-AdamsCounty-2026-market-event"

ROW = r'''{state:'Nebraska — Adams County',product:'Tax lien / certificate of tax sale',schedule:'Adams County Treasurer published its 2026 Annual Tax Sale for <span class="schedule-date">March 2, 2026</span> at 10:00 a.m. at the Hastings Public Library, with preregistration due February 20, 2026 and a final website-list edit scheduled for February 27, 2026. That sale has passed. Do not present a later Adams County sale as confirmed until the Treasurer publishes the current notice/list.',availability:'2026 annual public tax-lien/certificate sale passed — no current parcel inventory is asserted here. Use the Adams County Treasurer Tax Sales page and its current official list for any later sale or availability.',maxReturn:'14%/yr current statutory redemption interest',interest:'Neb. Rev. Stat. § 45-104.01 currently sets 14% annual interest on delinquent taxes or special assessments owed to Nebraska political subdivisions, and § 77-1824 applies that rate to redemption from a tax sale. Verify current law and the current county notice before bidding.',bid:'https://adamscountyne.gov/treasurer/57-tax-sales',canadian:'The published 2026 county procedures required preregistration, a registration form, Form W-9, a registration fee, and payment arrangements, but they do not establish a simple foreign-bidder rule. Do not assume Canadian eligibility; confirm current taxpayer-identification, registration, payment, and certificate requirements directly with the Adams County Treasurer.',itin:'The published 2026 procedures require Form W-9 and do not establish that an ITIN or foreign-tax form is accepted. Confirm current taxpayer-identification requirements directly with the Adams County Treasurer before relying on an ITIN.',online:'NO for the published 2026 procedure — Adams County describes an in-person sale at the Hastings Public Library. Registered companies receive bidder numbers by random drawing, then select properties in bidder-number rotation. Reconfirm the method for every later sale.',otc:'Do not infer current private-sale, over-the-counter, or county-held certificate inventory from the completed 2026 annual sale. The Treasurer office states that it handles public and private tax sales, but current availability must be confirmed from the current official Tax Sales page/list.',deed:'A tax-sale certificate is not immediate ownership or possession. Nebraska law provides redemption rights and a later statutory tax-deed/foreclosure process; verify current statutes, required notices, timing, title issues, and county procedures before relying on any deed or foreclosure outcome.',special:'This row covers the Adams County Treasurer delinquent-real-property tax-lien/certificate process, not an immediate tax-deed or sheriff-foreclosure auction. For 2026, the Treasurer published PDF and Excel tax-sale lists, stated that the website list would be updated as properties became unavailable, and used an in-person bidder-number rotation. Market-level only: do not bulk republish owner/taxpayer names and do not fabricate parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, foreclosure outcomes, or deed outcomes. Official Tax Sales page: https://adamscountyne.gov/treasurer/57-tax-sales . Official Treasurer page: https://adamscountyne.gov/treasurer . Nebraska statutes: https://nebraskalegislature.gov/laws/statutes.php?statute=45-104.01 and https://nebraskalegislature.gov/laws/statutes.php?statute=77-1824 .',source:'https://adamscountyne.gov/treasurer/57-tax-sales'}'''

EVENT = {
    "record_id": EVENT_ID,
    "record_type": "market_event",
    "state": "NE",
    "state_name": "Nebraska",
    "county": "Adams County",
    "sale_type": "tax_lien",
    "product_type": "Annual Tax Sale / certificate of tax sale",
    "auction_date": "2026-03-02",
    "sale_date": "2026-03-02",
    "auction_time": "10:00 CT",
    "auction_format": "In-person annual tax sale at the Hastings Public Library; registered companies received randomly drawn bidder numbers and selected properties in bidder-number rotation",
    "sale_status": "Adams County's officially published 2026 Annual Tax Sale occurred March 2, 2026. Historical market-level event only; no current parcel or certificate inventory is asserted.",
    "official_source_url": "https://adamscountyne.gov/treasurer/57-tax-sales",
    "secondary_official_source_url": "https://adamscountyne.gov/treasurer",
    "important_rules": "Market-level calendar event only. This is Adams County's delinquent-real-property tax-lien/certificate process, not an immediate tax-deed, sheriff-foreclosure sale, or immediate property ownership. No owner/taxpayer names, parcel inventory, opening/minimum bids, amounts due, or bidder-eligibility claims are republished or inferred here.",
    "data_source": "Adams County Treasurer official Tax Sales page and Treasurer page; Nebraska redemption statutes",
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
        raise SystemExit("Found Adams marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Adams marker but could not locate row end")
    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Adams repair outside rows array")
    return row_start, row_end


def ensure_index_row():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Adams County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Adams County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Adams County tax-lien market")


def ensure_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    properties = payload.setdefault("properties", [])
    matches = [i for i, item in enumerate(properties) if item.get("record_id") == EVENT_ID]
    if len(matches) > 1:
        raise SystemExit("Refusing to repair duplicate Adams County market events automatically")
    if matches:
        idx = matches[0]
        if properties[idx] == EVENT:
            print("Adams County calendar event already canonical")
            return
        properties[idx] = EVENT
        print("Restored canonical Adams County calendar event")
    else:
        properties.append(EVENT)
        print("Added Adams County calendar event")
    payload["updated_at"] = "2026-09-03T21:11:00Z"
    EVENTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ensure_index_row()
    ensure_calendar_event()


if __name__ == "__main__":
    main()
