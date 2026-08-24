#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Garrett County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Garrett County Maryland market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 6000]

    required = [
        "MARKET-LEVEL ONLY",
        "Tax Sale Certificate / property-tax lien",
        "May 18, 2026",
        "May 22, 2026",
        "not immediate ownership",
        "Current 2026 certificate redemption rate not independently verified",
        "judicial foreclosure/deed-sale records",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Garrett County Maryland safety/rule text missing: {expected}")

    for prohibited in ["owner_name:", "taxpayer_name:", "opening_bid:"]:
        if prohibited in row:
            raise SystemExit(f"Garrett County Maryland row contains prohibited property field: {prohibited}")

    print("Garrett County Maryland market safety validation passed")


if __name__ == "__main__":
    main()
