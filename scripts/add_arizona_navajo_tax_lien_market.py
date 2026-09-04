#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Arizona — Navajo County"
EVENT_ID = "AZ-NavajoCounty-2026-market-event"
SOURCE = "https://www.navajocountyaz.gov/459/February-Lien-Sale-Instructions"

ROW = r'''{state:'Arizona — Navajo County',product:'Tax lien / Certificate of Purchase',schedule:'Annual electronic tax-lien sale. Navajo County held the 2026 sale on <span class="schedule-date">February 11, 2026</span> through RealAuction; bidding opened February 3, 2026. County guidance says the sale is usually held on the second Wednesday of February.',availability:'After the annual auction, unsold tax liens become state-held liens and may be purchased over the counter March 1–December 31, subject to current county/RealAuction availability; the Certificate of Purchase books are closed January 1 through the last business day of February.',maxReturn:'16%/yr statutory max',interest:'Auction tax-lien certificates are awarded through the Arizona bid-down process, so the actual certificate rate may be below the statutory 16% annual ceiling. Navajo County states over-the-counter state-held liens are set at 16% annual simple interest, prorated monthly. Verify the specific certificate terms before relying on a rate.',bid:'https://www.navajocountyaz.gov/459/February-Lien-Sale-Instructions',canadian:'Navajo County uses online bidder registration through RealAuction for the February auction. Foreign bidders should confirm current taxpayer-identification, W-8/W-9 and payment requirements with the Treasurer/auction provider before registering or purchasing an over-the-counter lien.',itin:'Do not assume a foreign bidder can substitute documents without county confirmation. Verify the current investor-registration and taxpayer-identification requirements directly with the Treasurer/RealAuction.',online:'YES — Navajo County states its February tax-lien sale is electronic through RealAuction.',otc:'YES — county guidance says unsold liens become state-held liens available over the counter March 1–December 31, subject to parcel-specific current availability; the CP books are closed January 1 through the last business day of February.',deed:'A tax-lien purchase is a Certificate of Purchase and is a lien, not an immediate sale of the property. Navajo County says investors may initiate foreclosure proceedings after three years and that certificate holders seeking a Judgment Deed are responsible for the court process.',special:'Keep Navajo County tax liens distinct from the county\'s separate Back Tax Land/deed program, which can result in a quit claim deed and follows a different auction process. Advertised tax-lien parcels can be removed before sale because taxes are paid or because of bankruptcy, and advertised tax amounts may omit interest, penalties, fees, partial payments, or prior certificates. Market-level only: do not bulk republish owner/taxpayer names or fabricate parcel inventory, opening/minimum bids, current OTC availability, or amounts due. Use only current county/RealAuction publication for parcel-specific availability.',source:'https://www.navajocountyaz.gov/459/February-Lien-Sale-Instructions'}'''

EVENT = {
    "record_id": EVENT_ID,
    "record_type": "market_event",
    "state": "AZ",
    "state_name": "Arizona",
    "county": "Navajo County",
    "sale_type": "tax_lien",
    "product_type": "Tax lien / Certificate of Purchase",
    "auction_date": "2026-02-11",
    "sale_date": "2026-02-11",
    "auction_time": "07:00 MST; batches close hourly from 08:00 through 12:00 MST",
    "auction_format": "Electronic annual tax-lien sale through the county-linked RealAuction system",
    "sale_status": "Navajo County's officially published 2026 tax-lien sale occurred February 11, 2026. Historical market-level event only; no current parcel or certificate availability is asserted.",
    "official_source_url": SOURCE,
    "secondary_official_source_url": "https://www.navajocountyaz.gov/457/Property-Tax-Calendar",
    "important_rules": "Market-level calendar event only. Navajo County states this is a sale of delinquent-tax liens/Certificates of Purchase, not an immediate sale of the property; the county separately operates a Back Tax Land/deed program. Do not bulk republish owner/taxpayer names. No parcel inventory, property characteristics, assessed/appraised values, amounts due, opening/minimum bids, current OTC availability, bidder eligibility, redemption outcomes, or later deed outcomes are republished or inferred.",
    "data_source": "Navajo County Treasurer February Lien Sale Instructions and Property Tax Calendar",
    "last_verified": "2026-09-04",
    "market_level_only": True,
}


def find_row_bounds(text: str, start: int, end: int):
    marker_pos = text.find(MARKER, start, end)
    if marker_pos < 0:
        return None

    row_start = text.rfind("{state:", start, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Navajo marker but could not locate row start")

    # index.html contains multiple valid row-separator styles. Choose the
    # nearest valid terminator so repairing one stale row cannot consume later
    # county rows simply because a farther separator style was checked first.
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Navajo marker but could not locate row end")

    row_end = min(endings)
    return row_start, row_end + 1


def add_navajo():
    text = INDEX.read_text(encoding="utf-8")

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    bounds = find_row_bounds(text, start, end)
    if bounds:
        row_start, row_end = bounds
        if row_start < start or row_end > end + 1:
            raise SystemExit("Refusing to repair Navajo row outside rows array")
        existing = text[row_start:row_end]
        if existing == ROW:
            print("Arizona Navajo County row already canonical")
            return
        INDEX.write_text(text[:row_start] + ROW + text[row_end:], encoding="utf-8")
        print("Restored canonical Arizona Navajo County tax-lien market row")
        return

    before = text[:end]
    after = text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Arizona Navajo County tax-lien market")


def ensure_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    properties = payload.setdefault("properties", [])
    matches = [i for i, item in enumerate(properties) if item.get("record_id") == EVENT_ID]
    if len(matches) > 1:
        raise SystemExit("Refusing to repair duplicate Navajo County market events automatically")
    if matches:
        idx = matches[0]
        if properties[idx] == EVENT:
            print("Navajo County calendar event already canonical")
            return
        properties[idx] = EVENT
        print("Restored canonical Navajo County calendar event")
    else:
        properties.append(EVENT)
        print("Added Navajo County calendar event")
    payload["updated_at"] = "2026-09-04T06:00:00Z"
    EVENTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    add_navajo()
    ensure_calendar_event()


if __name__ == "__main__":
    main()
