#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Gila County"

ROW = r'''{state:'Arizona — Gila County',product:'Tax lien / Certificate of Purchase',schedule:'Arizona law requires county tax-lien sales to be held in February. In an official September 16, 2025 Gila County Board of Supervisors record, Treasurer Monica Wohlforth stated that remaining unpaid 2024 real-property taxes would be included in her tax lien sale. The next exact Gila County sale date and current advertised parcel list were not located in a stable official public source, so verify the current notice directly with the Treasurer before acting.',availability:'Annual February tax-lien sale confirmed by Arizona statute and Gila County Treasurer; no current parcel availability is asserted here',maxReturn:'16%/yr statutory ceiling',interest:'Arizona law awards a real-property tax lien to the purchaser who pays the full delinquent amount and offers to accept the lowest interest rate; delinquent-tax interest is capped at 16% per year. Actual certificate rates may therefore be lower.',bid:'https://taxes.gilacountyaz.gov/treasurer2/treasurerweb/',canadian:'No simple foreign-bidder eligibility rule was located in the stable official Gila County sources used for this row. Confirm registration, taxpayer-identification, payment, and attendance requirements directly with the Treasurer before participating.',itin:'Not stated as a simple rule in the stable official Gila County sources used here. Confirm acceptable taxpayer-identification documentation directly with the Treasurer.',online:'NOT ASSERTED — do not infer an online auction from the Treasurer tax-payment portal. Confirm the current auction format and venue from the current county sale notice.',otc:'NOT ASSERTED — this row does not claim current over-the-counter inventory without a stable official current list.',deed:'This is a tax-lien / Certificate of Purchase market, not a tax-deed auction. Gila County separately sells some land already deeded to the State under a different statutory process; those tax-deeded land sales must not be conflated with the Treasurer tax-lien sale.',special:'Market-level summary only. Official Gila County records confirm the Treasurer conducts a tax-lien sale, while the Treasurer portal provides parcel-level tax lookup. Do not bulk aggregate owner/taxpayer names. Do not fabricate parcel inventory, sale status, opening/minimum bids, purchase amounts, or availability. Verify any parcel against the Treasurer and current legal notice immediately before bidding.',source:'https://agenda.gilacountyaz.gov/docs/2025/REGULAR/20250916_701/700_09-16-25_1037_AGENDApacket.pdf'}'''


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
        raise SystemExit("Found Gila County marker but could not locate row start inside rows array")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + len("\n];"))
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Gila County marker but could not locate row end inside rows array")

    row_end = min(endings)
    if row_end >= rows_end + len("\n];"):
        raise SystemExit("Refusing Gila County repair outside rows array")
    return row_start, row_end + 1


def add_gila():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        row_start, row_end = bounds
        existing = text[row_start:row_end]
        if existing == ROW:
            print("Arizona Gila County canonical row already present")
            return
        INDEX.write_text(text[:row_start] + ROW + text[row_end:], encoding="utf-8")
        print("Restored canonical Arizona Gila County tax-lien market row")
        return

    _, end = rows_array_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Arizona Gila County tax-lien market")


def main():
    add_gila()


if __name__ == "__main__":
    main()
