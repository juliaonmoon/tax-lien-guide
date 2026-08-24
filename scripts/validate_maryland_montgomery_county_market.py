#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Montgomery County"
EXPECTED_RATE = "2026 redemption rate: 6%/yr owner-occupied; 20%/yr non-owner-occupied"

text = INDEX.read_text(encoding="utf-8")
start = text.find("{state:'" + MARKER + "'")
if start < 0:
    raise SystemExit("Montgomery County Maryland market row missing")
end = text.find("}\n", start)
if end < 0:
    end = text.find("}]", start)
row = text[start:end + 1]

checks = {
    "market-level safety label": "MARKET-LEVEL ONLY" in row,
    "official 2026 sale date": "June 8, 2026" in row,
    "owner/non-owner rate distinction": EXPECTED_RATE in row,
    "certificate/lien terminology": "Tax Sale Certificate / property-tax lien" in row,
    "official county source": "montgomerycountymd.gov/tax-sale-information-procedures" in row,
    "no immediate ownership claim": "not immediate ownership" in row,
}
for label, ok in checks.items():
    if not ok:
        raise SystemExit(f"Montgomery County validation failed: {label}")

# Fail closed if a later refactor turns this market-level entry into bulk property data.
for forbidden in ("owner_name:", "taxpayer_name:", "parcel_id:", "situs_address:", "opening_bid:"):
    if forbidden in row:
        raise SystemExit(f"Montgomery County row contains prohibited property-level field: {forbidden}")

# The official notice has monetary property data, but this guide must not embed it in the market row.
if re.search(r"\$\s*[0-9]", row):
    raise SystemExit("Montgomery County row contains a property-level dollar amount")

print("Montgomery County Maryland market safety validation passed")
