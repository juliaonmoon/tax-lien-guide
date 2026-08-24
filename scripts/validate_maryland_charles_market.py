#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'Maryland — Charles County'")
    if start < 0:
        raise SystemExit("Charles County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 6000]

    required = [
        "MARKET-LEVEL ONLY",
        "May 12, 2026",
        "Tax Sale Certificate / property-tax lien",
        "12%/yr county redemption rate",
        "1% per month",
        "may not be purchased over the counter",
        "not immediate ownership",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Charles County safety/rule text missing: {expected}")

    for field in ["owner_name:", "taxpayer_name:", "opening_bid:"]:
        if field in row:
            raise SystemExit(f"Charles County row contains prohibited property field: {field}")

    print("Charles County Maryland market safety validation passed")


if __name__ == "__main__":
    main()
