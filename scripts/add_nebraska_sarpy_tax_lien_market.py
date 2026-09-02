#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Sarpy County"

ROW = r'''{state:'Nebraska — Sarpy County',product:'Tax lien / tax sale certificate',schedule:'Sarpy County held its 2026 public tax sale on <span class="schedule-date">March 2, 2026</span> at the Sarpy County Boardroom. The 2026 annual sale has passed. The Treasurer also states that unpaid 2025 real-property taxes would be offered at a public tax sale on March 1, 2027; verify the current official sale page before relying on that future date.',availability:'2026 annual tax sale passed — do not infer current certificate inventory. Verify the Treasurer\'s current tax-sale page and published delinquent-tax list before planning around any future sale.',maxReturn:'14%/yr statutory redemption interest',interest:'Nebraska Revised Statutes 77-1824 and 77-1917 tie redemption interest on tax-sale certificates to the rate in section 45-104.01; that statute currently sets 14% per year for delinquent taxes or special assessments owed to political subdivisions. Verify current statutes before each sale because law can change.',bid:'https://www.sarpy.gov/981/Tax-Sale-Information',canadian:'Sarpy County publishes registration and tax-sale procedures but does not state a simple foreign-bidder rule on the public sale page. Do not assume Canadian eligibility; confirm identification, taxpayer-information, registration, and payment requirements directly with the Treasurer.',itin:'The public sale page does not establish that an ITIN or foreign-tax form is accepted in place of any required U.S. taxpayer documentation. Confirm directly with the Sarpy County Treasurer before registration.',online:'NO for the 2026 sale — the official county page scheduled the public sale for 9:00 A.M. at the Sarpy County Boardroom, 1210 Golden Gate Dr, Papillion.',otc:'Do not infer over-the-counter or county-held certificate inventory from the annual sale page. Verify any post-sale certificate availability directly with the Treasurer.',deed:'A tax-sale certificate is a lien, not immediate ownership or possession. Sarpy County states that a public tax sale results in a tax lien being placed on the property; Nebraska law provides separate redemption, tax-deed, notice, and foreclosure procedures. Obtain legal advice before any deed or foreclosure action.',special:'This row covers Sarpy County\'s Treasurer public delinquent real-property tax sale, not mortgage/sheriff foreclosure sales or ordinary deed sales. Market-level only: do not bulk republish owner/taxpayer names and do not fabricate parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, or deed outcomes. Official 2026 tax-sale page: https://www.sarpy.gov/981/Tax-Sale-Information . Official real-estate-tax page: https://www.sarpy.gov/366/Real-Estate-Taxes . Nebraska statutes: https://nebraskalegislature.gov/laws/statutes.php?statute=45-104.01 and https://nebraskalegislature.gov/laws/display_html.php?begin_section=77-1801&end_section=77-1863 .',source:'https://www.sarpy.gov/981/Tax-Sale-Information'}'''


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
        raise SystemExit("Found Sarpy marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Sarpy marker but could not locate row end")
    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Sarpy repair outside rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Sarpy County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Sarpy County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Sarpy County tax-lien market")


if __name__ == "__main__":
    main()
