#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Arizona — Navajo County"
EVENT_ID = "AZ-NavajoCounty-2026-market-event"
SOURCE_HOST = "www.navajocountyaz.gov"


def main():
    text = INDEX.read_text(encoding="utf-8")
    if text.count(MARKER) != 1:
        raise SystemExit(f"Expected exactly one Navajo County market row; found {text.count(MARKER)}")

    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    matches = [row for row in payload.get("properties", []) if row.get("record_id") == EVENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one Navajo County calendar event; found {len(matches)}")

    event = matches[0]
    required = {
        "record_type": "market_event",
        "state": "AZ",
        "county": "Navajo County",
        "sale_type": "tax_lien",
        "auction_date": "2026-02-11",
        "market_level_only": True,
    }
    for key, expected in required.items():
        if event.get(key) != expected:
            raise SystemExit(f"Navajo event {key!r} must be {expected!r}; got {event.get(key)!r}")

    source = event.get("official_source_url", "")
    if SOURCE_HOST not in source:
        raise SystemExit("Navajo event must use the official Navajo County source")

    rules = event.get("important_rules", "").lower()
    required_safety_phrases = (
        "not an immediate sale of the property",
        "back tax land/deed",
        "do not bulk republish owner/taxpayer names",
        "no parcel inventory",
        "assessed/appraised values",
        "opening/minimum bids",
        "bidder eligibility",
    )
    for phrase in required_safety_phrases:
        if phrase not in rules:
            raise SystemExit(f"Navajo event missing safety/legal guard: {phrase}")

    forbidden_keys = {
        "owner", "owner_name", "taxpayer", "taxpayer_name", "parcel_id", "address",
        "assessed_value", "appraised_value", "opening_bid", "minimum_bid", "amount_due"
    }
    present = forbidden_keys.intersection(event)
    if present:
        raise SystemExit(f"Navajo market-level event must not contain parcel/owner/value fields: {sorted(present)}")

    print("Navajo County Arizona market row/calendar event passed source and safety validation")


if __name__ == "__main__":
    main()
