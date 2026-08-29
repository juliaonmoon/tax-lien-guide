#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Elbert County"

ROW = r'''{state:'Colorado — Elbert County',product:'Tax lien / Certificate of Purchase',schedule:'MARKET-LEVEL ONLY — 2026 tax-lien sale scheduled for Nov 17, 2026 (alternate Nov 24 for inclement weather). Elbert County says the delinquent list will be available on its website in early October; do not create parcel rows before a current official list is safely available.',availability:'Upcoming — Nov 17, 2026',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Colorado certificate interest is set under state law. Elbert County’s current 2026 sale page does not publish the final 2026 certificate rate, so no prior-year rate is carried forward. Premium/bonus bids are separate from certificate interest.',bid:'https://www.elbertcounty-co.gov/321/Tax-Lien-Sale',canadian:'Current published registration requires a completed W-9. Foreign-bidder eligibility is not clearly published; verify directly with the Elbert County Treasurer before funding.',itin:'Current published registration requires a W-9; verify current taxpayer-identification eligibility/requirements directly with the Treasurer.',online:'No — Elbert County currently describes a live in-person auction in Kiowa for Nov 17, 2026.',otc:'The current page describes the annual sale and certificate administration but does not clearly publish current county-held/assignment inventory. Verify with the Treasurer.',deed:'A Tax Lien Sale Certificate of Purchase is not immediate property ownership. Elbert County separately publishes Treasurer’s Deed public-auction materials, which are a later and distinct process.',special:'MARKET-LEVEL ONLY until Elbert County posts its current October 2026 delinquent tax-lien list in a form that can be safely ingested. Do not substitute Public Trustee mortgage-foreclosure rows, Treasurer’s Deed auction rows, owner-name data, or deed/foreclosure opening bids for tax-lien listings. Do not fabricate parcel inventory, opening/minimum bids, lien/payoff amounts, current availability, property characteristics, redemption outcomes, deed outcomes, or bulk owner/taxpayer data.',source:'https://www.elbertcounty-co.gov/321/Tax-Lien-Sale'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Elbert County marker but could not locate row start")

    # index.html contains more than one supported row separator style. Always
    # choose the nearest valid terminator so a repair cannot consume a
    # neighboring county row.
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Elbert County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Elbert County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Elbert County tax-lien market row")
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
    print("Added Colorado Elbert County tax-lien market")


if __name__ == "__main__":
    main()
