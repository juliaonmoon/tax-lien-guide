#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Lancaster County"

ROW = r'''{state:'Nebraska — Lancaster County',product:'Tax lien / certificate of tax sale',schedule:'Lancaster County held its 2026 Public Delinquent Tax Lien Sale on <span class="schedule-date">March 2, 2026</span> at the Lancaster County Council Chambers. The 2026 annual sale has passed; monitor the official Treasurer publication for the next sale date rather than inferring one.',availability:'2026 annual tax-lien sale passed — next sale date not yet asserted here. Verify current county publications before planning to bid.',maxReturn:'14%/yr current statutory interest',interest:'Lancaster County\'s current Tax Sale Purchasing Information states that redeemed certificates receive the statutory current interest rate of 14% per year. Verify the current Treasurer publication before each sale because statutory rules can change.',bid:'https://www.lancaster.ne.gov/224/County-Treasurer',canadian:'The county requires annual bidder registration and a W-9 among its tax-sale forms. The public materials do not state a simple foreign-bidder rule, so do not assume Canadian eligibility; confirm accepted taxpayer-identification and payment requirements directly with the Treasurer.',itin:'The published registration packet calls for a W-9. It does not establish that an ITIN or foreign-tax form is accepted as a substitute; confirm directly with the Lancaster County Treasurer.',online:'NO for the 2026 sale — the official notice placed the public delinquent tax-lien sale at the Lancaster County Council Chambers.',otc:'Do not infer over-the-counter or county-held inventory. The public 2026 materials document the annual tax-lien sale; verify any later certificate availability directly with the Treasurer.',deed:'The certificate of tax sale is not immediate ownership or possession. Lancaster County states a certificate is generally held for three years before foreclosure can be pursued, subject to statutory exceptions and notice/deed procedures; obtain legal advice before any foreclosure or deed action.',special:'This row covers Lancaster County\'s Treasurer tax-lien/certificate sale, not sheriff foreclosure sales or other deed sales. Market-level only: do not bulk republish owner/taxpayer names and do not fabricate parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, or deed outcomes. Official 2026 sale notice: https://www.lancaster.ne.gov/DocumentCenter/View/640/Tax-Sale-Information-PDF . Official purchasing information: https://www.lancaster.ne.gov/DocumentCenter/View/641/Tax-Sale-Purchasing-Information-PDF .',source:'https://www.lancaster.ne.gov/224/County-Treasurer'}'''


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
