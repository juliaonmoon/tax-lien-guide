#!/usr/bin/env python3
from pathlib import Path

text = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
marker = "Indiana — Hamilton County 2026"

if marker not in text:
    raise SystemExit("Missing Hamilton County Indiana market row")

start = text.index(marker)
chunk = text[start:start + 7000]
required = [
    "Tax sale certificate / property-tax lien",
    "October 8, 2026",
    "MARKET-LEVEL SUMMARY ONLY",
    "tax deed is not immediate",
    "does not bulk republish owner/taxpayer names",
    "Sheriff foreclosure listings",
    "https://www.hamiltoncounty.in.gov/1380/Tax-Sale-Notice-2026",
]
for phrase in required:
    if phrase not in chunk:
        raise SystemExit(f"Hamilton County safety/provenance text missing: {phrase}")

for forbidden in ["owner:'", "taxpayer:'", "openingBid:", "minimumBid:"]:
    if forbidden in chunk:
        raise SystemExit(f"Unsupported property-level field found in Hamilton County row: {forbidden}")

print("Hamilton County Indiana market validation passed")
