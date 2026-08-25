#!/usr/bin/env python3
from pathlib import Path

text = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")
marker = "Indiana — Hancock County 2026"

if marker not in text:
    raise SystemExit("Missing Hancock County Indiana market row")

start = text.index(marker)
chunk = text[start:start + 7000]

required = [
    "Tax sale certificate / property-tax lien",
    "September 18, 2026",
    "MARKET-LEVEL SUMMARY ONLY",
    "online through SRI / ZeusAuction",
    "tax deed is not immediate",
    "Do not bulk republish owner/taxpayer names",
    "Sheriff foreclosure",
    "https://www.hancockin.gov/606/Tax-Sale",
]
for phrase in required:
    if phrase not in chunk:
        raise SystemExit(f"Hancock County safety/provenance text missing: {phrase}")

for forbidden in ["owner:'", "taxpayer:'", "openingBid:", "minimumBid:"]:
    if forbidden in chunk:
        raise SystemExit(f"Unsupported property-level field found in Hancock County row: {forbidden}")

print("Hancock County Indiana market validation passed")
