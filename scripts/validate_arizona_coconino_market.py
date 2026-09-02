#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Coconino County"

REQUIRED = (
    "product:'Tax lien / Certificate of Purchase'",
    "February 10, 2026",
    "September 2026 over-the-counter list",
    "maxReturn:'16%/yr max'",
    "rates range from 0% to 16%",
    "conveys no property rights",
    "https://www.coconino.az.gov/376/Tax-Liens",
)

FORBIDDEN = (
    "ownerName:",
    "taxpayerName:",
    "guaranteed return",
    "guaranteed property",
)


def market_row(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate market rows array")

    marker_pos = text.find(MARKER, rows_start, rows_end)
    if marker_pos < 0:
        raise SystemExit("Coconino County market row is missing")

    row_start = text.rfind("{state:", rows_start, marker_pos + 1)
    if row_start < rows_start:
        raise SystemExit("Coconino County row starts outside market rows array")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + len("\n];"))
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Could not locate Coconino County row end")

    row_end = min(endings) + 1
    if row_end > rows_end + 1:
        raise SystemExit("Coconino County row escapes market rows array")
    return text[row_start:row_end]


def main():
    row = market_row(INDEX.read_text(encoding="utf-8"))
    missing = [needle for needle in REQUIRED if needle not in row]
    if missing:
        raise SystemExit("Coconino County row missing required safety/source facts: " + ", ".join(missing))

    forbidden = [needle for needle in FORBIDDEN if needle.lower() in row.lower()]
    if forbidden:
        raise SystemExit("Coconino County row contains forbidden/unsafe fields: " + ", ".join(forbidden))

    print("Coconino County tax-lien market validation passed")


if __name__ == "__main__":
    main()
