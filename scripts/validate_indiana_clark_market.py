#!/usr/bin/env python3
from pathlib import Path

text = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
marker = "Indiana — Clark County 2026"

if marker not in text:
    raise SystemExit("Missing Clark County Indiana market row")

start = text.index(marker)
chunk = text[start:start + 6500]

required = [
    "Tax sale certificate / property-tax lien",
    "MARKET-LEVEL SUMMARY ONLY",
    "Tax Sale Certificate",
    "tax deed is not immediate",
    "SRI",
    "does not currently publish a specific 2026 sale date",
    "Do not bulk republish owner/taxpayer names",
    "Sheriff",
    "https://clarkcounty.in.gov/index.php/clark-county-indiana-government/clark-county-treasurer-s-office",
]
for phrase in required:
    if phrase not in chunk:
        raise SystemExit(f"Clark County safety/provenance text missing: {phrase}")

for forbidden in ["owner:'", "taxpayer:'", "openingBid:", "minimumBid:"]:
    if forbidden in chunk:
        raise SystemExit(f"Unsupported property-level field found in Clark County row: {forbidden}")

print("Clark County Indiana market validation passed")
