#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Colfax County"
EVENT_ID = "NE-ColfaxCounty-2026-market-event"
SOURCE = "https://colfaxcountyne.gov/treasurer-office/public-tax-sale-information/"


def extract_row(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate rows array")
    pos = text.find(MARKER, rows_start, rows_end)
    if pos < 0:
        raise SystemExit("Colfax County Nebraska market row is missing")
    start = text.rfind("{state:", rows_start, pos + 1)
    endings = [p for token in ("},\n", "}\n,", "}\n];") if (p := text.find(token, pos, rows_end + 3)) >= 0]
    if start < rows_start or not endings:
        raise SystemExit("Could not safely isolate Colfax County row")
    return text[start:min(endings) + 1]


def main():
    row = extract_row(INDEX.read_text(encoding="utf-8"))
    lower = row.lower()
    required = [
        "march 2, 2026",
        "tax lien / certificate of tax sale",
        "county courthouse",
        "no current parcel inventory is asserted here",
        "not immediate ownership or possession",
        "purchasing delinquent taxes, not the property",
        "do not bulk republish owner/taxpayer names",
        SOURCE,
    ]
    missing = [phrase for phrase in required if phrase not in lower]
    if missing:
        raise SystemExit("Colfax County row missing required source/safety text: " + ", ".join(missing))

    unsupported = [
        "current inventory is available",
        "currently available parcels",
        "canadian bidders are eligible",
        "itin is accepted",
        "guaranteed return",
        "guaranteed deed",
    ]
    bad = [phrase for phrase in unsupported if phrase in lower]
    if bad:
        raise SystemExit("Colfax County row contains unsupported claim(s): " + ", ".join(bad))

    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    matches = [item for item in payload.get("properties", []) if item.get("record_id") == EVENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one Colfax County calendar event, found {len(matches)}")
    event = matches[0]
    expected = {
        "record_type": "market_event",
        "state": "NE",
        "county": "Colfax County",
        "sale_type": "tax_lien",
        "auction_date": "2026-03-02",
        "sale_date": "2026-03-02",
        "market_level_only": True,
        "official_source_url": SOURCE,
    }
    for key, value in expected.items():
        if event.get(key) != value:
            raise SystemExit(f"Colfax County calendar event has unexpected {key}: {event.get(key)!r}")

    rules = event.get("important_rules", "").lower()
    for phrase in ("market-level calendar event only", "not an immediate tax-deed", "no owner/taxpayer names", "parcel inventory", "opening/minimum bids"):
        if phrase not in rules:
            raise SystemExit("Colfax County calendar event missing safety boundary text: " + phrase)
    if {"owner", "owner_name", "taxpayer", "taxpayer_name", "mailing_name"} & set(event):
        raise SystemExit("Colfax County market event must not contain owner/taxpayer fields")

    print("Colfax County Nebraska market and calendar validation passed")


if __name__ == "__main__":
    main()
