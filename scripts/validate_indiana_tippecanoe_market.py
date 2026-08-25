#!/usr/bin/env python3
from pathlib import Path

text = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
marker = "Indiana — Tippecanoe County 2026"

if marker not in text:
    raise SystemExit("Missing Tippecanoe County Indiana market row")

start = text.index(marker)
chunk = text[start:start + 7000]

required = [
    "Tax sale certificate / property-tax lien",
    "2026 Tax Sale Advertisement",
    "MARKET-LEVEL SUMMARY ONLY",
    "tax deed is not immediate",
    "SRI",
    "does not bulk republish owner/taxpayer names",
    "Commissioners’ Certificate Sale",
    "Sheriff/judicial foreclosure sales",
    "https://www.tippecanoe.in.gov/199/Tax-Sale",
]
for phrase in required:
    if phrase not in chunk:
        raise SystemExit(f"Tippecanoe County safety/provenance text missing: {phrase}")

for forbidden in ["owner:'", "taxpayer:'", "openingBid:", "minimumBid:"]:
    if forbidden in chunk:
        raise SystemExit(f"Unsupported property-level field found in Tippecanoe County row: {forbidden}")

print("Tippecanoe County Indiana market validation passed")
