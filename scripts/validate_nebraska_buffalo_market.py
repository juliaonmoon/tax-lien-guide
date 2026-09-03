#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Buffalo County"

REQUIRED = [
    "March 2, 2026",
    "Tax lien / tax sale certificate",
    "14%/yr statutory redemption interest",
    "Buffalo County Courthouse",
    "do not bulk republish owner/taxpayer names",
    "Do not treat them as current certificate inventory",
    "Do not represent the 2026 sale as an online auction",
    "not immediate ownership or possession",
    "buffalocounty.ne.gov/county-offices/treasurer",
]

FORBIDDEN_AFFIRMATIVE = [
    "guaranteed inventory",
    "guaranteed ownership",
    "guaranteed deed",
    "guaranteed return",
    "Canadian bidders are eligible",
    "ITIN accepted",
    "online auction for 2026",
]


def extract_row(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate rows array")
    pos = text.find(MARKER, rows_start, rows_end)
    if pos < 0:
        raise SystemExit("Buffalo County Nebraska market row is missing")
    start = text.rfind("{state:", rows_start, pos + 1)
    endings = [p for token in ("},\n", "}\n,", "}\n];") if (p := text.find(token, pos, rows_end + 3)) >= 0]
    if start < rows_start or not endings:
        raise SystemExit("Could not safely isolate Buffalo County row")
    return text[start:min(endings) + 1]


def main():
    row = extract_row(INDEX.read_text(encoding="utf-8"))
    missing = [item for item in REQUIRED if item not in row]
    if missing:
        raise SystemExit("Buffalo County row missing required safety/source text: " + ", ".join(missing))

    # Allow explicit safety disclaimers containing words like "guaranteed" or
    # "online auction" while rejecting unsupported affirmative claims.
    lower = row.lower()
    if "current inventory is available" in lower or "currently available parcels" in lower:
        raise SystemExit("Buffalo County row must not assert current parcel inventory")
    if "canadian bidders are eligible" in lower:
        raise SystemExit("Buffalo County row must not assert unverified Canadian eligibility")
    if "itin accepted" in lower or "itin is accepted" in lower:
        raise SystemExit("Buffalo County row must not assert unverified ITIN acceptance")
    if "the 2026 sale is an online auction" in lower or "2026 online auction" in lower:
        raise SystemExit("Buffalo County official 2026 materials describe an in-person courthouse sale")
    if "immediate ownership" in lower and "not immediate ownership" not in lower:
        raise SystemExit("Buffalo County row must preserve lien/certificate versus ownership distinction")

    print("Buffalo County Nebraska market validation passed")


if __name__ == "__main__":
    main()
