#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Yuma County"

ROW = r'''{state:'Arizona — Yuma County',product:'Tax lien / Certificate of Purchase',schedule:'Yuma County held its 2026 in-person tax-lien auction on <span class="schedule-date">February 17, 2026</span> for delinquent 2024 real-property taxes. The Treasurer publishes the annual date, bidder forms, and tax-sale booklet on its official tax-lien page.',availability:'2026 annual sale passed — monitor the Treasurer for the next sale and verify any current certificate availability directly with the county; do not infer inventory from a prior-year over-the-counter deadline.',maxReturn:'16%/yr statutory max',interest:'Arizona tax-lien certificates are subject to the state statutory ceiling of 16% simple annual interest; the actual certificate rate depends on the winning bid and may be lower.',bid:'https://www.yumacountyaz.gov/government/treasurer/tax-lien-information',canadian:'Yuma County\'s 2026 bidder materials provide a W-9 and bidder form for the annual sale. Do not assume foreign-bidder eligibility or accepted tax documentation; confirm current requirements directly with the Treasurer before participating.',itin:'The public 2026 sale page specifically provides a W-9 rather than foreign-taxpayer instructions. Do not assume an ITIN/W-8 substitute is accepted without Treasurer confirmation.',online:'NO for the 2026 annual sale — Yuma County states in-person registration and an in-person auction at the Board of Supervisors Auditorium.',otc:'The official 2026 Treasurer calendar says the county stopped accepting 2023 over-the-counter purchases on February 2, 2026. That historical deadline does not prove current inventory; verify any available certificate directly with the Treasurer.',deed:'A tax-lien certificate is not immediate property ownership, possession, or a right to enter/contact the property owner. Yuma County separately administers state tax-deeded property sales through the Board of Supervisors, and the county explicitly states those deed sales are not the Treasurer\'s February tax-lien sale.',special:'Keep the February Treasurer tax-lien auction separate from Yuma County state tax-deeded property auctions. Market-level only: do not bulk republish owner/taxpayer names or fabricate parcel inventory, opening/minimum bids, amounts due, current certificate availability, property characteristics, or foreclosure outcomes. The county warns that tax-sale information may change, so use the current official Treasurer publication for sale-specific facts.',source:'https://www.yumacountyaz.gov/government/treasurer/tax-lien-information'}'''


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
        raise SystemExit("Found Yuma marker but could not locate row start")

    candidates = [
        pos for pos in (
            text.find("},\n", marker_pos, rows_end),
            text.find("}\n", marker_pos, rows_end),
        ) if pos >= 0
    ]
    if candidates:
        row_end = min(candidates) + 1
    elif text.startswith("}", rows_end - 1):
        row_end = rows_end
    else:
        raise SystemExit("Found Yuma marker but could not locate row end")
    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Refusing Yuma repair outside rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Arizona Yuma County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Arizona Yuma County tax-lien market row")
        return

    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Arizona Yuma County tax-lien market")


if __name__ == "__main__":
    main()