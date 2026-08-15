#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Apache County"

ROW = r'''{state:'Arizona — Apache County',product:'Tax lien / Certificate of Purchase',schedule:'Apache County holds its annual online tax-lien auction each February. After the auction, unsold liens are normally offered over the counter from about mid-March through December 31.',availability:'2026 annual auction passed — OTC unsold liens may be available through Dec 31',maxReturn:'16%/yr statutory max',interest:'Arizona tax liens may be bid down from the statutory 16% annual rate; Apache County states investors may bid down the interest rate or bid a premium. Actual certificate yield depends on the winning bid and redemption timing.',bid:'https://www.apachecountyaz.gov/treasurer',canadian:'Apache County publishes a purchaser form and requests IRS Form W-9 for lien purchases. A non-U.S. bidder should confirm directly with the Treasurer whether foreign registration and an appropriate IRS form are accepted before funding or bidding.',itin:'County instructions currently reference Form W-9. Foreign bidders should confirm the current taxpayer-identification/withholding documentation accepted by the Treasurer rather than assuming W-9 eligibility.',online:'YES — the annual February auction is online through the county-linked official tax-lien auction site.',otc:'YES — Apache County states unsold liens are normally available over the counter from mid-March through December 31.',deed:'The purchase is a lien, not a deed. The county states a lien holder generally must wait at least three years from the first tax-lien sale before attempting judicial foreclosure through Apache County Superior Court.',special:'Apache County expressly states a certificate holder has no ownership or possession rights and should not contact the owner or enter/change the property. OTC purchasers must contact the Treasurer for the exact amount and fees for each parcel.',source:'https://www.apachecountyaz.gov/treasurer'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Arizona Apache County row already present")
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
    print("Added Arizona Apache County tax-lien market")


if __name__ == "__main__":
    main()
