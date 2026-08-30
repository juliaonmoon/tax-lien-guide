#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Collier County"

ROW = r'''{state:'Florida — Collier County',product:'Tax certificate / first-priority property-tax lien',schedule:'Florida counties conduct annual tax-certificate sales for unpaid real-property taxes; verify Collier County Tax Collector’s current tax-certificate sale notice, registration window, and official auction channel before bidding.',availability:'Annual tax-certificate sale; verify current county-held / unsold certificate inventory with the Collier County Tax Collector',maxReturn:'18%/yr statutory max',interest:'Florida tax-certificate auctions use reverse bidding: the certificate is awarded to the bidder accepting the lowest interest rate, subject to Florida’s statutory maximum. Do not treat the 18% statutory cap as the rate an investor will necessarily receive.',bid:'https://colliertaxcollector.com/online-payments/',canadian:'No simple Collier-specific foreign-bidder rule was found in the official sources used here. Verify current registration, taxpayer-identification, withholding, funding, and residency requirements directly with the Collier County Tax Collector before participating.',itin:'Verify current taxpayer-identification requirements with the Collier County Tax Collector / official auction platform; do not assume an ITIN alone guarantees eligibility.',online:'The Collier County Tax Collector currently links a Tax Certificate Sale from its official online-services page; verify the current auction platform and registration details from that official county path before bidding.',otc:'County-held certificate availability is county-specific; do not infer inventory from tax-deed records. Verify current Collier inventory and purchase procedure directly with the Tax Collector.',deed:'A tax certificate is a lien, not ownership. Collier County Clerk states that the Tax Collector first sells the certificate for delinquent real-estate taxes and, if taxes remain unpaid for the statutory period, the certificate holder may later initiate a separate tax-deed process.',special:'Keep the tax-certificate lien purchase distinct from Collier County Clerk tax-deed auctions. Tax-deed notices, minimum bids, property reports, and deed-sale results must not be substituted for tax-certificate sale inventory or certificate bids.',source:'https://www.collierclerk.com/tax-deed-sales/'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Collier County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Collier County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Collier County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Collier County tax-lien market row")
        return

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Florida Collier County tax-lien market")


if __name__ == "__main__":
    main()
