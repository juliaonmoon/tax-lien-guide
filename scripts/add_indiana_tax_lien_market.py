#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Indiana — Allen County 2026"

ROW = r'''{state:'Indiana — Allen County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Allen County\'s official 2026 tax sale is <span class="schedule-date">September 16, 2026</span>. The county published its 2026 Tax Sale List on August 6, 2026 and updates eligibility as owners redeem/pay before sale.',availability:'Upcoming — official 2026 list published',interest:'Redemption payments and purchaser return are governed by Indiana Code 6-1.1-24 and 6-1.1-25; verify the current statutory calculation and county handout for the specific sale.',bid:'https://www.allencounty.in.gov/270/Tax-Sale',canadian:'Not confirmed — verify current Allen County/SRI bidder-registration and U.S. taxpayer-form requirements before participating',itin:'Do not assume an ITIN alone is sufficient; verify the sale vendor\'s current registration requirements',online:'Verify current Allen County sale instructions; county page is the source of truth for 2026 details',otc:'NO for the annual tax sale; Allen County notes that certain unsold parcels may later be handled through the county/ACCDC process, which is a different disposition path',deed:'Purchaser receives a tax-sale certificate/lien first. A tax deed is not immediate; statutory redemption and notice procedures apply.',special:'Allen County warns that federal tax liens may survive unless the purchaser separately obtains a federal Certificate of Discharge. Treat the county\'s current list as dynamic because parcels can be removed before sale.',source:'https://www.allencounty.in.gov/270/Tax-Sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Indiana Allen County row already present")
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
