#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Dodge County"

ROW = r'''{state:'Nebraska — Dodge County',product:'Tax lien / certificate of tax sale',schedule:'Dodge County Treasurer publishes 2026 TAX SALE INFORMATION stating that the sale was held on <span class="schedule-date">March 2, 2026</span> at 8:30 A.M. in the Dodge County Board Room, 3rd floor of the Dodge County Courthouse, 435 N. Park Ave., Fremont. The Treasurer page also links the 2026 real-property tax-sale list and says the advertising list was published in the Fremont Tribune. The 2026 sale has passed; do not present a later sale as confirmed until the Treasurer publishes the current notice/list.',availability:'2026 public tax sale passed — no current parcel inventory is asserted here. Use the Dodge County Treasurer current tax-sale information and current official delinquent-real-property list for any later sale or availability.',maxReturn:'14%/yr current statutory redemption interest',interest:'Neb. Rev. Stat. § 45-104.01 currently sets 14% annual interest for delinquent taxes or special assessments owed to Nebraska political subdivisions, and § 77-1824 applies the rate specified in § 45-104.01 to redemption from a real-property tax sale. Verify current law and the current county notice before bidding.',bid:'https://dodgecounty.nebraska.gov/treasurer',canadian:'The published county page provides preregistration information but does not establish a simple foreign-bidder rule. Do not assume Canadian eligibility; confirm current taxpayer-identification, registration, payment, and certificate requirements directly with the Dodge County Treasurer.',itin:'The published county page does not establish that an ITIN or foreign-tax form is accepted. Confirm current taxpayer-identification requirements directly with the Dodge County Treasurer before relying on an ITIN.',online:'NO for the published 2026 procedure — Dodge County states that the sale was held in the Dodge County Board Room on the 3rd floor of the courthouse. Reconfirm the method for every later sale.',otc:'Do not infer current private-sale, over-the-counter, or county-held certificate inventory from the completed 2026 public tax sale or the delinquent list. Confirm any post-sale availability directly with the Treasurer under current Nebraska statutes and county procedures.',deed:'A tax-sale certificate is not immediate ownership or possession. Nebraska law provides a redemption process for real property sold for taxes and refers to the purchaser\'s tax-sale certificate before any later tax-deed process. Verify current Nebraska law and obtain appropriate legal advice before relying on any deed or foreclosure path.',special:'This row covers the Dodge County Treasurer delinquent-real-property tax-sale/certificate market, not a sheriff foreclosure or an immediate tax-deed auction. Market-level only: do not bulk republish owner/taxpayer names and do not fabricate parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, foreclosure outcomes, or deed outcomes. Official Treasurer source: https://dodgecounty.nebraska.gov/treasurer . Nebraska statute sources: https://nebraskalegislature.gov/laws/laws-index/chap45-full.html and https://nebraskalegislature.gov/laws/statutes.php?statute=77-1824 .',source:'https://dodgecounty.nebraska.gov/treasurer'}'''


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
        raise SystemExit("Found Dodge marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Dodge marker but could not locate row end")
    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Dodge repair outside rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Dodge County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Dodge County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Dodge County tax-lien market")


if __name__ == "__main__":
    main()
