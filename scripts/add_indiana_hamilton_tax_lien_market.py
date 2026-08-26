#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Indiana — Hamilton County 2026"

ROW = r'''{state:'Indiana — Hamilton County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Hamilton County officially schedules its 2026 Real Property Tax Sale for October 8, 2026 at 10:00 AM local time in the 2nd Floor Historic Courtroom, 33 N 9th St., Noblesville. The county posted the 2026 property listing/public notice and says the list is normally updated every Friday by noon before the sale.',availability:'Current 2026 tax-sale notice/list published — verify the live Hamilton County list before bidding because parcels can be removed after payment and the county updates the list before sale',interest:'Indiana tax-sale purchaser returns are governed by statutory redemption rather than a simple APR. Verify Hamilton County\'s current notice and Indiana Code 6-1.1-24 and 6-1.1-25 for the advertised statutory minimum amount, redemption amounts, notice duties, and deadlines.',bid:'https://www.hamiltoncounty.in.gov/452/Real-Property-Tax-Sale',canadian:'Not confirmed — verify current Hamilton County/SRI bidder-registration and U.S. taxpayer-document requirements directly before participating.',itin:'Do not assume an ITIN or W-8 alone is accepted; verify current Hamilton County/SRI registration and tax-form requirements.',online:'Hamilton County\'s official 2026 notice identifies an in-person sale location and time. The county also directs bidders to SRI for registration/general information; do not imply an online auction unless the county later publishes one.',otc:'This row covers Hamilton County\'s annual Real Property Tax Sale only. Do not substitute Hamilton County Sheriff\'s Sales, which are a separate foreclosure process.',deed:'The delinquent-tax auction is subject to a statutory right of redemption; a tax deed is not immediate. Indiana Code separately governs redemption, notices, and the later deed process.',special:'MARKET-LEVEL SUMMARY ONLY. Hamilton County has a clearly published 2026 tax-sale notice and changing property list, but this guide does not bulk republish owner/taxpayer names, freeze the list as guaranteed inventory, infer parcel-level opening/minimum bids, or mix Sheriff foreclosure listings into the tax-lien market. Use the current official county notice/list for parcel-specific amounts and eligibility.',source:'https://www.hamiltoncounty.in.gov/1380/Tax-Sale-Notice-2026'}'''


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
        print("Refreshed Hamilton County Indiana tax-lien market")
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
    print("Added Hamilton County Indiana tax-lien market")


if __name__ == "__main__":
    main()
