#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Rio Blanco County"

ROW = r'''{state:'Colorado — Rio Blanco County',product:'Tax lien / Certificate of Purchase',schedule:'MARKET-LEVEL ONLY — Rio Blanco County states its real-property tax-lien sale is held in mid-November each year, the week before Thanksgiving. The county has not yet published an exact 2026 sale date or 2026 parcel list on the current official page, so no parcel rows or exact date are inferred.',availability:'2026 exact sale date/list pending official publication',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Rio Blanco County states the annual certificate rate is set at nine percentage points above the applicable September federal discount rate. The 2026 rate is not yet published, so no prior-year rate is carried forward.',bid:'https://www.rbc.us/301/Tax-Lien-Sale',canadian:'Foreign-bidder eligibility is not clearly published in the current official county materials; verify registration, payment, and taxpayer-ID requirements directly with the Rio Blanco County Treasurer.',itin:'Current public materials do not clearly state foreign taxpayer-ID requirements; verify directly with the Treasurer before funding.',online:'No — the current official page describes the tax-lien sale as an in-office Treasurer auction; verify 2026 procedures before bidding.',otc:'County-held or assignment availability is not clearly stated on the current official page; verify directly with the Treasurer.',deed:'A tax-lien Certificate of Purchase is not ownership. Rio Blanco County states a Treasurer’s Deed may be pursued after the statutory period, and redemption can occur until the deed is issued.',special:'MARKET-LEVEL ONLY until Rio Blanco County publishes current 2026 sale-specific details in a form that can be safely ingested. The county states minimum bidding starts with the published taxes, interest, advertising, assessments, and certificate fees, with premium bidding in $1 increments; premium bid money is not refundable. Do not substitute Public Trustee foreclosures, Sheriff sales, owner-name data, prior-year parcel lists, or Treasurer’s Deed auction values for current tax-lien listings.',source:'https://www.rbc.us/301/Tax-Lien-Sale'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Rio Blanco County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Rio Blanco County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Rio Blanco County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Rio Blanco County tax-lien market row")
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
    print("Added Colorado Rio Blanco County tax-lien market")


if __name__ == "__main__":
    main()
