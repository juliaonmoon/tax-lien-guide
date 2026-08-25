#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Indiana — Clark County 2026"

ROW = r'''{state:'Indiana — Clark County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Clark County officially conducts a Treasurer tax-certificate sale for eligible delinquent real property, but the county page does not currently publish a specific 2026 sale date. Use the county Treasurer/Auditor pages and their official SRI link for the current schedule.',availability:'2026 market verified — current sale date and parcel eligibility must be checked through Clark County/SRI',interest:'Indiana tax-sale purchaser returns are governed by statutory redemption rather than a simple APR. Clark County states owners have one year from the auction date to redeem by paying the amounts prescribed by Indiana Code, including interest on amounts paid by the successful bidder. Verify the current county/SRI materials and Indiana Code 6-1.1-24 and 6-1.1-25 for parcel-specific amounts and deadlines.',bid:'https://clarkcounty.in.gov/index.php/clark-county-indiana-government/clark-county-treasurer-s-office',canadian:'Not confirmed — verify current Clark County/SRI bidder-registration and U.S. taxpayer-document requirements directly before participating.',itin:'Do not assume an ITIN or W-8 alone is accepted; verify current Clark County/SRI registration requirements.',online:'Not confirmed on the Clark County Treasurer page. The county directs investors to SRI for current auction and property information; do not assume format or bypass vendor registration controls.',otc:'Not confirmed for the annual Treasurer tax sale. Any later Commissioners Certificate Sale, county-held certificate disposition, or deed process is legally distinct and must not be represented as the annual Clark County tax-certificate sale.',deed:'Successful bidders obtain a lien through a Tax Sale Certificate issued by the County Auditor. Clark County states a tax deed is not immediate; only after the one-year redemption period and statutory procedures may an unredeemed certificate holder seek a deed.',special:'MARKET-LEVEL SUMMARY ONLY. Clark County directs investors to SRI for current available properties. Do not bulk republish owner/taxpayer names, freeze a dynamic SRI list as guaranteed 2026 inventory, infer parcel-level opening/minimum bids, bypass registration controls, or substitute Commissioners Certificate, Sheriff, or judicial-foreclosure sales for the annual Treasurer tax-certificate sale.',source:'https://clarkcounty.in.gov/index.php/clark-county-indiana-government/clark-county-treasurer-s-office'}'''


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
        print("Refreshed Clark County Indiana tax-lien market")
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
    print("Added Clark County Indiana tax-lien market")


if __name__ == "__main__":
    main()
