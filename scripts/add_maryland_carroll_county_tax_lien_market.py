#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Carroll County"

ROW = r'''{state:'Maryland — Carroll County',product:'Tax Sale Certificate / property-tax lien',schedule:'Carroll County\'s official 2026 Tax Sale Notice states online bidding began June 29, 2026 at 8:00 a.m. and ended June 30, 2026 at 12:00 p.m. Verify any later post-sale or certificate activity directly with the County.',availability:'Annual online county tax sale. Carroll County publishes official annual tax-sale notices, terms and results. This guide keeps Carroll at market level and does not bulk republish owner/taxpayer data or treat the completed June sale list as current inventory.',maxReturn:'2026 redemption rate: 10%/yr owner-occupied; 14%/yr non-owner-occupied',interest:'Carroll County\'s official 2026 notice states redemption interest is 10% per annum for owner-occupied property and 14% per annum for non-owner-occupied property. Verify certificate-specific terms and expenses directly with the County.',bid:'https://www.carrollcountymd.gov/government/directory/comptroller/collectionstaxes/',canadian:'County-specific. Carroll County required online registration, ACH payment and taxpayer-identification information for its 2026 sale. Verify current eligibility directly with the Collections Office; do not assume foreign eligibility.',itin:'Do not assume an ITIN alone satisfies Carroll County bidder requirements. Verify current taxpayer-ID, registration and payment-document requirements directly with the County.',online:'YES — Carroll County conducts its annual tax sale online.',otc:'Do not assume over-the-counter availability or a current purchase amount from the completed annual sale. Verify any county-held or post-sale certificate procedure directly with Carroll County.',deed:'The purchaser receives a Certificate of Sale and the owner retains possession while redemption remains open. A later Circuit Court action to foreclose rights of redemption and obtain a deed is a separate legal stage, not an immediate property purchase.',special:'MARKET-LEVEL ONLY. Carroll County publishes legitimate 2026 tax-sale materials, but this row does not bulk republish owner/taxpayer names or a completed-sale parcel list as current inventory. Do not fabricate parcel listings or opening bids, treat assessed value or delinquent balances as bids, or substitute Sheriff/judicial foreclosure or deed-sale data for Carroll County tax-sale certificates.',source:'https://www.carrollcountymd.gov/government/directory/comptroller/collectionstaxes/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Carroll County Maryland row already present")
        return

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before = text[:end]
    after = text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Carroll County Maryland tax-lien market")


if __name__ == "__main__":
    main()
