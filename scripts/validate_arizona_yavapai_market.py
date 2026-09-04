#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
MARKER = "Arizona — Yavapai County"
EVENT_ID = "AZ-YavapaiCounty-2026-market-event"
SOURCE = "https://www.yavapaiaz.gov/Mapping-and-Properties/Property-Taxes/Treasurers-Office/Treasurers-Tax-Lien-Sale"

REQUIRED = (
    "Tax lien / Certificate of Purchase",
    "February 10, 2026",
    "February 9, 2027",
    "16%",
    "may reduce the rate to 0%",
    "does not convey immediate ownership",
    "separate tax-deed sales",
    "Do not bulk aggregate owner/taxpayer names",
    SOURCE,
    "https://www.azleg.gov/ars/42/18114.htm",
)

FORBIDDEN_AFFIRMATIVE = (
    "guaranteed return",
    "guaranteed inventory",
    "guaranteed ownership",
    "current otc inventory",
)


def row_text(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate market rows array")

    marker = text.find(MARKER, rows_start, rows_end)
    if marker < 0:
        raise SystemExit("Yavapai County market row missing")

    start = text.rfind("{state:", rows_start, marker + 1)
    if start < rows_start:
        raise SystemExit("Yavapai County row start escaped market rows array")

    candidates = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker, rows_end + len("\n];"))
        if pos >= 0:
            candidates.append(pos + 1)
    if not candidates:
        raise SystemExit("Yavapai County row end not found")

    end = min(candidates)
    if end > rows_end + 1:
        raise SystemExit("Yavapai County row end escaped market rows array")
    return text[start:end]


def validate_event() -> None:
    payload = json.loads(EVENTS.read_text(encoding="utf-8"))
    events = [item for item in payload.get("properties", []) if item.get("record_id") == EVENT_ID]
    if len(events) != 1:
        raise SystemExit(f"Expected exactly one Yavapai County market event, found {len(events)}")
    event = events[0]
    required = {
        "record_type": "market_event",
        "state": "AZ",
        "county": "Yavapai County",
        "sale_type": "tax_lien",
        "auction_date": "2026-02-10",
        "sale_date": "2026-02-10",
        "official_source_url": SOURCE,
        "market_level_only": True,
    }
    bad = {key: (event.get(key), value) for key, value in required.items() if event.get(key) != value}
    if bad:
        raise SystemExit(f"Yavapai County event has incorrect canonical fields: {bad}")

    forbidden_keys = {
        "owner", "owner_name", "taxpayer", "taxpayer_name", "address", "parcel_id",
        "assessed_value", "appraised_value", "opening_bid", "minimum_bid", "purchase_amount",
    }
    present = forbidden_keys & set(event)
    if present:
        raise SystemExit(f"Yavapai market-level event must not contain parcel/owner/value fields: {sorted(present)}")

    rules = event.get("important_rules", "").lower()
    safeguards = (
        "not the separate county tax deed sales",
        "not immediate ownership or possession",
        "do not bulk republish owner/taxpayer names",
        "no parcel inventory",
        "opening/minimum bids",
        "assessed/appraised values",
    )
    missing = [item for item in safeguards if item not in rules]
    if missing:
        raise SystemExit(f"Yavapai event missing legal/data safeguards: {missing}")


def main():
    row = row_text(INDEX.read_text(encoding="utf-8"))
    lowered = row.lower()

    missing = [item for item in REQUIRED if item not in row]
    if missing:
        raise SystemExit(f"Yavapai County row missing required facts/safeguards: {missing}")

    bad = [item for item in FORBIDDEN_AFFIRMATIVE if item in lowered]
    if bad:
        raise SystemExit(f"Yavapai County row contains unsafe/misleading affirmative claim: {bad}")

    if "otc:'yes" in lowered:
        raise SystemExit("Yavapai County row must not assert current OTC availability without a current official inventory source")

    if "tax deed /" in lowered or "product:'tax deed" in lowered:
        raise SystemExit("Yavapai Treasurer row must remain classified as a tax-lien certificate market")

    validate_event()
    print("Yavapai County tax-lien market row and calendar event validated")


if __name__ == "__main__":
    main()
