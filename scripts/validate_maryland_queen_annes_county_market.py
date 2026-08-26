#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Queen Anne's County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'Maryland — Queen Anne\\'s County'")
    if start < 0:
        raise SystemExit("Queen Anne's County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 5000]

    required = [
        "MARKET-LEVEL ONLY",
        "Tax Sale Certificate / property-tax lien",
        "10%/yr county redemption rate",
        "10% a year",
        "not an immediate deed",
        "Over-the-Counter Tax Sale Certificates",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Queen Anne's County safety/rule text missing: {expected}")

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:", "minimum_bid:"]
    for field in forbidden:
        if field in row:
            raise SystemExit(f"Queen Anne's County market row contains prohibited property field: {field}")

    print("Queen Anne's County Maryland market safety validation passed")


if __name__ == "__main__":
    main()
