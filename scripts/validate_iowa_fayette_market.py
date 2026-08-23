#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def main():
    text = INDEX.read_text(encoding="utf-8")
    marker = "Iowa — Fayette County"
    if marker not in text:
        raise SystemExit("Fayette County market row is missing")

    start = text.index("{state:'Iowa — Fayette County'")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},\n", start)
    row = text[start:end + 1]

    required = [
        "MARKET-LEVEL ONLY",
        "2%/month redemption interest",
        "Tax Sale Certificate of Purchase",
        "does not itself convey title",
        "fayettecounty.iowa.gov/departments/treasurer",
    ]
    for token in required:
        if token not in row:
            raise SystemExit(f"Fayette safety/provenance token missing: {token}")

    forbidden = [
        "Sheriff sale opening bid",
        "owner_name:",
        "taxpayer_name:",
    ]
    for token in forbidden:
        if token in row:
            raise SystemExit(f"Unsafe Fayette content detected: {token}")

    print("Fayette County market safety validation passed")


if __name__ == "__main__":
    main()
