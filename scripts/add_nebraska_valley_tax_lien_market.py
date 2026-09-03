#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Valley County"

ROW = r'''{state:'Nebraska — Valley County',product:'Tax lien / certificate of tax sale',schedule:'Valley County states that its 2026 County Tax Sale was held on <span class="schedule-date">March 2, 2026</span>, and that the county tax sale is held on the first Monday in March at 9:00 A.M. at the County Courthouse. The county also links its public delinquent tax sale list through Nebraska Taxes Online. The 2026 sale has passed; do not present a later sale as confirmed until the Treasurer publishes the current notice/list.',availability:'2026 annual public tax-lien sale passed — no current parcel inventory is asserted here. Use the Valley County Treasurer current Public Tax Sale Information page and current Nebraska Taxes Online delinquent list for any later sale or availability.',maxReturn:'14%/yr current statutory redemption interest',interest:'Neb. Rev. Stat. § 45-104.01 currently sets 14% annual interest for delinquent taxes or special assessments owed to Nebraska political subdivisions, and § 77-1824 applies that statutory rate to redemption from a tax sale. Verify current law and the current county notice before bidding.',bid:'https://valleycountyne.gov/treasurer-office/public-tax-sale-information/',canadian:'The public county page describes a registration form and fee but does not establish a simple foreign-bidder rule. Do not assume Canadian eligibility; confirm current taxpayer-identification, registration, payment, and certificate requirements directly with the Valley County Treasurer.',itin:'The public county page does not establish that an ITIN or foreign-tax form is accepted. Confirm current taxpayer-identification requirements directly with the Valley County Treasurer before relying on an ITIN.',online:'NO for the published county procedure — Valley County describes the sale as held at the County Courthouse. Reconfirm the method for every later sale.',otc:'Do not infer current private-sale, over-the-counter, or county-held certificate inventory from the completed 2026 public sale or the county delinquent list. Confirm any post-sale availability directly with the Treasurer under current Nebraska statutes and county procedures.',deed:'A tax-sale certificate is not immediate ownership or possession. Valley County states that investors purchase delinquent taxes, not the property, and describes a three-year certificate period before foreclosure may be pursued if the certificate is not redeemed. Verify current Nebraska law and obtain appropriate legal advice before relying on any deed or foreclosure path.',special:'This row covers the Valley County Treasurer public delinquent-real-property tax-lien/certificate sale, not a sheriff foreclosure or tax-deed auction. The county states that its delinquent list is published online through Nebraska Taxes Online and warns investors that purchasing a certificate means purchasing delinquent taxes, not the property. Market-level only: do not bulk republish owner/taxpayer names and do not fabricate parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, foreclosure outcomes, or deed outcomes. Official Treasurer page: https://valleycountyne.gov/treasurer-office/public-tax-sale-information/ . Nebraska statute source: https://nebraskalegislature.gov/laws/laws-index/chap45-full.html and the current § 77-1824 text.',source:'https://valleycountyne.gov/treasurer-office/public-tax-sale-information/'}'''


def find_rows_bounds(text: str):
    rows_start = text.find("const rows=[")
    if rows_start < 0:
        raise SystemExit("Could not find rows array")
    rows_end = text.find("\n];", rows_start)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")
    return rows_start, rows_end


def find_row_bounds(text: str):
    rows_start, rows_end = find_rows_bounds(text)
    marker_pos = text.find(MARKER, rows_start, rows_end)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", rows_start, marker_pos + 1)
    if row_start < rows_start:
        raise SystemExit("Found Valley marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Valley marker but could not locate row end")
    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Valley repair outside rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Valley County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Valley County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Valley County tax-lien market")


if __name__ == "__main__":
    main()
