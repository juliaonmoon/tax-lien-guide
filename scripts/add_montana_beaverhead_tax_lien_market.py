#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Beaverhead County"

ROW = r'''{state:'Montana — Beaverhead County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Beaverhead County’s Treasurer publishes a Notice of Pending Assignment for county-held tax liens. No current 2026 bulk assignable-inventory feed was verified for safe republication, so no property-level rows are added.',availability:'County-administered assignment market — verify current eligible parcels, assignment timing, payoff amount, and notice requirements directly with the Beaverhead County Treasurer.',maxReturn:'10%/yr statutory delinquent-tax interest; 2% delinquency penalty applies under Montana law',interest:'Montana delinquent real-property taxes generally draw interest at 5/6 of 1% per month (10% annualized), plus the statutory 2% delinquency penalty. Assignment purchasers must follow Montana’s tax-lien assignment process and county requirements.',bid:'https://beaverheadcountymt.gov/departments/treasurer-motor-vehicle-licensing/',canadian:'Foreign-assignee eligibility is not clearly established in the accessible Beaverhead County guidance; verify identity, payment, notice, and tax-document requirements directly with the Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online reverse-auction process. Beaverhead County publishes a pending-assignment form administered through the Treasurer rather than a Florida-style rate auction.',otc:'Potentially — Beaverhead County’s official Notice of Pending Assignment states that an assignment of the county-held tax lien may be purchased after the required notice period. Verify current inventory and payoff amounts directly with the Treasurer.',deed:'A tax-lien assignment/certificate is not immediate property ownership. Any later tax-deed stage is a separate statutory process after applicable redemption and notice requirements.',special:'MARKET-LEVEL ONLY. Do not bulk republish taxpayer/owner information from tax records; do not infer a current 2026 parcel inventory from a blank assignment form; and do not present delinquent balances, penalties, interest totals, or later tax-deed values as tax-lien opening/minimum bids.',source:'https://beaverheadcountymt.gov/departments/treasurer-motor-vehicle-licensing/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Beaverhead County row already present")
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
    print("Added Montana Beaverhead County tax-lien market")


if __name__ == "__main__":
    main()
