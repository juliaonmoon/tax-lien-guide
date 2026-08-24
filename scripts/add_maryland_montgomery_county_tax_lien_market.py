#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Montgomery County"
SOURCE = "https://www.montgomerycountymd.gov/tax-sale-information-procedures"

ROW = r'''{state:'Maryland — Montgomery County',product:'Tax Sale Certificate / property-tax lien',schedule:'Montgomery County\'s official 2026 tax sale was held June 8, 2026 from 8:00 a.m. to 2:00 p.m. ET. The County states the next annual tax sale will be June 7, 2027. Verify any later sale or certificate availability directly with the Department of Finance.',availability:'Annual county tax-lien sale. The 2026 sale is complete. MARKET-LEVEL ONLY here: the County publishes delinquent-property notices containing owner/taxpayer information and inventory changes before sale, so this guide does not bulk republish that list as current investable inventory.',maxReturn:'2026 redemption rate: 6%/yr owner-occupied; 20%/yr non-owner-occupied',interest:'Montgomery County\'s official 2026 procedures state redemption interest is 6% per annum for owner-occupied properties and 20% per annum for non-owner-occupied properties, calculated daily from June 8, 2026. High-bid premiums, later taxes, expenses, invalid/void sales and certificate-specific circumstances can change investor economics.',bid:'https://www.montgomerycountymd.gov/tax-sale-information-procedures',canadian:'County-specific. The County tax sale is open to the public, but bidders must comply with the current sealed-bid, identity, payment and tax-documentation requirements. Verify current eligibility directly with Montgomery County before relying on foreign participation.',itin:'Do not assume an ITIN alone satisfies Montgomery County bidder requirements. Verify current bidder identity, tax-documentation and payment requirements directly with the Department of Finance.',online:'NO for the 2026 main sale — Montgomery County used a public sealed-bid process with bids delivered in person, by courier/mail, or by official tax-sale email during the stated sale window.',otc:'Do not assume over-the-counter availability. The County may later offer unsold groups or individual liens, but availability and terms must be verified directly with the County.',deed:'The successful bidder purchases a tax-sale certificate/property-tax lien, not immediate ownership. Foreclosure of the right of redemption and any resulting deed/title are later court/legal stages and are not treated as tax-deed listings here.',special:'MARKET-LEVEL ONLY. Do not bulk republish owner/taxpayer names from the County tax-sale notice, do not treat the advertised delinquent tax-sale amount or assessed/full cash value as an opening bid, and do not substitute Sheriff/judicial foreclosure or later deed records for Montgomery County tax-sale certificates.',source:'https://www.montgomerycountymd.gov/tax-sale-information-procedures'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montgomery County Maryland row already present")
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
    print("Added Montgomery County Maryland tax-lien market")


if __name__ == "__main__":
    main()
