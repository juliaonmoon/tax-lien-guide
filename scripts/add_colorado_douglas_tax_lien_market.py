#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Douglas County"

ROW = r'''{state:'Colorado — Douglas County',product:'Tax lien / tax sale certificate',schedule:'Douglas County maintains official Treasurer tax-lien records. As of Aug 29, 2026, the reviewed official public material does not publish a clearly accessible 2026 annual tax-lien sale date or current-year parcel list, so the guide keeps the 2026 annual sale pending rather than inferring it from historical records. Separately published 2026 Treasurer’s Deed / Certificate of Option auction notices are later-stage deed-process auctions and are not annual tax-lien sale dates.',availability:'2026 annual tax-lien sale date/list pending official publication; verify any certificate or assignment availability directly from current Treasurer records',maxReturn:'2026 rate not yet published; Colorado annual tax-lien redemption rate is determined from the September 1 statutory benchmark',interest:'Douglas County has not yet published the 2026 annual tax-lien redemption rate in the reviewed official material, so this guide does not carry forward a prior-year rate.',bid:'https://www.douglas.co.us/treasurer/',canadian:'The reviewed current Douglas County public material does not clearly establish a non-U.S.-person/W-8 bidder pathway. Verify current registration and taxpayer-ID requirements directly with the Treasurer before funding.',itin:'Current public Douglas County material reviewed does not clearly state whether an ITIN/W-8 is accepted for a non-U.S. bidder; verify with the Treasurer.',online:'Do not infer the 2026 annual-sale format from historical auction instructions. Verify the current-year format only from official Treasurer sale instructions when published.',otc:'County-held or assignment availability must be verified from current Douglas County Treasurer records; do not infer present availability from historical Certificates of Purchase or later deed-auction notices.',deed:'A tax-sale certificate/tax lien is not immediate property ownership. Douglas County separately publishes Treasurer’s Deed / Certificate of Option public-auction notices after the statutory lien/redemption process; those auctions are distinct from the annual tax-lien sale.',special:'MARKET-LEVEL ONLY. Keep Douglas County tax-sale Certificates of Purchase separate from Public Trustee mortgage foreclosures and later Treasurer’s Deed / Certificate of Option auctions. Historical Douglas County tax-lien instructions state that the minimum starting bid equals delinquent tax, interest, advertising, and fees shown for that sale, but no current 2026 parcel-level opening/minimum bids or annual parcel list are inferred from those older instructions. Do not fabricate parcel inventory, opening/minimum bids, lien/payoff amounts, current availability, property or ownership characteristics, redemption/deed outcomes, or bulk owner/taxpayer data.',source:'https://www.douglas.co.us/file-category/treasurer-documents/'}'''


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
    if row_start < 0:
        raise SystemExit("Found Douglas County marker but could not locate row start inside rows array")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + len("\n];"))
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Douglas County marker but could not locate row end inside rows array")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Douglas County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Douglas County tax-lien market row")
        return

    _, end = rows_array_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Colorado Douglas County tax-lien market")


if __name__ == "__main__":
    main()
