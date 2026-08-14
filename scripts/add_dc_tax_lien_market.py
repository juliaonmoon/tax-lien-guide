#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "District of Columbia — OTR"

ROW = r'''{state:'District of Columbia — OTR',product:'Real property tax lien / Certificate of Sale',schedule:'The 2026 annual DC Real Property Tax Lien Sale was postponed from July 15 and is now scheduled to begin <span class="schedule-date">August 19, 2026</span>. OTR also operates an online over-the-counter tax-lien program for liens that were offered but not sold at the annual sale, subject to blackout periods.',availability:'Upcoming — August 19, 2026',interest:'Highest-bidder sale. The certificate represents the tax lien, not immediate ownership; redemption and later foreclosure rights are governed by DC law and the current OTR sale terms.',bid:'https://otr.cfo.dc.gov/page/real-property-tax-lien-sale-and-resources',canadian:'Foreign-bidder eligibility is not stated simply on the public page. Confirm current MyTax.DC registration, business-tax registration, certification and payment requirements with OTR before funding.',itin:'Purchasers must satisfy OTR registration requirements, including the applicable DC business-tax registration process. Confirm the taxpayer-ID documentation required for a foreign individual or entity before registering.',online:'Registration is through MyTax.DC; annual-sale mechanics and payment instructions are published by OTR. OTC tax liens can be viewed and purchased online on eligible business days.',otc:'YES — OTR says eligible liens bid off to the District can be purchased over the counter online Monday–Friday, subject to blackout periods around scheduled sales.',deed:'A Certificate of Sale is not a deed. A purchaser must follow DC redemption and foreclosure-of-right-of-redemption procedures before a tax deed can be obtained.',special:'The 2026 sale date changed: OTR currently states the annual sale is postponed to August 19, 2026. Registration is mandatory and purchasers must make the required deposit before bidding. OTR also restricts participation by bidders with specified tax delinquencies or certain fraud-related convictions.',source:'https://otr.cfo.dc.gov/page/real-property-tax-lien-sale-and-resources'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("District of Columbia row already present")
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
    print("Added District of Columbia tax-lien market")


if __name__ == "__main__":
    main()
