#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Baltimore City"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Baltimore City market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 6000]

    required = [
        "MARKET-LEVEL ONLY",
        "May 18, 2026",
        "Tax Sale Certificate / property-tax lien",
        "12%/yr owner-occupied residential; 18%/yr all other property",
        "not immediate ownership",
        "Foreclosure of the right of redemption",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Baltimore City safety/rule text missing: {expected}")

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:"]
    for field in forbidden:
        if field in row:
            raise SystemExit(f"Baltimore City market row contains prohibited property field: {field}")

    print("Baltimore City Maryland market safety validation passed")


if __name__ == "__main__":
    main()
