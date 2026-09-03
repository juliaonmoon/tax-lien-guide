#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Buffalo County"
EVENT_ID = "NE-BuffaloCounty-2026-market-event"

REQUIRED = [
    "March 2, 2026",
    "Tax lien / tax sale certificate",
    "14%/yr statutory redemption interest",
    "Buffalo County Courthouse",
    "do not bulk republish owner/taxpayer names",
    "Do not treat them as current certificate inventory",
    "Do not represent the 2026 sale as an online auction",
    "not immediate ownership or possession",
    "buffalocounty.ne.gov/county-offices/treasurer",
]


def extract_row(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate rows array")
    pos = text.find(MARKER, rows_start, rows_end)
    if pos < 0:
        raise SystemExit("Buffalo County Nebraska market row is missing")
    start = text.rfind("{state:", rows_start, pos + 1)
    endings = [p for token in ("},\n", "}\n,", "}\n];") if (p := text.find(token, pos, rows_end + 3)) >= 0]
    if start < rows_start or not endings:
        raise SystemExit("Could not safely isolate Buffalo County row")
    return text[start:min(endings) + 1]


def validate_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    matches = [item for item in payload.get("properties", []) if item.get("record_id") == EVENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one Buffalo County calendar event, found {len(matches)}")
    event = matches[0]
    required_pairs = {
        "record_type": "market_event",
        "state": "NE",
        "state_name": "Nebraska",
        "county": "Buffalo County",
        "sale_type": "tax_lien",
        "auction_date": "2026-03-02",
        "sale_date": "2026-03-02",
        "auction_time": "09:00 CT",
        "official_source_url": "https://buffalocounty.ne.gov/Portals/0/2026%20TAX%20SALE%20INFORMATION%20FOR%20WEBSITE%20%281%29.pdf",
        "market_level_only": True,
    }
    wrong = [f"{key}={event.get(key)!r}" for key, value in required_pairs.items() if event.get(key) != value]
    if wrong:
        raise SystemExit("Buffalo County calendar event has incorrect required fields: " + ", ".join(wrong))
    text = json.dumps(event, ensure_ascii=False).lower()
    required_text = [
        "historical market-level event",
        "no current parcel or certificate inventory is asserted",
        "in-person tax-sale certificate sale",
        "not an online auction",
        "not immediate property transfer",
        "no owner names",
    ]
    missing = [phrase for phrase in required_text if phrase not in text]
    if missing:
        raise SystemExit("Buffalo County calendar event missing safety/source text: " + ", ".join(missing))
    forbidden = [
        "current inventory is available",
        "currently available parcels",
        "canadian bidders are eligible",
        "itin accepted",
        "guaranteed return",
        "guaranteed deed",
        "immediate ownership",
    ]
    bad = [phrase for phrase in forbidden if phrase in text]
    if bad:
        raise SystemExit("Buffalo County calendar event contains unsupported claim(s): " + ", ".join(bad))


def main():
    row = extract_row(INDEX.read_text(encoding="utf-8"))
    missing = [item for item in REQUIRED if item not in row]
    if missing:
        raise SystemExit("Buffalo County row missing required safety/source text: " + ", ".join(missing))

    lower = row.lower()
    if "current inventory is available" in lower or "currently available parcels" in lower:
        raise SystemExit("Buffalo County row must not assert current parcel inventory")
    if "canadian bidders are eligible" in lower:
        raise SystemExit("Buffalo County row must not assert unverified Canadian eligibility")
    if "itin accepted" in lower or "itin is accepted" in lower:
        raise SystemExit("Buffalo County row must not assert unverified ITIN acceptance")
    if "the 2026 sale is an online auction" in lower or "2026 online auction" in lower:
        raise SystemExit("Buffalo County official 2026 materials describe an in-person courthouse sale")
    if "immediate ownership" in lower and "not immediate ownership" not in lower:
        raise SystemExit("Buffalo County row must preserve lien/certificate versus ownership distinction")

    validate_calendar_event()
    print("Buffalo County Nebraska market and calendar validation passed")


if __name__ == "__main__":
    main()
