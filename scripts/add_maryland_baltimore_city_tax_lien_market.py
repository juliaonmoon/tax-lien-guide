#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Baltimore City"

ROW = r'''{state:'Maryland — Baltimore City',product:'Tax Sale Certificate / property-tax lien',schedule:'Maryland\'s official 2026 tax-sale schedule lists Baltimore City\'s tax sale for May 18, 2026. Baltimore City also publishes a 2026 Tax Sale Book and current tax-sale services.',availability:'2026 annual sale passed; verify any City-held/resale activity directly with Baltimore City Finance. This guide keeps Baltimore City at market level rather than treating an old sale list as current inventory.',maxReturn:'2026 redemption rate: 12%/yr owner-occupied residential; 18%/yr all other property',interest:'Baltimore City Code Article 28 §8-1 sets redemption interest at 12% annually for residential real property designated as the owner\'s principal residence and 18% annually for all other property.',bid:'https://pay.baltimorecity.gov/TaxBooklet',canadian:'City-specific bidder registration, tax-ID and payment rules apply. Verify current eligibility directly with Baltimore City before registration.',itin:'Do not assume an ITIN alone satisfies Baltimore City bidder requirements; confirm current tax-ID and bidder documentation with the City.',online:'YES — Baltimore City uses an online tax-sale process and publishes a 2026 Tax Sale Book.',otc:'City-held/resale procedures are separate from the annual tax-sale certificate auction. Verify current availability directly with Baltimore City; do not infer OTC inventory from prior sale lists.',deed:'The annual tax sale transfers a tax-sale certificate/lien, not immediate ownership. Foreclosure of the right of redemption and any later deed/title transfer are separate legal stages.',special:'MARKET-LEVEL ONLY. Baltimore City has a legitimate 2026 tax-lien certificate market, but this row does not bulk republish owner/taxpayer names or a stale parcel inventory. Do not fabricate parcel listings or opening bids, treat delinquent balances or assessments as bids, or substitute judicial foreclosure, in-rem foreclosure, receiver-sale, or deed-sale data for Baltimore City tax-sale certificates.',source:'https://pay.baltimorecity.gov/TaxBooklet'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Baltimore City Maryland row already present")
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
    print("Added Baltimore City Maryland tax-lien market")


if __name__ == "__main__":
    main()
