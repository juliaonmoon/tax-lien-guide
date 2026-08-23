#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Jasper County"

ROW = r'''{state:'Iowa — Jasper County',product:'Tax sale certificate / property-tax lien',schedule:'Jasper County administers its annual tax sale in June under Iowa Code Chapter 446. The 2026 annual June sale has passed; verify any current adjourned/public-bidder availability with the Treasurer.',availability:'2026 annual sale passed; verify current adjourned/public-bidder certificate availability with Jasper County Treasurer',maxReturn:'2%/month redemption interest',interest:'Jasper County states that redemption from tax sale requires 2% interest per month. The annual tax sale is an open competitive process for delinquent property taxes; the purchaser receives a tax-sale certificate/lien interest, not immediate ownership of the property.',bid:'https://www.jasperia.org/treasurer/property_tax/',canadian:'County and auction-registration rules apply. Confirm current bidder eligibility, identification, payment, and tax-document requirements directly with Jasper County Treasurer before registering.',itin:'Verify Jasper County bidder tax-identification requirements; do not assume an ITIN alone establishes eligibility.',online:'Yes for bidder registration through the county-linked Iowa Tax Auction system; confirm the current auction/registration terms with the Treasurer.',otc:'Jasper County may use later statutory tax-sale/public-bidder processes for delinquencies not resolved at the annual sale. Verify current availability with the Treasurer; do not infer inventory from delinquent balances or newspaper notices.',deed:'A tax-sale certificate is a lien interest, not title. Any later tax deed requires the separate Iowa statutory notice, redemption, and deed process.',special:'MARKET-LEVEL ONLY. Jasper County advertises delinquent parcels in the Newton Daily News and makes lists available through the Treasurer, but this integration does not bulk republish parcel records or owner/taxpayer names. Do not fabricate parcel listings or opening bids, and do not substitute Jasper County Sheriff mortgage-foreclosure sales for the Treasurer tax-sale certificate market.',source:'https://www.jasperia.org/treasurer/property_tax/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Jasper County row already present")
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
    print("Added Iowa Jasper County tax-lien market")


if __name__ == "__main__":
    main()
