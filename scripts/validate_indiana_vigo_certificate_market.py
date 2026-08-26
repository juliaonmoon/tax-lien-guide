#!/usr/bin/env python3
from pathlib import Path

text = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
marker = "Indiana — Vigo County 2026 Commissioners’ Certificate Sale"

if marker not in text:
    raise SystemExit("Missing Vigo County Indiana Commissioners certificate-sale row")

start = text.index(marker)
chunk = text[start:start + 7500]

required = [
    "Commissioners’ tax-sale certificate / property-tax lien",
    "March 25, 2026",
    "MARKET-LEVEL SUMMARY ONLY",
    "not the ordinary annual Treasurer tax sale",
    "not a Sheriff/judicial foreclosure",
    "does not bulk republish owner/taxpayer names",
    "not immediate ownership",
    "https://www.vigocounty.in.gov/egov/documents/1769177825_36315.pdf",
]
for phrase in required:
    if phrase not in chunk:
        raise SystemExit(f"Vigo County safety/provenance text missing: {phrase}")

for forbidden in ["owner:'", "taxpayer:'", "openingBid:", "minimumBid:"]:
    if forbidden in chunk:
        raise SystemExit(f"Unsupported property-level field found in Vigo County row: {forbidden}")

print("Vigo County Indiana Commissioners certificate-sale market validation passed")
