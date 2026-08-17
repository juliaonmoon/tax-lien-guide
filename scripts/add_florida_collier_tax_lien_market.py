#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Collier County"

ROW = r'''{state:'Florida — Collier County',product:'Tax certificate / first-priority property-tax lien',schedule:'Florida counties conduct annual tax-certificate sales for unpaid real-property taxes; Florida DOR publishes the 2026 county sale information. Verify Collier County Tax Collector’s current sale notice and registration details before bidding.',availability:'Annual tax-certificate sale; verify current county-held inventory with the Tax Collector',maxReturn:'18%/yr statutory max',interest:'Florida tax-certificate auctions use reverse bidding: the certificate is awarded to the bidder accepting the lowest interest rate, subject to Florida’s statutory maximum. Verify certificate-specific redemption treatment before bidding.',bid:'https://floridarevenue.com/property/Pages/Cofficial.aspx',canadian:'No simple Collier-specific foreign-bidder rule was found in the official sources used here. Verify current registration, taxpayer-identification and payment requirements directly with the Collier County Tax Collector before funding.',itin:'Verify current taxpayer-identification and withholding requirements with the Collier County Tax Collector / official auction platform; do not assume an ITIN alone guarantees eligibility.',online:'Florida DOR’s 2026 county tax-certificate sale information identifies whether each county sale is live or electronic; confirm Collier’s current platform from the official county notice.',otc:'County-held certificate availability is county-specific; verify current Collier inventory and purchase procedure directly with the Tax Collector.',deed:'A tax certificate is a lien, not ownership. If taxes remain unpaid for the statutory period, an eligible certificate holder may apply for a separate tax-deed process. Collier Clerk conducts tax-deed sales separately.',special:'Keep the tax-certificate lien purchase distinct from Collier County Clerk tax-deed auctions. The Clerk states that the tax-deed process begins after a Tax Collector certificate has remained unpaid for the statutory period and that tax-deed property is sold buyer-beware / as-is.',source:'https://www.collierclerk.com/accessing-tax-deed-sales-in-collier-county/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Collier County row already present")
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
    print("Added Florida Collier County tax-lien market")


if __name__ == "__main__":
    main()
