#!/usr/bin/env python3
from pathlib import Path

text = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
marker = "Indiana — Decatur County 2026"

if marker not in text:
    raise SystemExit("Missing Decatur County Indiana market row")

start = text.index(marker)
chunk = text[start:start + 6000]

required = [
    "Tax sale certificate / property-tax lien",
    "2026 Tax Sale — Second Advertisement",
    "MARKET-LEVEL SUMMARY ONLY",
    "title is not immediate",
    "does not bulk republish owner/taxpayer names",
    "Sheriff/judicial foreclosure sales",
    "https://decaturcounty.in.gov/auditor/",
]
for phrase in required:
    if phrase not in chunk:
        raise SystemExit(f"Decatur County safety/provenance text missing: {phrase}")

for forbidden in ["owner:'", "taxpayer:'", "openingBid:", "minimumBid:"]:
    if forbidden in chunk:
        raise SystemExit(f"Unsupported property-level field found in Decatur County row: {forbidden}")

print("Decatur County Indiana market validation passed")
