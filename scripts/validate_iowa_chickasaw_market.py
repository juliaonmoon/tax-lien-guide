#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Chickasaw County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Chickasaw County market row is missing")

    candidates = [p for p in (text.find("},\n", start), text.find("}\n", start)) if p >= 0]
    if not candidates:
        raise SystemExit("Could not find end of Chickasaw County market row")
    end = min(candidates) + 1
    row = text[start:end]

    required = [
        "MARKET-LEVEL ONLY",
        "2%/month redemption interest",
        "June 15, 2026",
        "Tax Sale Certificate of Purchase",
        "does not itself convey title",
        "Sheriff mortgage-foreclosure sales",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Chickasaw County safety/rule text missing: {expected}")

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:"]
    for field in forbidden:
        if field in row:
            raise SystemExit(f"Chickasaw County market row contains prohibited property field: {field}")

    print("Chickasaw County market safety validation passed")


if __name__ == "__main__":
    main()
