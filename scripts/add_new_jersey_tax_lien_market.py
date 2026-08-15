#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "New Jersey — municipal tax sales"

ROW = r'''{state:'New Jersey — municipal tax sales',product:'Tax sale certificate / municipal tax lien',schedule:'New Jersey municipalities hold tax sales for delinquent municipal charges; sale dates are set and advertised locally rather than on one statewide 2026 calendar. Verify the current municipality notice before bidding.',availability:'Municipality-specific — monitor local 2026 notices',interest:'New Jersey tax-sale bidding and redemption terms are governed by Title 54. The winning bidder receives a tax sale certificate/lien, not immediate title; verify the current municipal notice for bid-rate, premium and payment rules.',bid:'https://www.nj.gov/dca/dlgs/programs/tax_collector.shtml',canadian:'Municipality-specific; verify bidder registration, payment method and any taxpayer-identification requirements before participating',itin:'Municipality-specific; do not assume an ITIN alone satisfies registration requirements',online:'Varies by municipality; use the municipality tax collector and advertised sale notice as the source of truth',otc:'Municipal-held tax sale certificates may later be sold under New Jersey law, but availability and method are municipality-specific',deed:'The tax sale certificate is a lien, not ownership. If it is not redeemed, foreclosure of the right of redemption is a later legal process subject to New Jersey law.',special:'New Jersey DCA publishes official tax-collection resources and a Basics of New Jersey Tax Sales guide. Municipalities are the operative sale authorities, so dates and bidder rules must be verified locally rather than inferred statewide.',source:'https://www.nj.gov/dca/dlgs/programs/tax_collector.shtml'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("New Jersey municipal tax-sale row already present")
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
    print("Added New Jersey municipal tax-lien market")


if __name__ == "__main__":
    main()
