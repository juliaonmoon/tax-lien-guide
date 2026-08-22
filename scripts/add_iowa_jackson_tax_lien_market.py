#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Jackson County"

ROW = r'''{state:'Iowa — Jackson County',product:'Tax sale certificate / property-tax lien',schedule:'Jackson County held its 2026 annual tax sale on June 15, 2026. Bidding was online through GovEase, with adjourned tax sales possible on later business days when bidders are present and parcels remain available.',availability:'2026 annual June sale passed; verify current adjourned/public-bidder certificate availability with Jackson County Treasurer',maxReturn:'2%/month redemption interest',interest:'Jackson County states that 2% interest per month accrues on the outstanding tax-sale amount during redemption, for up to three years. Purchasing delinquent taxes does not transfer ownership of the property.',bid:'https://jacksoncounty.iowa.gov/treasurer/tax_sale/',canadian:'2026 terms require bidders to be at least 18 and complete the county/GovEase registration requirements, including a W-9. Do not attempt to bypass age, tax-identification, or registration requirements; confirm current eligibility directly with Jackson County before planning to bid.',itin:'The 2026 terms require an online W-9 and applicable federal tax identification. Do not assume an ITIN or other document substitutes for the county\'s stated requirements.',online:'Yes — Jackson County states the annual tax sale is conducted online through GovEase.',otc:'Unsold delinquencies may proceed to adjourned/public-bidder sale procedures. Verify current certificate availability with the Treasurer rather than inferring inventory from advertisements or delinquent balances.',deed:'A tax-sale certificate is a lien interest, not ownership. Jackson County states that after one year and nine months without redemption, an investor may begin the separate statutory 90-day notice process to seek a tax sale deed.',special:'MARKET-LEVEL ONLY. Jackson County publishes qualifying delinquent parcels in the county\'s official publication and a nightly-updated list through bidder registration. This integration does not bulk republish parcel or owner/taxpayer data. Do not fabricate parcel listings or opening bids, and do not substitute Sheriff mortgage-foreclosure sales for the Treasurer tax-sale certificate market.',source:'https://jacksoncounty.iowa.gov/treasurer/tax_sale/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Jackson County row already present")
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
    print("Added Iowa Jackson County tax-lien market")


if __name__ == "__main__":
    main()
