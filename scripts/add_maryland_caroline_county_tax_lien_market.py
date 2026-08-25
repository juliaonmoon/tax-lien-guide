#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Caroline County"

ROW = r'''{state:'Maryland — Caroline County',product:'Tax Sale Certificate / property-tax lien',schedule:'Caroline County held its 2026 online tax sale from August 20–21, 2026. Verify future annual dates and any post-sale availability directly with the Caroline County Tax Office.',availability:'MARKET-LEVEL ONLY. The 2026 annual sale has passed. This guide does not republish the county\'s eligible-property list as current post-sale inventory.',maxReturn:'Current 2026 certificate redemption rate not independently verified; confirm with Caroline County',interest:'Caroline County states that the county sells its first lien on the property at tax sale. The owner or another person with a legal interest may redeem until the right of redemption is finally barred by Circuit Court decree. Do not confuse delinquent-tax interest or penalties with the purchaser\'s certificate return.',bid:'https://www.carolinemd.org/170/Tax-Sale',canadian:'Foreign-bidder eligibility is not clearly established by the current county page. Verify current registration and tax-identification requirements directly with Caroline County.',itin:'Not independently verified; confirm bidder tax-ID requirements with the Caroline County Tax Office before registration.',online:'Yes — Caroline County states the 2026 tax sale was conducted by online auction.',otc:'No current over-the-counter certificate inventory is claimed from the official source reviewed for this market.',deed:'The tax sale sells the county\'s first lien, not immediate property ownership. Redemption can continue until the right of redemption is barred by Circuit Court decree; any later title transfer is a separate legal stage.',special:'MARKET-LEVEL ONLY. Do not bulk republish owner/taxpayer names from the eligible-property list, treat the completed 2026 list as current inventory, fabricate opening bids from delinquent balances or assessments, or substitute judicial foreclosure/deed-sale records for Caroline County tax-sale liens.',source:'https://www.carolinemd.org/170/Tax-Sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Caroline County Maryland row already present")
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
    print("Added Caroline County Maryland tax-lien market")


if __name__ == "__main__":
    main()
