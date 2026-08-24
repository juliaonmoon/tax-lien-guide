#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Prince George's County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'Maryland — Prince George\\'s County'")
    if start < 0:
        raise SystemExit("Prince George's County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 7000]

    required = [
        "MARKET-LEVEL ONLY",
        "May 11, 2026",
        "Tax Sale Certificate / property-tax lien",
        "10%/yr owner-occupied; 20%/yr non-principal residence or unimproved parcel",
        "not immediate ownership",
        "does not bulk republish owner/taxpayer names",
        "June 10, 2026",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Prince George's County safety/rule text missing: {expected}")

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:"]
    for field in forbidden:
        if field in row:
            raise SystemExit(f"Prince George's County market row contains prohibited property field: {field}")

    print("Prince George's County Maryland market safety validation passed")


if __name__ == "__main__":
    main()
