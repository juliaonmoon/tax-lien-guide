#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Arizona — Graham County"
EVENT_ID = "AZ-GrahamCounty-2026-market-event"
SOURCE = "https://www.graham.az.gov/362/Tax-Sale-Lien-Guidelines"

ROW = r'''{state:'Arizona — Graham County',product:'Tax lien / Certificate of Purchase',schedule:'Annual in-person tax-lien sale is held each February; the official 2026 sale was February 25, 2026. State-owned liens not sold at auction may be purchased later by assignment when the Treasurer\'s current Active Certificate Report shows Investor ID 1.',availability:'2026 annual auction passed — check the current official Active Certificate Report for state-owned assignment liens',maxReturn:'16%/yr statutory max',interest:'Graham County states competitive bidding is based on the least interest rate accepted by the bidder, with 16% as the maximum; state-owned liens available by assignment carry 16% interest. Actual yield depends on the certificate rate and redemption timing.',bid:'https://www.graham.az.gov/360/Tax-Lien-Information',canadian:'County registration requires bidder and taxpayer-identification information. A non-U.S. bidder should confirm directly with the Treasurer which foreign taxpayer documentation is accepted before participating.',itin:'Do not assume a U.S.-person tax form applies to a foreign bidder. Confirm the current taxpayer-identification and withholding documentation accepted by Graham County before funding or bidding.',online:'NO — Graham County states the annual sale is held in person; telephone and mail bids are not accepted.',otc:'YES, BY ASSIGNMENT WHEN OFFICIALLY LISTED — parcels not sold at the annual sale are assigned to the state. Only certificates shown with Investor ID 1 on the county\'s current Active Certificate Report should be treated as available for assignment; obtain the current total due from the Treasurer.',deed:'A tax-lien purchase is a Certificate of Purchase, not an immediate deed or ownership interest. Any later foreclosure/Treasurer\'s-deed process is legally distinct and must follow Arizona law.',special:'Market-level summary only. Do not bulk republish owner/taxpayer names from county records. Do not fabricate parcel inventory, opening/minimum bids, current assignment availability, or amounts due. Graham County separately operates tax-deed processes; keep those distinct from this tax-lien Certificate of Purchase market.',source:'https://www.graham.az.gov/362/Tax-Sale-Lien-Guidelines'}'''

EVENT = {
    "record_id": EVENT_ID,
    "record_type": "market_event",
    "state": "AZ",
    "state_name": "Arizona",
    "county": "Graham County",
    "sale_type": "tax_lien",
    "product_type": "Tax lien / Certificate of Purchase",
    "auction_date": "2026-02-25",
    "sale_date": "2026-02-25",
    "auction_time": "09:00 MST until completed",
    "auction_format": "In-person annual tax-lien sale at the Graham County General Services Building; telephone and mail bids are not accepted",
    "sale_status": "Graham County's officially published 2026 tax-lien sale occurred February 25, 2026. Historical market-level event only; no current parcel or assignment availability is asserted.",
    "official_source_url": SOURCE,
    "secondary_official_source_url": "https://www.graham.az.gov/361/Active-Certificate-List-PDF",
    "important_rules": "Market-level calendar event only. Graham County states the investor receives a Certificate of Purchase for a delinquent-tax lien, not immediate ownership of the property. Any later foreclosure/Treasurer-deed process is separate. Do not bulk republish owner/taxpayer names. No parcel inventory, property characteristics, assessed/appraised values, amounts due, opening/minimum bids, current assignment availability, bidder eligibility, redemption outcomes, or later deed outcomes are republished or inferred.",
    "data_source": "Graham County Treasurer Tax Sale & Lien Guidelines and Active Certificates of Purchase",
    "last_verified": "2026-09-04",
    "market_level_only": True,
}


def find_row_bounds(text: str, start: int, end: int):
    marker_pos = text.find(MARKER, start, end)
    if marker_pos < 0:
        return None

    row_start = text.rfind("{state:", start, marker_pos + 1)
    if row_start < start:
        raise SystemExit("Found Graham County marker but could not locate row start inside rows array")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Graham County marker but could not locate row end")

    row_end = min(endings) + 1
    if row_end > end + 1:
        raise SystemExit("Refusing Graham County repair outside rows array")
    return row_start, row_end


def add_graham():
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
        existing = text[row_start:row_end]
        if existing == ROW:
            print("Arizona Graham County canonical row already present")
        else:
            INDEX.write_text(text[:row_start] + ROW + text[row_end:], encoding="utf-8")
            print("Restored canonical Arizona Graham County tax-lien market row")
    else:
        before = text[:end]
        after = text[end:]
        insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
        INDEX.write_text(before + insertion + after, encoding="utf-8")
        print("Added Arizona Graham County tax-lien market")


def ensure_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    properties = payload.setdefault("properties", [])
    matches = [i for i, item in enumerate(properties) if item.get("record_id") == EVENT_ID]
    if len(matches) > 1:
        raise SystemExit("Refusing to repair duplicate Graham County market events automatically")
    if matches:
        idx = matches[0]
        if properties[idx] == EVENT:
            print("Graham County calendar event already canonical")
            return
        properties[idx] = EVENT
        print("Restored canonical Graham County calendar event")
    else:
        properties.append(EVENT)
        print("Added Graham County calendar event")
    payload["updated_at"] = "2026-09-04T07:00:00Z"
    EVENTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    add_graham()
    ensure_calendar_event()


if __name__ == "__main__":
    main()
