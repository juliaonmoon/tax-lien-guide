#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nebraska — Saunders County"

ROW = r'''{state:'Nebraska — Saunders County',product:'Tax lien / tax sale certificate',schedule:'Saunders County Treasurer published its 2026 County Tax Sale for <span class="schedule-date">March 2, 2026</span>. The county states that the tax sale is held the first Monday in March each year at 9:00 a.m. at the County Courthouse. The 2026 sale has passed; verify every later date and notice directly with the Treasurer before relying on it.',availability:'2026 public sale passed — no current parcel inventory is asserted here. Saunders County states that after the public sale closes, remaining delinquent taxes are offered under Private Tax Sale; verify current availability and procedure directly with the Treasurer/current official list.',maxReturn:'14%/yr stated certificate interest',interest:'The Saunders County Treasurer FAQ states the tax-sale certificate interest rate is 14%. Nebraska law governs redemption and certificate procedures; verify current county guidance and current statutes before relying on any return.',bid:'https://saunderscounty.ne.gov/treasurer-office/public-tax-sale-information/',canadian:'The published county materials require registration and payment arrangements but do not establish a simple foreign-bidder rule. Do not assume Canadian eligibility; confirm identification, taxpayer-information, registration, payment, and certificate requirements directly with the Saunders County Treasurer.',itin:'The official public tax-sale page links a W-9 form but does not establish that an ITIN or foreign-tax form is accepted. Confirm current taxpayer-identification requirements directly with the Saunders County Treasurer before relying on an ITIN.',online:'NO for the published procedure — Saunders County describes an in-person sale at the County Courthouse, with bidder order determined by number drawing and one choice per bidder per round. The delinquent list is published online, but that is not an online auction claim.',otc:'Saunders County states that after the public sale closes, delinquent taxes are offered under Private Tax Sale. This is not a claim that any particular parcel or certificate is currently available; verify current inventory and purchase procedure directly with the Treasurer/current official list.',deed:'A tax-sale certificate is not immediate ownership or possession. The Treasurer expressly states that certificate purchasers are purchasing delinquent taxes, not the property, and that later foreclosure steps arise only after the certificate matures and redemption has not occurred. Verify current Nebraska law and obtain legal advice before relying on any foreclosure or deed outcome.',special:'This row covers the Saunders County Treasurer delinquent-real-property tax-lien/certificate process, not an immediate tax-deed or sheriff-foreclosure auction. The official 2026 page publishes the March 2, 2026 sale date, delinquent-list link, registration fee, in-person rotation procedure, payment requirements, three-year redemption period, and 14% interest statement. Market-level only: do not bulk republish owner/taxpayer names and do not fabricate parcel inventory, opening/minimum bids, amounts due, property characteristics, bidder eligibility, redemption outcomes, foreclosure outcomes, or deed outcomes. Official Public Tax Sale Information page: https://saunderscounty.ne.gov/treasurer-office/public-tax-sale-information/ .',source:'https://saunderscounty.ne.gov/treasurer-office/public-tax-sale-information/'}'''


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
        raise SystemExit("Found Saunders marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Saunders marker but could not locate row end")
    row_end = min(endings) + 1
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Saunders repair outside rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Nebraska Saunders County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Nebraska Saunders County tax-lien market row")
        return
    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Nebraska Saunders County tax-lien market")


if __name__ == "__main__":
    main()
