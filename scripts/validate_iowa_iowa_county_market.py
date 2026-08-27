#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Iowa County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Iowa County market row is missing")

    candidates = [p for p in (text.find("},", start), text.find("}\n", start)) if p >= 0]
    if not candidates:
        raise SystemExit("Could not find end of Iowa County market row")
    end = min(candidates) + 1
    row = text[start:end]

    required = [
        "MARKET-LEVEL ONLY",
        "2%/month redemption interest",
        "held electronically",
        "Sheriff foreclosure sales",
        "not immediate property ownership",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Iowa County safety/rule text missing: {expected}")

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:"]
    for field in forbidden:
        if field in row:
            raise SystemExit(f"Iowa County market row contains prohibited property field: {field}")

    print("Iowa County Iowa market safety validation passed")


if __name__ == "__main__":
    main()
