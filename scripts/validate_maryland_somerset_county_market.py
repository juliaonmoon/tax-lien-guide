#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Somerset County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Somerset County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 6000]

    required = [
        "MARKET-LEVEL ONLY",
        "Tax Lien Certificate / property-tax lien",
        "June 11, 2026",
        "not immediate ownership",
        "redemption rate not verified",
        "Do not bulk copy owner/taxpayer names",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Somerset County safety/rule text missing: {expected}")

    for prohibited in ["owner_name:", "taxpayer_name:", "opening_bid:"]:
        if prohibited in row:
            raise SystemExit(f"Somerset County market row contains prohibited property field: {prohibited}")

    if "18%/yr county redemption rate" in row or "20%/yr" in row or "12%/yr county redemption rate" in row:
        raise SystemExit("Somerset County row contains an unverified county-specific certificate return rate")

    print("Somerset County Maryland market safety validation passed")


if __name__ == "__main__":
    main()
