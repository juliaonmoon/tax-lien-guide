#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Clear Creek County"

ROW = r'''{state:'Colorado — Clear Creek County',product:'Tax lien certificate / Certificate of Purchase',schedule:'Clear Creek County’s official Treasurer page schedules the 2026 annual internet Tax Lien Sale for November 6, 2026, covering delinquent 2025 property taxes. The delinquent list is scheduled for newspaper publication October 8, 15 and 22, 2026; auction registration/research opens on or about October 15, and the county says its research list will be available beginning the week of October 15.',availability:'Upcoming — November 6, 2026; current parcel research list expected beginning the week of October 15',maxReturn:'Variable annual statutory rate; 2026 rate pending until the September 1 rate-setting point',interest:'Clear Creek County states that a redeemed Tax Lien Certificate of Purchase pays nine percentage points above the Federal Reserve discount rate as of September 1 of the sale year. The official 2026 page currently marks the 2026 rate TBD. Premium/bonus bids earn no interest and are not returned on redemption.',bid:'https://www.clearcreekcounty.us/548/2026-Tax-Lien-Sale',canadian:'No under current published rules — Clear Creek County states that only bidders with a U.S. Taxpayer ID are allowed to participate. Do not assume a foreign-bidder exception unless the Treasurer publishes one.',itin:'A U.S. Taxpayer ID is required by the county’s published 2026 registration rules; confirm the exact acceptable taxpayer-ID type with the Treasurer before registration.',online:'Yes — one-day internet auction administered by SRI through Zeus Auction on November 6, 2026, with bidding scheduled for 8:00 AM–5:00 PM Mountain time.',otc:'Yes, potentially after the annual sale. The county states that unsold liens are struck off to the County and available for purchase through the Treasurer’s Office after December 1. Current availability must be confirmed with the Treasurer.',deed:'The Certificate of Purchase is only a tax lien and does not convey ownership, possession, use, improvement or access. The county separately documents the later public-auction process for a certificate of option for Treasurer’s Deed; that later deed-stage proceeding must not be presented as the original tax-lien sale.',special:'MARKET-LEVEL ONLY until Clear Creek County publishes the October 2026 delinquent-lien/research list in a form that can be safely and unambiguously ingested. Do not substitute Public Trustee mortgage-foreclosure rows, Treasurer’s Deed auction rows, owner-name data, older-year rates, or fabricated parcel/opening-bid data. The county states initial bidding begins at taxes, interest, advertising and fees due; any amount above that is a non-interest-bearing premium. Do not fabricate parcel inventory, opening/minimum bids, payoff amounts, current availability, property characteristics, redemption/deed outcomes, or bulk owner/taxpayer data.',source:'https://www.clearcreekcounty.us/548/2026-Tax-Lien-Sale'}'''


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
        raise SystemExit("Found Clear Creek County marker but could not locate row start within rows array")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 4)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Clear Creek County marker but could not locate row end within rows array")
    return row_start, min(endings) + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Clear Creek County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Clear Creek County tax-lien market row")
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
    print("Added Colorado Clear Creek County tax-lien market")


if __name__ == "__main__":
    main()
