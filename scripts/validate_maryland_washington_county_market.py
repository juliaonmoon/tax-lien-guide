#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Washington County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Washington County Maryland market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 6000]

    required = [
        "MARKET-LEVEL ONLY",
        "Tax Lien Certificate / property-tax lien",
        "June 2, 2026",
        "6%/yr county redemption rate",
        "6% interest per annum",
        "not immediate ownership",
        "no longer available for sale",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Washington County Maryland safety/rule text missing: {expected}")

    for prohibited in ["owner_name:", "taxpayer_name:", "opening_bid:"]:
        if prohibited in row:
            raise SystemExit(f"Washington County Maryland row contains prohibited property field: {prohibited}")

    if "Sheriff/judicial foreclosure" not in row:
        raise SystemExit("Washington County Maryland row must preserve lien-vs-judicial-foreclosure distinction")

    print("Washington County Maryland market safety validation passed")


if __name__ == "__main__":
    main()
