#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Clear Creek County"

ROW = r'''{state:'Colorado — Clear Creek County',product:'Tax lien certificate',schedule:'Clear Creek County’s official Treasurer page schedules the 2026 annual internet Tax Lien Sale for November 6, 2026. Registration/research opens about October 15, 2026; the delinquent-tax list is published in October and the county says the research list will be available on its website beginning the week of October 15.',availability:'Upcoming — November 6, 2026; current parcel list expected in October',maxReturn:'Variable annual statutory rate; 2026 rate pending until September 1',interest:'Clear Creek County states that a redeemed Tax Lien Certificate of Purchase pays nine percentage points above the Federal Reserve discount rate as of September 1 of the sale year. The official 2026 page currently marks the 2026 rate TBD. Premium/bonus bids earn no interest and are not returned on redemption.',bid:'https://www.clearcreekcounty.us/548/2026-Tax-Lien-Sale',canadian:'No under current published rules — Clear Creek County states that only bidders with a U.S. Taxpayer ID are allowed to participate. Do not assume a foreign-bidder exception unless the Treasurer publishes one.',itin:'A U.S. Taxpayer ID is required by the county’s published 2026 registration rules; confirm the exact acceptable taxpayer-ID type with the Treasurer before registration.',online:'Yes — one-day internet auction administered by SRI through Zeus Auction on November 6, 2026.',otc:'Yes, potentially after the annual sale. The county states that unsold liens are struck off to the County and available for purchase through the Treasurer’s Office after December 1. Current availability must be confirmed with the Treasurer.',deed:'The Certificate of Purchase is only a tax lien and does not convey ownership, possession, use, improvement or access. The county separately documents the later public-auction process for a certificate of option for Treasurer’s Deed, generally after the statutory waiting period.',special:'MARKET-LEVEL ONLY until Clear Creek County publishes the October 2026 delinquent-lien list in a form that can be safely and unambiguously ingested. Do not substitute Public Trustee mortgage-foreclosure rows, Treasurer’s Deed auction rows, owner-name data, older-year rates, or fabricated parcel/opening-bid data. The county states initial bidding begins at taxes, interest, advertising and fees due; any amount above that is a non-interest-bearing premium.',source:'https://www.clearcreekcounty.us/548/2026-Tax-Lien-Sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Clear Creek County row already present")
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
