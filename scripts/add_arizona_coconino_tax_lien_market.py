#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Coconino County"

ROW = r'''{state:'Arizona — Coconino County',product:'Tax lien / Certificate of Purchase',schedule:'Coconino County held its 2026 online Tax Lien Sale on February 10, 2026. The Treasurer publishes an updated over-the-counter list after the auction; the official Tax Lien Packet states leftover liens are available from March through December. Verify current inventory and amounts directly with the Treasurer before any purchase.',availability:'Official September 2026 over-the-counter list is published by the Coconino County Treasurer; live availability can change as liens are purchased or redeemed',maxReturn:'16%/yr max',interest:'At the annual auction, certificates are awarded to the bidder accepting the lowest interest rate; the official Tax Certificate Process states certificate rates range from 0% to 16%. Unsold certificates become state-held liens bearing 16% and may be purchased over the counter.',bid:'https://www.coconino.az.gov/376/Tax-Liens',canadian:'The Treasurer requires anyone bidding at the annual auction or purchasing over-the-counter liens to register for a Coconino bidder number through the official auction system. The county materials do not state a simple foreign-bidder eligibility rule; confirm registration, tax-documentation, and payment requirements directly with the Treasurer.',itin:'Not stated as a simple rule in the current Coconino County Treasurer materials. Registration records include tax-documentation information; confirm acceptable taxpayer-identification documentation directly with the Treasurer/official auction system.',online:'YES — Coconino County states its official Tax Lien Certificate Auction is conducted over the internet.',otc:'YES — the Treasurer states liens left over after the annual auction are available over the counter from March through December and currently links a downloadable September 2026 list. This guide does not mirror owner/taxpayer names or treat the list as guaranteed live inventory.',deed:'You are not purchasing property. Coconino County explicitly states a Certificate of Purchase is a lien against real property and conveys no property rights. Judicial foreclosure, if legally available later, is a separate process.',special:'Market-level summary only from current official Coconino County Treasurer sources. Do not bulk aggregate owner/taxpayer names. Do not fabricate parcel availability, property characteristics, opening/minimum bids, or purchase amounts. The Treasurer warns purchasers to research the real property and states certificates can be redeemed; verify every parcel and amount in the official county systems.',source:'https://www.coconino.az.gov/376/Tax-Liens'}'''


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
        raise SystemExit("Found Coconino County marker but could not locate row start inside rows array")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + len("\n];"))
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Coconino County marker but could not locate row end inside rows array")

    row_end = min(endings)
    if row_end >= rows_end + len("\n];"):
        raise SystemExit("Refusing Coconino County repair outside rows array")
    return row_start, row_end + 1


def add_coconino():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        row_start, row_end = bounds
        existing = text[row_start:row_end]
        if existing == ROW:
            print("Arizona Coconino County canonical row already present")
            return
        INDEX.write_text(text[:row_start] + ROW + text[row_end:], encoding="utf-8")
        print("Restored canonical Arizona Coconino County tax-lien market row")
        return

    _, end = rows_array_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Arizona Coconino County tax-lien market")


def main():
    add_coconino()


if __name__ == "__main__":
    main()
