#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Adams County"

ROW = r'''{state:'Nebraska — Adams County',product:'Tax lien / certificate of tax sale',schedule:'Adams County Treasurer published its 2026 Annual Tax Sale for <span class="schedule-date">March 2, 2026</span> at 10:00 a.m. at the Hastings Public Library, with preregistration due February 20, 2026 and a final website-list edit scheduled for February 27, 2026. That sale has passed. Do not present a later Adams County sale as confirmed until the Treasurer publishes the current notice/list.',availability:'2026 annual public tax-lien/certificate sale passed — no current parcel inventory is asserted here. Use the Adams County Treasurer Tax Sales page and its current official list for any later sale or availability.',maxReturn:'14%/yr current statutory redemption interest',interest:'Neb. Rev. Stat. § 45-104.01 currently sets 14% annual interest on delinquent taxes or special assessments owed to Nebraska political subdivisions, and § 77-1824 applies that rate to redemption from a tax sale. Verify current law and the current county notice before bidding.',bid:'https://adamscountyne.gov/treasurer/57-tax-sales',canadian:'The published 2026 county procedures required preregistration, a registration form, Form W-9, a registration fee, and payment arrangements, but they do not establish a simple foreign-bidder rule. Do not assume Canadian eligibility; confirm current taxpayer-identification, registration, payment, and certificate requirements directly with the Adams County Treasurer.',itin:'The published 2026 procedures require Form W-9 and do not establish that an ITIN or foreign-tax form is accepted. Confirm current taxpayer-identification requirements directly with the Adams County Treasurer before relying on an ITIN.',online:'NO for the published 2026 procedure — Adams County describes an in-person sale at the Hastings Public Library. Registered companies receive bidder numbers by random drawing, then select properties in bidder-number rotation. Reconfirm the method for every later sale.',otc:'Do not infer current private-sale, over-the-counter, or county-held certificate inventory from the completed 2026 annual sale. The Treasurer office states that it handles public and private tax sales, but current availability must be confirmed from the current official Tax Sales page/list.',deed:'A tax-sale certificate is not immediate ownership or possession. Nebraska law provides redemption rights and a later statutory tax-deed/foreclosure process; verify current statutes, required notices, timing, title issues, and county procedures before relying on any deed or foreclosure outcome.',special:'This row covers the Adams County Treasurer delinquent-real-property tax-lien/certificate process, not an immediate tax-deed or sheriff-foreclosure auction. For 2026, the Treasurer published PDF and Excel tax-sale lists, stated that the website list would be updated as properties became unavailable, and used an in-person bidder-number rotation. Market-level only: do not bulk republish owner/taxpayer names and do not fabricate parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, foreclosure outcomes, or deed outcomes. Official Tax Sales page: https://adamscountyne.gov/treasurer/57-tax-sales . Official Treasurer page: https://adamscountyne.gov/treasurer . Nebraska statutes: https://nebraskalegislature.gov/laws/statutes.php?statute=45-104.01 and https://nebraskalegislature.gov/laws/statutes.php?statute=77-1824 .',source:'https://adamscountyne.gov/treasurer/57-tax-sales'}'''


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
        raise SystemExit("Found Adams marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Adams marker but could not locate row end")
    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Adams repair outside rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Adams County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Adams County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Adams County tax-lien market")


if __name__ == "__main__":
    main()
