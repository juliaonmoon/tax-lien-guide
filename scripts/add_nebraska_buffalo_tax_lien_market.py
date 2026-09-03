#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Buffalo County"
EVENT_ID = "NE-BuffaloCounty-2026-market-event"

ROW = r'''{state:'Nebraska — Buffalo County',product:'Tax lien / tax sale certificate',schedule:'Buffalo County held its 2026 public tax sale on <span class="schedule-date">March 2, 2026</span> at the Buffalo County Courthouse in Kearney. The county\'s official 2026 instructions describe registration, tax-sale certificates, and an updated pre-sale parcel list.',availability:'The official 2026 advertising list and sale instructions are historical sale materials. Do not treat them as current certificate inventory after the March 2, 2026 sale. Confirm any currently available delinquent-tax opportunity directly with the Buffalo County Treasurer.',maxReturn:'14%/yr statutory redemption interest',interest:'Nebraska tax-sale certificates are governed by state law; the applicable statutory redemption interest rate is currently 14% per year. Verify current Nebraska statutes before relying on the rate because law can change.',bid:'https://buffalocounty.ne.gov/county-offices/treasurer',canadian:'Buffalo County publishes bidder registration requirements, but the public 2026 materials do not establish a simple foreign-bidder eligibility rule. Do not assume Canadian eligibility; confirm registration, taxpayer-information, payment, and attendance requirements directly with the Treasurer.',itin:'The public county materials require a W-9 for 2026 registration and do not establish that an ITIN or foreign-tax form is accepted instead. Confirm directly with the Buffalo County Treasurer before relying on any substitute documentation.',online:'The official 2026 instructions describe an in-person public sale at the Buffalo County Courthouse in Kearney. Do not represent the 2026 sale as an online auction.',otc:'No current over-the-counter inventory is asserted here. The county\'s 2026 materials describe the annual public sale and a pre-sale updated parcel list; post-sale availability must be verified with the Treasurer.',deed:'A Nebraska tax-sale certificate represents a lien-related certificate, not immediate ownership or possession of the property. Nebraska law separately governs redemption, tax-deed, notice, and foreclosure procedures.',special:'This row covers Buffalo County\'s delinquent real-property tax lien/certificate sale, not sheriff/mortgage foreclosure or an ordinary deed sale. Market-level only: do not bulk republish owner/taxpayer names from the delinquent list and do not fabricate parcel availability, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, or deed outcomes. Official Treasurer page: https://buffalocounty.ne.gov/county-offices/treasurer . Official 2026 tax-sale instructions: https://buffalocounty.ne.gov/Portals/0/2026%20TAX%20SALE%20INFORMATION%20FOR%20WEBSITE%20%281%29.pdf . Official 2026 delinquent-tax advertising list: https://buffalocounty.ne.gov/files/Treasurer/2026/2026%20Advertising%20List%202-2-2026.pdf . Nebraska statutes: https://nebraskalegislature.gov/laws/display_html.php?begin_section=77-1801&end_section=77-1863 .',source:'https://buffalocounty.ne.gov/county-offices/treasurer'}'''

EVENT = {
    "record_id": EVENT_ID,
    "record_type": "market_event",
    "state": "NE",
    "state_name": "Nebraska",
    "county": "Buffalo County",
    "sale_type": "tax_lien",
    "product_type": "Public Tax Sale / tax sale certificate",
    "auction_date": "2026-03-02",
    "sale_date": "2026-03-02",
    "auction_time": "09:00 CT",
    "auction_format": "In-person Public Tax Sale at the Buffalo County Courthouse in Kearney",
    "sale_status": "Buffalo County's officially published 2026 public sale occurred March 2, 2026. Historical market-level event only; no current parcel or certificate inventory is asserted.",
    "official_source_url": "https://buffalocounty.ne.gov/Portals/0/2026%20TAX%20SALE%20INFORMATION%20FOR%20WEBSITE%20%281%29.pdf",
    "secondary_official_source_url": "https://buffalocounty.ne.gov/county-offices/treasurer",
    "important_rules": "Market-level calendar event only. The 2026 procedure was an in-person tax-sale certificate sale, not an online auction or immediate property transfer. The registration materials require a W-9 but do not establish foreign-bidder or ITIN acceptance. No owner names, current parcel inventory, opening/minimum bids, property characteristics, redemption outcomes, or deed outcomes are republished or inferred.",
    "data_source": "Buffalo County Treasurer 2026 Tax Sale Information and Treasurer page",
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
        raise SystemExit("Found Buffalo marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Buffalo marker but could not locate row end")
    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Buffalo repair outside rows array")
    return row_start, row_end


def ensure_index_row():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Buffalo County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Buffalo County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Buffalo County tax-lien market")


def ensure_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    properties = payload.setdefault("properties", [])
    matches = [i for i, item in enumerate(properties) if item.get("record_id") == EVENT_ID]
    if len(matches) > 1:
        raise SystemExit("Refusing to repair duplicate Buffalo County market-event records automatically")
    if matches:
        idx = matches[0]
        if properties[idx] == EVENT:
            print("Buffalo County calendar event already canonical")
            return
        properties[idx] = EVENT
        print("Restored canonical Buffalo County calendar event")
    else:
        properties.append(EVENT)
        print("Added Buffalo County calendar event")
    payload["updated_at"] = "2026-09-03T12:11:00Z"
    EVENTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ensure_index_row()
    ensure_calendar_event()


if __name__ == "__main__":
    main()
