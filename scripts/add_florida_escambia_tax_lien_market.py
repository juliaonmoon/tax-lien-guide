#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Escambia County"

ROW = r'''{state:'Florida — Escambia County',product:'Tax certificate / first-priority property-tax lien',schedule:'Escambia County is required to hold its annual tax-certificate sale on or before June 1. The county conducts the sale online; unsold certificates become county-held and may later be purchased through the county\'s published process.',availability:'2026 annual sale passed — county-held certificates may be available',maxReturn:'18%/yr statutory max',interest:'Reverse auction: bidding starts at 18% and moves downward. The certificate is awarded to the bidder accepting the lowest interest rate. If there are no bidders, the certificate is issued to Escambia County at 18% annual interest.',bid:'https://escambiataxcollector.com/property-tax/certificate-sale/',canadian:'Escambia requires bidder registration and taxpayer-identification information through the official auction process. Foreign-bidder eligibility and U.S. tax-document requirements should be confirmed directly with the Tax Collector before funding an account.',itin:'Escambia publishes taxpayer-identification requirements for bidder registration; verify whether a W-9 or other IRS documentation applies to your status before bidding.',online:'YES — Escambia County states that its tax-certificate auction is conducted online through its official tax-lien sale site / LienHub process.',otc:'YES — county-held certificates are available for purchase online after the annual sale, subject to current availability and the county\'s published rules.',deed:'A tax certificate is a lien, not ownership. After the statutory waiting period an eligible certificate holder may apply for a separate tax-deed process; Escambia County Clerk conducts tax-deed sales separately.',special:'Escambia expressly warns bidders that they are buying a tax certificate, not the property. Certificates can be bid as low as 0%, and county-held certificates are assigned at the county\'s published terms. Research each parcel before bidding.',source:'https://escambiataxcollector.com/property-tax/certificate-sale/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Escambia County row already present")
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
    print("Added Florida Escambia County tax-lien market")


if __name__ == "__main__":
    main()
