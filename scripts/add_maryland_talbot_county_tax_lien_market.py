#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Talbot County"

ROW = r'''{state:'Maryland — Talbot County',product:'Tax Sale Certificate / property-tax lien',schedule:'Talbot County held its 2026 tax sale on May 20, 2026. Verify future annual dates directly with Talbot County Finance.',availability:'MARKET-LEVEL ONLY. Talbot County publishes official tax-sale information and 2026 results; completed sale results are not treated here as current inventory.',maxReturn:'6%/yr county redemption rate',interest:'Talbot County states that tax-sale certificates redeem at 6% annual interest, calculated monthly. High-bid premium amounts do not earn interest.',bid:'https://www.talbotcountymd.gov/abouttaxsale',canadian:'Not evaluated in this guide.',itin:'Not evaluated in this guide.',online:'Official county tax-sale information is published online.',otc:'Talbot County states that properties not sold at the annual tax sale are not offered later over the counter.',deed:'The tax sale transfers a lien/certificate interest, not immediate property ownership. Any later foreclosure of redemption and deed/title transfer are separate legal stages.',special:'MARKET-LEVEL ONLY. Do not bulk republish owner/taxpayer names, treat completed sale results as current inventory, fabricate parcel/opening-bid data, treat assessed or delinquent balances as bids, or substitute foreclosure/deed-sale records for Talbot County tax-sale certificates.',source:'https://www.talbotcountymd.gov/abouttaxsale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Talbot County Maryland row already present")
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
    print("Added Talbot County Maryland tax-lien market")


if __name__ == "__main__":
    main()
