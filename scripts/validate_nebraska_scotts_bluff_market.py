#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Scotts Bluff County"
EVENT_ID = "NE-ScottsBluffCounty-2026-market-event"

REQUIRED = (
    "March 2, 2026",
    "14%/yr stated certificate interest",
    "purchasing delinquent taxes, not the property",
    "do not bulk republish owner/taxpayer names",
    "https://scottsbluffcountyne.gov/treasurer-office/public-tax-sale-information/",
)
FORBIDDEN = (
    "guaranteed return",
    "guaranteed deed",
    "Canadian eligible: yes",
    "current inventory is available",
    "immediate ownership",
)


def extract_row(text: str) -> str:
    start = text.find("const rows=[")
    end = text.find("\n];", start)
    if start < 0 or end < 0:
        raise SystemExit("Could not locate market rows array")
    marker = text.find(MARKER, start, end)
    if marker < 0:
        raise SystemExit("Scotts Bluff Nebraska market row is missing")
    row_start = text.rfind("{state:", start, marker + 1)
    endings = [p for token in ("},\n", "}\n,", "}\n];") if (p := text.find(token, marker, end + 3)) >= 0]
    if row_start < start or not endings:
        raise SystemExit("Scotts Bluff Nebraska row boundaries are invalid")
    return text[row_start:min(endings) + 1]


def validate_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    matches = [item for item in payload.get("properties", []) if item.get("record_id") == EVENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one Scotts Bluff County calendar event, found {len(matches)}")
    event = matches[0]
    required_pairs = {
        "record_type": "market_event",
        "state": "NE",
        "state_name": "Nebraska",
        "county": "Scotts Bluff County",
        "sale_type": "tax_lien",
        "auction_date": "2026-03-02",
        "sale_date": "2026-03-02",
        "official_source_url": "https://scottsbluffcountyne.gov/treasurer-office/public-tax-sale-information/",
        "market_level_only": True,
    }
    wrong = [f"{key}={event.get(key)!r}" for key, expected in required_pairs.items() if event.get(key) != expected]
    if wrong:
        raise SystemExit("Scotts Bluff County calendar event has incorrect required fields: " + ", ".join(wrong))
    text = json.dumps(event, ensure_ascii=False).lower()
    required_text = (
        "historical market-level event",
        "no current parcel inventory is asserted",
        "not an immediate property transfer",
        "no owner names, parcel inventory, opening/minimum bids",
    )
    missing = [phrase for phrase in required_text if phrase not in text]
    if missing:
        raise SystemExit("Scotts Bluff County calendar event missing safety/source text: " + ", ".join(missing))
    bad = [phrase for phrase in ("currently available parcels", "guaranteed return", "guaranteed deed", "immediate ownership") if phrase in text]
    if bad:
        raise SystemExit("Scotts Bluff County calendar event contains unsupported claim(s): " + ", ".join(bad))


def main():
    row = extract_row(INDEX.read_text(encoding="utf-8"))
    lowered = row.lower()
    missing = [value for value in REQUIRED if value.lower() not in lowered]
    if missing:
        raise SystemExit("Scotts Bluff Nebraska row missing required safety/source facts: " + ", ".join(missing))
    bad = [value for value in FORBIDDEN if value.lower() in lowered]
    if bad:
        raise SystemExit("Scotts Bluff Nebraska row contains unsafe/unverified claims: " + ", ".join(bad))
    if "no for the published procedure" not in lowered or "in person" not in lowered:
        raise SystemExit("Scotts Bluff row must preserve the official in-person sale method")
    if "no particular parcel or certificate is asserted as currently available" not in lowered:
        raise SystemExit("Scotts Bluff row must not imply current private-sale inventory")
    validate_calendar_event()
    print("Scotts Bluff Nebraska tax-lien market and calendar validation passed")


if __name__ == "__main__":
    main()
