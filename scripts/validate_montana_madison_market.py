#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Madison County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Missing generated Madison County market row")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 5000]

    required = [
        "MARKET-LEVEL ONLY",
        "10%/yr statutory delinquent-tax interest",
        "in person or by mail",
        "not immediate property ownership",
    ]
    for value in required:
        if value not in row:
            raise SystemExit(f"Madison County safety/rule text missing: {value}")

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:"]
    for value in forbidden:
        if value in row:
            raise SystemExit(f"Madison County market row must not publish restricted property-level field: {value}")

    print("Verified Madison County MARKET-LEVEL ONLY tax-lien boundary")


if __name__ == "__main__":
    main()
