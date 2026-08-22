#!/usr/bin/env python3
"""Validate the safe market-level Teton County, Montana tax-lien row."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Teton County"


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Teton County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start : end + 1 if end >= 0 else len(text)]

    required = [
        "MARKET-LEVEL ONLY",
        "maxReturn:'10%/yr statutory delinquent-tax interest'",
        "5/6 of 1% per month (10% annualized)",
        "tax-lien assignment is not immediate property ownership",
    ]
    missing = [token for token in required if token not in row]
    if missing:
        raise SystemExit("Teton County safety validation failed; missing: " + ", ".join(missing))

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:", "minimum_bid:"]
    present = [token for token in forbidden if token in row]
    if present:
        raise SystemExit("Teton County row contains prohibited property-level fields: " + ", ".join(present))

    print("Teton County Montana market-level safety boundary verified")


if __name__ == "__main__":
    main()
