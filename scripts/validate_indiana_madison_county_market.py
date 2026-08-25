#!/usr/bin/env python3
from pathlib import Path

text = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
marker = "Indiana — Madison County 2026"

if marker not in text:
    raise SystemExit("Missing Madison County Indiana market row")

start = text.index(marker)
chunk = text[start:start + 7000]

required = [
    "Tax sale certificate / property-tax lien",
    "Notice of Real Property Tax Sale",
    "Tax Sale Information for Potential Buyers",
    "MARKET-LEVEL SUMMARY ONLY",
    "title is not immediate",
    "does not bulk republish owner/taxpayer names",
    "does not invent one",
    "Sheriff/judicial foreclosure sales",
    "https://www.madisoncounty.in.gov/departments/treasurer%27s-office",
]
for phrase in required:
    if phrase not in chunk:
        raise SystemExit(f"Madison County safety/provenance text missing: {phrase}")

for forbidden in ["owner:'", "taxpayer:'", "openingBid:", "minimumBid:"]:
    if forbidden in chunk:
        raise SystemExit(f"Unsupported property-level field found in Madison County row: {forbidden}")

print("Madison County Indiana market validation passed")
