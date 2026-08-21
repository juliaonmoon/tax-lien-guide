#!/usr/bin/env python3
"""Validate Lake County Montana market-level tax-lien safety boundaries."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Lake County"


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit(f"Missing generated market row: {MARKER}")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start : end + 1 if end >= 0 else len(text)]

    required = [
        "MARKET-LEVEL ONLY",
        "maxReturn:'10%/yr statutory delinquent-tax interest'",
        "tax-lien assignment is not property ownership",
        "Do not bulk collect owner/taxpayer names",
    ]
    missing = [item for item in required if item not in row]
    if missing:
        raise SystemExit("Lake County Montana safety validation failed: " + ", ".join(missing))

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:"]
    present = [item for item in forbidden if item in row]
    if present:
        raise SystemExit("Lake County Montana row contains forbidden property-level fields: " + ", ".join(present))

    print("Verified Lake County Montana market-level lien safeguards")


if __name__ == "__main__":
    main()
