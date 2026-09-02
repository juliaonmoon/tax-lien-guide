#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Hall County"

ROW = r'''{state:'Nebraska — Hall County',product:'Tax lien / tax sale certificate',schedule:'Hall County held its 2026 public delinquent real-property tax sale on <span class="schedule-date">March 2, 2026</span>. The official Treasurer page now states that all 2024 and prior delinquent taxes were purchased at that sale.',availability:'No remaining delinquent taxes are currently offered for sale according to the Hall County Treasurer\'s official delinquent-tax page. Do not infer current certificate inventory from the archived advertising list.',maxReturn:'14%/yr statutory redemption interest',interest:'Nebraska law governs redemption interest for tax-sale certificates; the applicable statutory rate is currently 14% per year. Verify current Nebraska statutes before relying on the rate because law can change.',bid:'https://files.hallcountyne.gov/departments/treasurer/delinquent_tax_list.php',canadian:'Hall County publishes tax-sale investor instructions, but the public page does not establish a simple foreign-bidder eligibility rule. Do not assume Canadian eligibility; confirm registration, identification, taxpayer-information, and payment requirements directly with the Treasurer.',itin:'The public county page does not establish that an ITIN or foreign-tax form is accepted in place of any required U.S. taxpayer documentation. Confirm directly with the Hall County Treasurer.',online:'The official 2026 notice describes a public sale in Grand Island; do not represent the 2026 sale as an online auction unless the Treasurer publishes that information.',otc:'NO current inventory is published. The Treasurer states there are no remaining delinquent taxes for sale after the March 2, 2026 public tax sale.',deed:'A tax-sale certificate represents a tax lien, not immediate ownership or possession of the property. Nebraska law provides separate redemption, deed, notice, and foreclosure procedures.',special:'This row covers Hall County\'s delinquent real-property tax lien sale, not sheriff/mortgage foreclosure or ordinary deed sales. Market-level only: do not bulk republish owner/taxpayer names from the advertising list and do not fabricate parcel availability, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, or deed outcomes. Official Treasurer delinquent-tax page: https://files.hallcountyne.gov/departments/treasurer/delinquent_tax_list.php . Official 2026 advertising list: https://reports.hallcountyne.gov/Treasurer/Delinquent/advertlist.php . Nebraska statutes: https://nebraskalegislature.gov/laws/display_html.php?begin_section=77-1801&end_section=77-1863 .',source:'https://files.hallcountyne.gov/departments/treasurer/delinquent_tax_list.php'}'''


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
        raise SystemExit("Found Hall marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Hall marker but could not locate row end")
    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Hall repair outside rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Hall County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Hall County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Hall County tax-lien market")


if __name__ == "__main__":
    main()
