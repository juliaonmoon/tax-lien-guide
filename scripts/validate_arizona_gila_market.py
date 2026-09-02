#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Gila County"

REQUIRED = (
    "Tax lien / Certificate of Purchase",
    "February",
    "16%",
    "not a tax-deed auction",
    "Do not bulk aggregate owner/taxpayer names",
    "https://agenda.gilacountyaz.gov/",
)

FORBIDDEN = (
    "immediate ownership",
    "guaranteed return",
    "guaranteed inventory",
    "current OTC inventory",
)


def row_text(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate market rows array")

    marker = text.find(MARKER, rows_start, rows_end)
    if marker < 0:
        raise SystemExit("Gila County market row missing")

    start = text.rfind("{state:", rows_start, marker + 1)
    if start < rows_start:
        raise SystemExit("Gila County row start escaped market rows array")

    candidates = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker, rows_end + len("\n];"))
        if pos >= 0:
            candidates.append(pos + 1)
    if not candidates:
        raise SystemExit("Gila County row end not found")

    end = min(candidates)
    if end > rows_end + 1:
        raise SystemExit("Gila County row end escaped market rows array")
    return text[start:end]


def main():
    row = row_text(INDEX.read_text(encoding="utf-8"))
    lowered = row.lower()

    missing = [item for item in REQUIRED if item not in row]
    if missing:
        raise SystemExit(f"Gila County row missing required facts/safeguards: {missing}")

    bad = [item for item in FORBIDDEN if item.lower() in lowered]
    if bad:
        raise SystemExit(f"Gila County row contains unsafe/misleading language: {bad}")

    if "online:'yes" in lowered or "otc:'yes" in lowered:
        raise SystemExit("Gila County row must not assert online/OTC availability without a stable official current source")

    print("Gila County tax-lien market row validated")


if __name__ == "__main__":
    main()
