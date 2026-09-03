#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Frontier County"
EVENT_ID = "NE-FrontierCounty-2026-market-event"

REQUIRED = [
    "March 2, 2026",
    "Tax lien / tax sale certificate",
    "14%/yr stated certificate interest",
    "first Monday in March",
    "2026 public sale passed",
    "no current parcel inventory is asserted here",
    "buying delinquent taxes, not the property",
    "not immediate ownership or possession",
    "three-year redemption period",
    "do not bulk republish owner/taxpayer names",
    "frontiercounty.ne.gov/treasurer-office/public-tax-sale-information/",
]


def extract_row(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate rows array")
    pos = text.find(MARKER, rows_start, rows_end)
    if pos < 0:
        raise SystemExit("Frontier County Nebraska market row is missing")
    start = text.rfind("{state:", rows_start, pos + 1)
    endings = [p for token in ("},\n", "}\n,", "}\n];") if (p := text.find(token, pos, rows_end + 3)) >= 0]
    if start < rows_start or not endings:
        raise SystemExit("Could not safely isolate Frontier County row")
    return text[start:min(endings) + 1]


def validate_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    matches = [item for item in payload.get("properties", []) if item.get("record_id") == EVENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one Frontier County calendar event, found {len(matches)}")
    event = matches[0]
    required_pairs = {
        "record_type": "market_event",
        "state": "NE",
        "state_name": "Nebraska",
        "county": "Frontier County",
        "sale_type": "tax_lien",
        "auction_date": "2026-03-02",
        "sale_date": "2026-03-02",
        "auction_time": "09:00 CT",
        "official_source_url": "https://frontiercounty.ne.gov/treasurer-office/public-tax-sale-information/",
        "market_level_only": True,
    }
    wrong = [f"{key}={event.get(key)!r}" for key, value in required_pairs.items() if event.get(key) != value]
    if wrong:
        raise SystemExit("Frontier County calendar event has incorrect required fields: " + ", ".join(wrong))
    text = json.dumps(event, ensure_ascii=False).lower()
    required_text = [
        "historical market-level event",
        "not current parcel inventory",
        "buy delinquent taxes, not the property",
        "three-year redemption",
        "14% interest",
        "no owner names",
    ]
    missing = [phrase for phrase in required_text if phrase not in text]
    if missing:
        raise SystemExit("Frontier County calendar event missing safety/source text: " + ", ".join(missing))
    forbidden = [
        "current inventory is available",
        "currently available parcels",
        "guaranteed return",
        "guaranteed deed",
        "immediate ownership",
    ]
    bad = [phrase for phrase in forbidden if phrase in text]
    if bad:
        raise SystemExit("Frontier County calendar event contains unsupported claim(s): " + ", ".join(bad))


def main():
    row = extract_row(INDEX.read_text(encoding="utf-8"))
    missing = [item for item in REQUIRED if item not in row]
    if missing:
        raise SystemExit("Frontier County row missing required safety/source text: " + ", ".join(missing))

    lower = row.lower()
    forbidden = [
        "current inventory is available",
        "currently available parcels",
        "private-sale inventory is available",
        "canadian bidders are eligible",
        "itin accepted",
        "itin is accepted",
        "online auction platform",
        "guaranteed return",
        "guaranteed deed",
        "immediate tax deed auction",
    ]
    bad = [phrase for phrase in forbidden if phrase in lower]
    if bad:
        raise SystemExit("Frontier County row contains unsupported claim(s): " + ", ".join(bad))
    if "private tax sale" in lower and "not a claim that any particular parcel or certificate is currently available" not in lower:
        raise SystemExit("Frontier private-sale text must not imply current inventory")
    if "not the property" not in lower:
        raise SystemExit("Frontier row must preserve tax-certificate versus property-ownership distinction")
    if "no for the published sale procedure" not in lower:
        raise SystemExit("Frontier row must preserve the official in-person sale method")
    if "w-9" in lower and "does not establish that an itin or a foreign-tax form is accepted" not in lower:
        raise SystemExit("Frontier W-9 text must not imply unsupported ITIN/foreign-tax-form acceptance")

    validate_calendar_event()
    print("Frontier County Nebraska market and calendar validation passed")


if __name__ == "__main__":
    main()
