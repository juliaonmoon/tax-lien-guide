#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Polk County"

ROW = r'''{state:'Florida — Polk County',product:'Tax certificate / property-tax lien',schedule:'Polk County holds its annual tax-certificate sale on or before June 1. The 2026 annual sale has passed; remaining county-held certificates may be purchased through the county\'s official online tax-certificate system while inventory is available.',availability:'2026 annual sale passed — county-held certificates may be available',maxReturn:'18%/yr statutory max',interest:'Reverse auction: certificate interest ranges from 0% to 18%, and the certificate is awarded to the bidder accepting the lowest rate. Unsold certificates are struck off to Polk County; remaining county-held certificates may later be purchased at 18% interest on a first-come-first-served basis.',bid:'https://www.polktaxes.com/services/delinquency-and-tax-sale-information/',canadian:'Polk County requires preregistration for the annual certificate auction. Foreign-bidder eligibility and required tax documentation should be confirmed with the Tax Collector and auction platform before funding an account.',itin:'Verify the current taxpayer-identification and IRS-document requirements with the Polk County Tax Collector / official auction platform before bidding.',online:'YES — Polk County directs bidders to its official online tax-certificate sale website.',otc:'YES — after the regular sale, remaining county-held certificates may be purchased online on a first-come-first-served basis, subject to current inventory.',deed:'A tax certificate is a lien, not ownership. After at least two years from April 1 of the certificate year, an eligible certificate holder may apply for a separate tax-deed process; the Clerk conducts the eventual property auction.',special:'Polk County explicitly distinguishes the tax-certificate lien from the later tax-deed sale. A certificate can be held for a minimum of two years and generally no more than seven years before the holder must act under the applicable rules. Research title and parcel conditions independently before bidding.',source:'https://www.polktaxes.com/services/delinquency-and-tax-sale-information/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Polk County row already present")
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
    print("Added Florida Polk County tax-lien market")


if __name__ == "__main__":
    main()
