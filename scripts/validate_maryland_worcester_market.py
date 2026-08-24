#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Worcester County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Worcester County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 5000]

    required = [
        "MARKET-LEVEL ONLY",
        "May 13, 2026",
        "May 15, 2026",
        "Tax Sale Certificate / property-tax lien",
        "10%/yr county redemption rate",
        "Over the Counter Lien",
        "foreclosure-of-the-right-of-redemption",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Worcester County safety/rule text missing: {expected}")

    for field in ["owner_name:", "taxpayer_name:", "opening_bid:"]:
        if field in row:
            raise SystemExit(f"Worcester County row contains prohibited property field: {field}")

    print("Worcester County Maryland market safety validation passed")


if __name__ == "__main__":
    main()
