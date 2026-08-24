#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Cecil County"

ROW = r'''{state:'Maryland — Cecil County',product:'Tax Sale Certificate / property-tax lien',schedule:'Cecil County publishes official tax-sale procedures and conditions for its county tax-sale certificate program. Verify the current annual sale date and any post-sale certificate availability directly with the Office of Finance before acting.',availability:'County tax-sale certificate market. This guide keeps Cecil County at market level because the public sale materials include owner/property details and are not treated here as a clean unrestricted current inventory feed.',maxReturn:'12%/yr county redemption rate',interest:'Cecil County\'s official Tax Sale Procedures and Conditions state that interest payable on monies paid at the time of sale is 1% per month (12% per year) until further notice. Verify certificate-specific expenses and current terms directly with the County.',bid:'https://www.ccgov.org/government/finance/tax-sale',canadian:'County-specific. Cecil County requires bidder registration and a W-9 in its published procedures. Verify current eligibility directly with the Office of Finance; do not assume foreign eligibility.',itin:'Do not assume an ITIN alone satisfies Cecil County bidder requirements. The published procedures require bidder registration and a W-9; verify current taxpayer-ID requirements directly with the County.',online:'Verify current sale format and registration method with Cecil County\'s Office of Finance for the current annual sale.',otc:'Do not assume over-the-counter availability or infer a current purchase amount from a completed annual sale. Verify any post-sale certificate procedure directly with Cecil County.',deed:'The purchaser receives a tax-sale Certificate of Sale/lien interest. Any later action to foreclose the right of redemption and obtain title is a separate legal stage, not an immediate property purchase.',special:'MARKET-LEVEL ONLY. Do not bulk republish owner/taxpayer names from Cecil County sale materials, fabricate a current parcel inventory or opening bids, treat assessment/delinquent balances as bids, or substitute Sheriff/judicial foreclosure or deed-sale data for Cecil County tax-sale certificates.',source:'https://www.ccgov.org/home/showpublisheddocument/55474/638828357781870000'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Cecil County Maryland row already present")
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
    print("Added Cecil County Maryland tax-lien market")


if __name__ == "__main__":
    main()
