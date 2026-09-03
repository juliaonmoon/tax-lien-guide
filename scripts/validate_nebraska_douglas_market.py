#!/usr/bin/env python3
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / "index.html"
MARKER = "Nebraska — Douglas County"

REQUIRED = (
    "March 2, 2026",
    "February 5 through March 2, 2026",
    "14%/yr current statutory interest",
    "Tax lien / certificate of tax sale",
    "not immediate ownership or possession",
    "do not describe the annual tax-lien sale as a tax-deed auction",
    "do not bulk republish owner/taxpayer names",
    "https://treasurer.douglascounty-ne.gov/public-tax-sale/",
    "https://www.omahadailyrecord.com/sites/default/files/DELINQUENT%20TAX%20DOUGLAS%20COUNTY%202025%20p%201.pdf",
    "https://nebraskalegislature.gov/laws/statutes.php?statute=77-1802",
    "https://nebraskalegislature.gov/laws/statutes.php?statute=77-1824",
)

FORBIDDEN_AFFIRMATIVE = (
    "guaranteed return",
    "guaranteed deed",
    "Canadian eligible: yes",
    "ITIN accepted",
    "2027 sale confirmed",
    "March 1, 2027 confirmed",
)


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("const rows=[")
    end = text.find("\n];", start)
    if start < 0 or end < 0:
        raise SystemExit("Could not locate market rows array")

    marker = text.find(MARKER, start, end)
    if marker < 0:
        raise SystemExit("Douglas Nebraska market row is missing")
    row_start = text.rfind("{state:", start, marker + 1)
    next_row = text.find("{state:", marker + len(MARKER), end)
    row_end = next_row if next_row >= 0 else end
    if row_start < start or row_end > end or row_start >= row_end:
        raise SystemExit("Douglas Nebraska row boundaries are invalid")

    row = text[row_start:row_end]
    missing = [value for value in REQUIRED if value not in row]
    if missing:
        raise SystemExit("Douglas Nebraska row missing required safety/source facts: " + ", ".join(missing))

    lowered = row.lower()
    bad = [value for value in FORBIDDEN_AFFIRMATIVE if value.lower() in lowered]
    if bad:
        raise SystemExit("Douglas Nebraska row contains unsafe/unverified claims: " + ", ".join(bad))

    # Current-inventory claims must remain explicitly disclaimed; the completed
    # 2026 advertisement is historical evidence, not a live parcel feed.
    if "no current parcel inventory is asserted here" not in lowered:
        raise SystemExit("Douglas Nebraska row must disclaim current parcel inventory")
    if "do not infer current private-sale, over-the-counter, or county-held certificate inventory" not in lowered:
        raise SystemExit("Douglas Nebraska row must disclaim inferred post-sale inventory")

    print("Douglas Nebraska tax-lien market validation passed")


if __name__ == "__main__":
    main()
