#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Delaware County"

ROW = r'''{state:'Iowa — Delaware County',product:'Tax sale certificate / property-tax lien',schedule:'Delaware County holds its annual tax sale on the third Monday in June at 8:00 a.m., with an adjourned sale scheduled for the third Monday of each subsequent month. The 2026 annual June sale has passed; verify current adjourned/public-bidder availability with the Treasurer.',availability:'2026 annual sale passed; verify current adjourned/public-bidder certificate availability with Delaware County Treasurer',maxReturn:'2%/month redemption interest',interest:'Delaware County states that redemption from tax sale requires 2% interest per month. The Treasurer conducts annual and adjourned tax sales and issues Certificates of Purchase; the certificate is a lien interest, not immediate property ownership.',bid:'https://delawarecounty.iowa.gov/treasurer/',canadian:'County and auction-registration rules apply. Confirm current bidder eligibility, identification, payment, and tax-document requirements directly with Delaware County Treasurer before registering.',itin:'Verify Delaware County bidder tax-identification requirements; do not assume an ITIN alone establishes eligibility.',online:'County-specific. Delaware County publishes 2026 Tax Sale Terms and Conditions and a Tax Sale Certificate Inquiry; confirm the current auction/registration format with the Treasurer.',otc:'Unsold delinquencies may enter adjourned or public-bidder tax-sale processes under Iowa law. Verify live availability with Delaware County Treasurer; do not infer inventory from delinquent balances or certificate-search results.',deed:'A Certificate of Purchase at Tax Sale is a lien interest, not title. Delaware County separately administers redemption and the later tax-sale-deed process if statutory notice and redemption requirements are satisfied.',special:'MARKET-LEVEL ONLY. Delaware County publishes official tax-sale terms and a public Tax Sale Certificate Inquiry, but this integration does not bulk republish parcel/certificate records or owner/taxpayer names. Do not fabricate parcel listings or opening bids, and do not substitute Delaware County Sheriff mortgage-foreclosure sales for the Treasurer tax-sale certificate market.',source:'https://delawarecounty.iowa.gov/treasurer/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Delaware County row already present")
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
    print("Added Iowa Delaware County tax-lien market")


if __name__ == "__main__":
    main()
