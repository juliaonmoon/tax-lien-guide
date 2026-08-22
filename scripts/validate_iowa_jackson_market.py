#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Jackson County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Jackson County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 6000]

    required = [
        "MARKET-LEVEL ONLY",
        "2%/month redemption interest",
        "June 15, 2026",
        "does not transfer ownership",
        "Sheriff mortgage-foreclosure sales",
        "at least 18",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Jackson County safety/rule text missing: {expected}")

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:"]
    for field in forbidden:
        if field in row:
            raise SystemExit(f"Jackson County market row contains prohibited property field: {field}")

    print("Jackson County market safety validation passed")


if __name__ == "__main__":
    main()
