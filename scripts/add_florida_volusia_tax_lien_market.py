#!/usr/bin/env python3
from pathlib import Path

from add_florida_manatee_tax_lien_market import main as add_manatee

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Volusia County"

ROW = r'''{state:'Florida — Volusia County',product:'Tax certificate / first-priority property-tax lien',schedule:'Volusia County conducts its annual tax-certificate sale on or before June 1. The 2026 annual sale has passed; certificate information is published through the Tax Collector / LienHub, with current inventory and sale materials subject to the official site.',availability:'2026 annual sale passed — monitor official certificate inventory',maxReturn:'18%/yr statutory max',interest:'Reverse auction: tax certificates are sold to the bidder accepting the lowest interest rate. If there are no bids, the certificate is struck off to Volusia County at 18%, the maximum rate allowed by Florida law.',bid:'https://www.vctaxcollector.org/taxes/tax-certificate-info.html',canadian:'The Tax Collector states that anyone may participate, but registration requires taxpayer-identification information and sale funding through the official auction system. Foreign bidders should confirm acceptable IRS documentation and payment eligibility before funding.',itin:'Volusia requires registered bidders to provide a Federal Taxpayer Identification Number or Social Security Number and reports interest to the IRS. A non-U.S. bidder should confirm acceptable foreign-taxpayer documentation with the Tax Collector / auction platform before bidding.',online:'YES — Volusia County states its tax-certificate sale is conducted online through LienHub.',otc:'County-held / transferred certificates may exist after the sale, but current availability and transfer eligibility must be verified through the Tax Collector / official certificate system; do not assume every struck-off certificate is freely available.',deed:'A tax certificate is a lien, not title. After the statutory waiting period, an eligible certificate holder may submit a separate tax-deed application; the later tax-deed sale is a distinct process.',special:'Volusia explicitly warns that buying a tax certificate does not convey title or a right to enter the property. Certificate holders are also subject to restrictions on contacting owners. Research the parcel, title, environmental and legal risks independently before bidding.',source:'https://www.vctaxcollector.org/taxes/tax-certificate-info.html'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Volusia County row already present")
    else:
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
        print("Added Florida Volusia County tax-lien market")

    # Keep Manatee County in every recurring refresh without adding a second
    # competing data-write workflow.
    add_manatee()


if __name__ == "__main__":
    main()
