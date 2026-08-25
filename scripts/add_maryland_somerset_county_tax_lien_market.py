#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Somerset County"

ROW = r'''{state:'Maryland — Somerset County',product:'Tax Lien Certificate / property-tax lien',schedule:'Maryland SDAT lists Somerset County\'s 2026 tax sale for June 11, 2026.',availability:'MARKET-LEVEL ONLY. Somerset County is a verified Maryland tax-sale jurisdiction, but this guide does not bulk republish owner/taxpayer records or infer a current parcel inventory from dated sale notices.',maxReturn:'County-specific 2026 certificate redemption rate not verified from a current official Somerset County source; confirm with the Somerset County Tax Office before relying on a rate.',interest:'Maryland law treats the tax sale as a sale of a tax-lien certificate rather than the real property itself. This guide does not state a Somerset-specific 2026 purchaser return until an official current county source clearly publishes it.',bid:'https://dat.maryland.gov/Pages/Tax-Sale-Schedule.aspx',canadian:'Current Somerset County foreign-bidder eligibility and tax-ID requirements were not verified from a current 2026 county bidder packet; confirm directly with the Somerset County Tax Office.',itin:'Current Somerset County bidder tax-document requirements were not verified from a current 2026 county bidder packet; confirm directly with the Somerset County Tax Office.',online:'The official Maryland 2026 schedule verifies the June 11 sale date, but a current official Somerset County source clearly establishing the 2026 auction format was not verified in this run.',otc:'Current 2026 over-the-counter certificate availability was not verified from a current official Somerset County source.',deed:'Maryland tax sale transfers a tax-lien certificate, not immediate ownership of the real property. Foreclosure of the right of redemption and any later deed/title transfer are separate legal stages.',special:'MARKET-LEVEL ONLY. Do not bulk copy owner/taxpayer names, recycle prior-year parcel lists, infer current inventory, fabricate opening/minimum bids, or substitute judicial foreclosure/deed-sale records for Somerset County tax-lien certificates.',source:'https://dat.maryland.gov/Pages/tax-collectors.aspx'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Somerset County Maryland row already present")
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
    print("Added Somerset County Maryland tax-lien market")


if __name__ == "__main__":
    main()
