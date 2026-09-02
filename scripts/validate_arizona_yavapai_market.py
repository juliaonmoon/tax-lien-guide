#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Yavapai County"

REQUIRED = (
    "Tax lien / Certificate of Purchase",
    "February 10, 2026",
    "February 9, 2027",
    "16%",
    "may reduce the rate to 0%",
    "does not convey immediate ownership",
    "separate tax-deed sales",
    "Do not bulk aggregate owner/taxpayer names",
    "https://www.yavapaiaz.gov/Mapping-and-Properties/Property-Taxes/Treasurers-Office/Treasurers-Tax-Lien-Sale",
    "https://www.azleg.gov/ars/42/18114.htm",
)

FORBIDDEN_AFFIRMATIVE = (
    "guaranteed return",
    "guaranteed inventory",
    "guaranteed ownership",
    "current otc inventory",
)


def row_text(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate market rows array")

    marker = text.find(MARKER, rows_start, rows_end)
    if marker < 0:
        raise SystemExit("Yavapai County market row missing")

    start = text.rfind("{state:", rows_start, marker + 1)
    if start < rows_start:
        raise SystemExit("Yavapai County row start escaped market rows array")

    candidates = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker, rows_end + len("\n];"))
        if pos >= 0:
            candidates.append(pos + 1)
    if not candidates:
        raise SystemExit("Yavapai County row end not found")

    end = min(candidates)
    if end > rows_end + 1:
        raise SystemExit("Yavapai County row end escaped market rows array")
    return text[start:end]


def main():
    row = row_text(INDEX.read_text(encoding="utf-8"))
    lowered = row.lower()

    missing = [item for item in REQUIRED if item not in row]
    if missing:
        raise SystemExit(f"Yavapai County row missing required facts/safeguards: {missing}")

    bad = [item for item in FORBIDDEN_AFFIRMATIVE if item in lowered]
    if bad:
        raise SystemExit(f"Yavapai County row contains unsafe/misleading affirmative claim: {bad}")

    if "otc:'yes" in lowered:
        raise SystemExit("Yavapai County row must not assert current OTC availability without a current official inventory source")

    if "tax deed /" in lowered or "product:'tax deed" in lowered:
        raise SystemExit("Yavapai Treasurer row must remain classified as a tax-lien certificate market")

    print("Yavapai County tax-lien market row validated")


if __name__ == "__main__":
    main()
