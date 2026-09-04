#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Arizona — Pima County"
EVENT_ID = "AZ-PimaCounty-2026-market-event"
SOURCE = "https://www.to.pima.gov/taxLienSale/"

REQUIRED = (
    "Tax lien / Certificate of Purchase",
    "April 1",
    "December 15",
    "16%",
    "0%",
    "You are not purchasing property",
    SOURCE,
)

FORBIDDEN = (
    "guaranteed return",
    "guaranteed inventory",
)

FORBIDDEN_EVENT_KEYS = {
    "owner",
    "owner_name",
    "taxpayer",
    "taxpayer_name",
    "mailing_name",
    "assessed_value",
    "appraised_value",
    "opening_bid",
    "minimum_bid",
}


def row_text(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate market rows array")

    marker = text.find(MARKER, rows_start, rows_end)
    if marker < 0:
        raise SystemExit("Pima County market row missing")

    start = text.rfind("{state:", rows_start, marker + 1)
    if start < rows_start:
        raise SystemExit("Pima County row start escaped market rows array")

    candidates = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker, rows_end + len("\n];"))
        if pos >= 0:
            candidates.append(pos + 1)
    if not candidates:
        raise SystemExit("Pima County row end not found")

    end = min(candidates)
    if end > rows_end + 1:
        raise SystemExit("Pima County row end escaped market rows array")
    return text[start:end]


def validate_event() -> None:
    doc = json.loads(EVENTS.read_text(encoding="utf-8"))
    matches = [item for item in doc.get("properties", []) if item.get("record_id") == EVENT_ID]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one Pima County market event, found {len(matches)}")

    event = matches[0]
    if event.get("record_type") != "market_event" or event.get("market_level_only") is not True:
        raise SystemExit("Pima County calendar record must remain a market-level event")
    if event.get("state") != "AZ" or event.get("county") != "Pima County":
        raise SystemExit("Pima County calendar jurisdiction mismatch")
    if event.get("sale_type") != "tax_lien":
        raise SystemExit("Pima County calendar event must be classified as tax_lien")
    if event.get("auction_date") != "2026-02-26" or event.get("sale_date") != "2026-02-26":
        raise SystemExit("Pima County 2026 official auction date must remain February 26, 2026")
    if event.get("official_source_url") != SOURCE:
        raise SystemExit("Pima County calendar event must use the official Treasurer source")
    if FORBIDDEN_EVENT_KEYS & set(event):
        raise SystemExit("Pima County market event must not contain parcel/owner/value/bid fields")

    text = " ".join(str(value) for value in event.values()).lower()
    required_event_phrases = (
        "certificate of purchase",
        "no parcel inventory",
        "do not bulk republish owner/taxpayer names",
        "not a purchase of the property",
        "april 1",
        "december 15",
    )
    missing = [phrase for phrase in required_event_phrases if phrase not in text]
    if missing:
        raise SystemExit(f"Pima County event missing required safety/source facts: {missing}")
    for phrase in ("guaranteed return", "guaranteed deed", "guaranteed redemption"):
        if phrase in text:
            raise SystemExit(f"Unsafe Pima County calendar claim: {phrase}")


def main():
    row = row_text(INDEX.read_text(encoding="utf-8"))
    lowered = row.lower()

    missing = [item for item in REQUIRED if item not in row]
    if missing:
        raise SystemExit(f"Pima County row missing required facts: {missing}")

    bad = [item for item in FORBIDDEN if item.lower() in lowered]
    if bad:
        raise SystemExit(f"Pima County row contains unsafe/misleading language: {bad}")

    if "owner" in lowered and "do not bulk" not in lowered:
        raise SystemExit("Pima County row must not encourage owner-name aggregation")

    validate_event()
    print("Pima County tax-lien market row and calendar event validated")


if __name__ == "__main__":
    main()
