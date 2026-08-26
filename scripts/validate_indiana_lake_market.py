#!/usr/bin/env python3
from pathlib import Path

text = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
marker = "Indiana — Lake County 2026"

if marker not in text:
    raise SystemExit("Missing Lake County Indiana market row")

start = text.index(marker)
chunk = text[start:start + 8000]
required = [
    "Tax sale certificate / property-tax lien",
    "September 4-8, 2026",
    "July 29, 2026",
    "ZeusAuction",
    "MARKET-LEVEL SUMMARY ONLY",
    "does not bulk republish owner/taxpayer names",
    "does not give immediate ownership",
    "Commissioners Tax Sale",
    "Sheriff/judicial foreclosure",
    "minimum bids are prescribed by law and may change before the auction",
    "https://www.lakecountyin.gov/departments/auditor-taxsales/lake-county-treasurer-tax-sale",
]
for phrase in required:
    if phrase not in chunk:
        raise SystemExit(f"Lake County safety/provenance text missing: {phrase}")

for forbidden in ["owner:'", "taxpayer:'", "openingBid:", "minimumBid:"]:
    if forbidden in chunk:
        raise SystemExit(f"Unsupported property-level field found in Lake County row: {forbidden}")

print("Lake County Indiana market validation passed")
