#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Yellowstone County"

ROW = r'''{state:'Montana — Yellowstone County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Yellowstone County documents the real-property tax-lien attachment and third-party assignment process. A current 2026 bulk lien inventory that is clearly appropriate for automated republication was not verified, so no property rows are published here.',availability:'Tax liens attach to delinquent real property under Montana law and may be assigned to third parties after required notice; verify current availability directly with the Yellowstone County Treasurer',maxReturn:'10%/yr statutory delinquent-tax interest',interest:'Yellowstone County states delinquent real-property taxes accrue a 2% penalty plus interest at 5/6 of 1% per month (10% annualized). The county issues real-property tax assignment certificates under Montana law.',bid:'https://www.yellowstonecountymt.gov/Treasurer/property-taxes.asp',canadian:'Current foreign-bidder eligibility is not clearly established in the public county guidance; verify identity, payment, notice, and tax-document requirements directly with the Treasurer before attempting an assignment.',itin:'The accessible county guidance does not establish a specific U.S. taxpayer-ID rule for foreign assignees; verify directly with the Treasurer.',online:'No verified online reverse auction. Yellowstone County publishes tax-lien/assignment guidance and tax-record tools, but assignments follow Montana statutory procedures rather than a Florida-style auction.',otc:'YES — county-held real-property tax liens may be assigned to third parties after required statutory notice and county procedures; availability changes as taxpayers redeem.',deed:'A tax-lien assignment/certificate is not property ownership. A tax deed is a separate later statutory process if the lien remains unredeemed.',special:'MARKET-LEVEL ONLY. Yellowstone County issues real-property tax assignment certificates and separately issues tax deeds. Do not bulk republish owner names from tax-record search, infer a 2026 parcel inventory from older tax-sale notices, or treat delinquent tax balances as opening bids.',source:'https://www.yellowstonecountymt.gov/Treasurer/property-taxes.asp'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Yellowstone County row already present")
        return

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Montana Yellowstone County tax-lien market")


if __name__ == "__main__":
    main()
