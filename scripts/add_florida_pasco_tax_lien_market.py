#!/usr/bin/env python3
from pathlib import Path

from add_florida_seminole_tax_lien_market import main as add_seminole_market

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Pasco County"

ROW = r'''{state:'Florida — Pasco County',product:'Tax certificate / property-tax lien',schedule:'Florida law requires the annual tax-certificate sale on or before June 1. Pasco County conducts certificate bidding online through LienHub.',availability:'2026 annual sale passed — monitor the official Pasco County Tax Collector certificate inquiry and county-owned certificate resources for current availability and future sale notices',maxReturn:'18%/yr statutory max',interest:'Reverse auction: Pasco County states certificates are issued to the bidder accepting the lowest interest rate. Bids may range from 18% down to 0% in 1/4% increments. If a redeemed certificate earns less than the statutory minimum interest, Florida law provides the applicable minimum-redemption-interest treatment except for 0% bids.',bid:'https://www.pascotaxes.com/taxes/tax-information/delinquent-real-estate-taxes/tax-sale-information/',canadian:'Pasco requires bidder registration and U.S. tax-reporting information. Foreign bidders should confirm acceptable taxpayer-identification documentation, funding, and banking eligibility directly with the Tax Collector before participating.',itin:'The Tax Collector states purchasers must provide a Social Security Number or Federal Identification Number for IRS reporting. Foreign bidders should confirm whether an ITIN or other IRS documentation is accepted before bidding.',online:'YES — Pasco County states certificate bidding is conducted online through LienHub.',otc:'County-owned certificate availability is linked by the Tax Collector under delinquent real-estate tax resources; use the current official inquiry/list and verify live certificate status rather than assuming inventory remains available.',deed:'A tax certificate is a lien and does not convey title or a legal interest in the real estate. After the statutory waiting period, an eligible certificate holder may file a separate tax-deed application; any resulting tax-deed property sale is a distinct process.',special:'Pasco explicitly states a tax-certificate sale is not a land sale and does not permit the purchaser to enter the property or harass the owner. Preserve that distinction: do not substitute later tax-deed inventory or tax-deed opening/minimum bids for tax-certificate data.',source:'https://www.pascotaxes.com/taxes/tax-information/delinquent-real-estate-taxes/tax-sale-information/'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Pasco County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Pasco County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Pasco County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Pasco County tax-lien market row")
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
    print("Added Florida Pasco County tax-lien market")


if __name__ == "__main__":
    main()
    # Keep Seminole in the recurring publisher without adding another
    # competing workflow. Seminole remains independently idempotent.
    add_seminole_market()
