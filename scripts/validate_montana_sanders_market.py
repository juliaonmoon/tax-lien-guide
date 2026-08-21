#!/usr/bin/env python3
"""Validate Sanders County's market-level tax-lien safety boundary."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Sanders County"


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Sanders County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start : end + 1] if end >= 0 else text[start : start + 6000]

    required = [
        "MARKET-LEVEL ONLY",
        "10%/yr statutory delinquent-tax interest",
        "tax assignment",
        "not immediate property ownership",
    ]
    missing = [item for item in required if item not in row]
    if missing:
        raise SystemExit("Sanders County safety validation failed; missing: " + ", ".join(missing))

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:"]
    found = [item for item in forbidden if item in row]
    if found:
        raise SystemExit("Sanders County row contains prohibited property-level fields: " + ", ".join(found))

    print("Sanders County market-level safety boundary verified")


if __name__ == "__main__":
    main()
