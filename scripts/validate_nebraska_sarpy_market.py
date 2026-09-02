#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Sarpy County"


def main():
    text = INDEX.read_text(encoding="utf-8")
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("rows array not found")
    marker = text.find(MARKER, rows_start, rows_end)
    if marker < 0:
        raise SystemExit("Sarpy County market row missing")
    start = text.rfind("{state:", rows_start, marker + 1)
    end = text.find("},\n", marker, rows_end + 3)
    if end < 0:
        end = text.find("}\n];", marker, rows_end + 3)
    if start < rows_start or end < 0:
        raise SystemExit("Sarpy County row bounds invalid")
    row = text[start:end + 1]

    required = [
        "Tax lien / tax sale certificate",
        "March 2, 2026",
        "March 1, 2027",
        "14%/yr statutory redemption interest",
        "tax-sale certificate is a lien, not immediate ownership",
        "do not bulk republish owner/taxpayer names",
        "https://www.sarpy.gov/981/Tax-Sale-Information",
        "https://www.sarpy.gov/366/Real-Estate-Taxes",
    ]
    for token in required:
        if token not in row:
            raise SystemExit(f"Sarpy County row missing required source/safety token: {token}")

    forbidden = [
        "guaranteed return",
        "guaranteed inventory",
        "guaranteed ownership",
        "current parcels available",
    ]
    lower = row.lower()
    for token in forbidden:
        if token in lower:
            raise SystemExit(f"Sarpy County row contains unsafe/unverified claim: {token}")

    if row.count("Nebraska — Sarpy County") != 1:
        raise SystemExit("Sarpy County row is duplicated or malformed")
    print("Sarpy County Nebraska tax-lien market validation passed")


if __name__ == "__main__":
    main()
