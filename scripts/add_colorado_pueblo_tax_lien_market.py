#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Pueblo County"

ROW = r'''{state:'Colorado — Pueblo County',product:'Tax lien / tax certificate',schedule:'Pueblo County operates tax-lien sales through the Treasurer. As of Aug 29, 2026, the current official annual tax-lien page still publishes 2025 sale materials rather than a 2026 annual sale date/property list, so the guide keeps the 2026 annual sale pending official publication. Pueblo also separately publishes county-held lien information and Treasurer’s Deed auction schedules.',availability:'2026 annual sale date/list pending official publication; verify any county-held certificate availability from the current Treasurer source before treating it as available',maxReturn:'2026 rate not yet set; Colorado rate is set after Sep 1',interest:'Colorado sets the annual tax-lien redemption rate using the statutory September 1 benchmark. Pueblo County has not yet published the 2026 rate, so the guide does not carry forward a prior-year rate.',bid:'https://county.pueblo.org/treasurers-department/2025-tax-lien-sale-information',canadian:'The reviewed Pueblo County bidder material does not clearly establish a non-U.S.-person/W-8 pathway. Verify current registration and tax-ID requirements directly with the Treasurer before funding.',itin:'Official Pueblo bidder materials reviewed do not clearly state whether an ITIN/W-8 is accepted for a non-U.S. bidder; verify with the Treasurer.',online:'Annual sale format should be verified from the current-year Treasurer instructions before bidding; do not infer the 2026 format from 2025 materials.',otc:'County-held lien information is published separately by the Treasurer. Treat availability as source-current and conditional rather than assuming every historical county-held lien remains assignable.',deed:'A tax-lien certificate is not property ownership. Pueblo separately administers Treasurer’s Deed / Certificate of Option auctions after the statutory process; those deed auctions are distinct from the annual tax-lien sale.',special:'MARKET-LEVEL ONLY. Use the Treasurer’s annual tax-lien and county-held-lien sources for lien investing, and keep them separate from Pueblo County Public Trustee mortgage foreclosures and the later Treasurer’s Deed auction schedule. The current deed-auction page includes 2026 auction dates, but those are not annual tax-lien sale dates. Do not fabricate parcel inventory, opening/minimum bids, lien/payoff amounts, current availability, property or ownership characteristics, redemption/deed outcomes, or bulk owner/taxpayer data.',source:'https://county.pueblo.org/treasurers-department/county-held-properties'}'''


def rows_array_bounds(text: str):
    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")
    return start, end


def find_row_bounds(text: str, rows_start: int, rows_end: int):
    marker_pos = text.find(MARKER, rows_start, rows_end)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", rows_start, marker_pos + 1)
    if row_start < rows_start:
        raise SystemExit("Found Pueblo County marker but could not locate row start inside rows array")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + len("\n];"))
        if pos >= 0 and pos <= rows_end:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Pueblo County marker but could not locate row end inside rows array")
    row_end = min(endings) + 1
    if row_end > rows_end:
        raise SystemExit("Pueblo County row repair would escape rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    rows_start, rows_end = rows_array_bounds(text)
    bounds = find_row_bounds(text, rows_start, rows_end)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Pueblo County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Pueblo County tax-lien market row")
        return

    before, after = text[:rows_end], text[rows_end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Colorado Pueblo County tax-lien market")


if __name__ == "__main__":
    main()
