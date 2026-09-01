#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Routt County"

ROW = r'''{state:'Colorado — Routt County',product:'Tax lien certificate',schedule:'Routt County’s official Treasurer page schedules the 2026 online Tax Lien Sale for October 30, 2026. Registration opens October 2, 2026 and closes October 29, 2026. The county says the complete lien list will be published in September.',availability:'Upcoming — October 30, 2026; official delinquent-lien list expected in September',maxReturn:'Variable annual statutory rate; 2026 rate pending until September 1',interest:'Routt County states that Colorado sets the annual certificate redemption rate at nine percentage points above the federal discount rate as of September 1 of that year. Premium bids do not earn interest. Do not carry an older year’s rate into 2026 before the current rate is officially set.',bid:'https://www.co.routt.co.us/1004/Tax-Lien-Sale',canadian:'The county’s public registration instructions require a completed IRS W-9 and ACH bank information. Because W-9 is for U.S. persons, foreign-bidder eligibility is not established by the current public instructions; confirm directly with the Treasurer before funding.',itin:'Current public instructions specify IRS Form W-9; they do not clearly publish a foreign-bidder/W-8 pathway. Verify eligibility and taxpayer-ID requirements directly with Routt County.',online:'Yes — Routt County states the October 30, 2026 tax-lien sale will be online through the county’s official auction provider.',otc:'The current official page describes assignments between certificate holders, but does not clearly publish a standing county-held/OTC lien inventory for 2026. Do not assume unsold liens are available without Treasurer confirmation.',deed:'A Tax Lien Sale Certificate of Purchase is only a lien and does not transfer ownership or possession. Routt County separately documents the later Treasurer’s Deed / Certificate of Option public-auction process under current Colorado law.',special:'MARKET-LEVEL ONLY until Routt County publishes its September 2026 delinquent-lien list in a form that can be safely and unambiguously ingested. Do not substitute Public Trustee mortgage-foreclosure rows, Treasurer’s Deed auction rows, owner-name data, older-year lien lists/rates, or fabricated parcel/opening-bid data.',source:'https://www.co.routt.co.us/1004/Tax-Lien-Sale'}'''


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
        raise SystemExit("Found Routt County marker but could not locate row start inside rows array")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + len("\n];"))
        if pos >= 0 and pos <= rows_end:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Routt County marker but could not locate row end inside rows array")
    row_end = min(endings) + 1
    if row_end > rows_end:
        raise SystemExit("Routt County row repair would escape rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    rows_start, rows_end = rows_array_bounds(text)
    bounds = find_row_bounds(text, rows_start, rows_end)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Routt County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Routt County tax-lien market row")
        return

    before, after = text[:rows_end], text[rows_end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Colorado Routt County tax-lien market")


if __name__ == "__main__":
    main()
