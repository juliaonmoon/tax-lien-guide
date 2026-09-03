#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Adams County"
EVENT_ID = "NE-AdamsCounty-2026-market-event"

REQUIRED = [
    "March 2, 2026",
    "Tax lien / certificate of tax sale",
    "14%/yr current statutory redemption interest",
    "Hastings Public Library",
    "bidder-number rotation",
    "2026 annual public tax-lien/certificate sale passed",
    "no current parcel inventory is asserted here",
    "not immediate ownership or possession",
    "do not bulk republish owner/taxpayer names",
    "adamscountyne.gov/treasurer/57-tax-sales",
]


def extract_row(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate rows array")
    pos = text.find(MARKER, rows_start, rows_end)
    if pos < 0:
        raise SystemExit("Adams County Nebraska market row is missing")
    start = text.rfind("{state:", rows_start, pos + 1)
    endings = [p for token in ("},\n", "}\n,", "}\n];") if (p := text.find(token, pos, rows_end + 3)) >= 0]
    if start < rows_start or not endings:
        raise SystemExit("Could not safely isolate Adams County row")
    return text[start:min(endings) + 1]


def validate_calendar_event() -> None:
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    matches = [item for item in payload.get("properties", []) if item.get("record_id") == EVENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one Adams County calendar event, found {len(matches)}")
    event = matches[0]
    expected = {
        "record_type": "market_event",
        "state": "NE",
        "county": "Adams County",
        "sale_type": "tax_lien",
        "auction_date": "2026-03-02",
        "sale_date": "2026-03-02",
        "market_level_only": True,
        "official_source_url": "https://adamscountyne.gov/treasurer/57-tax-sales",
    }
    for key, value in expected.items():
        if event.get(key) != value:
            raise SystemExit(f"Adams County calendar event has unexpected {key}: {event.get(key)!r}")
    rules = event.get("important_rules", "").lower()
    required_rules = [
        "market-level calendar event only",
        "tax-lien/certificate",
        "not an immediate tax-deed",
        "no owner/taxpayer names",
        "parcel inventory",
        "opening/minimum bids",
    ]
    missing_rules = [phrase for phrase in required_rules if phrase not in rules]
    if missing_rules:
        raise SystemExit("Adams County calendar event missing safety boundary text: " + ", ".join(missing_rules))
    forbidden_keys = {"owner", "owner_name", "taxpayer", "taxpayer_name", "mailing_name"}
    if forbidden_keys & set(event):
        raise SystemExit("Adams County market event must not contain owner/taxpayer fields")


def main():
    row = extract_row(INDEX.read_text(encoding="utf-8"))
    missing = [item for item in REQUIRED if item not in row]
    if missing:
        raise SystemExit("Adams County row missing required safety/source text: " + ", ".join(missing))

    lower = row.lower()
    forbidden = [
        "current inventory is available",
        "currently available parcels",
        "private-sale inventory is available",
        "over-the-counter inventory is available",
        "canadian bidders are eligible",
        "itin accepted",
        "itin is accepted",
        "2026 online auction",
        "the march 2026 sale is an online auction",
        "guaranteed return",
        "guaranteed deed",
    ]
    bad = [phrase for phrase in forbidden if phrase in lower]
    if bad:
        raise SystemExit("Adams County row contains unsupported claim(s): " + ", ".join(bad))
    if "immediate ownership" in lower and "not immediate ownership" not in lower:
        raise SystemExit("Adams County row must preserve lien/certificate versus ownership distinction")
    if "no for the published 2026 procedure" not in lower:
        raise SystemExit("Adams County row must preserve the official in-person 2026 sale method")

    validate_calendar_event()
    print("Adams County Nebraska market and calendar validation passed")


if __name__ == "__main__":
    main()
