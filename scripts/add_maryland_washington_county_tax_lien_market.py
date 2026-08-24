#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Washington County"

ROW = r'''{state:'Maryland — Washington County',product:'Tax Lien Certificate / property-tax lien',schedule:'Washington County held its 2026 tax sale on June 2, 2026 at 9:00 a.m. The official Maryland 2026 tax-sale schedule also lists Washington County on June 2.',availability:'MARKET-LEVEL ONLY. Washington County published an official 2026 tax-sale advertisement, but this guide does not bulk republish owner/taxpayer records or treat the completed June sale list as current inventory.',maxReturn:'6%/yr county redemption rate',interest:'Washington County states that redemption includes 6% interest per annum from the date of tax sale to redemption. The certificate of sale is a tax lien; ownership remains with the property owner unless the right of redemption is later foreclosed by court order.',bid:'https://www.washco-md.net/treasurers-office/tax-sale-information/',canadian:'Foreign-bidder eligibility is not clearly established by the current county tax-sale page. Verify current bidder registration and tax-identification requirements directly with Washington County before attempting to participate.',itin:'Washington County requires bidder registration, but this guide does not infer whether an ITIN, SSN, EIN, or other tax identifier is sufficient for a foreign bidder. Verify current requirements directly with the Treasurer.',online:'No — the official 2026 notice states the June 2 sale was conducted at the Washington County Office Building in Hagerstown.',otc:'No current OTC inventory is claimed. Washington County states that, once the tax sale is complete, unsold properties are no longer available for sale through that sale process.',deed:'The purchaser receives a Certificate of Sale / property-tax lien, not immediate ownership. A later Circuit Court action to foreclose the right of redemption is a separate legal stage and can ultimately lead to a deed only after statutory requirements are satisfied.',special:'MARKET-LEVEL ONLY. The official 2026 advertisement lists parcels and opening amounts, but this guide does not bulk copy taxpayer/owner names, republish the completed-sale parcel list as current inventory, infer opening bids from assessed values, or substitute Sheriff/judicial foreclosure or deed-sale records for Washington County tax-lien certificates.',source:'https://www.washco-md.net/treasurers-office/tax-sale-information/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Washington County Maryland row already present")
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
    print("Added Washington County Maryland tax-lien market")


if __name__ == "__main__":
    main()
