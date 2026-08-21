#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Rosebud County"

ROW = r'''{state:'Montana — Rosebud County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Rosebud County Treasurer publishes official Tax Lien Assignment Information and a Notice of Pending Assignment. No current 2026 bulk assignable-inventory feed was verified for safe republication, so no property-level rows are added.',availability:'County-administered tax-lien assignment market — verify current eligible parcels, assignment timing, exact payoff amount, and statutory notice requirements directly with the Rosebud County Treasurer.',maxReturn:'10%/yr statutory delinquent-tax interest; 2% delinquency penalty applies under Montana law',interest:'Montana delinquent real-property taxes draw interest at 5/6 of 1% per month (10% annualized), plus the statutory 2% delinquency penalty. Rosebud County publishes tax-lien assignment guidance and directs purchasers to Montana tax-lien statutes.',bid:'https://rosebudcountymt.gov/departments/treasurer/',canadian:'Foreign-assignee eligibility is not clearly established in the accessible Rosebud County guidance; verify identity, payment, notice, and tax-document requirements directly with the Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online reverse-auction process. Rosebud County administers tax-lien assignments through the Treasurer rather than a Florida-style rate auction.',otc:'Potentially — Rosebud County publishes Tax Lien Assignment Information and a Notice of Pending Assignment for county-held liens. Verify current eligible inventory and payoff amounts directly with the Treasurer.',deed:'A tax-lien assignment/certificate is not immediate property ownership. Rosebud County separately handles later tax-deed procedures after applicable redemption and notice requirements.',special:'MARKET-LEVEL ONLY. Do not bulk republish owner/taxpayer data from delinquent-tax records; do not infer a current 2026 parcel inventory from general delinquent-tax search results; and do not present delinquent balances, penalties, interest totals, or later tax-deed values as tax-lien opening/minimum bids.',source:'https://rosebudcountymt.gov/departments/treasurer/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Rosebud County row already present")
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
    print("Added Montana Rosebud County tax-lien market")


if __name__ == "__main__":
    main()
