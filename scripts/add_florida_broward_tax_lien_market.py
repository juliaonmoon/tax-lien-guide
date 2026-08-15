#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Broward County"

ROW = r'''{state:'Florida — Broward County',product:'Tax certificate / first-priority property-tax lien',schedule:'Broward County tax certificates are sold annually after delinquency through a reverse-auction process; verify the current Tax Collector sale notice and registration window before bidding.',availability:'Annual sale / county-held certificates may remain after the auction',maxReturn:'18%/yr max',interest:'Reverse auction: bidding starts at 18% and moves downward in 0.25% increments. The certificate goes to the bidder accepting the lowest interest rate; certificates receiving no bids become county-held at 18%.',bid:'https://www.broward.org/RecordsTaxesTreasury/Pages/Glossary.aspx',canadian:'Foreign-bidder eligibility and U.S. tax-document requirements should be confirmed directly with the Broward County Tax Collector before registration.',itin:'Verify current taxpayer-identification and withholding requirements with the Tax Collector before bidding.',online:'Broward County describes tax certificates as competitive-bid investments; use the current Tax Collector sale instructions for the operative auction platform and registration steps.',otc:'County-held certificates exist when no bidder purchases a certificate at the annual auction; availability and purchase procedure should be verified with the Tax Collector.',deed:'A tax certificate is a lien, not ownership. If statutory conditions are later met, a certificate holder may apply for a separate tax-deed process; that later deed auction is a different product.',special:'Broward County explicitly defines a tax certificate as an interest-bearing first lien and says it conveys no property rights or ownership. Do not confuse this market with Broward County tax-deed auctions.',source:'https://www.broward.org/RecordsTaxesTreasury/Pages/Glossary.aspx'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Broward County row already present")
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
    print("Added Florida Broward County tax-lien market")


if __name__ == "__main__":
    main()
