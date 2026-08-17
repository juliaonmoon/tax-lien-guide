#!/usr/bin/env python3
from pathlib import Path

from add_florida_seminole_tax_lien_market import main as add_seminole_market

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Pasco County"

ROW = r'''{state:'Florida — Pasco County',product:'Tax certificate / property-tax lien',schedule:'Florida law requires the annual tax-certificate sale on or before June 1. Pasco County conducts bidding online through LienHub.',availability:'2026 annual sale passed — monitor the official Tax Collector / LienHub pages for current certificates and future sale notices',maxReturn:'18%/yr statutory max',interest:'Reverse auction: Pasco County states certificates are issued to the bidder accepting the lowest interest rate. Bids may range from 18% down to 0% in 1/4% increments. The County notes the statutory minimum-redemption-interest rule, except for 0% bids.',bid:'https://www.pascotaxes.com/taxes/tax-information/delinquent-real-estate-taxes/tax-sale-information/',canadian:'Pasco requires bidder registration, ACH funding, and U.S. tax-reporting information. Foreign bidders should confirm acceptable taxpayer-identification documentation and banking eligibility directly with the Tax Collector before participating.',itin:'The Tax Collector states purchasers must provide a Social Security Number or Federal Identification Number for IRS reporting. Foreign bidders should confirm whether an ITIN or other IRS documentation is accepted before bidding.',online:'YES — Pasco County states bidding is conducted online through LienHub, with deposits and final payments made by ACH.',otc:'County-owned certificate availability is linked by the Tax Collector under delinquent real-estate tax resources; use the current official inquiry/list rather than assuming inventory remains available.',deed:'A tax certificate is a lien and does not convey title or a legal interest in the real estate. After the statutory waiting period, an eligible certificate holder may file a separate tax-deed application; any later tax-deed sale is a distinct property auction.',special:'Pasco explicitly states a tax-certificate sale is not a land sale and does not permit the purchaser to enter the property or harass the owner. Homestead parcels can also have special tax-deed opening-bid treatment under Florida law.',source:'https://www.pascotaxes.com/taxes/tax-information/delinquent-real-estate-taxes/tax-sale-information/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Pasco County row already present")
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
    print("Added Florida Pasco County tax-lien market")


if __name__ == "__main__":
    main()
    # Keep Seminole in the recurring publisher without adding another
    # competing workflow. This remains idempotent because the Seminole
    # appender checks for its own marker before writing.
    add_seminole_market()
