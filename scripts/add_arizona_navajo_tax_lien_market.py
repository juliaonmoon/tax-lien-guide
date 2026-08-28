#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Navajo County"

ROW = r'''{state:'Arizona — Navajo County',product:'Tax lien / Certificate of Purchase',schedule:'Annual electronic tax-lien sale. Navajo County held the 2026 sale on <span class="schedule-date">February 11, 2026</span> through RealAuction; bidding opened February 3, 2026. County guidance says the sale is usually held on the second Wednesday of February.',availability:'After the annual auction, unsold tax liens become state-held liens and may be purchased over the counter March 1–December 31, subject to current county/RealAuction availability; the Certificate of Purchase books are closed January 1 through the last business day of February.',maxReturn:'16%/yr statutory max',interest:'Auction tax-lien certificates are awarded through the Arizona bid-down process, so the actual certificate rate may be below the statutory 16% annual ceiling. Navajo County states over-the-counter state-held liens are set at 16% annual simple interest, prorated monthly. Verify the specific certificate terms before relying on a rate.',bid:'https://www.navajocountyaz.gov/459/February-Lien-Sale-Instructions',canadian:'Navajo County uses online bidder registration through RealAuction for the February auction. Foreign bidders should confirm current taxpayer-identification, W-8/W-9 and payment requirements with the Treasurer/auction provider before registering or purchasing an over-the-counter lien.',itin:'Do not assume a foreign bidder can substitute documents without county confirmation. Verify the current investor-registration and taxpayer-identification requirements directly with the Treasurer/RealAuction.',online:'YES — Navajo County states its February tax-lien sale is electronic through RealAuction.',otc:'YES — county guidance says unsold liens become state-held liens available over the counter March 1–December 31, subject to parcel-specific current availability; the CP books are closed January 1 through the last business day of February.',deed:'A tax-lien purchase is a Certificate of Purchase and is a lien, not an immediate sale of the property. Navajo County says investors may initiate foreclosure proceedings after three years and that certificate holders seeking a Judgment Deed are responsible for the court process.',special:'Keep Navajo County tax liens distinct from the county\'s separate Back Tax Land/deed program, which can result in a quit claim deed and follows a different auction process. Advertised tax-lien parcels can be removed before sale because taxes are paid or because of bankruptcy, and advertised tax amounts may omit interest, penalties, fees, partial payments, or prior certificates. Market-level only: do not bulk republish owner/taxpayer names or fabricate parcel inventory, opening/minimum bids, current OTC availability, or amounts due. Use only current county/RealAuction publication for parcel-specific availability.',source:'https://www.navajocountyaz.gov/459/February-Lien-Sale-Instructions'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Navajo marker but could not locate row start")
    row_end = text.find("}\n", marker_pos)
    if row_end < 0:
        row_end = text.find("},\n", marker_pos)
        if row_end < 0:
            raise SystemExit("Found Navajo marker but could not locate row end")
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Arizona Navajo County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Arizona Navajo County tax-lien market row")
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
    print("Added Arizona Navajo County tax-lien market")


if __name__ == "__main__":
    main()
