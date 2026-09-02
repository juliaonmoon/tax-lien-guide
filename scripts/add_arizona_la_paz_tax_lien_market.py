#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — La Paz County"

ROW = r'''{state:'Arizona — La Paz County',product:'Tax lien / Certificate of Purchase',schedule:'La Paz County Treasurer states that its 2026 tax-lien sale was held Wednesday, February 25, 2026. The Treasurer also states that an over-the-counter list of available parcels was prepared for April 1, 2026. Verify current availability and purchase instructions directly with the Treasurer because parcel status can change.',availability:'2026 annual sale completed February 25; Treasurer announced an over-the-counter list for April 1, 2026 — current availability must be verified with the Treasurer',maxReturn:'16%/yr max',interest:'Arizona tax-lien bidding is to the purchaser who pays the full delinquent amount and accepts the lowest interest rate; under A.R.S. § 42-18114 the accepted rate may not exceed the rate prescribed by § 42-18053 (16% simple per year). The actual certificate rate can therefore be lower.',bid:'https://lapaztreas.com/tax-lien-sale-1',canadian:'The current public La Paz County Treasurer page does not state a simple foreign-bidder eligibility rule. Confirm identification, registration, payment, and tax-document requirements directly with the Treasurer before attempting to participate.',itin:'Not stated as a simple rule on the current public Treasurer page. Confirm acceptable taxpayer-identification documentation directly with the Treasurer.',online:'NO CLAIM — the current official Treasurer page confirms the 2026 sale date and OTC list but does not establish that the county-run sale is online.',otc:'YES — the Treasurer states an over-the-counter list of available parcels was to be ready April 1, 2026. The county charges for the list; this guide does not copy a paid/restricted list or claim that any parcel remains available.',deed:'This is a tax-lien market, not an immediate property sale. A tax-lien purchase does not itself transfer title; any later foreclosure/right-to-redeem process is separate and governed by Arizona law.',special:'Market-level summary only from the current La Paz County Treasurer tax-lien page plus Arizona statutory bidding rules. Do not bulk aggregate owner/taxpayer names. Do not fabricate parcel inventory, opening/minimum bids, purchase amounts, or current availability. The Treasurer currently states the OTC list costs $75, so this guide does not reproduce or bypass that paid list.',source:'https://lapaztreas.com/tax-lien-sale-1'}'''


def rows_array_bounds(text: str):
    rows_start = text.find("const rows=[")
    if rows_start < 0:
        raise SystemExit("Could not find rows array")
    rows_end = text.find("\n];", rows_start)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")
    return rows_start, rows_end


def find_row_bounds(text: str):
    rows_start, rows_end = rows_array_bounds(text)
    marker_pos = text.find(MARKER, rows_start, rows_end)
    if marker_pos < 0:
        return None

    row_start = text.rfind("{state:", rows_start, marker_pos + 1)
    if row_start < rows_start:
        raise SystemExit("Found La Paz County marker but could not locate row start inside rows array")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + len("\n];"))
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found La Paz County marker but could not locate row end inside rows array")

    row_end = min(endings)
    if row_end >= rows_end + len("\n];"):
        raise SystemExit("Refusing La Paz County repair outside rows array")
    return row_start, row_end + 1


def add_la_paz():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        row_start, row_end = bounds
        existing = text[row_start:row_end]
        if existing == ROW:
            print("Arizona La Paz County canonical row already present")
            return
        INDEX.write_text(text[:row_start] + ROW + text[row_end:], encoding="utf-8")
        print("Restored canonical Arizona La Paz County tax-lien market row")
        return

    _, end = rows_array_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Arizona La Paz County tax-lien market")


def main():
    add_la_paz()


if __name__ == "__main__":
    main()
