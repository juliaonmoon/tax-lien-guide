#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def extract_row(text: str, state: str) -> str:
    start = text.find("{state:'" + state + "'")
    if start < 0:
        raise SystemExit(f"{state} market row is missing")
    comma_end = text.find("},", start)
    newline_end = text.find("}\n", start)
    candidates = [pos for pos in (comma_end, newline_end) if pos >= 0]
    end = min(candidates) if candidates else min(len(text), start + 8000)
    return text[start:end]


def validate_row(row: str, county: str, required: list[str]):
    for expected in required:
        if expected not in row:
            raise SystemExit(f"{county} safety/rule text missing: {expected}")
    for field in ["owner_name:", "taxpayer_name:", "opening_bid:", "minimum_bid:"]:
        if field in row:
            raise SystemExit(f"{county} row contains prohibited property field: {field}")


def main():
    text = INDEX.read_text(encoding="utf-8")

    calvert = extract_row(text, "Maryland — Calvert County")
    validate_row(calvert, "Calvert County", [
        "MARKET-LEVEL ONLY",
        "May 22, 2026",
        "Tax Sale Certificate / property-tax lien",
        "10%/yr county redemption rate",
        "Certificate of Sale",
        "not immediate title",
        "foreclose the right of redemption",
    ])

    print("Calvert County Maryland market safety validation passed")


if __name__ == "__main__":
    main()
