#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def extract_row(text: str, state: str) -> str:
    start = text.find("{state:'" + state + "'")
    if start < 0:
        raise SystemExit(f"{state} market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    return text[start:end if end > start else start + 8000]


def validate_row(row: str, county: str, required: list[str]):
    for expected in required:
        if expected not in row:
            raise SystemExit(f"{county} safety/rule text missing: {expected}")
    for field in ["owner_name:", "taxpayer_name:", "opening_bid:"]:
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

    queen_annes = extract_row(text, "Maryland — Queen Anne\\'s County")
    validate_row(queen_annes, "Queen Anne's County", [
        "MARKET-LEVEL ONLY",
        "May 19, 2026",
        "May 18, 2027",
        "Tax Sale Certificate / property-tax lien",
        "10%/yr county redemption rate",
        "Available Over-the-Counter Tax Sale Certificates",
        "Contact the Treasury Division for the current certificate purchase amount",
        "not immediate ownership or possession",
        "foreclosure-of-redemption",
    ])

    if "opening or purchase bid where the county tells purchasers to contact Treasury" not in queen_annes:
        raise SystemExit("Queen Anne's County must explicitly prohibit inferred OTC/opening bid amounts")

    print("Calvert and Queen Anne's County Maryland market safety validation passed")


if __name__ == "__main__":
    main()
