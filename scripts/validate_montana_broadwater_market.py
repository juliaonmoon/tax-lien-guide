#!/usr/bin/env python3
"""Guard Broadwater County's market-level tax-lien safety boundary."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Broadwater County"


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Broadwater County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start : end + 2 if end >= 0 else len(text)]

    required = [
        "MARKET-LEVEL ONLY",
        "10%/yr statutory delinquent-tax interest",
        "not a sale of the property",
    ]
    for value in required:
        if value not in row:
            raise SystemExit(f"Broadwater County safety text missing: {value}")

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:"]
    for field in forbidden:
        if field in row:
            raise SystemExit(f"Broadwater County market row must not publish restricted/unsupported field: {field}")

    print("Broadwater County market-level tax-lien safety boundary verified")


if __name__ == "__main__":
    main()
