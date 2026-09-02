#!/usr/bin/env python3
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "index.html"
MARKER = "Nebraska — Hall County"

REQUIRED = (
    "March 2, 2026",
    "No remaining delinquent taxes are currently offered for sale",
    "14%/yr statutory redemption interest",
    "tax lien, not immediate ownership or possession",
    "do not bulk republish owner/taxpayer names",
    "https://files.hallcountyne.gov/departments/treasurer/delinquent_tax_list.php",
    "https://reports.hallcountyne.gov/Treasurer/Delinquent/advertlist.php",
)

FORBIDDEN = (
    "guaranteed return",
    "guaranteed deed",
    "Canadian eligible: yes",
    "current otc inventory",
    "online auction",
)


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("const rows=[")
    end = text.find("\n];", start)
    if start < 0 or end < 0:
        raise SystemExit("Could not locate market rows array")

    marker = text.find(MARKER, start, end)
    if marker < 0:
        raise SystemExit("Hall Nebraska market row is missing")
    row_start = text.rfind("{state:", start, marker + 1)
    next_row = text.find("{state:", marker + len(MARKER), end)
    row_end = next_row if next_row >= 0 else end
    if row_start < start or row_end > end or row_start >= row_end:
        raise SystemExit("Hall Nebraska row boundaries are invalid")

    row = text[row_start:row_end]
    missing = [value for value in REQUIRED if value not in row]
    if missing:
        raise SystemExit("Hall Nebraska row missing required safety/source facts: " + ", ".join(missing))

    lowered = row.lower()
    bad = [value for value in FORBIDDEN if value.lower() in lowered]
    if bad:
        raise SystemExit("Hall Nebraska row contains unsafe/unverified claims: " + ", ".join(bad))

    print("Hall Nebraska tax-lien market validation passed")


if __name__ == "__main__":
    main()
