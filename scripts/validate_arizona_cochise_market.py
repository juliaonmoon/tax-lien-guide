#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Cochise County"

REQUIRED = (
    "Tax lien / Certificate of Purchase",
    "February",
    "Available Tax Liens",
    "updated nightly",
    "16%",
    "not an immediate sale of the property",
    "Do not bulk aggregate owner/taxpayer names",
    "https://www.cochise.az.gov/439/Treasurer",
)

FORBIDDEN = (
    "guaranteed return",
    "immediate ownership",
    "current opening bid",
)


def row_text(text: str) -> str:
    rows_start = text.find("const rows=[")
    rows_end = text.find("\n];", rows_start)
    if rows_start < 0 or rows_end < 0:
        raise SystemExit("Could not locate market rows array")

    marker = text.find(MARKER, rows_start, rows_end)
    if marker < 0:
        raise SystemExit("Cochise County market row missing")

    start = text.rfind("{state:", rows_start, marker + 1)
    if start < rows_start:
        raise SystemExit("Cochise County row start escaped market rows array")

    candidates = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker, rows_end + len("\n];"))
        if pos >= 0:
            candidates.append(pos + 1)
    if not candidates:
        raise SystemExit("Cochise County row end not found")

    end = min(candidates)
    if end > rows_end + 1:
        raise SystemExit("Cochise County row end escaped market rows array")
    return text[start:end]


def main():
    row = row_text(INDEX.read_text(encoding="utf-8"))
    lowered = row.lower()

    missing = [item for item in REQUIRED if item not in row]
    if missing:
        raise SystemExit(f"Cochise County row missing required facts/safeguards: {missing}")

    bad = [item for item in FORBIDDEN if item.lower() in lowered]
    if bad:
        raise SystemExit(f"Cochise County row contains unsafe/misleading language: {bad}")

    # Reject affirmative inventory guarantees, while permitting explicit safety
    # disclaimers such as "do not treat ... as guaranteed inventory".
    guarantee_patterns = (
        r"availability\s*:\s*['\"]guaranteed\b",
        r"\b(?:is|are|remains?|offers?|provides?)\s+guaranteed\s+inventory\b",
    )
    if any(re.search(pattern, lowered) for pattern in guarantee_patterns):
        raise SystemExit("Cochise County availability must remain live-source-qualified")

    print("Cochise County tax-lien market row validated")


if __name__ == "__main__":
    main()
