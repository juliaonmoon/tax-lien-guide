#!/usr/bin/env python3
from pathlib import Path

text = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
marker = "Indiana — Monroe County 2026"

if marker not in text:
    raise SystemExit("Missing Monroe County Indiana market row")

start = text.index(marker)
chunk = text[start:start + 5000]

required = [
    "Tax sale certificate / property-tax lien",
    "October 7, 2026",
    "ZeusAuction",
    "MARKET-LEVEL SUMMARY ONLY",
    "does not offer certificates for properties not sold",
    "tax title deed",
    "Do not bulk republish owner/taxpayer names",
]
for phrase in required:
    if phrase not in chunk:
        raise SystemExit(f"Monroe County safety/provenance text missing: {phrase}")

for forbidden in ["owner:'", "taxpayer:'", "openingBid:", "minimumBid:"]:
    if forbidden in chunk:
        raise SystemExit(f"Unsupported property-level field found in Monroe County row: {forbidden}")

print("Monroe County Indiana market validation passed")
