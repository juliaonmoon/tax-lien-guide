#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Muscatine County"


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Missing generated Muscatine County market row")
    end = text.find("}\n", start)
    row = text[start:] if end < 0 else text[start:end + 1]

    required = [
        "MARKET-LEVEL ONLY",
        "maxReturn:'2%/month redemption interest'",
        "does not transfer ownership",
        "Do not fabricate parcel listings",
    ]
    for token in required:
        if token not in row:
            raise SystemExit(f"Muscatine County safety/rule text missing: {token}")

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:", "minimum_bid:"]
    for token in forbidden:
        if token in row:
            raise SystemExit(f"Muscatine County market-level row must not contain {token}")

    print("Muscatine County market-level safety validation passed")


if __name__ == "__main__":
    main()
