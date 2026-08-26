#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Indiana — Allen County 2026"

ROW = r'''{state:'Indiana — Allen County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Allen County officially states that its 2026 Tax Sale will be held September 16, 2026. The county published a 2026 Tax Sale List dated August 20, 2026 and says more information will be posted as available.',availability:'Current 2026 tax-sale list published — verify the live Allen County Tax Sale page before bidding because eligibility, balances, and sale status can change before the sale',interest:'Indiana tax-sale purchaser returns are governed by statutory redemption rather than a simple advertised APR. Verify Allen County\'s current 2026 General Tax Sale Information and Indiana Code 6-1.1-24 and 6-1.1-25 for minimum-bid components, redemption amounts, notice duties, and deadlines.',bid:'https://www.allencounty.in.gov/270/Tax-Sale',canadian:'Not confirmed — verify current Allen County auction registration, tax-form, and bidder-eligibility requirements directly before participating.',itin:'Do not assume an ITIN, W-8, or foreign registration is accepted. Allen County has historically required U.S. tax documentation for registration; verify the current 2026 instructions rather than reusing prior-year requirements.',online:'Allen County\'s official 2026 Tax Sale page confirms the September 16, 2026 sale and publishes the current list. Do not infer the auction platform or registration method until the county\'s current 2026 instructions expressly publish them.',otc:'This row covers Allen County\'s annual delinquent real-property Tax Sale only. Unsold properties may later follow a separate county/ACCDC process; do not substitute Sheriff foreclosure sales or later county-owned-property dispositions.',deed:'Buying at the Tax Sale does not give immediate ownership. Indiana law provides a redemption period and separate statutory notice/deed procedures before a purchaser may receive a tax title deed.',special:'MARKET-LEVEL SUMMARY ONLY. Allen County currently publishes a 2026 Tax Sale List, but this guide does not bulk republish owner/taxpayer names, freeze the list as guaranteed inventory, copy parcel-level minimum bids without a dedicated current-source ingestion/validation path, or mix Sheriff/judicial foreclosure inventory into the tax-lien market. Use the official county page and current documents for parcel-specific amounts and eligibility.',source:'https://www.allencounty.in.gov/270/Tax-Sale'}'''


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
        print("Refreshed Allen County Indiana tax-lien market")
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
    print("Added Allen County Indiana tax-lien market")


if __name__ == "__main__":
    main()
