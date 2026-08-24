#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Baltimore County"

ROW = r'''{state:'Maryland — Baltimore County',product:'Tax Sale Certificate / property-tax lien',schedule:'Baltimore County\'s official 2026 tax-sale portal states the Main Sale is August 27, 2026 from 9:00 a.m. to 12:00 p.m.; bidder registration is closed. Verify any later or adjourned activity directly with the County.',availability:'Annual county tax sale. Baltimore County posts properties for the annual tax sale and operates an official tax-sale portal. This guide keeps the market at market level and does not bulk republish owner/taxpayer data or treat a post-sale list as current inventory.',maxReturn:'12%/yr county redemption rate',interest:'Baltimore County Code §11-2-402 provides 12% annual interest for redemption of property sold at tax sale. High-bid premium treatment and certificate-specific terms can affect investor economics, so verify the current County terms.',bid:'https://taxsale.baltimorecountymd.gov/ords/r/obf/tax_sale_ext/tax-sale-closure-public',canadian:'County-specific. Baltimore County requires bidder registration and payment/tax documentation. Verify current eligibility requirements directly with the Office of Budget and Finance; do not assume foreign eligibility.',itin:'Do not assume an ITIN alone satisfies Baltimore County bidder requirements. Verify taxpayer-ID, registration, ACH/payment and documentation requirements directly with the County.',online:'YES — Baltimore County operates an official online tax-sale portal.',otc:'Unsold liens may become Baltimore County-held liens. Do not assume over-the-counter availability or price; verify current county-held certificate procedures directly with the County.',deed:'The successful bidder purchases a tax-sale certificate/lien, not immediate ownership. A later court action to foreclose the right of redemption and obtain title is a separate legal stage and is not treated as a tax-deed listing here.',special:'MARKET-LEVEL ONLY. Baltimore County has a legitimate 2026 tax-certificate sale, but this row does not bulk republish owner/taxpayer names or a stale parcel inventory. Do not fabricate parcel listings or opening bids, treat assessed value or delinquent balance as a bid, or substitute Sheriff/judicial foreclosure or deed-sale data for Baltimore County tax-sale certificates.',source:'https://taxsale.baltimorecountymd.gov/ords/r/obf/tax_sale_ext/tax-sale-closure-public'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Baltimore County Maryland row already present")
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
    print("Added Baltimore County Maryland tax-lien market")


if __name__ == "__main__":
    main()
