#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Indiana — Madison County 2026"

ROW = r'''{state:'Indiana — Madison County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Madison County currently publishes a Notice of Real Property Tax Sale and separate Tax Sale Information for Potential Buyers through the official Treasurer\'s Office. The county page does not currently expose a clearly verifiable 2026 sale date in machine-readable text, so this guide does not invent one.',availability:'Current tax-sale market confirmed — verify the latest Madison County Treasurer/Auditor notice and buyer instructions before participating because sale timing, parcel eligibility, and amounts can change',interest:'Indiana tax-sale purchaser returns are governed by statutory redemption rather than a simple APR. Verify Madison County\'s current sale materials and Indiana Code 6-1.1-24 and 6-1.1-25 for minimum-bid components, redemption amounts, notice duties, and deadlines.',bid:'https://www.madisoncounty.in.gov/departments/treasurer%27s-office',canadian:'Not confirmed — verify current Madison County bidder-registration and U.S. taxpayer-document requirements directly before participating.',itin:'Do not assume an ITIN or W-8 alone is accepted; verify current Madison County/vendor registration requirements.',online:'Not inferred. The official Treasurer page links Tax Sale Information for Potential Buyers, but the guide does not assume an auction platform or bypass any registration controls.',otc:'Not confirmed for the annual Treasurer tax sale. Do not treat commissioner/certificate-sale or later deed-disposition paths as identical to the annual tax-sale certificate process.',deed:'The Treasurer/Auditor tax-sale process creates a tax-sale certificate/lien first. Madison County separately directs tax-sale redemption matters to the Auditor and deed/ownership matters to the Recorder; title is not immediate.',special:'MARKET-LEVEL SUMMARY ONLY. Madison County confirms a current real-property tax-sale process and buyer-information path, but this guide does not bulk republish owner/taxpayer names, freeze a changing advertised list as guaranteed inventory, infer a 2026 auction date not exposed in the current machine-readable county page, fabricate parcel-level opening/minimum bids, bypass registration controls, or substitute Sheriff/judicial foreclosure sales.',source:'https://www.madisoncounty.in.gov/departments/treasurer%27s-office'}'''


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
        print("Refreshed Madison County Indiana tax-lien market")
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
    print("Added Madison County Indiana tax-lien market")


if __name__ == "__main__":
    main()
