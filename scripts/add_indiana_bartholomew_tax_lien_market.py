#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Indiana — Bartholomew County 2026"

ROW = r'''{state:'Indiana — Bartholomew County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Bartholomew County conducts Treasurer real-property tax sales for delinquent taxes and directs investors to SRI for current tax-sale information. A specific 2026 annual-sale date is not currently published on the county Treasurer page, so the guide does not invent one.',availability:'Current tax-sale market confirmed — verify the live Bartholomew County/SRI notice and current property eligibility before bidding',interest:'Indiana tax-sale purchaser returns are governed by statutory redemption rather than a simple APR. Verify Bartholomew County\'s current SRI sale packet and Indiana Code 6-1.1-24 and 6-1.1-25 for parcel-specific minimum bid components, redemption amounts, notice duties, and deadlines.',bid:'https://bartholomew.in.gov/treasurer.html',canadian:'Not confirmed — verify current Bartholomew County/SRI bidder-registration and U.S. taxpayer-document requirements directly before participating.',itin:'Do not assume an ITIN or W-8 alone is accepted; verify Bartholomew County/SRI current registration and tax-form requirements.',online:'Bartholomew County directs investors to SRI for current tax-sale information. Do not assume the auction format beyond the current official county/SRI materials and do not bypass vendor registration controls.',otc:'Not confirmed for the annual Treasurer tax sale. Do not treat later county-held certificate, assignment, or deed disposition paths as identical to the annual tax-certificate sale.',deed:'The Treasurer tax sale is a tax-sale certificate/lien process; title is not immediate. Any later tax deed requires separate Indiana statutory redemption, notice, and deed procedures.',special:'MARKET-LEVEL SUMMARY ONLY. The county Treasurer confirms the tax-sale process and directs investors to SRI for current information, but the guide does not bulk republish owner/taxpayer names, freeze a changing SRI list as guaranteed inventory, infer parcel-level opening/minimum bids, or substitute Bartholomew County Sheriff/judicial foreclosure sales for the Treasurer tax sale.',source:'https://bartholomew.in.gov/treasurer.html'}'''


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
        print("Refreshed Bartholomew County Indiana tax-lien market")
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
    print("Added Bartholomew County Indiana tax-lien market")


if __name__ == "__main__":
    main()
