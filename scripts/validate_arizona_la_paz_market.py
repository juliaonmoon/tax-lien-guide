#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — La Paz County"

REQUIRED = (
    "Tax lien / Certificate of Purchase",
    "February 25, 2026",
    "over-the-counter",
    "April 1, 2026",
    "16%",
    "not an immediate property sale",
    "Do not bulk aggregate owner/taxpayer names",
    "does not reproduce or bypass that paid list",
    "https://lapaztreas.com/tax-lien-sale-1",
)

FORBIDDEN = (
    "guaranteed return",
    "guaranteed inventory",
    "immediate ownership",
    "current opening bid",
    "current minimum bid",
)


def row_text(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate market rows array")

    marker = text.find(MARKER, rows_start, rows_end)
    if marker < 0:
        raise SystemExit("La Paz County market row missing")

    start = text.rfind("{state:", rows_start, marker + 1)
    if start < rows_start:
        raise SystemExit("La Paz County row start escaped market rows array")

    candidates = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker, rows_end + len("\n];"))
        if pos >= 0:
            candidates.append(pos + 1)
    if not candidates:
        raise SystemExit("La Paz County row end not found")

    end = min(candidates)
    if end > rows_end + 1:
        raise SystemExit("La Paz County row end escaped market rows array")
    return text[start:end]


def main():
    row = row_text(INDEX.read_text(encoding="utf-8"))
    lowered = row.lower()

    missing = [item for item in REQUIRED if item not in row]
    if missing:
        raise SystemExit(f"La Paz County row missing required facts/safeguards: {missing}")

    bad = [item for item in FORBIDDEN if item.lower() in lowered]
    if bad:
        raise SystemExit(f"La Paz County row contains unsafe/misleading language: {bad}")

    print("La Paz County tax-lien market row validated")


if __name__ == "__main__":
    main()
