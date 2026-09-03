#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Scotts Bluff County"
EVENT_ID = "NE-ScottsBluffCounty-2026-market-event"

ROW = r'''{state:'Nebraska — Scotts Bluff County',product:'Tax lien / tax sale certificate',schedule:'Scotts Bluff County states its public tax sale is held the first Monday in March each year at 9:00 a.m. The 2026 sale therefore occurred on <span class="schedule-date">March 2, 2026</span>; the county\'s 2026 registration form required registrations and fees by February 26, 2026. Verify every future sale date directly with the Treasurer.',availability:'2026 public sale passed. The county says parcels remaining after the public sale may be offered through Private Tax Sale, but no particular parcel or certificate is asserted as currently available here; verify the current official delinquent-tax list and Treasurer procedure.',maxReturn:'14%/yr stated certificate interest',interest:'The Scotts Bluff County Treasurer states the interest rate earned on tax-sale certificates is 14%. Verify current county guidance and Nebraska law before relying on any return.',bid:'https://scottsbluffcountyne.gov/treasurer-office/public-tax-sale-information/',canadian:'The county registration materials collect taxpayer-identification and other registration information but do not establish a simple foreign-bidder rule. Do not assume Canadian eligibility; confirm current identification, taxpayer-information, registration, payment, and certificate requirements directly with the Scotts Bluff County Treasurer.',itin:'The official registration page requires an SS / Tax Identification number and the tax-sale information page links a W-9, but the county does not state that an ITIN or foreign-tax form is accepted. Confirm current taxpayer-identification requirements directly with the Treasurer.',online:'NO for the published procedure — Scotts Bluff County states the public sale is held in person at the County Administration Building in Gering and uses a round-robin bidder process. The delinquent list is available online, but that is not an online-auction claim.',otc:'The county states remaining parcel taxes after the public sale are offered under Private Tax Sale. This is not a claim that any particular parcel or certificate is currently available; verify current inventory and purchase procedure directly with the Treasurer/current official list.',deed:'A tax-sale certificate is not immediate ownership or possession. The Treasurer expressly states that the certificate purchaser is purchasing delinquent taxes, not the property, that the holder has only a lien, and that a property owner has three years from certificate issuance to redeem before foreclosure can begin.',special:'MARKET-LEVEL ONLY. This row covers Scotts Bluff County\'s delinquent-real-property tax-lien/certificate process, not an immediate tax-deed, sheriff sale, or mortgage-foreclosure transfer. The official Treasurer page publishes the annual first-Monday-in-March schedule, in-person round-robin procedure, daily-updated delinquent-list link, 14% interest statement, three-year redemption statement, and explicit warning that a certificate is a lien rather than ownership. Do not bulk republish owner/taxpayer names and do not fabricate parcel availability, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, foreclosure outcomes, or deed outcomes. Official source: https://scottsbluffcountyne.gov/treasurer-office/public-tax-sale-information/ .',source:'https://scottsbluffcountyne.gov/treasurer-office/public-tax-sale-information/'}'''

EVENT = {
    "record_id": EVENT_ID,
    "record_type": "market_event",
    "state": "NE",
    "state_name": "Nebraska",
    "county": "Scotts Bluff County",
    "sale_type": "tax_lien",
    "product_type": "Public tax sale / tax sale certificate",
    "auction_date": "2026-03-02",
    "sale_date": "2026-03-02",
    "auction_time": "09:00 MT",
    "auction_format": "In-person public tax sale; round-robin bidder procedure",
    "sale_status": "The 2026 public tax sale has passed. Historical market-level event only; no current parcel inventory is asserted. The county says remaining parcel taxes may move to Private Tax Sale after the public sale, subject to current official availability and procedure.",
    "official_source_url": "https://scottsbluffcountyne.gov/treasurer-office/public-tax-sale-information/",
    "secondary_official_source_url": "https://scottsbluffcountyne.gov/treasurer-office/public-tax-sale-information/public-tax-sale-registration-form/",
    "important_rules": "Market-level calendar event only. This is a tax-lien/certificate sale, not an immediate property transfer. The county states certificate holders have a lien, not ownership; no owner names, parcel inventory, opening/minimum bids, or bidder-eligibility claims are republished or inferred here.",
    "data_source": "Scotts Bluff County Treasurer official Public Tax Sale Information and 2026 registration form",
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
        raise SystemExit("Scotts Bluff row boundaries are invalid")
    return row_start, min(endings) + 1


def ensure_index_row():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Scotts Bluff County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Scotts Bluff County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Scotts Bluff County tax-lien market")


def ensure_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    properties = payload.setdefault("properties", [])
    matches = [i for i, item in enumerate(properties) if item.get("record_id") == EVENT_ID]
    if len(matches) > 1:
        raise SystemExit("Refusing to repair duplicate Scotts Bluff County market events automatically")
    if matches:
        idx = matches[0]
        if properties[idx] == EVENT:
            print("Scotts Bluff County calendar event already canonical")
            return
        properties[idx] = EVENT
        print("Restored canonical Scotts Bluff County calendar event")
    else:
        properties.append(EVENT)
        print("Added Scotts Bluff County calendar event")
    payload["updated_at"] = "2026-09-03T17:20:00Z"
    EVENTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ensure_index_row()
    ensure_calendar_event()


if __name__ == "__main__":
    main()
