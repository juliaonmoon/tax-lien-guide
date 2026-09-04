#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Arizona — Coconino County"
EVENT_ID = "AZ-CoconinoCounty-2026-market-event"
SOURCE = "https://www.coconino.az.gov/376/Tax-Liens"

REQUIRED = (
    "product:'Tax lien / Certificate of Purchase'",
    "February 10, 2026",
    "September 2026 over-the-counter list",
    "maxReturn:'16%/yr max'",
    "rates range from 0% to 16%",
    "conveys no property rights",
    SOURCE,
)

FORBIDDEN = (
    "ownerName:",
    "taxpayerName:",
    "guaranteed return",
    "guaranteed property",
    "guaranteed inventory",
)

FORBIDDEN_EVENT_KEYS = {
    "owner",
    "owner_name",
    "taxpayer",
    "taxpayer_name",
    "mailing_name",
    "parcel_id",
    "parcel_number",
    "address",
    "situs_address",
    "assessed_value",
    "appraised_value",
    "opening_bid",
    "minimum_bid",
}


def market_row(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate market rows array")

    marker_pos = text.find(MARKER, rows_start, rows_end)
    if marker_pos < 0:
        raise SystemExit("Coconino County market row is missing")

    row_start = text.rfind("{state:", rows_start, marker_pos + 1)
    if row_start < rows_start:
        raise SystemExit("Coconino County row starts outside market rows array")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + len("\n];"))
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Could not locate Coconino County row end")

    row_end = min(endings) + 1
    if row_end > rows_end + 1:
        raise SystemExit("Coconino County row escapes market rows array")
    return text[row_start:row_end]


def validate_event() -> None:
    doc = json.loads(EVENTS.read_text(encoding="utf-8"))
    matches = [item for item in doc.get("properties", []) if item.get("record_id") == EVENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one Coconino County market event, found {len(matches)}")

    event = matches[0]
    if event.get("record_type") != "market_event" or event.get("market_level_only") is not True:
        raise SystemExit("Coconino County calendar record must remain a market-level event")
    if event.get("state") != "AZ" or event.get("county") != "Coconino County":
        raise SystemExit("Coconino County calendar jurisdiction mismatch")
    if event.get("sale_type") != "tax_lien":
        raise SystemExit("Coconino County calendar event must be classified as tax_lien")
    if event.get("auction_date") != "2026-02-10" or event.get("sale_date") != "2026-02-10":
        raise SystemExit("Coconino County 2026 official auction date must remain February 10, 2026")
    if event.get("official_source_url") != SOURCE:
        raise SystemExit("Coconino County calendar event must use the official Treasurer source")
    if FORBIDDEN_EVENT_KEYS & set(event):
        raise SystemExit("Coconino County market event must not contain parcel/owner/value/bid fields")

    text = " ".join(str(value) for value in event.values()).lower()
    required_event_phrases = (
        "certificate of purchase",
        "no immediate property rights",
        "do not bulk republish owner/taxpayer names",
        "do not fabricate or mirror parcel inventory",
        "september 2026",
    )
    missing = [phrase for phrase in required_event_phrases if phrase not in text]
    if missing:
        raise SystemExit(f"Coconino County event missing required safety/source facts: {missing}")
    for phrase in ("guaranteed return", "guaranteed deed", "guaranteed redemption"):
        if phrase in text:
            raise SystemExit(f"Unsafe Coconino County calendar claim: {phrase}")


def main():
    row = market_row(INDEX.read_text(encoding="utf-8"))
    missing = [needle for needle in REQUIRED if needle not in row]
    if missing:
        raise SystemExit("Coconino County row missing required safety/source facts: " + ", ".join(missing))

    forbidden = [needle for needle in FORBIDDEN if needle.lower() in row.lower()]
    if forbidden:
        raise SystemExit("Coconino County row contains forbidden/unsafe fields: " + ", ".join(forbidden))

    if "owner" in row.lower() and "do not bulk" not in row.lower():
        raise SystemExit("Coconino County row must not encourage owner-name aggregation")

    validate_event()
    print("Coconino County tax-lien market row and calendar event validated")


if __name__ == "__main__":
    main()
