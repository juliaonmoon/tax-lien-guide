#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Frontier County"
EVENT_ID = "NE-FrontierCounty-2026-market-event"

ROW = r'''{state:'Nebraska — Frontier County',product:'Tax lien / tax sale certificate',schedule:'Frontier County Treasurer published its 2026 County Tax Sale for <span class="schedule-date">March 2, 2026</span> starting at 9:00 a.m. The county states that its public tax sale is held the first Monday in March each year at 9:00 a.m. at the County Courthouse. The 2026 public sale has passed; verify every later date and notice directly with the Treasurer before relying on it.',availability:'2026 public sale passed — no current parcel inventory is asserted here. Frontier County states that after the public sale closes, remaining delinquent taxes are offered under Private Tax Sale; verify current availability and purchase procedure directly with the Treasurer/current official delinquent-tax source.',maxReturn:'14%/yr stated certificate interest',interest:'The Frontier County Treasurer public tax-sale page states the tax-sale certificate interest rate is 14% and the redemption time is three years. Nebraska law governs redemption, subsequent-tax, foreclosure, and certificate procedures; verify current county guidance and statutes before relying on any return or outcome.',bid:'https://frontiercounty.ne.gov/treasurer-office/public-tax-sale-information/',canadian:'The published county materials describe registration, taxpayer-identification, payment, and certificate requirements but do not establish a simple foreign-bidder rule. Do not assume Canadian eligibility; confirm current identification, registration, payment, tax-form, and certificate requirements directly with the Frontier County Treasurer.',itin:'The official 2026 registration form requests a completed W-9 and Federal ID or SS number. It does not establish that an ITIN or a foreign-tax form is accepted. Confirm current taxpayer-identification requirements directly with the Frontier County Treasurer before relying on an ITIN.',online:'NO for the published sale procedure — Frontier County describes an in-person sale at the County Courthouse with bidder order determined by drawing and one choice per bidder per round. The official delinquent-tax list is linked online through Nebraska Taxes Online, but that is not an online-auction claim.',otc:'Frontier County states that after the public sale closes, delinquent taxes are offered under Private Tax Sale. This is not a claim that any particular parcel or certificate is currently available; verify current inventory and purchase procedure directly with the Treasurer/current official delinquent-tax source.',deed:'A tax-sale certificate is not immediate ownership or possession. Frontier County expressly states that purchasers are buying delinquent taxes, not the property; it describes a three-year redemption period and says later foreclosure steps arise only if the certificate is not redeemed. Verify current Nebraska law and obtain legal advice before relying on any foreclosure or deed outcome.',special:'This row covers the Frontier County Treasurer delinquent-real-property tax-lien/certificate process, not an immediate tax-deed or sheriff-foreclosure auction. The official 2026 page publishes the March 2, 2026 sale date, 9:00 a.m. start, official delinquent-list link, registration process, in-person rotation procedure, payment requirements, three-year redemption period, and 14% interest statement. Market-level only: do not bulk republish owner/taxpayer names and do not fabricate parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, foreclosure outcomes, or deed outcomes. Official Public Tax Sale Information page: https://frontiercounty.ne.gov/treasurer-office/public-tax-sale-information/ .',source:'https://frontiercounty.ne.gov/treasurer-office/public-tax-sale-information/'}'''

EVENT = {
    "record_id": EVENT_ID,
    "record_type": "market_event",
    "state": "NE",
    "state_name": "Nebraska",
    "county": "Frontier County",
    "sale_type": "tax_lien",
    "product_type": "Public Tax Sale / tax sale certificate",
    "auction_date": "2026-03-02",
    "sale_date": "2026-03-02",
    "auction_time": "09:00 CT",
    "auction_format": "In-person County Tax Sale at the Frontier County Courthouse; bidder order is determined by drawing and each round allows one choice per bidder",
    "sale_status": "Frontier County's officially published 2026 public sale occurred March 2, 2026. This is a historical market-level event, not current parcel inventory; verify any current Private Tax Sale availability directly with the Treasurer.",
    "official_source_url": "https://frontiercounty.ne.gov/treasurer-office/public-tax-sale-information/",
    "secondary_official_source_url": "https://frontiercounty.ne.gov/wp-content/uploads/sites/43/2026/02/Tax-Sale-Registration-Form.pdf",
    "important_rules": "Market-level calendar event only. Frontier County states certificate purchasers buy delinquent taxes, not the property; its page states a three-year redemption time and 14% interest. The public sale is separate from any later foreclosure process. No owner names, parcel inventory, opening/minimum bids, or current private-sale availability are republished or inferred here.",
    "data_source": "Frontier County Treasurer Public Tax Sale Information and official 2026 Tax Sale Registration Form",
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
        raise SystemExit("Found Frontier marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Frontier marker but could not locate row end")
    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Frontier repair outside rows array")
    return row_start, row_end


def ensure_index_row():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Frontier County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Frontier County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Frontier County tax-lien market")


def ensure_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    properties = payload.setdefault("properties", [])
    matches = [i for i, item in enumerate(properties) if item.get("record_id") == EVENT_ID]
    if len(matches) > 1:
        raise SystemExit("Refusing to repair duplicate Frontier County market-event records automatically")
    if matches:
        idx = matches[0]
        if properties[idx] == EVENT:
            print("Frontier County calendar event already canonical")
            return
        properties[idx] = EVENT
        print("Restored canonical Frontier County calendar event")
    else:
        properties.append(EVENT)
        print("Added Frontier County calendar event")
    payload["updated_at"] = "2026-09-03T11:30:00Z"
    EVENTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ensure_index_row()
    ensure_calendar_event()


if __name__ == "__main__":
    main()
