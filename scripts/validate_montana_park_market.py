#!/usr/bin/env python3
"""Validate the public Park County Montana market row without touching owner data."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Park County"


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Park County Montana market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start : end + 1 if end >= 0 else len(text)]

    required = [
        "MARKET-LEVEL ONLY",
        "maxReturn:'10%/yr statutory delinquent-tax interest'",
        "Tax lien assignment / certificate",
        "not immediate property ownership",
    ]
    missing = [value for value in required if value not in row]
    if missing:
        raise SystemExit("Park County Montana safety validation failed: " + ", ".join(missing))

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:"]
    present = [value for value in forbidden if value in row]
    if present:
        raise SystemExit("Park County Montana row contains forbidden property-level fields: " + ", ".join(present))

    print("Park County Montana market safety validation passed")


if __name__ == "__main__":
    main()
