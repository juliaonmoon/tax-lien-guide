#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Gage County"

REQUIRED = [
    "March 2, 2026",
    "Tax lien / certificate of tax sale",
    "14%/yr current statutory redemption interest",
    "District Courtroom",
    "2026 public tax-lien/certificate sale passed",
    "no current parcel inventory is asserted here",
    "purchasing delinquent taxes, not the property",
    "not immediate ownership or possession",
    "do not bulk republish owner/taxpayer names",
    "gagecountyne.gov/treasurer-office/public-tax-sale-information/",
]


def extract_row(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate rows array")
    pos = text.find(MARKER, rows_start, rows_end)
    if pos < 0:
        raise SystemExit("Gage County Nebraska market row is missing")
    start = text.rfind("{state:", rows_start, pos + 1)
    endings = [p for token in ("},\n", "}\n,", "}\n];") if (p := text.find(token, pos, rows_end + 3)) >= 0]
    if start < rows_start or not endings:
        raise SystemExit("Could not safely isolate Gage County row")
    return text[start:min(endings) + 1]


def main():
    row = extract_row(INDEX.read_text(encoding="utf-8"))
    missing = [item for item in REQUIRED if item not in row]
    if missing:
        raise SystemExit("Gage County row missing required safety/source text: " + ", ".join(missing))

    lower = row.lower()
    forbidden = [
        "current inventory is available",
        "currently available parcels",
        "private-sale inventory is available",
        "canadian bidders are eligible",
        "itin accepted",
        "itin is accepted",
        "2026 online auction",
        "the march 2026 sale is an online auction",
        "guaranteed return",
        "guaranteed deed",
        "immediate tax deed auction",
    ]
    bad = [phrase for phrase in forbidden if phrase in lower]
    if bad:
        raise SystemExit("Gage County row contains unsupported claim(s): " + ", ".join(bad))
    if "immediate ownership" in lower and "not immediate ownership" not in lower:
        raise SystemExit("Gage County row must preserve lien/certificate versus ownership distinction")
    if "no for the published 2026 procedure" not in lower:
        raise SystemExit("Gage County row must preserve the official in-person 2026 sale method")
    if "private tax sale" in lower and "not a claim that any particular parcel or certificate is currently available" not in lower:
        raise SystemExit("Gage County private-sale text must not imply current inventory")

    print("Gage County Nebraska market validation passed")


if __name__ == "__main__":
    main()
