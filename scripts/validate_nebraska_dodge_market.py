#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Dodge County"
EVENT_ID = "NE-DodgeCounty-2026-market-event"

REQUIRED = [
    "March 2, 2026",
    "8:30 A.M.",
    "Dodge County Board Room",
    "Tax lien / certificate of tax sale",
    "14%/yr current statutory redemption interest",
    "2026 public tax sale passed",
    "no current parcel inventory is asserted here",
    "not immediate ownership or possession",
    "do not bulk republish owner/taxpayer names",
    "dodgecounty.nebraska.gov/treasurer",
    "nebraskalegislature.gov/laws/statutes.php?statute=77-1824",
]


def extract_row(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate rows array")
    pos = text.find(MARKER, rows_start, rows_end)
    if pos < 0:
        raise SystemExit("Dodge County Nebraska market row is missing")
    start = text.rfind("{state:", rows_start, pos + 1)
    endings = [p for token in ("},\n", "}\n,", "}\n];") if (p := text.find(token, pos, rows_end + 3)) >= 0]
    if start < rows_start or not endings:
        raise SystemExit("Could not safely isolate Dodge County row")
    return text[start:min(endings) + 1]


def validate_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    matches = [item for item in payload.get("properties", []) if item.get("record_id") == EVENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one Dodge County calendar event, found {len(matches)}")
    event = matches[0]
    expected = {
        "record_type": "market_event",
        "state": "NE",
        "county": "Dodge County",
        "sale_type": "tax_lien",
        "auction_date": "2026-03-02",
        "sale_date": "2026-03-02",
        "market_level_only": True,
    }
    for key, value in expected.items():
        if event.get(key) != value:
            raise SystemExit(f"Dodge County calendar event has unexpected {key}: {event.get(key)!r}")
    if event.get("official_source_url") != "https://dodgecounty.nebraska.gov/treasurer":
        raise SystemExit("Dodge County calendar event must use the official Treasurer source")
    forbidden_keys = {"owner", "owner_name", "taxpayer", "taxpayer_name", "mailing_name", "parcel_id", "opening_bid", "minimum_bid"}
    bad_keys = forbidden_keys & set(event)
    if bad_keys:
        raise SystemExit("Dodge County calendar event contains forbidden parcel/owner field(s): " + ", ".join(sorted(bad_keys)))
    rules = event.get("important_rules", "").lower()
    required_rules = [
        "market-level calendar event only",
        "tax-lien/certificate",
        "not an immediate tax-deed",
        "no owner/taxpayer names",
        "parcel inventory",
        "opening/minimum bids",
        "bidder-eligibility claims",
    ]
    missing = [phrase for phrase in required_rules if phrase not in rules]
    if missing:
        raise SystemExit("Dodge County calendar event missing safety boundary text: " + ", ".join(missing))


def main():
    row = extract_row(INDEX.read_text(encoding="utf-8"))
    missing = [item for item in REQUIRED if item not in row]
    if missing:
        raise SystemExit("Dodge County row missing required safety/source text: " + ", ".join(missing))

    lower = row.lower()
    forbidden = [
        "current inventory is available",
        "currently available parcels",
        "private-sale inventory is available",
        "over-the-counter inventory is available",
        "canadian bidders are eligible",
        "itin accepted",
        "itin is accepted",
        "immediate ownership and possession",
        "online auction is available",
    ]
    bad = [phrase for phrase in forbidden if phrase in lower]
    if bad:
        raise SystemExit("Dodge County row contains unsupported claim(s): " + ", ".join(bad))

    if "immediate tax-deed auction" in lower and "not a sheriff foreclosure or an immediate tax-deed auction" not in lower:
        raise SystemExit("Dodge County row must not represent the Treasurer tax-lien sale as an immediate tax-deed auction")
    if "immediate ownership" in lower and "not immediate ownership" not in lower:
        raise SystemExit("Dodge County row must preserve certificate versus ownership distinction")
    if "no for the published 2026 procedure" not in lower:
        raise SystemExit("Dodge County row must preserve the official 2026 courthouse sale method")
    if "verify current law" not in lower:
        raise SystemExit("Dodge County row must preserve statutory freshness caveat")

    validate_event()
    print("Dodge County Nebraska market validation passed")


if __name__ == "__main__":
    main()
