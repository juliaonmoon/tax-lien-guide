#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Indiana — Tippecanoe County 2026"

ROW = r'''{state:'Indiana — Tippecanoe County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Tippecanoe County currently publishes a 2026 Tax Sale Advertisement and directs investors to SRI for the most up-to-date property list. The county page confirms the annual real-estate tax-sale program, but this market summary does not invent a sale date that is not independently verified from the current official advertisement.',availability:'Current 2026 tax-sale advertisement published — verify the live Tippecanoe County/SRI list because parcel eligibility and statutory minimum bids can change before sale',interest:'Indiana tax-sale purchaser returns are governed by statutory redemption rather than a simple APR. Verify Tippecanoe County\'s current 2026 advertisement/SRI materials and Indiana Code 6-1.1-24 and 6-1.1-25 for parcel-specific minimum-bid components, redemption amounts, notice duties, and deadlines.',bid:'https://www.tippecanoe.in.gov/199/Tax-Sale',canadian:'Not confirmed — verify current Tippecanoe County/SRI bidder-registration and U.S. taxpayer-document requirements directly before participating.',itin:'Do not assume an ITIN or W-8 alone is accepted; verify the current Tippecanoe County/SRI registration and tax-form requirements.',online:'Tippecanoe County directs investors to SRI for the most up-to-date list. Do not assume auction format beyond the current official advertisement and do not bypass vendor registration controls.',otc:'The annual Treasurer tax sale is separate from Tippecanoe County\'s Commissioners’ Certificate Sale. The county conducted a Commissioners’ Certificate Sale on April 23, 2026 for certificates on certain properties that had previously failed to receive sufficient bids; do not present that later certificate-sale path as the annual tax sale.',deed:'The annual delinquent-tax sale is a tax-sale certificate/lien process. A tax deed is not immediate; Indiana Code separately governs redemption and the later deed process.',special:'MARKET-LEVEL SUMMARY ONLY. Tippecanoe County publishes a 2026 Tax Sale Advertisement and directs users to SRI for a changing current list, but the guide does not bulk republish owner/taxpayer names, freeze that list as guaranteed inventory, infer parcel-level opening/minimum bids, or substitute Sheriff/judicial foreclosure sales. Keep the separate Commissioners’ Certificate Sale distinct from the annual Treasurer tax sale.',source:'https://www.tippecanoe.in.gov/199/Tax-Sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        row_re = re.compile(
            rf"\{{state:'{re.escape(MARKER)}'.*?\}}(?=\s*,|\s*\n\];)",
            re.S,
        )
        updated, count = row_re.subn(ROW, text, count=1)
        if count != 1:
            raise SystemExit(f"Could not uniquely refresh {MARKER}")
        INDEX.write_text(updated, encoding="utf-8")
        print("Refreshed Tippecanoe County Indiana tax-lien market")
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
    print("Added Tippecanoe County Indiana tax-lien market")


if __name__ == "__main__":
    main()
