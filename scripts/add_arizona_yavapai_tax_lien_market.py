#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Yavapai County"

ROW = r'''{state:'Arizona — Yavapai County',product:'Tax lien / Certificate of Purchase',schedule:'Yavapai County held its 2026 online tax-lien auction on <span class="schedule-date">February 10, 2026</span>. The County currently lists the next annual auction for <span class="schedule-date">February 9, 2027</span>. Verify any current over-the-counter inventory directly on the official tax-sale site.',availability:'2026 annual sale passed — next auction Feb 9, 2027',maxReturn:'16%/yr max',interest:'Arizona tax-lien bidding awards the lien to the bidder accepting the lowest interest rate; the statutory ceiling is 16% simple interest per year, so the actual certificate rate may be lower.',bid:'https://www.yavapaiaz.gov/Mapping-and-Properties/Property-Taxes/Treasurers-Office/Treasurers-Tax-Lien-Sale',canadian:'Foreign-bidder eligibility is not stated as a simple rule on the public county page. Confirm current registration, federal-tax-ID and payment requirements with the Yavapai County Treasurer before participating.',itin:'Yavapai bidder tools use federal taxpayer-identification information. Confirm the accepted documentation for a foreign individual or entity with the Treasurer before registering.',online:'YES — Yavapai County states that its annual tax-lien auction is online through its official auction site.',otc:'The Treasurer has historically offered unsold tax-lien certificates over the counter on a first-come basis. Do not assume 2026 inventory remains available; verify the current official auction portal before purchase.',deed:'A Certificate of Purchase is a lien, not immediate ownership. Foreclosure of the right to redeem is a later judicial process subject to Arizona statutory waiting, notice and court requirements.',special:'Important distinction: Yavapai County separately sells tax-deeded real property through the Board of Supervisors. This row covers the Treasurer tax-lien sale only, not the tax-deed program.',source:'https://www.yavapaiaz.gov/Mapping-and-Properties/Property-Taxes/Treasurers-Office/Treasurers-Tax-Lien-Sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Arizona Yavapai County row already present")
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
    print("Added Arizona Yavapai County tax-lien market")


if __name__ == "__main__":
    main()
