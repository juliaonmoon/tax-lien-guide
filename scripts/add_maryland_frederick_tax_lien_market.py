#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Frederick County"

ROW = r'''{state:'Maryland — Frederick County',product:'Tax Sale Certificate / property-tax lien',schedule:'Frederick County held its 2026 internet-based tax sale on May 11, 2026. Registration ran April 1–30, 2026. Verify the next current-year notice before participating.',availability:'Annual county tax sale using an internet-based auction and high-bid-premium method. The county publishes a current tax-sale listing before the sale and removes redeemed accounts as payments are received. This guide does not republish the owner-name-bearing sale publication as a current post-sale inventory.',maxReturn:'8%/yr county redemption rate',interest:'Frederick County states the redemption interest rate on the 2026 certificate of sale is 8% per annum. High-bid premium amounts do not earn interest and should not be treated as part of the certificate yield.',bid:'https://frederickcountymd.gov/2005/Tax-Sale',canadian:'County-specific. Registration requires online bidder registration, ACH payment capability, and county documentation. Verify current eligibility and tax-document requirements directly with Frederick County before participating.',itin:'Do not assume an ITIN alone satisfies Frederick County bidder eligibility. The 2026 procedures require registration, banking information, and matching bidder/payment documentation; verify current taxpayer-ID requirements directly with the county.',online:'YES — Frederick County conducts the tax-lien certificate auction online through its designated tax-sale auction site.',otc:'No general over-the-counter inventory is assumed. Verify any assignments or post-sale certificate availability directly with Frederick County; do not infer availability from an expired pre-sale list.',deed:'The successful bidder receives a certificate of sale / tax lien, not immediate ownership. A later court action to foreclose the right of redemption is a separate legal stage and is not treated here as a tax-deed sale listing.',special:'MARKET-LEVEL ONLY. Frederick County had a legitimate May 11, 2026 tax-lien certificate sale and publishes an official current-year sale list, but that publication contains owner information and changes as accounts are redeemed. This guide does not bulk republish owner/taxpayer names, does not treat assessed value or delinquent balance as an opening bid, and does not substitute later foreclosure/deed records for tax-sale certificates.',source:'https://frederickcountymd.gov/2005/Tax-Sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Frederick County Maryland row already present")
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
    print("Added Frederick County Maryland tax-lien market")


if __name__ == "__main__":
    main()
