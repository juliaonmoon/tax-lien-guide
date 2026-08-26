#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Carroll County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Carroll County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 5000]

    # The row is stored as a JavaScript single-quoted literal, so apostrophes
    # inside field values are escaped (Treasurer\'s). Normalize that storage
    # encoding before checking the human-readable source/safety text.
    readable_row = row.replace("\\'", "'")

    required = [
        "MARKET-LEVEL ONLY",
        "third Monday in June",
        "2%/month redemption interest",
        "does not itself convey title",
        "Sheriff mortgage-foreclosure sales",
        "Treasurer's Office",
    ]
    for expected in required:
        if expected not in readable_row:
            raise SystemExit(f"Carroll County safety/rule text missing: {expected}")

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:"]
    for field in forbidden:
        if field in row:
            raise SystemExit(f"Carroll County market row contains prohibited property field: {field}")

    print("Carroll County market safety validation passed")


if __name__ == "__main__":
    main()
