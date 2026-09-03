#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Platte County"

ROW = r'''{state:'Nebraska — Platte County',product:'Tax lien / tax sale certificate',schedule:'Platte County reports its March 2026 public tax sale and publishes official tax-sale rules stating that the public tax sale opens on the first Monday in March. In 2026 that date was <span class="schedule-date">March 2, 2026</span>.',availability:'The Treasurer\'s current public Tax Sales report lists 244 properties at first publication, 138 parcels on the day of the March 2026 sale, and 119 certificates sold. Those figures are historical sale results, not current unsold inventory. Confirm any currently available delinquent-tax opportunity directly with the Platte County Treasurer.',maxReturn:'14%/yr statutory redemption interest',interest:'Platte County\'s official tax-sale rules state that a purchaser buys the delinquent taxes, not the property, and that interest on the taxes accrues at the Nebraska statutory rate of 14%. Verify current Nebraska law before relying on the rate because statutes can change.',bid:'https://plattecounty.net/treasurer/',canadian:'Platte County publishes bidder registration materials, but the public Treasurer materials reviewed here do not establish a simple foreign-bidder eligibility rule. Do not assume Canadian eligibility; confirm registration, taxpayer-information, payment, and attendance requirements directly with the Treasurer.',itin:'The Treasurer publishes a W-9 link for tax-sale participants, but the public materials reviewed here do not establish that an ITIN or foreign-tax form is accepted instead. Confirm acceptable taxpayer documentation directly with the Platte County Treasurer.',online:'The public Treasurer materials reviewed here do not identify the March 2026 sale as an online auction. Do not represent it as online unless the Treasurer publishes that information for a specific sale.',otc:'Nebraska law provides for private sale of property remaining unsold after the public auction, but no current Platte County over-the-counter/private-sale inventory is asserted here. Verify current availability directly with the Treasurer.',deed:'A Platte County tax-sale certificate represents a tax lien/certificate interest, not immediate ownership or possession of the property. The county\'s official rules state that the purchaser is buying the taxes and NOT the property; Nebraska law separately governs redemption, notice, tax-deed, and foreclosure procedures.',special:'This row covers Platte County\'s delinquent real-property tax lien/certificate sale, not a sheriff/mortgage foreclosure or ordinary deed sale. Market-level only: do not bulk republish owner/taxpayer names from delinquent-tax materials and do not fabricate parcel availability, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, or deed outcomes. Official Treasurer page and March 2026 sale report: https://plattecounty.net/treasurer/ . Official Platte County public tax-sale rules: https://plattecounty.net/wp-content/uploads/2024/07/Tax-Sale-Information-2024.pdf . Nebraska statutes: https://nebraskalegislature.gov/laws/display_html.php?begin_section=77-1801&end_section=77-1863 .',source:'https://plattecounty.net/treasurer/'}'''


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
        raise SystemExit("Found Platte marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Platte marker but could not locate row end")
    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Platte repair outside rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Platte County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Platte County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Platte County tax-lien market")


if __name__ == "__main__":
    main()
