#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def main():
    text = INDEX.read_text(encoding="utf-8")
    marker = "Iowa — Mahaska County"
    if marker not in text:
        raise SystemExit("Mahaska County market row is missing")

    start = text.index("{state:'Iowa — Mahaska County'")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},\n", start)
    row = text[start:end + 1]

    required = [
        "MARKET-LEVEL ONLY",
        "2%/month redemption interest",
        "Tax Sale Certificate of Purchase",
        "does not itself convey title",
        "mahaskacountyia.gov/treasurer",
    ]
    for token in required:
        if token not in row:
            raise SystemExit(f"Mahaska safety/provenance token missing: {token}")

    forbidden = [
        "Sheriff sale opening bid",
        "owner_name:",
        "taxpayer_name:",
    ]
    for token in forbidden:
        if token in row:
            raise SystemExit(f"Unsafe Mahaska content detected: {token}")

    print("Mahaska County market safety validation passed")


if __name__ == "__main__":
    main()
