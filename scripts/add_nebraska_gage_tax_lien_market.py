#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Gage County"

ROW = r'''{state:'Nebraska — Gage County',product:'Tax lien / certificate of tax sale',schedule:'Gage County Treasurer published its 2026 County Tax Sale for <span class="schedule-date">March 2, 2026</span> at 9:00 a.m. in the District Courtroom on the third floor of the Gage County Courthouse in Beatrice. The 2026 sale has passed. Do not present a later Gage County sale date, time, venue, or parcel list as confirmed until the Treasurer publishes the current notice/list.',availability:'2026 public tax-lien/certificate sale passed — no current parcel inventory is asserted here. The Treasurer publishes the delinquent-tax advertising list and states that parcels remaining unsold after the public sale may move to Private Tax Sale; current availability must be verified from the Treasurer/current official list.',maxReturn:'14%/yr current statutory redemption interest',interest:'The Gage County Treasurer FAQ states a 14% interest rate for tax-sale certificates. Nebraska law governs the certificate/redemption process; verify current law and the current county notice before bidding.',bid:'https://gagecountyne.gov/treasurer-office/public-tax-sale-information/',canadian:'The published 2026 county rules required bidder registration, photo identification, a distinct taxpayer-identification number, Form W-9, registration fee, and payment arrangements, but they do not establish a simple foreign-bidder rule. Do not assume Canadian eligibility; confirm current taxpayer-identification, registration, payment, and certificate requirements directly with the Gage County Treasurer.',itin:'The published 2026 rules require Form W-9 and a Taxpayer Identification Number or Social Security Number, but do not establish that an ITIN or foreign-tax form is accepted. Confirm current taxpayer-identification requirements directly with the Gage County Treasurer before relying on an ITIN.',online:'NO for the published 2026 procedure — Gage County describes an in-person public sale at the courthouse, with bidder order selected by drawing and one choice per bidder per round. Nebraska Taxes Online is used for the public delinquent list, not asserted here as an online auction platform. Reconfirm the method for every later sale.',otc:'The Treasurer states that delinquent taxes remaining unsold after the public sale are offered under Private Tax Sale. This is not a claim that any particular parcel or certificate is currently available; verify current inventory and purchase procedure directly from the Gage County Treasurer/current official list.',deed:'A tax-sale certificate is not immediate ownership or possession. The Treasurer explicitly says certificate purchasers are purchasing delinquent taxes, not the property. Redemption and any later foreclosure/tax-deed process are governed by Nebraska law; verify current statutes, notices, timing, title issues, and county procedures before relying on any deed or foreclosure outcome.',special:'This row covers the Gage County Treasurer delinquent-real-property tax-lien/certificate process, not an immediate tax-deed or sheriff-foreclosure auction. For 2026, the Treasurer published Tax Sale Rules plus official PDF and Excel advertising lists and described an in-person bidder-order rotation. Market-level only: do not bulk republish owner/taxpayer names and do not fabricate parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, foreclosure outcomes, or deed outcomes. Official Public Tax Sale Information page: https://gagecountyne.gov/treasurer-office/public-tax-sale-information/ .',source:'https://gagecountyne.gov/treasurer-office/public-tax-sale-information/'}'''


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
        raise SystemExit("Found Gage marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Gage marker but could not locate row end")
    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Gage repair outside rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Gage County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Gage County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Gage County tax-lien market")


if __name__ == "__main__":
    main()
