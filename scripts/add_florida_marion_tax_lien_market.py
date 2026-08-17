#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Marion County"

ROW = r'''{state:'Florida — Marion County',product:'Tax certificate / enforceable first lien',schedule:'Marion County conducts its annual tax-certificate sale on or before June 1. The Tax Collector also publishes downloadable tax-sale files and a current unredeemed-certificate data file on its official site.',availability:'2026 annual sale passed — official unredeemed-certificate and county-held purchase tools remain available subject to current inventory',maxReturn:'18%/yr statutory max',interest:'Reverse auction: Marion County states bids begin at 18% and progress downward, with the certificate issued to the lowest interest-rate bidder. Actual return depends on the winning rate and redemption timing.',bid:'https://www.mariontax.com/tax-certificate-deed-sales',canadian:'Marion County describes the tax-certificate sale as open to participants, but foreign-bidder registration, banking and U.S. tax-document requirements should be confirmed directly with the Tax Collector before funding.',itin:'Verify current taxpayer-identification requirements with the Marion County Tax Collector / official sale system; do not assume an ITIN alone guarantees eligibility.',online:'Official Marion County online services include Certificate Tax Sale, management of held certificates, tax-deed application, and purchase of county-held certificates.',otc:'YES — Marion County provides an official online Purchase County Held Certificates service. Inventory is dynamic; use only the current official system/data.',deed:'A tax certificate is an enforceable first lien, not ownership. Tax deed is a separate later process if statutory conditions are met and the certificate remains unredeemed.',special:'Marion County publishes official downloadable tax-sale data and a current Listing of Un-Redeemed Certificates & Supporting Data file. Preserve tax-certificate terminology and do not treat those records as property ownership or tax-deed listings.',source:'https://www.mariontax.com/tax-certificate-deed-sales'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Marion County row already present")
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
    print("Added Florida Marion County tax-lien market")


if __name__ == "__main__":
    main()
