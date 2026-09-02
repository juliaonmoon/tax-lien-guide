#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Yavapai County"

ROW = r'''{state:'Arizona — Yavapai County',product:'Tax lien / Certificate of Purchase',schedule:'Yavapai County\'s official Treasurer page lists the previous online tax-lien auction as <span class="schedule-date">February 10, 2026</span> and the next auction as <span class="schedule-date">February 9, 2027</span>. Verify the Treasurer page before relying on the future date because schedules can change.',availability:'2026 annual auction passed. The county publishes auction results and an official auction site, but this row does not claim that any specific certificate remains available after the sale; verify current county/auction records before acting.',maxReturn:'Up to 16%/yr bid rate; competitive bidding may reduce the rate to 0%',interest:'Arizona law requires tax-lien sales in February and awards a lien to the bidder paying the delinquent amount who accepts the lowest redemption-interest rate, subject to the statutory maximum. Yavapai\'s official historical results show certificates can sell from 16% down to 0%. Verify current statutes and auction rules before bidding.',bid:'https://www.yavapaiaz.gov/Mapping-and-Properties/Property-Taxes/Treasurers-Office/Treasurers-Tax-Lien-Sale',canadian:'The public Treasurer page does not establish a simple foreign-bidder rule. Do not assume Canadian eligibility; confirm registration, taxpayer-identification, payment, and withholding requirements through the official auction site/Treasurer.',itin:'The public Treasurer page does not establish that an ITIN is sufficient for every bidder. Confirm current taxpayer-identification requirements with the official auction provider and Treasurer before registration.',online:'YES — the official Treasurer page identifies an online tax-lien auction and links to the official auction website.',otc:'Do not infer current over-the-counter inventory from prior-year notices or results. Confirm any post-auction certificate availability directly through the Treasurer/official auction records.',deed:'Purchase of a tax-lien certificate does not convey immediate ownership or possession. Arizona law provides a separate redemption and foreclosure process before a deed may issue. Yavapai also maintains a separate Tax Deed Sales page for properties already deeded to the state.',special:'This row covers Yavapai County Treasurer tax-lien certificates, not the county\'s separate tax-deed sales. Do not bulk aggregate owner/taxpayer names and do not fabricate parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, or deed outcomes. Official Treasurer tax-lien page: https://www.yavapaiaz.gov/Mapping-and-Properties/Property-Taxes/Treasurers-Office/Treasurers-Tax-Lien-Sale . Arizona statutes: https://www.azleg.gov/ars/42/18112.htm , https://www.azleg.gov/ars/42/18114.htm , and https://www.azleg.gov/ars/42/18118.htm .',source:'https://www.yavapaiaz.gov/Mapping-and-Properties/Property-Taxes/Treasurers-Office/Treasurers-Tax-Lien-Sale'}'''


def find_row_bounds(text: str, start: int, end: int):
    marker_pos = text.find(MARKER, start, end)
    if marker_pos < 0:
        return None

    row_start = text.rfind("{state:", start, marker_pos + 1)
    if row_start < start:
        raise SystemExit("Found Yavapai marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Yavapai marker but could not locate row end")

    row_end = min(endings) + 1
    if not (start <= row_start < row_end <= end):
        raise SystemExit("Refusing Yavapai repair outside rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    bounds = find_row_bounds(text, start, end)
    if bounds:
        row_start, row_end = bounds
        existing = text[row_start:row_end]
        if existing == ROW:
            print("Arizona Yavapai County row already canonical")
            return
        INDEX.write_text(text[:row_start] + ROW + text[row_end:], encoding="utf-8")
        print("Restored canonical Arizona Yavapai County tax-lien market row")
        return

    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Arizona Yavapai County tax-lien market")


if __name__ == "__main__":
    main()
