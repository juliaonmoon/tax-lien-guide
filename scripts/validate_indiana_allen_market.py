#!/usr/bin/env python3
from pathlib import Path

text = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
marker = "Indiana — Allen County 2026"

if marker not in text:
    raise SystemExit("Missing Allen County Indiana market row")

start = text.index(marker)
chunk = text[start:start + 7500]
required = [
    "Tax sale certificate / property-tax lien",
    "September 16, 2026",
    "August 20, 2026",
    "MARKET-LEVEL SUMMARY ONLY",
    "does not bulk republish owner/taxpayer names",
    "does not give immediate ownership",
    "Sheriff",
    "https://www.allencounty.in.gov/270/Tax-Sale",
]
for phrase in required:
    if phrase not in chunk:
        raise SystemExit(f"Allen County safety/provenance text missing: {phrase}")

for forbidden in ["owner:'", "taxpayer:'", "openingBid:", "minimumBid:"]:
    if forbidden in chunk:
        raise SystemExit(f"Unsupported property-level field found in Allen County row: {forbidden}")

print("Allen County Indiana market validation passed")
