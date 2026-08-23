#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def main():
    text = INDEX.read_text(encoding="utf-8")
    marker = "Iowa — Marion County"
    if marker not in text:
        raise SystemExit("Marion County market row is missing")

    start = text.index("{state:'Iowa — Marion County'")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},\n", start)
    row = text[start:end + 1]

    required = [
        "MARKET-LEVEL ONLY",
        "2%/month redemption interest",
        "Tax Sale Certificate of Purchase",
        "does not transfer ownership",
        "marioncountyiowa.gov/treasurer/tax_sale",
        "June 15, 2026",
    ]
    for token in required:
        if token not in row:
            raise SystemExit(f"Marion safety/provenance token missing: {token}")

    forbidden = [
        "Sheriff sale opening bid",
        "owner_name:",
        "taxpayer_name:",
        "opening_bid:",
    ]
    for token in forbidden:
        if token in row:
            raise SystemExit(f"Unsafe Marion content detected: {token}")

    print("Marion County market safety validation passed")


if __name__ == "__main__":
    main()
