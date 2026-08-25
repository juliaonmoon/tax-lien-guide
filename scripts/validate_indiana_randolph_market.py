#!/usr/bin/env python3
from pathlib import Path

text = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
marker = "Indiana — Randolph County 2026"

if marker not in text:
    raise SystemExit("Missing Randolph County Indiana market row")

start = text.index(marker)
chunk = text[start:start + 6000]

required = [
    "Tax sale certificate / property-tax lien",
    "MARKET-LEVEL SUMMARY ONLY",
    "Tax Sale Certificate/lien, not the real estate",
    "SRI",
    "Commissioners Certificate Sale",
    "does not bulk republish owner/taxpayer names",
    "https://www.in.gov/counties/randolph/departments/treasurer/tax-certificate-sales/",
]
for phrase in required:
    if phrase not in chunk:
        raise SystemExit(f"Randolph County safety/provenance text missing: {phrase}")

for forbidden in ["owner:'", "taxpayer:'", "openingBid:", "minimumBid:"]:
    if forbidden in chunk:
        raise SystemExit(f"Unsupported property-level field found in Randolph County row: {forbidden}")

print("Randolph County Indiana market validation passed")
