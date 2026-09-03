#!/usr/bin/env python3
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "index.html"
MARKER = "Nebraska — Lancaster County"

REQUIRED = (
    "March 2, 2026",
    "14%/yr current statutory redemption interest",
    "certificate of tax sale",
    "current list is for Private Sale",
    "No parcels available at this time",
    "not immediate ownership or possession",
    "do not bulk republish owner/taxpayer names",
    "https://www.lancaster.ne.gov/DocumentCenter/View/640/Tax-Sale-Information-PDF",
    "https://www.lancaster.ne.gov/DocumentCenter/View/641/Tax-Sale-Purchasing-Information-PDF",
    "https://www.lancaster.ne.gov/396/Delinquent-Tax-Listing",
    "https://www.lancaster.ne.gov/849/Tax-Delinquency-Listing",
    "nebraskalegislature.gov/laws/statutes.php?statute=s4501004001",
    "nebraskalegislature.gov/laws/statutes.php?statute=77-1824",
)

FORBIDDEN = (
    "guaranteed inventory",
    "guaranteed return",
    "guaranteed deed",
    "Canadian eligible: yes",
    "canadian bidders are eligible",
    "ITIN accepted",
    "ITIN is accepted",
    "next sale March 2027",
    "private-sale inventory is available",
    "private sale inventory is available",
    "currently available private-sale parcels",
    "current parcel inventory is available",
)


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("const rows=[")
    end = text.find("\n];", start)
    if start < 0 or end < 0:
        raise SystemExit("Could not locate market rows array")

    marker = text.find(MARKER, start, end)
    if marker < 0:
        raise SystemExit("Lancaster Nebraska market row is missing")
    row_start = text.rfind("{state:", start, marker + 1)
    next_row = text.find("{state:", marker + len(MARKER), end)
    row_end = next_row if next_row >= 0 else end
    if row_start < start or row_end > end or row_start >= row_end:
        raise SystemExit("Lancaster Nebraska row boundaries are invalid")

    row = text[row_start:row_end]
    missing = [value for value in REQUIRED if value not in row]
    if missing:
        raise SystemExit("Lancaster Nebraska row missing required safety/source facts: " + ", ".join(missing))

    lowered = row.lower()
    bad = [value for value in FORBIDDEN if value.lower() in lowered]
    if bad:
        raise SystemExit("Lancaster Nebraska row contains unsafe/unverified claims: " + ", ".join(bad))

    if "no for the published 2026 procedure" not in lowered:
        raise SystemExit("Lancaster Nebraska row must preserve the official in-person 2026 sale method")
    if "do not represent private-sale certificates as available" not in lowered:
        raise SystemExit("Lancaster Nebraska row must preserve current no-inventory safety language")
    if "verify current law" not in lowered:
        raise SystemExit("Lancaster Nebraska row must preserve statutory freshness caveat")

    print("Lancaster Nebraska tax-lien market validation passed")


if __name__ == "__main__":
    main()
