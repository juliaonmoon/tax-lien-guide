#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Graham County"

ROW = r'''{state:'Arizona — Graham County',product:'Tax lien / Certificate of Purchase',schedule:'Annual in-person tax-lien sale is held each February; the 2026 sale was February 25. State-owned liens not sold at auction may be purchased later by assignment.',availability:'2026 annual auction passed — state-owned assignment liens may be available',maxReturn:'16%/yr statutory max',interest:'Graham County states the maximum bid is 16% simple interest per year and the lowest acceptable bid is 0%; the lowest interest-rate bid wins. State-owned liens assigned after the sale carry 16% interest.',bid:'https://www.graham.az.gov/360/Tax-Lien-Information',canadian:'County registration requires a bidder form and taxpayer identification information. A non-U.S. bidder should confirm directly with the Treasurer which foreign taxpayer documentation is accepted before participating.',itin:'The county bidder form requests a Tax Payer ID Number and directs bidders to provide it to the Treasurer by phone rather than through the online form. Foreign bidders should confirm acceptable IRS documentation with the county.',online:'NO — Graham County states bidders must be present; telephone and mail bids are not accepted.',otc:'YES — parcels not sold at the annual sale are assigned to the state and may be purchased later by assignment. Graham County publishes an Active Certificate Report / assignment list.',deed:'A tax-lien purchase is not a deed. Graham County states the lien holder may begin foreclosure of the right to redeem three years after the lien was first offered for sale, subject to Arizona law and court process.',special:'The county separately operates tax-deed sales. This row is only for tax-lien Certificates of Purchase and state-owned lien assignments. Graham County warns that legal issues, bankruptcy, or valuation corrections can affect enforceability or expected interest.',source:'https://www.graham.az.gov/362/Tax-Sale-Lien-Guidelines'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Arizona Graham County row already present")
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
    print("Added Arizona Graham County tax-lien market")


if __name__ == "__main__":
    main()
