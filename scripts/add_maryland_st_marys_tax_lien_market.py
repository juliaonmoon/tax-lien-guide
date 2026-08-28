#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
# index.html stores the JavaScript apostrophe escaped inside the row literal.
# Match that serialized form so repeated workflow runs do not append duplicates.
MARKER = r"Maryland — St. Mary\'s County"

ROW = r'''{state:'Maryland — St. Mary\'s County',product:'Tax Sale Certificate / property-tax lien',schedule:'St. Mary\'s County held its 2026 online tax sale on March 6, 2026 at 10:00 a.m. Eastern time.',availability:'Annual online tax-lien certificate sale. The county also publishes current over-the-counter tax-lien certificates through the County Attorney; verify the official county list because availability changes as liens are purchased, redeemed, or enter foreclosure.',maxReturn:'6%/yr county redemption rate',interest:'St. Mary\'s County states that when a property is redeemed, the certificate holder is reimbursed for taxes paid plus interest at an annual rate of 6% through the month of redemption. This return applies to the certificate, not ownership of the property.',bid:'https://www.stmaryscountymd.gov/Treasurer/TaxSaleAuction/',canadian:'The 2026 county rules state that annual-auction bidder registration is accepted only for U.S. persons or U.S. entities as defined for IRS Form W-9. Do not assume Canadian/foreign eligibility for the annual auction; verify current rules directly with the Treasurer.',itin:'The published 2026 annual-auction rule requires a U.S. person/entity eligible for Form W-9; an ITIN by itself should not be assumed to satisfy bidder eligibility.',online:'YES — the March 6, 2026 annual tax sale was conducted online.',otc:'YES — St. Mary\'s County publishes over-the-counter tax-lien certificates available through the County Attorney. The published OTC list contains owner information, so this guide does not bulk ingest or republish that list.',deed:'Holding a Certificate of Sale does not convey title, possession, or ownership. If the property is not redeemed, the bidder may separately pursue foreclosure of the right of redemption through court procedures.',special:'MARKET-LEVEL ONLY. The official 2026 sale/OTC materials contain taxpayer or property-owner information. This guide does not bulk republish those names, does not convert advertised delinquent balances into fabricated opening bids, and keeps the tax-lien certificate/OTC assignment process distinct from any later foreclosure-of-redemption or deed/title proceeding.',source:'https://www.stmaryscountymd.gov/Treasurer/TaxSaleAuction/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("St. Mary's County Maryland row already present")
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
    print("Added St. Mary's County Maryland tax-lien market")


if __name__ == "__main__":
    main()
