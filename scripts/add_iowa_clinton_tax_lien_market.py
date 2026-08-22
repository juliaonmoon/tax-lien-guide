#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Clinton County"

ROW = r'''{state:'Iowa — Clinton County',product:'Tax sale certificate / property-tax lien',schedule:'Clinton County states its annual public tax sale is held on the third Monday in June and is conducted online through GovEase. Qualifying delinquent parcels are published in the county\'s official publication during the last week of May; current parcel availability may change as taxes are paid.',availability:'2026 annual sale cycle passed; verify adjourned/public-bidder certificate availability with Clinton County Treasurer',maxReturn:'2%/month redemption interest',interest:'Clinton County states that a winning tax-sale purchaser pays the outstanding taxes and receives a tax-sale certificate rather than ownership. Redemption interest accrues at 2% per month, and a deed is a separate later statutory stage after the applicable redemption and notice process.',bid:'https://clintoncounty-ia.gov/treasurer/tax_sale/',canadian:'County bidder-registration and tax-identification rules apply. Confirm current eligibility and required documentation with Clinton County Treasurer and the current auction platform before attempting registration.',itin:'Verify current Clinton County bidder tax-identification requirements; do not assume an ITIN alone establishes eligibility.',online:'Yes for the annual sale — Clinton County states the auction is held online through GovEase. Registration is required for the current auction listing.',otc:'Unsold delinquencies may enter Iowa public-bidder/adjourned-sale procedures; current Clinton County certificate availability must be verified with the Treasurer rather than inferred.',deed:'A tax-sale certificate does not transfer ownership. Clinton County states a purchaser may only begin the later tax-deed process after the statutory holding period and notice/redemption requirements.',special:'MARKET-LEVEL ONLY. Clinton County says qualifying parcels are published in the official county publication and an updated auction list is available through bidder registration. Do not fabricate parcel listings, bypass registration, bulk republish owner/taxpayer names, or confuse Sheriff foreclosure sales with the Treasurer tax-sale certificate process.',source:'https://clintoncounty-ia.gov/treasurer/tax_sale/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Clinton County row already present")
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
    print("Added Iowa Clinton County tax-lien market")


if __name__ == "__main__":
    main()
