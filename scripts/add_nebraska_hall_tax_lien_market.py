#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Hall County"
EVENT_ID = "NE-HallCounty-2026-market-event"

ROW = r'''{state:'Nebraska — Hall County',product:'Tax lien / tax sale certificate',schedule:'Hall County held its 2026 public delinquent real-property tax sale on <span class="schedule-date">March 2, 2026</span>. The official Treasurer page now states that all 2024 and prior delinquent taxes were purchased at that sale.',availability:'No remaining delinquent taxes are currently offered for sale according to the Hall County Treasurer\'s official delinquent-tax page. Do not infer current certificate inventory from the archived advertising list.',maxReturn:'14%/yr statutory redemption interest',interest:'Nebraska Revised Statute 77-1824 ties tax-sale redemption interest to section 45-104.01; section 45-104.01 currently states fourteen percent per annum. Verify current Nebraska statutes before relying on the rate because law can change.',bid:'https://reports.hallcountyne.gov/Treasurer/Delinquent/advertlist.php',canadian:'The public Hall County notice does not establish a simple foreign-bidder eligibility rule. Do not assume Canadian eligibility; confirm registration, identification, taxpayer-information, and payment requirements directly with the Treasurer.',itin:'The public county notice does not establish that an ITIN or foreign-tax form is accepted in place of any required U.S. taxpayer documentation. Confirm directly with the Hall County Treasurer.',online:'NO for the published 2026 sale notice — Hall County describes a public sale at the Grand Island Public Library. The delinquent list is published online, but that is not an online-auction claim.',otc:'NO current inventory is published. The Treasurer states there are no remaining delinquent taxes for sale after the March 2, 2026 public tax sale.',deed:'A tax-sale certificate represents a tax lien, not immediate ownership or possession of the property. Nebraska law provides separate redemption, deed, notice, and foreclosure procedures.',special:'MARKET-LEVEL ONLY. This row covers Hall County\'s delinquent real-property tax lien sale, not sheriff/mortgage foreclosure or ordinary deed sales. The official 2026 notice states that all 2024 and prior delinquent taxes were purchased on March 2, 2026 and that there are no remaining delinquent taxes for sale. Do not bulk republish owner/taxpayer names from the advertising list and do not fabricate parcel availability, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, foreclosure outcomes, or deed outcomes. Official 2026 advertising list: https://reports.hallcountyne.gov/Treasurer/Delinquent/advertlist.php . Nebraska statutes: https://nebraskalegislature.gov/laws/statutes.php?statute=77-1824 and https://nebraskalegislature.gov/laws/statutes.php?statute=45-104.01 .',source:'https://reports.hallcountyne.gov/Treasurer/Delinquent/advertlist.php'}'''

EVENT = {
    "record_id": EVENT_ID,
    "record_type": "market_event",
    "state": "NE",
    "state_name": "Nebraska",
    "county": "Hall County",
    "sale_type": "tax_lien",
    "product_type": "Public tax sale / tax sale certificate",
    "auction_date": "2026-03-02",
    "sale_date": "2026-03-02",
    "auction_time": "09:00-17:00 CT",
    "auction_format": "In-person public tax sale at the Grand Island Public Library",
    "sale_status": "Hall County's officially published 2026 public sale occurred March 2, 2026. The Treasurer states all 2024 and prior delinquent taxes were purchased and there are no remaining delinquent taxes for sale. Historical market-level event only; no current parcel inventory.",
    "official_source_url": "https://reports.hallcountyne.gov/Treasurer/Delinquent/advertlist.php",
    "secondary_official_source_url": "https://nebraskalegislature.gov/laws/statutes.php?statute=77-1824",
    "important_rules": "Market-level calendar event only. This is a tax-lien/certificate sale, not an immediate property transfer. Nebraska redemption interest is governed by section 77-1824 and the rate referenced in section 45-104.01. No owner names, parcel inventory, opening/minimum bids, or bidder-eligibility claims are republished or inferred here.",
    "data_source": "Hall County Treasurer official delinquent-tax sale notice and Nebraska Legislature",
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
        raise SystemExit("Found Hall marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Hall marker but could not locate row end")
    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Hall repair outside rows array")
    return row_start, row_end


def ensure_index_row():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Hall County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Hall County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Hall County tax-lien market")


def ensure_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    properties = payload.setdefault("properties", [])
    matches = [i for i, item in enumerate(properties) if item.get("record_id") == EVENT_ID]
    if len(matches) > 1:
        raise SystemExit("Refusing to repair duplicate Hall County market-event records automatically")
    if matches:
        idx = matches[0]
        if properties[idx] == EVENT:
            print("Hall County calendar event already canonical")
            return
        properties[idx] = EVENT
        print("Restored canonical Hall County calendar event")
    else:
        properties.append(EVENT)
        print("Added Hall County calendar event")
    payload["updated_at"] = "2026-09-03T15:15:00Z"
    EVENTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ensure_index_row()
    ensure_calendar_event()


if __name__ == "__main__":
    main()
