#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Park County"

ROW = r'''{state:'Montana — Park County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Park County Treasurer publishes a delinquent-tax list and an official Notice of pending tax assignment. No current 2026 bulk lien-assignment inventory has been verified for safe republication, so no property-level rows are added.',availability:'Park County publishes delinquent-tax and pending-assignment information through the Treasurer. Verify current assignment availability and required notice/payment steps directly with the Treasurer before attempting an assignment.',maxReturn:'10%/yr statutory delinquent-tax interest',interest:'Montana delinquent real-property taxes draw interest at 5/6 of 1% per month (10% annualized), plus the statutory penalty. A tax-lien assignee pays delinquent taxes, penalties, interest, costs and applicable assignment fees under Montana law.',bid:'https://www.parkcountymt.gov/government-departments/treasurer/',canadian:'Foreign-assignee eligibility is not clearly established in the accessible Park County guidance; verify identity, payment, notice and tax-document requirements directly with the Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online reverse-auction process. This is a statutory tax-lien assignment market, not a tax-deed auction or Florida-style rate auction.',otc:'Potentially — Park County publishes a Notice of pending tax assignment and delinquent-tax information. Current assignable inventory and timing must be verified directly with the Treasurer.',deed:'A tax-lien assignment is not immediate property ownership. A later tax deed, if statutory redemption and notice requirements are satisfied, is a separate stage.',special:'MARKET-LEVEL ONLY. Do not infer a current 2026 assignable parcel inventory from the delinquent-tax list, do not bulk collect owner/taxpayer names, and do not substitute tax-deed or foreclosure parcels/opening bids for tax-lien assignments.',source:'https://www.parkcountymt.gov/government-departments/treasurer/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Park County row already present")
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
    print("Added Montana Park County tax-lien market")


if __name__ == "__main__":
    main()
