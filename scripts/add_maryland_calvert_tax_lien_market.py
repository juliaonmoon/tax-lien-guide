#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

ROWS = [
    (
        "Maryland — Calvert County",
        r'''{state:'Maryland — Calvert County',product:'Tax Sale Certificate / property-tax lien',schedule:'Calvert County held its 2026 public tax sale on May 22, 2026 at 10:00 a.m. Verify the current county notice before participating in any future sale.',availability:'Annual county tax-lien certificate sale for qualifying delinquent real-property taxes and certain water/sewer charges. Calvert County currently publishes 2026 tax-sale results with bids, but this guide does not treat past results as current inventory.',maxReturn:'10%/yr county redemption rate',interest:'Calvert County states that when a sold property is redeemed, the certificate holder is reimbursed qualifying taxes and costs plus 10% annual interest. The owner may redeem until final foreclosure.',bid:'https://www.calvertcountymd.gov/taxsale',canadian:'County-specific. Calvert County requires bidder registration and compliance with its current tax-sale procedures. Do not assume Canadian or other foreign eligibility; verify current taxpayer-identification, payment, and registration requirements directly with the County before participating.',itin:'Do not assume an ITIN alone satisfies Calvert County bidder eligibility. Verify current taxpayer-identification and registration requirements directly with the Treasurer before bidding.',online:'NO — the official 2026 notice scheduled an in-person public sale at the County Administration Building. Verify the current format for future sales.',otc:'Not established from the current official source. Do not infer over-the-counter certificate availability from the published 2026 sale results.',deed:'A successful bidder receives a Certificate of Sale, not immediate title or possession. After the statutory redemption period, obtaining title requires a separate court action to foreclose the right of redemption.',special:'MARKET-LEVEL ONLY. Calvert County publishes a legitimate annual tax-lien certificate sale and 2026 results, but this guide does not bulk republish owner/taxpayer names, treat stale sale results as current inventory, or fabricate parcel/opening-bid records. The county states no property may be sold below the qualifying taxes and charges due, but verify the official sale publication/results for any property-specific bid amount. Do not substitute Sheriff judicial-foreclosure, later deed/title proceedings, assessed values, or delinquent balances for a current tax-lien opening bid.',source:'https://www.calvertcountymd.gov/taxsale'}''',
    ),
]


def append_row(text: str, row: str) -> str:
    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")
    before = text[:end]
    after = text[end:]
    insertion = "\n" + row if before.rstrip().endswith(',') else ",\n" + row
    return before + insertion + after


def main():
    text = INDEX.read_text(encoding="utf-8")
    added = []
    for marker, row in ROWS:
        if marker in text:
            continue
        text = append_row(text, row)
        added.append(marker)

    if not added:
        print("Calvert County Maryland row already present")
        return

    INDEX.write_text(text, encoding="utf-8")
    print("Added Maryland tax-lien market: " + ", ".join(added))


if __name__ == "__main__":
    main()
