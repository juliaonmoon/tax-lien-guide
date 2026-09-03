#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Valley County"

REQUIRED = [
    "March 2, 2026",
    "Tax lien / certificate of tax sale",
    "14%/yr current statutory redemption interest",
    "first Monday in March",
    "County Courthouse",
    "2026 annual public tax-lien sale passed",
    "no current parcel inventory is asserted here",
    "not immediate ownership or possession",
    "purchasing delinquent taxes, not the property",
    "do not bulk republish owner/taxpayer names",
    "valleycountyne.gov/treasurer-office/public-tax-sale-information/",
]


def extract_row(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate rows array")
    pos = text.find(MARKER, rows_start, rows_end)
    if pos < 0:
        raise SystemExit("Valley County Nebraska market row is missing")
    start = text.rfind("{state:", rows_start, pos + 1)
    endings = [p for token in ("},\n", "}\n,", "}\n];") if (p := text.find(token, pos, rows_end + 3)) >= 0]
    if start < rows_start or not endings:
        raise SystemExit("Could not safely isolate Valley County row")
    return text[start:min(endings) + 1]


def main():
    row = extract_row(INDEX.read_text(encoding="utf-8"))
    missing = [item for item in REQUIRED if item not in row]
    if missing:
        raise SystemExit("Valley County row missing required safety/source text: " + ", ".join(missing))

    lower = row.lower()
    forbidden = [
        "current inventory is available",
        "currently available parcels",
        "private-sale inventory is available",
        "over-the-counter inventory is available",
        "canadian bidders are eligible",
        "itin accepted",
        "itin is accepted",
        "tax deed auction",
        "immediate ownership and possession",
    ]
    bad = [phrase for phrase in forbidden if phrase in lower]
    if bad:
        raise SystemExit("Valley County row contains unsupported claim(s): " + ", ".join(bad))
    if "immediate ownership" in lower and "not immediate ownership" not in lower:
        raise SystemExit("Valley County row must preserve lien/certificate versus ownership distinction")
    if "no for the published county procedure" not in lower:
        raise SystemExit("Valley County row must preserve the official courthouse sale method")

    print("Valley County Nebraska market validation passed")


if __name__ == "__main__":
    main()
