#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Muscatine County"

ROW = r'''{state:'Iowa — Muscatine County',product:'Tax sale certificate / property-tax lien',schedule:'Muscatine County states its 2026 annual tax sale was held online on June 15, 2026. The county advertises delinquent parcels in late May and says the official current parcel listing is available through the county-designated Iowa Tax Auction registration site around June 1 and updated until sale day.',availability:'2026 annual sale cycle passed; verify any adjourned/public-bidder certificate availability with Muscatine County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa Code Chapter 447 provides 2% per month redemption interest on qualifying tax-sale certificates. A certificate is a lien interest; later deed acquisition requires the separate statutory redemption/notice process.',bid:'https://www.muscatinecountyiowa.gov/treasurer/tax_sale/',canadian:'County bidder-registration and tax-identification rules apply. Confirm current eligibility and required documentation with Muscatine County Treasurer and the current auction platform before attempting registration.',itin:'Verify current Muscatine County bidder tax-identification requirements; do not assume an ITIN alone establishes eligibility.',online:'Yes for the annual sale — Muscatine County says the tax sale is an online event. The official current parcel listing is made available through the county-designated auction registration site.',otc:'Any post-sale, public-bidder, adjourned-sale, or certificate-assignment availability must be verified with the Treasurer; do not infer current inventory from prior publications.',deed:'A tax-sale certificate does not transfer ownership. A later tax deed is a separate statutory stage governed by Iowa redemption and notice requirements.',special:'MARKET-LEVEL ONLY. Muscatine County says the official parcel list is maintained through the county-designated auction registration site. Do not fabricate parcel listings, bypass registration, bulk republish owner/taxpayer names, or confuse Sheriff foreclosure sales with the Treasurer tax-sale certificate process.',source:'https://www.muscatinecountyiowa.gov/treasurer/tax_sale/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Muscatine County row already present")
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
    print("Added Iowa Muscatine County tax-lien market")


if __name__ == "__main__":
    main()
