#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Arizona — Apache County"
EVENT_ID = "AZ-ApacheCounty-2026-market-event"
SOURCE = "https://www.apachecountyaz.gov/treasurer"


def fail(message: str):
    raise SystemExit(f"Apache County market validation failed: {message}")


def main():
    index_text = INDEX.read_text(encoding="utf-8")
    if index_text.count(MARKER) != 1:
        fail(f"expected exactly one comparison row, found {index_text.count(MARKER)}")

    start = index_text.find("{state:'" + MARKER + "'")
    if start < 0:
        fail("comparison row not found")
    end = index_text.find("}\n", start)
    if end < 0:
        end = index_text.find("},\n", start)
    row = index_text[start : end + 1] if end >= 0 else index_text[start : start + 6000]
    row_lower = row.lower()

    required_row_text = (
        "tax lien / Certificate of Purchase",
        "not an immediate deed or ownership interest",
        "Do not bulk republish owner/taxpayer names",
        "Do not fabricate parcel inventory, opening/minimum bids",
        SOURCE,
    )
    for text in required_row_text:
        if text.lower() not in row_lower:
            fail(f"comparison row missing required safety/source text: {text!r}")

    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    matches = [item for item in payload.get("properties", []) if item.get("record_id") == EVENT_ID]
    if len(matches) != 1:
        fail(f"expected exactly one calendar event, found {len(matches)}")
    event = matches[0]

    expected = {
        "record_type": "market_event",
        "state": "AZ",
        "county": "Apache County",
        "sale_type": "tax_lien",
        "auction_date": "2026-02-18",
        "sale_date": "2026-02-18",
        "official_source_url": SOURCE,
        "market_level_only": True,
    }
    for key, value in expected.items():
        if event.get(key) != value:
            fail(f"calendar event {key!r} expected {value!r}, got {event.get(key)!r}")

    event_text = json.dumps(event, ensure_ascii=False).lower()
    required_event_text = (
        "certificate of purchase",
        "tax lien",
        "not a deed",
        "do not bulk republish owner/taxpayer names",
        "no current parcel or over-the-counter inventory",
    )
    for text in required_event_text:
        if text not in event_text:
            fail(f"calendar event missing required boundary: {text!r}")

    forbidden_keys = {
        "owner",
        "owner_name",
        "taxpayer",
        "taxpayer_name",
        "parcel_id",
        "parcel_number",
        "opening_bid",
        "minimum_bid",
        "assessed_value",
        "appraised_value",
    }
    present = sorted(key for key in forbidden_keys if key in event)
    if present:
        fail(f"market-level calendar event contains forbidden parcel/personal fields: {present}")

    for unsupported in ("guaranteed return", "guaranteed deed", "immediate ownership"):
        if unsupported in event_text and f"not {unsupported}" not in event_text and f"no {unsupported}" not in event_text:
            fail(f"calendar event contains unsupported claim: {unsupported!r}")

    print("Apache County tax-lien comparison row and calendar event pass source/safety validation")


if __name__ == "__main__":
    main()
