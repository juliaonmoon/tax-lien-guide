#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Carter County"


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit("Carter County market row is missing")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start : end + 2] if end >= 0 else text[start : start + 5000]

    required = [
        "MARKET-LEVEL ONLY",
        "10%/yr statutory delinquent-tax interest",
        "tax lien is not immediate property ownership",
        "do not bulk collect owner/taxpayer names",
        "do not present delinquent balances or later tax-deed values as tax-lien opening/minimum bids",
    ]
    missing = [item for item in required if item not in row]
    if missing:
        raise SystemExit("Carter County safety validation failed: " + ", ".join(missing))

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:", "minimum_bid:"]
    present = [item for item in forbidden if item in row]
    if present:
        raise SystemExit("Carter County market-level row contains forbidden property-level fields: " + ", ".join(present))

    print("Verified Carter County Montana market-level tax-lien safety boundary")


if __name__ == "__main__":
    main()
