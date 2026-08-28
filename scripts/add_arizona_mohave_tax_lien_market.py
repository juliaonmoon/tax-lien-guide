#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Mohave County"

ROW = r'''{state:'Arizona — Mohave County',product:'Tax lien / Certificate of Purchase',schedule:'Mohave County operates an annual tax-lien sale and accepts assignment requests for state/county-held liens from <span class="schedule-date">April 15–November 30</span> each year. The current Treasurer materials confirm the assignment window and identify parcels available for lien assignment; verify the official Treasurer/auction materials for any specific annual sale date before relying on it.',availability:'State/county-held lien assignments may be requested Apr 15–Nov 30, first come/first served, subject to current county-published availability',maxReturn:'16%/yr max',interest:'Arizona tax-lien certificates are subject to the statutory 16% simple annual ceiling. At auction, the actual certificate rate may be bid down; assignment terms and any specific certificate rate must be verified from official records.',bid:'https://www.mohave.gov/departments/treasurer/tax-liens/tax-lien-sale/',canadian:'Mohave County explicitly provides W-8BEN instructions for people living outside the United States when requesting tax-lien assignments. Confirm current bidder-number, payment and tax-document requirements before participating.',itin:'Foreign assignment applicants are directed to complete W-8BEN rather than assuming a U.S. SSN. Confirm whether any additional taxpayer-identification documentation is required for the annual auction.',online:'Verify the current annual tax-lien auction method from the official Treasurer/auction materials before relying on vendor or format details. Assignment requests use the Treasurer process.',otc:'YES — assignment requests for state/county-held tax liens are accepted April 15 through November 30, first come/first served, subject to current official availability and county review.',deed:'A tax-lien certificate or assignment is a lien, not immediate ownership or a sale of real property. Judicial foreclosure of the right to redeem is a later court process under Arizona law; county guidance also warns that liens expire after the statutory period if foreclosure is not commenced.',special:'Do not confuse Mohave tax liens with the separate Tax Deed Auction/OTC Tax Deed program. The Treasurer tax-lien program sells or assigns liens; the tax-deed program concerns real property already deeded to the State. Market-level only: do not bulk republish owner/taxpayer names, fabricate parcel inventory, opening/minimum bids, current availability, or amounts due. Use only current county-published parcel availability for specific lien assignments.',source:'https://www.mohave.gov/departments/treasurer/tax-liens/assignment-requests-for-state-liens/'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Mohave marker but could not locate row start")
    row_end = text.find("}\n", marker_pos)
    if row_end < 0:
        row_end = text.find("},\n", marker_pos)
        if row_end < 0:
            raise SystemExit("Found Mohave marker but could not locate row end")
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Arizona Mohave County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Arizona Mohave County tax-lien market row")
        return

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before = text[:end]
    after = text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Arizona Mohave County tax-lien market")


if __name__ == "__main__":
    main()
