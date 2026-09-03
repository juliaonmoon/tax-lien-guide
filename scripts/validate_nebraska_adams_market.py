#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Adams County"

REQUIRED = [
    "March 2, 2026",
    "Tax lien / certificate of tax sale",
    "14%/yr current statutory redemption interest",
    "Hastings Public Library",
    "bidder-number rotation",
    "2026 annual public tax-lien/certificate sale passed",
    "no current parcel inventory is asserted here",
    "not immediate ownership or possession",
    "do not bulk republish owner/taxpayer names",
    "adamscountyne.gov/treasurer/57-tax-sales",
]


def extract_row(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate rows array")
    pos = text.find(MARKER, rows_start, rows_end)
    if pos < 0:
        raise SystemExit("Adams County Nebraska market row is missing")
    start = text.rfind("{state:", rows_start, pos + 1)
    endings = [p for token in ("},\n", "}\n,", "}\n];") if (p := text.find(token, pos, rows_end + 3)) >= 0]
    if start < rows_start or not endings:
        raise SystemExit("Could not safely isolate Adams County row")
    return text[start:min(endings) + 1]


def main():
    row = extract_row(INDEX.read_text(encoding="utf-8"))
    missing = [item for item in REQUIRED if item not in row]
    if missing:
        raise SystemExit("Adams County row missing required safety/source text: " + ", ".join(missing))

    lower = row.lower()
    forbidden = [
        "current inventory is available",
        "currently available parcels",
        "private-sale inventory is available",
        "over-the-counter inventory is available",
        "canadian bidders are eligible",
        "itin accepted",
        "itin is accepted",
        "2026 online auction",
        "the march 2026 sale is an online auction",
        "guaranteed return",
        "guaranteed deed",
    ]
    bad = [phrase for phrase in forbidden if phrase in lower]
    if bad:
        raise SystemExit("Adams County row contains unsupported claim(s): " + ", ".join(bad))
    if "immediate ownership" in lower and "not immediate ownership" not in lower:
        raise SystemExit("Adams County row must preserve lien/certificate versus ownership distinction")
    if "no for the published 2026 procedure" not in lower:
        raise SystemExit("Adams County row must preserve the official in-person 2026 sale method")

    print("Adams County Nebraska market validation passed")


if __name__ == "__main__":
    main()
