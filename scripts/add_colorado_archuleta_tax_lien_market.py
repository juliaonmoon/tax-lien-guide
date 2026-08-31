#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Archuleta County"

ROW = r'''{state:'Colorado — Archuleta County',product:'Tax lien / Certificate of Purchase',schedule:'MARKET-LEVEL ONLY — Archuleta County officially conducts Treasurer tax-lien sales. As of Aug 28, 2026, the latest official delinquent-tax publication located on the county site is the 2024 publication for the Nov 7, 2024 internet tax-lien sale; no current 2026 sale date or parcel list is inferred from that older publication.',availability:'2026 tax-lien sale date/list not verified on the official county site; verify directly with the Treasurer and current county publication before treating any parcel, date, amount, or availability as current.',maxReturn:'2026 rate not verified; do not carry a prior-year certificate rate forward',interest:'Colorado tax-lien certificate interest is set under state law. Archuleta County administers tax liens and a later separate Treasurer’s Deed process; no prior-year certificate rate is carried forward as a 2026 return.',bid:'https://archuletacounty.org/DocumentCenter/View/4571/DELINQUENT-TAXES-2024-RP-PUBLICATION-LIST-',canadian:'Foreign-bidder eligibility is not clearly published in the current official county materials reviewed; verify registration and taxpayer-ID requirements directly with the Archuleta County Treasurer.',itin:'Current official materials reviewed do not clearly establish ITIN-only or non-U.S.-person eligibility; verify directly with the Treasurer before funding.',online:'The latest official delinquent-tax publication located on the county site used an internet auction for the Nov 7, 2024 sale; do not assume the same format for 2026 unless the county publishes it.',otc:'County-held or assignment availability is not verified for 2026; do not infer current inventory from prior-year materials.',deed:'A tax-lien Certificate of Purchase is a lien, not immediate ownership. Archuleta County separately states that after a lien is 3 years old, the lienholder may apply for a Treasurer’s Deed, subject to the statutory process and redemption.',special:'MARKET-LEVEL ONLY until Archuleta County publishes current 2026 tax-lien material that can be safely verified. Keep the Treasurer tax-lien sale separate from Public Trustee deed-of-trust foreclosure sales and from the later Treasurer’s Deed process. Do not fabricate parcel inventory, opening/minimum bids, lien/payoff amounts, current availability, ownership/property characteristics, redemption outcomes, or deed outcomes, and do not bulk republish owner/taxpayer names.',source:'https://www.archuletacounty.org/301/Treasurer-Deeds'}'''


def find_row_bounds(text: str):
    rows_start = text.find("const rows=[")
    if rows_start < 0:
        raise SystemExit("Could not find rows array")
    rows_end = text.find("\n];", rows_start)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")

    marker_pos = text.find(MARKER, rows_start, rows_end)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", rows_start, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Archuleta County marker but could not locate row start")
    row_end_candidates = [
        pos for terminator in ("},\n", "}\n")
        if (pos := text.find(terminator, marker_pos, rows_end)) >= 0
    ]
    if not row_end_candidates:
        raise SystemExit("Found Archuleta County marker but could not locate row end within rows array")
    row_end = min(row_end_candidates)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Archuleta County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Archuleta County tax-lien market row")
        return

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Colorado Archuleta County tax-lien market")


if __name__ == "__main__":
    main()
