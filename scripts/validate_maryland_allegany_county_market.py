#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Allegany County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Allegany County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 6000]
    required = [
        "MARKET-LEVEL ONLY",
        "Tax Lien Certificate / property-tax lien",
        "10%/yr owner-occupied; 18%/yr non-owner-occupied",
        "2026 list of tax lien certificates available for OTC purchase",
        "foreign bidder registrations are not allowed",
        "not immediate ownership",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Allegany County safety/rule text missing: {expected}")
    for field in ["owner_name:", "taxpayer_name:", "opening_bid:"]:
        if field in row:
            raise SystemExit(f"Allegany County market row contains prohibited property field: {field}")
    print("Allegany County Maryland market safety validation passed")


if __name__ == "__main__":
    main()
