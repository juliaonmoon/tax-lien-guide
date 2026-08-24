#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Wicomico County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Wicomico County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 6000]

    required = [
        "MARKET-LEVEL ONLY",
        "Tax Lien Certificate / property-tax lien",
        "June 9, 2026",
        "June 23 through December 31, 2026",
        "W-9 and purchaser agreement",
        "not immediate ownership",
        "redemption rate not verified",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Wicomico County safety/rule text missing: {expected}")

    for prohibited in ["owner_name:", "taxpayer_name:", "opening_bid:"]:
        if prohibited in row:
            raise SystemExit(f"Wicomico County market row contains prohibited property field: {prohibited}")

    if "15%" in row or "18%" in row or "10%/yr" in row:
        raise SystemExit("Wicomico County row contains an unverified certificate return rate")

    print("Wicomico County Maryland market safety validation passed")


if __name__ == "__main__":
    main()
