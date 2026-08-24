#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Anne Arundel County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Anne Arundel County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 5000]

    required = [
        "MARKET-LEVEL ONLY",
        "June 3, 2026",
        "Tax Sale Certificate / first-lien property-tax lien",
        "18%/yr county redemption rate",
        "not the property itself",
        "foreclosure-of-redemption",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Anne Arundel County safety/rule text missing: {expected}")

    for field in ["owner_name:", "taxpayer_name:", "opening_bid:"]:
        if field in row:
            raise SystemExit(f"Anne Arundel County row contains prohibited property field: {field}")

    print("Anne Arundel County Maryland market safety validation passed")


if __name__ == "__main__":
    main()
