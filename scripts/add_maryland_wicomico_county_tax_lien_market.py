#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Wicomico County"

ROW = r'''{state:'Maryland — Wicomico County',product:'Tax Lien Certificate / property-tax lien',schedule:'Wicomico County held its 2026 public tax sale on June 9, 2026. The county states that its 2026 over-the-counter sale runs from June 23 through December 31, 2026.',availability:'MARKET-LEVEL ONLY. Wicomico County publishes an official OTC list, but this guide does not bulk republish owner/taxpayer records or treat a dated advertised list as guaranteed current inventory.',maxReturn:'County-specific 2026 certificate redemption rate not verified from a current official source; verify with Wicomico County before bidding or buying OTC.',interest:'Wicomico County publishes current tax-sale and OTC procedures, but this guide does not state a certificate return rate until a current official county source clearly publishes the applicable 2026 redemption interest.',bid:'https://www.wicomicocounty.org/392/Tax-Sale-Information',canadian:'The county requires a W-9 and purchaser agreement for OTC purchases. This guide does not infer foreign-bidder eligibility; verify current tax-ID and purchaser requirements directly with Wicomico County.',itin:'Wicomico County currently instructs OTC purchasers to submit a W-9 and purchaser agreement. Verify current purchaser tax-document requirements directly with the county.',online:'The 2026 annual sale was an in-person public auction at the Wicomico Civic Center; current sale information and OTC documents are published online.',otc:'Yes — Wicomico County states that the 2026 OTC sale runs June 23 through December 31, 2026. Use the county source for the current list and current purchase amount.',deed:'The county issues a Certificate of Sale / tax lien rather than immediate ownership. Foreclosure of the right of redemption and any later deed/title transfer are separate legal stages.',special:'MARKET-LEVEL ONLY. The official 2026 notice says properties without an opening bid are withdrawn and purchasers pay the taxes and charges due, but this guide does not bulk copy taxpayer names, republish property-level bids from the advertised list, infer current OTC inventory, or substitute foreclosure/deed records for Wicomico tax-lien certificates.',source:'https://www.wicomicocounty.org/392/Tax-Sale-Information'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Wicomico County Maryland row already present")
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
    print("Added Wicomico County Maryland tax-lien market")


if __name__ == "__main__":
    main()
