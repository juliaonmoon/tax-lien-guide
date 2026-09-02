#!/usr/bin/env python3
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "index.html"
MARKER = "Nebraska — Lancaster County"

REQUIRED = (
    "March 2, 2026",
    "14%/yr current statutory interest",
    "certificate of tax sale",
    "not immediate ownership or possession",
    "do not bulk republish owner/taxpayer names",
    "https://www.lancaster.ne.gov/DocumentCenter/View/640/Tax-Sale-Information-PDF",
    "https://www.lancaster.ne.gov/DocumentCenter/View/641/Tax-Sale-Purchasing-Information-PDF",
)

FORBIDDEN = (
    "guaranteed inventory",
    "guaranteed return",
    "guaranteed deed",
    "Canadian eligible: yes",
    "next sale March 2027",
)


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("const rows=[")
    end = text.find("\n];", start)
    if start < 0 or end < 0:
        raise SystemExit("Could not locate market rows array")

    marker = text.find(MARKER, start, end)
    if marker < 0:
        raise SystemExit("Lancaster Nebraska market row is missing")
    row_start = text.rfind("{state:", start, marker + 1)
    next_row = text.find("{state:", marker + len(MARKER), end)
    row_end = next_row if next_row >= 0 else end
    if row_start < start or row_end > end or row_start >= row_end:
        raise SystemExit("Lancaster Nebraska row boundaries are invalid")

    row = text[row_start:row_end]
    missing = [value for value in REQUIRED if value not in row]
    if missing:
        raise SystemExit("Lancaster Nebraska row missing required safety/source facts: " + ", ".join(missing))

    lowered = row.lower()
    bad = [value for value in FORBIDDEN if value.lower() in lowered]
    if bad:
        raise SystemExit("Lancaster Nebraska row contains unsafe/unverified claims: " + ", ".join(bad))

    print("Lancaster Nebraska tax-lien market validation passed")


if __name__ == "__main__":
    main()
