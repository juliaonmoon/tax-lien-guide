#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Allegany County"

ROW = r'''{state:'Maryland — Allegany County',product:'Tax Lien Certificate / property-tax lien',schedule:'Allegany County held its 2026 online tax lien sale on May 28, 2026. The county currently publishes a 2026 list of tax lien certificates available for over-the-counter purchase.',availability:'MARKET-LEVEL ONLY. Allegany County publishes an official 2026 OTC certificate list, but this guide does not bulk republish owner/taxpayer records or infer current inventory from stale sale data.',maxReturn:'2026 redemption rate: 10%/yr owner-occupied; 18%/yr non-owner-occupied',interest:'Allegany County\'s 2026 bidding rules state 0.8333% per month / 10% APR for owner-occupied properties and 1.5% per month / 18% APR for non-owner-occupied properties on qualifying amounts paid at tax sale; subsequent taxes paid by the purchaser do not earn interest.',bid:'https://www.alleganygov.org/200/Tax-Lien-Sale-Information',canadian:'2026 auction rules state foreign bidder registrations are not allowed. Verify OTC eligibility directly with Allegany County before relying on this restriction outside the annual auction.',itin:'Annual auction registration requires tax documentation; verify current OTC purchaser requirements directly with Allegany County.',online:'The annual auction is online and the county publishes official tax-lien sale documents and OTC certificate information online.',otc:'Yes — Allegany County currently publishes a 2026 list of tax lien certificates available for OTC purchase. Use the county source for the current list and purchase instructions.',deed:'The county sells a Certificate of Sale / tax lien, not immediate ownership. The owner retains redemption rights until those rights are foreclosed through the separate court process; any later deed/title transfer is a separate legal stage.',special:'MARKET-LEVEL ONLY. The 2026 notice says auction bidding begins no lower than the taxes/charges due, but this guide does not copy owner/taxpayer data or publish property-level opening bids from the county advertisement/OTC list. Do not bypass registration, automate the auction website, fabricate inventory, or substitute foreclosure/deed-sale records for Allegany tax-lien certificates.',source:'https://www.alleganygov.org/200/Tax-Lien-Sale-Information'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Allegany County Maryland row already present")
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
    print("Added Allegany County Maryland tax-lien market")


if __name__ == "__main__":
    main()
