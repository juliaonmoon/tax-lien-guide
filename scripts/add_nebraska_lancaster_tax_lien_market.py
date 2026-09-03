#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Lancaster County"
EVENT_ID = "NE-LancasterCounty-2026-market-event"
SOURCE = "https://www.lancaster.ne.gov/444/Tax-Sale-Information"
DETAILS = "https://www.lancaster.ne.gov/DocumentCenter/View/641/Tax-Sale-Purchasing-Information-PDF"

ROW = r'''{state:'Nebraska — Lancaster County',product:'Tax lien / certificate of tax sale',schedule:'Lancaster County held its 2026 Public Delinquent Tax Lien Sale on <span class="schedule-date">March 2, 2026</span> at the Lancaster County Council Chambers. The 2026 annual sale has passed; monitor the official Treasurer publication for the next sale date rather than inferring one.',availability:'The Treasurer\'s current Delinquent Tax Listing page says the current list is for Private Sale and, as currently published, “No parcels available at this time.” Do not fabricate post-sale inventory; recheck the official page before asserting availability.',maxReturn:'14%/yr current statutory redemption interest',interest:'Neb. Rev. Stat. § 45-104.01 currently sets 14% annual interest on delinquent taxes or special assessments owing to Nebraska political subdivisions, and § 77-1824 applies the rate specified in § 45-104.01 to redemption from a real-property tax sale. Verify current law and the current Treasurer publication before relying on the rate.',bid:'https://www.lancaster.ne.gov/444/Tax-Sale-Information',canadian:'The county requires annual bidder registration and publishes tax-sale forms, but its public materials do not establish a simple foreign-bidder rule. Do not assume Canadian eligibility; confirm accepted taxpayer-identification, registration, payment, representation, and certificate requirements directly with the Lancaster County Treasurer.',itin:'The published registration materials include Form W-9 but do not establish that an ITIN or foreign-tax form is accepted as a substitute. Confirm current taxpayer-identification requirements directly with the Lancaster County Treasurer.',online:'NO for the published 2026 procedure — Lancaster County states bidders must be present on the day of sale, with the public sale conducted at the Lancaster County Council Chambers. Reconfirm the method for every later sale.',otc:'Lancaster County currently labels its post-sale delinquent-tax page “Private Sale,” but the same official page presently states “No parcels available at this time.” Do not represent private-sale certificates as available unless the Treasurer publishes current parcel inventory.',deed:'A tax-sale certificate is not immediate ownership or possession. Nebraska law provides a redemption process for real property sold for taxes and refers to the purchaser\'s tax-sale certificate before any later tax-deed process. Verify current Nebraska law and obtain appropriate legal advice before relying on any deed or foreclosure path.',special:'This row covers Lancaster County\'s Treasurer public delinquent tax-lien/certificate sale and any officially published post-sale private-sale availability, not sheriff foreclosure sales or immediate tax-deed auctions. Market-level only: do not bulk republish owner/taxpayer names and do not fabricate parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, foreclosure outcomes, or deed outcomes. Official 2026 sale notice: https://www.lancaster.ne.gov/DocumentCenter/View/640/Tax-Sale-Information-PDF . Official purchasing information: https://www.lancaster.ne.gov/DocumentCenter/View/641/Tax-Sale-Purchasing-Information-PDF . Current private-sale status: https://www.lancaster.ne.gov/396/Delinquent-Tax-Listing . Tax-sale listing procedure: https://www.lancaster.ne.gov/849/Tax-Delinquency-Listing . Nebraska statutes: https://nebraskalegislature.gov/laws/statutes.php?statute=s4501004001 and https://nebraskalegislature.gov/laws/statutes.php?statute=77-1824 .',source:'https://www.lancaster.ne.gov/444/Tax-Sale-Information'}'''

EVENT = {
    "record_id": EVENT_ID,
    "record_type": "market_event",
    "state": "NE",
    "state_name": "Nebraska",
    "county": "Lancaster County",
    "sale_type": "tax_lien",
    "product_type": "Public Delinquent Tax Lien Sale / certificate of tax sale",
    "auction_date": "2026-03-02",
    "sale_date": "2026-03-02",
    "auction_time": "09:00 CT (2026 check-in 08:30 CT)",
    "auction_format": "In-person Public Tax Sale; round-robin format under Neb. Rev. Stat. § 77-1807",
    "sale_status": "Lancaster County's officially published 2026 Public Delinquent Tax Lien Sale occurred March 2, 2026. The county's current private-sale page states no parcels are available at this time; no current parcel or certificate inventory is asserted here.",
    "official_source_url": SOURCE,
    "secondary_official_source_url": DETAILS,
    "important_rules": "Market-level calendar event only. This is Lancaster County's delinquent-real-property tax-lien/certificate process, not an immediate tax-deed, sheriff-foreclosure sale, or immediate property ownership. No owner/taxpayer names, parcel inventory, opening/minimum bids, amounts due, property characteristics, or bidder-eligibility claims are republished or inferred here.",
    "data_source": "Lancaster County Treasurer official Tax Sale Information and Purchasing Tax Sale Certificates instructions",
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
        raise SystemExit("Found Lancaster marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Lancaster marker but could not locate row end")

    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Lancaster repair outside rows array")
    return row_start, row_end


def ensure_index_row():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Lancaster County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Lancaster County tax-lien market row")
        return

    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Lancaster County tax-lien market")


def ensure_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    properties = payload.setdefault("properties", [])
    matches = [i for i, item in enumerate(properties) if item.get("record_id") == EVENT_ID]
    if len(matches) > 1:
        raise SystemExit("Refusing to repair duplicate Lancaster County market events automatically")
    if matches:
        idx = matches[0]
        if properties[idx] == EVENT:
            print("Lancaster County calendar event already canonical")
            return
        properties[idx] = EVENT
        print("Restored canonical Lancaster County calendar event")
    else:
        properties.append(EVENT)
        print("Added Lancaster County calendar event")
    payload["updated_at"] = "2026-09-03T23:20:00Z"
    EVENTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ensure_index_row()
    ensure_calendar_event()


if __name__ == "__main__":
    main()
