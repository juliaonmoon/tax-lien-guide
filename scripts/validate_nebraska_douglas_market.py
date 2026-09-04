#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Nebraska — Douglas County"
EVENT_ID = "NE-DouglasCounty-2026-market-event"

REQUIRED = (
    "March 2, 2026",
    "February 5 through March 2, 2026",
    "14%/yr current statutory interest",
    "Tax lien / certificate of tax sale",
    "not immediate ownership or possession",
    "do not describe the annual tax-lien sale as a tax-deed auction",
    "do not bulk republish owner/taxpayer names",
    "https://treasurer.douglascounty-ne.gov/public-tax-sale/",
    "https://www.omahadailyrecord.com/sites/default/files/DELINQUENT%20TAX%20DOUGLAS%20COUNTY%202025%20p%201.pdf",
    "https://nebraskalegislature.gov/laws/statutes.php?statute=77-1802",
    "https://nebraskalegislature.gov/laws/statutes.php?statute=77-1824",
)

FORBIDDEN_AFFIRMATIVE = (
    "guaranteed return",
    "guaranteed deed",
    "Canadian eligible: yes",
    "ITIN accepted",
    "2027 sale confirmed",
    "March 1, 2027 confirmed",
)


def validate_calendar_event():
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    matches = [row for row in payload.get("properties", []) if row.get("record_id") == EVENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one Douglas County calendar event, found {len(matches)}")
    event = matches[0]
    expected = {
        "record_type": "market_event",
        "state": "NE",
        "county": "Douglas County",
        "sale_type": "tax_lien",
        "auction_date": "2026-03-02",
        "sale_date": "2026-03-02",
        "market_level_only": True,
    }
    for key, value in expected.items():
        if event.get(key) != value:
            raise SystemExit(f"Douglas County calendar event has unexpected {key}: {event.get(key)!r}")
    if event.get("official_source_url") != "https://treasurer.douglascounty-ne.gov/public-tax-sale/":
        raise SystemExit("Douglas County calendar event must use the official Treasurer source")
    forbidden_keys = {"owner", "owner_name", "taxpayer", "taxpayer_name", "mailing_name", "parcel_id", "opening_bid", "minimum_bid"}
    bad_keys = forbidden_keys & set(event)
    if bad_keys:
        raise SystemExit("Douglas County calendar event contains forbidden parcel/owner field(s): " + ", ".join(sorted(bad_keys)))
    rules = event.get("important_rules", "").lower()
    required_rules = [
        "market-level calendar event only",
        "tax-lien/certificate",
        "not a sheriff foreclosure",
        "tax-deed auction",
        "no owner/taxpayer names",
        "parcel inventory",
        "opening/minimum bids",
        "bidder eligibility",
    ]
    missing = [phrase for phrase in required_rules if phrase not in rules]
    if missing:
        raise SystemExit("Douglas County calendar event missing safety boundary text: " + ", ".join(missing))


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("const rows=[")
    end = text.find("\n];", start)
    if start < 0 or end < 0:
        raise SystemExit("Could not locate market rows array")

    marker = text.find(MARKER, start, end)
    if marker < 0:
        raise SystemExit("Douglas Nebraska market row is missing")
    row_start = text.rfind("{state:", start, marker + 1)
    next_row = text.find("{state:", marker + len(MARKER), end)
    row_end = next_row if next_row >= 0 else end
    if row_start < start or row_end > end or row_start >= row_end:
        raise SystemExit("Douglas Nebraska row boundaries are invalid")

    row = text[row_start:row_end]
    missing = [value for value in REQUIRED if value not in row]
    if missing:
        raise SystemExit("Douglas Nebraska row missing required safety/source facts: " + ", ".join(missing))

    lowered = row.lower()
    bad = [value for value in FORBIDDEN_AFFIRMATIVE if value.lower() in lowered]
    if bad:
        raise SystemExit("Douglas Nebraska row contains unsafe/unverified claims: " + ", ".join(bad))
    if "no current parcel inventory is asserted here" not in lowered:
        raise SystemExit("Douglas Nebraska row must disclaim current parcel inventory")
    if "do not infer current private-sale, over-the-counter, or county-held certificate inventory" not in lowered:
        raise SystemExit("Douglas Nebraska row must disclaim inferred post-sale inventory")

    validate_calendar_event()
    print("Douglas Nebraska tax-lien market validation passed")


if __name__ == "__main__":
    main()
