#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Cedar County"

ROW = r'''{state:'Iowa — Cedar County',product:'Tax sale certificate / property-tax lien',schedule:'Cedar County held its 2026 online tax sale on the third Monday in June. The Treasurer publishes qualifying delinquent parcels in the official county publication in late May and directs registered bidders to the county-designated Iowa Tax Auction system for the nightly-updated list.',availability:'2026 annual June sale passed; verify current adjourned/public-bidder certificate availability with Cedar County Treasurer',maxReturn:'2%/month redemption interest',interest:'Cedar County states that 2% interest per month accrues on the outstanding tax-sale amount during redemption. Purchasing at tax sale does not transfer ownership of the property.',bid:'https://cedarcounty.iowa.gov/treasurer/tax_sale/',canadian:'County and auction-platform bidder-registration rules apply. Confirm current identification, payment, and tax-document requirements directly with Cedar County before registering.',itin:'Verify Cedar County and the county-designated Iowa Tax Auction tax-identification requirements; do not assume an ITIN alone establishes eligibility.',online:'Yes for the annual sale — Cedar County states the tax sale is conducted online through the county-designated Iowa Tax Auction system.',otc:'Unsold delinquencies may move to Iowa public-bidder/adjourned-sale procedures. Verify current certificate availability with the Treasurer rather than inferring inventory from delinquent balances or advertisements.',deed:'A tax-sale certificate is a lien interest, not ownership. Cedar County states the investor may begin the separate statutory deed process after one year and nine months if the certificate has not been redeemed, including the required 90-day notice process.',special:'MARKET-LEVEL ONLY. Cedar County publishes qualifying delinquent parcels through its official publication and a bidder-registration auction system; this integration does not bulk republish parcel or owner/taxpayer data. Do not fabricate parcel listings or opening bids, and do not substitute Sheriff mortgage-foreclosure sales for the Treasurer tax-sale certificate market.',source:'https://cedarcounty.iowa.gov/treasurer/tax_sale/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Cedar County row already present")
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
    print("Added Iowa Cedar County tax-lien market")


if __name__ == "__main__":
    main()
