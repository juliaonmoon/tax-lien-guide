#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Dorchester County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    if text.count(MARKER) != 1:
        raise SystemExit(f"Expected exactly one Dorchester County market row, found {text.count(MARKER)}")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Dorchester County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 7000]

    required = [
        "MARKET-LEVEL ONLY",
        "Tax Sale Certificate / property-tax lien",
        "May 18, 2026",
        "May 19, 2026",
        "completed 2026 sale",
        "10%/yr in the latest official Terms of Sale currently linked by the county (2025)",
        "Do not assume that rate or all terms are unchanged for a future sale",
        "not immediate possession or title",
        "right of redemption is finally foreclosed",
        "Do not bulk republish owner/taxpayer names",
        "https://dorchestercountymd.com/departments/finance-treasury/tax-sale/",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Dorchester County safety/rule text missing: {expected}")

    prohibited = [
        "owner_name:",
        "taxpayer_name:",
        "opening_bid:",
        "10%/yr county redemption rate",
        "held its 2026 tax sale on May 19, 2026",
    ]
    for field in prohibited:
        if field in row:
            raise SystemExit(f"Dorchester County market row contains unsafe/stale claim: {field}")

    print("Dorchester County Maryland market safety validation passed")


if __name__ == "__main__":
    main()
