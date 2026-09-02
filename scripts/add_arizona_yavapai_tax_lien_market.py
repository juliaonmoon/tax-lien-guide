#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Yavapai County"

ROW = r'''{state:'Arizona — Yavapai County',product:'Tax lien / Certificate of Purchase',schedule:'Yavapai County held its 2026 online tax-lien auction on <span class="schedule-date">February 10, 2026</span>. The County currently lists the next annual auction for <span class="schedule-date">February 9, 2027</span>. Use the current official Treasurer publication and auction site for the exact sale terms and parcel list.',availability:'2026 annual sale passed — next auction Feb 9, 2027. Do not infer current over-the-counter inventory; verify any certificate availability directly through the official Treasurer/auction publication.',maxReturn:'16%/yr statutory max',interest:'Arizona tax-lien bidding awards the lien to the bidder accepting the lowest interest rate; the statutory ceiling is 16% simple interest per year, so the actual certificate rate may be lower.',bid:'https://www.yavapaiaz.gov/Mapping-and-Properties/Property-Taxes/Treasurers-Office/Treasurers-Tax-Lien-Sale',canadian:'Foreign-bidder eligibility is not stated as a simple rule on the public county page. Confirm current registration, federal-tax-ID and payment requirements with the Yavapai County Treasurer before participating.',itin:'Yavapai bidder tools use federal taxpayer-identification information. Confirm the accepted documentation for a foreign individual or entity with the Treasurer before registering.',online:'YES — Yavapai County states that its annual tax-lien auction is online through its official auction site.',otc:'Do not assume current over-the-counter inventory. Verify any available certificate directly from the official Treasurer or auction publication before relying on it.',deed:'A Certificate of Purchase is a tax lien, not immediate property ownership, possession, or a right to enter/contact the property owner. Any later foreclosure/deed process is legally distinct and subject to Arizona statutory requirements.',special:'Important distinction: Yavapai County separately sells tax-deeded real property through the Board of Supervisors. This row covers the Treasurer tax-lien sale only, not the tax-deed program. Market-level only: do not bulk republish owner/taxpayer names or fabricate parcel inventory, opening/minimum bids, amounts due, current certificate availability, property characteristics, or foreclosure outcomes.',source:'https://www.yavapaiaz.gov/Mapping-and-Properties/Property-Taxes/Treasurers-Office/Treasurers-Tax-Lien-Sale'}'''


def find_row_bounds(text: str, start: int, end: int):
    marker_pos = text.find(MARKER, start, end)
    if marker_pos < 0:
        return None

    row_start = text.rfind("{state:", start, marker_pos + 1)
    if row_start < start:
        raise SystemExit("Found Yavapai marker but could not locate row start")

    # index.html contains multiple valid row-separator styles. Choose the
    # nearest valid terminator so repairing one stale row cannot consume later
    # county rows simply because a farther separator style was checked first.
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Yavapai marker but could not locate row end")

    row_end = min(endings) + 1
    if row_start < start or row_end > end:
        raise SystemExit("Refusing Yavapai repair outside rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    bounds = find_row_bounds(text, start, end)
    if bounds:
        row_start, row_end = bounds
        existing = text[row_start:row_end]
        if existing == ROW:
            print("Arizona Yavapai County row already canonical")
            return
        INDEX.write_text(text[:row_start] + ROW + text[row_end:], encoding="utf-8")
        print("Restored canonical Arizona Yavapai County tax-lien market row")
        return

    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Arizona Yavapai County tax-lien market")


if __name__ == "__main__":
    main()
