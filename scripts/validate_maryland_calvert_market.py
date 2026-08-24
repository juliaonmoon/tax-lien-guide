#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'Maryland — Calvert County'")
    if start < 0:
        raise SystemExit("Calvert County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start:end if end > start else start + 7000]

    required = [
        "MARKET-LEVEL ONLY",
        "May 22, 2026",
        "Tax Sale Certificate / property-tax lien",
        "10%/yr county redemption rate",
        "Certificate of Sale",
        "not immediate title",
        "foreclose the right of redemption",
    ]
    for expected in required:
        if expected not in row:
            raise SystemExit(f"Calvert County safety/rule text missing: {expected}")

    for field in ["owner_name:", "taxpayer_name:", "opening_bid:"]:
        if field in row:
            raise SystemExit(f"Calvert County row contains prohibited property field: {field}")

    print("Calvert County Maryland market safety validation passed")


if __name__ == "__main__":
    main()
