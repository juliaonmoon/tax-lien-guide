#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Harford County"

ROW = r'''{state:'Maryland — Harford County',product:'Tax Sale Certificate / property-tax lien',schedule:'Harford County held its 2026 online tax sale on June 3, 2026. Verify the current county notice before participating in any future sale.',availability:'Annual online county tax-lien certificate sale. Harford County also accepts over-the-counter sale/assignment of eligible tax liens after the annual tax-sale process; verify current inventory and assignment requirements directly with the County.',maxReturn:'10%/yr county redemption rate',interest:'Harford County Resolution No. 040-25 sets the redemption rate at 10% per year for properties sold at tax sale on or after May 1, 2026. The 2026 Terms of Sale likewise state a 10% annual rate.',bid:'https://www.harfordcountymd.gov/3350/Tax-sale',canadian:'County-specific. Harford County requires online bidder registration and tax-sale compliance. Do not assume Canadian or other foreign eligibility; verify current taxpayer-identification, entity, payment, and registration requirements directly with the County before participating.',itin:'Do not assume an ITIN alone satisfies Harford County bidder eligibility. Verify current tax-ID and registration requirements directly with Harford County before attempting to bid or take an assignment.',online:'YES — Harford County conducted the 2026 tax sale as an online public auction.',otc:'YES — Harford County states that it accepts over-the-counter sale/assignment of eligible tax liens after the annual tax-sale process; current inventory and procedures must be verified with the County.',deed:'The purchaser receives a tax-sale certificate/lien, not immediate ownership. The owner retains a statutory right of redemption; any later complaint to foreclose that right is a separate legal stage.',special:'MARKET-LEVEL ONLY. Harford County conducts a legitimate tax-lien certificate sale and publishes tax-sale results, but this guide does not bulk republish owner/taxpayer names or treat a stale result list as current inventory. Do not fabricate parcel listings or opening bids, treat assessed values as bids, or substitute Sheriff judicial-foreclosure or later deed/title proceedings for the original tax-sale certificate. For the annual auction, bidding begins at the officially determined taxes and other charges due; verify the live county auction for the actual amount.',source:'https://www.harfordcountymd.gov/3350/Tax-sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Harford County Maryland row already present")
        return

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before = text[:end]
    after = text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Harford County Maryland tax-lien market")


if __name__ == "__main__":
    main()
