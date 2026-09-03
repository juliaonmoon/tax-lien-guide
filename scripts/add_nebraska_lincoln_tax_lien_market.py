#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Lincoln County"

ROW = r'''{state:'Nebraska — Lincoln County',product:'Tax lien / certificate of tax sale',schedule:'Lincoln County states that its Public Tax Lien Sale is held on the first Monday in March at the Lincoln County Courthouse. For 2026 that date was <span class="schedule-date">March 2, 2026</span>; the Treasurer posted a 2026 delinquent-ad list and required bidder preregistration by February 20, 2026. That sale has passed. Do not present a later Lincoln County sale as confirmed until the Treasurer publishes the current notice/list.',availability:'2026 annual public tax-lien sale passed — no current parcel inventory is asserted here. Use the Lincoln County Treasurer\'s current Tax Sale section and current delinquent list for any later sale or availability.',maxReturn:'14%/yr current statutory redemption interest',interest:'Neb. Rev. Stat. § 45-104.01 currently sets 14% annual interest for delinquent taxes or special assessments owed to Nebraska political subdivisions, and § 77-1824 applies that rate to redemption from a tax sale. Verify current law and the current county notice before bidding.',bid:'https://lincolncountyne.gov/treasurer/',canadian:'The public county instructions require preregistration, a registration fee, Form W-9, and payment arrangements, but they do not establish a simple foreign-bidder rule. Do not assume Canadian eligibility; confirm current taxpayer-identification, registration, payment, and certificate requirements directly with the Lincoln County Treasurer.',itin:'The public county instructions require Form W-9 and do not establish that an ITIN or foreign-tax form is accepted. Confirm current taxpayer-identification requirements directly with the Lincoln County Treasurer before relying on an ITIN.',online:'NO for the published 2026 procedure — the Treasurer describes an in-person public tax-lien sale at the Lincoln County Courthouse with bidder-number drawing and assigned seating. Reconfirm the method for every later sale.',otc:'Do not infer current private-sale, over-the-counter, or county-held certificate inventory from the completed 2026 public sale. Confirm any post-sale availability directly with the Treasurer under current Nebraska statutes and county procedures.',deed:'A tax-sale certificate is not immediate ownership or possession. Lincoln County states that a certificate is held for three years before foreclosure may be pursued and warns that statutory foreclosure/deed timelines apply; verify current Nebraska law and obtain appropriate legal advice before relying on any deed or foreclosure path.',special:'This row covers the Lincoln County Treasurer public delinquent-real-property tax-lien/certificate sale, not a sheriff foreclosure or tax-deed auction. The Treasurer states that the delinquent list is published before the sale, that bidders should use the most current list, and that the sale uses a round-robin format. Market-level only: do not bulk republish owner/taxpayer names and do not fabricate parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, foreclosure outcomes, or deed outcomes. Official Treasurer page: https://lincolncountyne.gov/treasurer/ . Nebraska statutes: https://nebraskalegislature.gov/laws/statutes.php?statute=s4501004001 and https://nebraskalegislature.gov/laws/statutes.php?statute=77-1824 .',source:'https://lincolncountyne.gov/treasurer/'}'''


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
        raise SystemExit("Found Lincoln marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Lincoln marker but could not locate row end")
    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Lincoln repair outside rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Lincoln County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Lincoln County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Lincoln County tax-lien market")


if __name__ == "__main__":
    main()
