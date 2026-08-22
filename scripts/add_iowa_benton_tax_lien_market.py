#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Benton County"

ROW = r'''{state:'Iowa — Benton County',product:'Tax sale certificate / property-tax lien',schedule:'Benton County holds its annual public tax sale online on the third Monday in June. The county states its current 2026 publication list was posted May 26, 2026; the annual 2026 sale cycle has passed, so verify any adjourned/public-bidder availability directly with the Treasurer.',availability:'2026 annual sale passed; verify current adjourned/public-bidder certificate availability with Benton County Treasurer',maxReturn:'2%/month redemption interest',interest:'Benton County states that a tax-sale purchaser earns 2% interest per month during redemption, subject to Iowa law. The tax-sale purchase does not transfer ownership; deed proceedings can begin only after the separate statutory waiting, notice, and redemption process.',bid:'https://www.bentoncountyia.gov/treasurer/tax_sales/',canadian:'County and auction-platform bidder-registration rules apply. Confirm current eligibility, identification, payment, and tax-document requirements before registering.',itin:'Verify Benton County and Iowa Tax Auction bidder tax-identification requirements; do not assume an ITIN alone establishes eligibility.',online:'Yes — Benton County says the annual tax sale is conducted online through the county-designated Iowa tax auction platform.',otc:'Unsold delinquencies may later enter Iowa public-bidder or adjourned-sale processes. Verify live availability with Benton County Treasurer; do not infer inventory from delinquent balances or the May publication.',deed:'The tax-sale certificate is a lien interest, not ownership. Benton County states deed proceedings may begin after the statutory one-year-nine-month period and required notice/redemption steps.',special:'MARKET-LEVEL ONLY. Benton County publishes a current 2026 tax-sale list, but this integration does not bulk republish that parcel list or owner/taxpayer names. Do not fabricate parcel listings or opening bids, and do not substitute Benton County Sheriff mortgage-foreclosure sales for the Treasurer tax-sale certificate market.',source:'https://www.bentoncountyia.gov/treasurer/tax_sales/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Benton County row already present")
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
    print("Added Iowa Benton County tax-lien market")


if __name__ == "__main__":
    main()
