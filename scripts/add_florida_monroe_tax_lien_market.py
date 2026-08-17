#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Monroe County"

ROW = r'''{state:'Florida — Monroe County',product:'Tax certificate / first lien',schedule:'Annual online tax-certificate sale opens in early to mid-May and closes on or before June 1. Monroe County directs bidders to its official auction site for exact yearly dates.',availability:'2026 annual sale passed — county-held certificates may be available through the official county/LienHub process',maxReturn:'18%/yr statutory max',interest:'Reverse auction: bidding begins at 18% and moves downward in 0.25% increments. Each certificate is awarded to the bidder accepting the lowest rate; 0% bids earn no interest.',bid:'https://monroetaxcollector.com/services/tax-certificate-information/',canadian:'NO for the annual auction under the current published rule — Monroe County states it accepts bids only from U.S. persons qualified to complete IRS Form W-9 and provide a valid U.S. TIN.',itin:'A foreign bidder using Form W-8/ITIN does not satisfy Monroe County\'s published annual-auction requirement; the county says bidders must qualify as U.S. persons for Form W-9 and provide a valid U.S. TIN.',online:'YES — registration, bidding, certificate awards and ACH funding are handled on the county\'s official auction website.',otc:'YES — county-held certificates may be purchased after the tax sale through the official online county/LienHub process, subject to current inventory and eligibility rules.',deed:'A tax certificate is a first lien and does not convey property rights. After the statutory waiting period, an eligible certificate holder may apply for the separate tax-deed process; the later property auction is distinct from the certificate sale.',special:'Monroe County explicitly states that the tax-certificate sale is NOT a sale of real property and does not give the certificate holder a direct means to acquire the property. The county also prohibits certificate-holder contact intended to encourage or demand payment during the statutory restricted period.',source:'https://monroetaxcollector.com/services/tax-certificate-information/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Monroe County row already present")
        return

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Florida Monroe County tax-lien market")


if __name__ == "__main__":
    main()
