#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Teller County"

ROW = r'''{state:'Colorado — Teller County',product:'Tax lien / Certificate of Purchase',schedule:'MARKET-LEVEL ONLY — Teller County schedules its online 2026 Tax Lien Sale for <span class="schedule-date">Nov 9, 2026</span>. The county says updated 2026 tax-lien sale rules will be posted Oct 1 and the available-parcel list by Oct 8, 2026.',availability:'Upcoming — Nov 9, 2026; parcel list expected Oct 8',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Colorado tax-lien certificate interest is set annually under state law. Teller County has not yet posted its updated 2026 sale rules/rate, so no prior-year rate is carried forward.',bid:'https://www.co.teller.co.us/Treasurers-Office',canadian:'The current Treasurer page does not clearly publish foreign-bidder eligibility. Verify current registration and tax-document requirements with Teller County before funding.',itin:'Not clearly published on the current Treasurer page; verify current taxpayer-identification requirements with the county/GovEase.',online:'YES — Teller County states the Nov 9, 2026 tax-lien sale will be online through GovEase.',otc:'County-held availability is county-specific; verify current inventory directly with the Teller County Treasurer rather than inferring availability.',deed:'A tax-lien Certificate of Purchase is not immediate property ownership. Any later Treasurer\'s Deed process is separate and should not be confused with the annual tax-lien sale.',special:'MARKET-LEVEL ONLY until Teller County publishes its Oct 8, 2026 available-parcel list and updated Oct 1 sale rules. Do not substitute Public Trustee mortgage-foreclosure rows, Treasurer\'s Deed auction rows, owner-name data, or foreclosure/deed opening bids for tax-lien listings.',source:'https://www.co.teller.co.us/Treasurers-Office'}'''


def rows_array_bounds(text: str):
    rows_start = text.find("const rows=[")
    if rows_start < 0:
        raise SystemExit("Could not find rows array")
    rows_end = text.find("\n];", rows_start)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")
    return rows_start, rows_end


def find_row_bounds(text: str, rows_start: int, rows_end: int):
    marker_pos = text.find(MARKER, rows_start, rows_end)
    if marker_pos < 0:
        return None

    row_start = text.rfind("{state:", rows_start, marker_pos + 1)
    if row_start < rows_start:
        raise SystemExit("Found Teller County marker but could not locate row start inside rows array")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Teller County marker but could not locate row end inside rows array")

    row_end = min(endings) + 1
    if row_end > rows_end:
        raise SystemExit("Teller County row repair would escape rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    rows_start, rows_end = rows_array_bounds(text)
    bounds = find_row_bounds(text, rows_start, rows_end)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Teller County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Teller County tax-lien market row")
        return

    before, after = text[:rows_end], text[rows_end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Colorado Teller County tax-lien market")


if __name__ == "__main__":
    main()
