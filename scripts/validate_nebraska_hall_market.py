#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Hall County"
EVENT_ID = "NE-HallCounty-2026-market-event"

REQUIRED = (
    "March 2, 2026",
    "No remaining delinquent taxes are currently offered for sale",
    "14%/yr statutory redemption interest",
    "tax lien, not immediate ownership or possession",
    "do not bulk republish owner/taxpayer names",
    "https://reports.hallcountyne.gov/Treasurer/Delinquent/advertlist.php",
    "https://nebraskalegislature.gov/laws/statutes.php?statute=77-1824",
    "https://nebraskalegislature.gov/laws/statutes.php?statute=45-104.01",
)

FORBIDDEN = (
    "guaranteed return",
    "guaranteed deed",
    "Canadian eligible: yes",
    "current otc inventory",
    "current inventory is available",
)


def extract_row(text: str) -> str:
    start = text.find("const rows=[")
    end = text.find("\n];", start)
    if start < 0 or end < 0:
        raise SystemExit("Could not locate market rows array")
    marker = text.find(MARKER, start, end)
    if marker < 0:
        raise SystemExit("Hall Nebraska market row is missing")
    row_start = text.rfind("{state:", start, marker + 1)
    endings = [p for token in ("},\n", "}\n,", "}\n];") if (p := text.find(token, marker, end + 3)) >= 0]
    if row_start < start or not endings:
        raise SystemExit("Hall Nebraska row boundaries are invalid")
    return text[row_start:min(endings) + 1]


def validate_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    matches = [item for item in payload.get("properties", []) if item.get("record_id") == EVENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one Hall County calendar event, found {len(matches)}")
    event = matches[0]
    required_pairs = {
        "record_type": "market_event",
        "state": "NE",
        "state_name": "Nebraska",
        "county": "Hall County",
        "sale_type": "tax_lien",
        "auction_date": "2026-03-02",
        "sale_date": "2026-03-02",
        "official_source_url": "https://reports.hallcountyne.gov/Treasurer/Delinquent/advertlist.php",
        "market_level_only": True,
    }
    wrong = [f"{key}={event.get(key)!r}" for key, expected in required_pairs.items() if event.get(key) != expected]
    if wrong:
        raise SystemExit("Hall County calendar event has incorrect required fields: " + ", ".join(wrong))
    text = json.dumps(event, ensure_ascii=False).lower()
    required_text = [
        "no remaining delinquent taxes for sale",
        "historical market-level event",
        "no current parcel inventory",
        "not an immediate property transfer",
        "no owner names",
        "no owner names, parcel inventory, opening/minimum bids",
    ]
    missing = [phrase for phrase in required_text if phrase not in text]
    if missing:
        raise SystemExit("Hall County calendar event missing safety/source text: " + ", ".join(missing))
    bad = [phrase for phrase in ("currently available parcels", "guaranteed return", "guaranteed deed", "immediate ownership") if phrase in text]
    if bad:
        raise SystemExit("Hall County calendar event contains unsupported claim(s): " + ", ".join(bad))


def main():
    row = extract_row(INDEX.read_text(encoding="utf-8"))
    lowered = row.lower()
    missing = [value for value in REQUIRED if value.lower() not in lowered]
    if missing:
        raise SystemExit("Hall Nebraska row missing required safety/source facts: " + ", ".join(missing))
    bad = [value for value in FORBIDDEN if value.lower() in lowered]
    if bad:
        raise SystemExit("Hall Nebraska row contains unsafe/unverified claims: " + ", ".join(bad))
    if "no for the published 2026 sale notice" not in lowered:
        raise SystemExit("Hall row must preserve the official in-person sale method")
    if "there are no remaining delinquent taxes for sale" not in lowered:
        raise SystemExit("Hall row must preserve the county's current no-inventory statement")
    validate_calendar_event()
    print("Hall Nebraska tax-lien market and calendar validation passed")


if __name__ == "__main__":
    main()
