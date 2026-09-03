#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Dodge County"

REQUIRED = [
    "March 2, 2026",
    "8:30 A.M.",
    "Dodge County Board Room",
    "Tax lien / certificate of tax sale",
    "14%/yr current statutory redemption interest",
    "2026 public tax sale passed",
    "no current parcel inventory is asserted here",
    "not immediate ownership or possession",
    "do not bulk republish owner/taxpayer names",
    "dodgecounty.nebraska.gov/treasurer",
    "nebraskalegislature.gov/laws/statutes.php?statute=77-1824",
]


def extract_row(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate rows array")
    pos = text.find(MARKER, rows_start, rows_end)
    if pos < 0:
        raise SystemExit("Dodge County Nebraska market row is missing")
    start = text.rfind("{state:", rows_start, pos + 1)
    endings = [p for token in ("},\n", "}\n,", "}\n];") if (p := text.find(token, pos, rows_end + 3)) >= 0]
    if start < rows_start or not endings:
        raise SystemExit("Could not safely isolate Dodge County row")
    return text[start:min(endings) + 1]


def main():
    row = extract_row(INDEX.read_text(encoding="utf-8"))
    missing = [item for item in REQUIRED if item not in row]
    if missing:
        raise SystemExit("Dodge County row missing required safety/source text: " + ", ".join(missing))

    lower = row.lower()
    forbidden = [
        "current inventory is available",
        "currently available parcels",
        "private-sale inventory is available",
        "over-the-counter inventory is available",
        "canadian bidders are eligible",
        "itin accepted",
        "itin is accepted",
        "immediate tax-deed auction",
        "immediate ownership and possession",
        "online auction is available",
    ]
    bad = [phrase for phrase in forbidden if phrase in lower]
    if bad:
        raise SystemExit("Dodge County row contains unsupported claim(s): " + ", ".join(bad))

    if "immediate ownership" in lower and "not immediate ownership" not in lower:
        raise SystemExit("Dodge County row must preserve certificate versus ownership distinction")
    if "no for the published 2026 procedure" not in lower:
        raise SystemExit("Dodge County row must preserve the official 2026 courthouse sale method")
    if "verify current law" not in lower:
        raise SystemExit("Dodge County row must preserve statutory freshness caveat")

    print("Dodge County Nebraska market validation passed")


if __name__ == "__main__":
    main()
