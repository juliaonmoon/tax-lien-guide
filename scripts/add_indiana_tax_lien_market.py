#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Indiana — Allen County 2026"

ROW = r'''{state:'Indiana — Allen County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Allen County\'s official 2026 tax sale is <span class="schedule-date">September 16, 2026</span>. The county currently labels its 2026 Tax Sale List as updated August 20, 2026; eligibility remains dynamic as owners redeem/pay before sale.',availability:'Upcoming — official 2026 list published',interest:'Redemption payments and purchaser return are governed by Indiana Code 6-1.1-24 and 6-1.1-25. Indiana State Board of Accounts guidance describes 110% of the minimum bid for redemption within six months and 115% after six months but before one year, plus 10% annual interest on qualifying amounts above the minimum bid and certain later taxes/assessments. Verify the current county handout for the specific sale.',bid:'https://www.allencounty.in.gov/270/Tax-Sale',canadian:'Not confirmed — verify current Allen County/GovEase bidder-registration and U.S. taxpayer-form requirements before participating',itin:'Do not assume an ITIN alone is sufficient; verify the sale vendor\'s current registration requirements',online:'Allen County publishes current 2026 sale instructions on its official Tax Sale page; verify the linked current-year handout before registering',otc:'NO for the annual tax sale; Allen County notes that certain unsold parcels may later be handled through the county/ACCDC process, which is a different disposition path',deed:'Purchaser receives a tax-sale certificate/lien first. A tax deed is not immediate; statutory redemption and notice procedures apply.',special:'MARKET-LEVEL SUMMARY ONLY. Allen County warns that federal tax liens may survive unless the purchaser separately obtains a federal Certificate of Discharge. Treat the county\'s current list as dynamic because parcels can be removed before sale. Do not bulk republish owner names or treat a prior snapshot as guaranteed current inventory.',source:'https://www.allencounty.in.gov/270/Tax-Sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")

    if MARKER in text:
        # Refresh the existing generated row instead of silently returning.
        # This keeps current-year county dates/rules from going stale when the
        # official page changes after the market was first added.
        row_re = re.compile(
            r"\{state:'Indiana — Allen County 2026'.*?\}(?=\s*,|\s*\n\];)",
            re.S,
        )
        updated, count = row_re.subn(ROW, text, count=1)
        if count != 1:
            raise SystemExit("Could not uniquely refresh Allen County Indiana row")
        INDEX.write_text(updated, encoding="utf-8")
        print("Refreshed Indiana — Allen County 2026 tax-lien market")
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
    print("Added Indiana — Allen County 2026 tax-lien market")


if __name__ == "__main__":
    main()
