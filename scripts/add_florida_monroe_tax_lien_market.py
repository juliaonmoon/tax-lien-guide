#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Monroe County"

ROW = r'''{state:'Florida — Monroe County',product:'Tax certificate / first lien',schedule:'Annual online tax-certificate sale opens in early to mid-May and starts to close on or before June 1. Monroe County directs bidders to its official auction schedule for exact yearly dates.',availability:'2026 annual sale passed — county-held certificates may be available after the sale through Monroe County’s official LienHub process, subject to current inventory and eligibility rules',maxReturn:'18%/yr statutory max',interest:'Reverse auction: bidding begins at 18% and moves downward in 0.25% increments. Each certificate is awarded to the bidder accepting the lowest rate; 0% bids earn no interest.',bid:'https://monroetaxcollector.com/services/tax-certificate-information/',canadian:'NO for the annual auction under the current published rule — Monroe County states it accepts bids only from U.S. persons qualified to complete IRS Form W-9 and provide a valid U.S. TIN.',itin:'A foreign bidder using Form W-8/ITIN does not satisfy Monroe County’s published annual-auction requirement; the county says bidders must qualify as U.S. persons for Form W-9 and provide a valid U.S. TIN.',online:'YES — registration, bidding, certificate awards and ACH funding are handled on the county’s official auction website.',otc:'YES — county-held certificates may be purchased after the tax sale through the official Monroe County/LienHub process, subject to current inventory and eligibility rules.',deed:'A tax certificate is a first lien and does not convey property rights. After the statutory waiting period, an eligible certificate holder may apply for the separate tax-deed process; the Clerk conducts any later property auction.',special:'Monroe County explicitly states that the tax-certificate sale is NOT a sale of real property and does not give the certificate holder a direct means to acquire the property. Preserve tax-certificate-vs-tax-deed terminology, do not treat a certificate as ownership, and do not substitute later tax-deed inventory or deed-sale opening/minimum bids for tax-certificate data. The county also restricts certificate-holder contact intended to encourage or demand payment during the statutory period.',source:'https://monroetaxcollector.com/services/tax-certificate-information/'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Monroe County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Monroe County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Monroe County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Monroe County tax-lien market row")
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
