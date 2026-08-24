#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Dorchester County"

ROW = r'''{state:'Maryland — Dorchester County',product:'Tax Sale Certificate / property-tax lien',schedule:'Dorchester County held its 2026 tax sale on May 19, 2026. Verify future annual dates directly with Dorchester County Treasury.',availability:'MARKET-LEVEL ONLY. Dorchester County publishes official tax-sale terms; no owner/taxpayer inventory is bulk republished here.',maxReturn:'10%/yr county redemption rate',interest:'Dorchester County states that interest paid on delinquent taxes, fees, advertising and miscellaneous costs paid on the tax-sale date is 10% per year; subsequent taxes paid by the purchaser do not earn interest.',bid:'https://dorchestercountymd.com/departments/finance-treasury/tax-sale/',canadian:'Not evaluated in this guide.',itin:'Not evaluated in this guide.',online:'Official county tax-sale information and terms are published online.',otc:'Not represented as an over-the-counter inventory unless Dorchester County publishes a current official offering.',deed:'The tax sale issues a Certificate of Sale / lien interest, not immediate property ownership. Foreclosure of redemption and any later deed/title transfer are separate legal stages.',special:'MARKET-LEVEL ONLY. Do not bulk republish owner/taxpayer names, fabricate parcel inventory or opening bids, treat delinquent balances as bids, bypass bidder registration, or substitute foreclosure/deed-sale records for Dorchester County tax-sale certificates.',source:'https://dorchestercountymd.com/departments/finance-treasury/tax-sale/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Dorchester County Maryland row already present")
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
    print("Added Dorchester County Maryland tax-lien market")


if __name__ == "__main__":
    main()
