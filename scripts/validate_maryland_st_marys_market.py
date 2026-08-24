#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — St. Mary's County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'Maryland — St. Mary\\'s County'")
    if start < 0:
        raise SystemExit("St. Mary's County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 6000]

    required = [
        "MARKET-LEVEL ONLY",
        "March 6, 2026",
        "Tax Sale Certificate / property-tax lien",
        "6%/yr county redemption rate",
        "does not convey title",
        "over-the-counter",
        "U.S. persons or U.S. entities",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"St. Mary's County safety/rule text missing: {expected}")

    for field in ["owner_name:", "taxpayer_name:", "opening_bid:"]:
        if field in row:
            raise SystemExit(f"St. Mary's County row contains prohibited property field: {field}")

    print("St. Mary's County Maryland market safety validation passed")


if __name__ == "__main__":
    main()
