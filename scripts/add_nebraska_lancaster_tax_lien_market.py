#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Lancaster County"

ROW = r'''{state:'Nebraska — Lancaster County',product:'Tax lien / certificate of tax sale',schedule:'Lancaster County held its 2026 Public Delinquent Tax Lien Sale on <span class="schedule-date">March 2, 2026</span> at the Lancaster County Council Chambers. The 2026 annual sale has passed; monitor the official Treasurer publication for the next sale date rather than inferring one.',availability:'The Treasurer\'s current Delinquent Tax Listing page says the current list is for Private Sale and, as currently published, “No parcels available at this time.” Do not fabricate post-sale inventory; recheck the official page before asserting availability.',maxReturn:'14%/yr current statutory redemption interest',interest:'Neb. Rev. Stat. § 45-104.01 currently sets 14% annual interest on delinquent taxes or special assessments owing to Nebraska political subdivisions, and § 77-1824 applies the rate specified in § 45-104.01 to redemption from a real-property tax sale. Verify current law and the current Treasurer publication before relying on the rate.',bid:'https://www.lancaster.ne.gov/444/Tax-Sale-Information',canadian:'The county requires annual bidder registration and publishes tax-sale forms, but its public materials do not establish a simple foreign-bidder rule. Do not assume Canadian eligibility; confirm accepted taxpayer-identification, registration, payment, representation, and certificate requirements directly with the Lancaster County Treasurer.',itin:'The published registration materials include Form W-9 but do not establish that an ITIN or foreign-tax form is accepted as a substitute. Confirm current taxpayer-identification requirements directly with the Lancaster County Treasurer.',online:'NO for the published 2026 procedure — Lancaster County states bidders must be present on the day of sale, with the public sale conducted at the Lancaster County Council Chambers. Reconfirm the method for every later sale.',otc:'Lancaster County currently labels its post-sale delinquent-tax page “Private Sale,” but the same official page presently states “No parcels available at this time.” Do not represent private-sale certificates as available unless the Treasurer publishes current parcel inventory.',deed:'A tax-sale certificate is not immediate ownership or possession. Nebraska law provides a redemption process for real property sold for taxes and refers to the purchaser\'s tax-sale certificate before any later tax-deed process. Verify current Nebraska law and obtain appropriate legal advice before relying on any deed or foreclosure path.',special:'This row covers Lancaster County\'s Treasurer public delinquent tax-lien/certificate sale and any officially published post-sale private-sale availability, not sheriff foreclosure sales or immediate tax-deed auctions. Market-level only: do not bulk republish owner/taxpayer names and do not fabricate parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, foreclosure outcomes, or deed outcomes. Official 2026 sale notice: https://www.lancaster.ne.gov/DocumentCenter/View/640/Tax-Sale-Information-PDF . Official purchasing information: https://www.lancaster.ne.gov/DocumentCenter/View/641/Tax-Sale-Purchasing-Information-PDF . Current private-sale status: https://www.lancaster.ne.gov/396/Delinquent-Tax-Listing . Tax-sale listing procedure: https://www.lancaster.ne.gov/849/Tax-Delinquency-Listing . Nebraska statutes: https://nebraskalegislature.gov/laws/statutes.php?statute=s4501004001 and https://nebraskalegislature.gov/laws/statutes.php?statute=77-1824 .',source:'https://www.lancaster.ne.gov/444/Tax-Sale-Information'}'''


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
        raise SystemExit("Found Lancaster marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Lancaster marker but could not locate row end")

    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Lancaster repair outside rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Lancaster County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Lancaster County tax-lien market row")
        return

    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Lancaster County tax-lien market")


if __name__ == "__main__":
    main()
