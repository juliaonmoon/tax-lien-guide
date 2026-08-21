#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Glacier County"

ROW = r'''{state:'Montana — Glacier County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Glacier County’s Treasurer explicitly publishes that certain delinquent real-property parcels are eligible for Tax Assignment(s). The accessible delinquency report contains taxpayer names and is not a current 2026 assignable-inventory feed, so no property-level rows are republished.',availability:'County-administered assignment market — verify the current eligible years, parcel status, assignment timing, payoff amount, and notice requirements directly with the Glacier County Treasurer.',maxReturn:'10%/yr statutory delinquent-tax interest; 2% delinquency penalty applies under Montana law',interest:'Montana delinquent real-property taxes draw interest at 5/6 of 1% per month (10% annualized), plus the statutory 2% delinquency penalty. An assignment purchaser must follow Montana’s tax-lien assignment process and pay the amounts/costs required by the Treasurer.',bid:'https://glaciercountymt.gov/departments/treasurer/',canadian:'Foreign-assignee eligibility is not clearly established in the accessible Glacier County guidance; verify identity, payment, notice, and tax-document requirements directly with the Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online reverse-auction process. Glacier County describes tax assignments administered through the Treasurer, not a Florida-style interest-rate auction.',otc:'Potentially — the Treasurer states that eligible delinquent real-property parcels may be available for Tax Assignment(s). Current assignable inventory and eligibility must be verified directly with the Treasurer.',deed:'A tax-lien assignment/certificate is not immediate property ownership. Any later tax-deed stage is a separate statutory process after applicable redemption and notice requirements.',special:'MARKET-LEVEL ONLY. Do not bulk republish the county delinquency report because it contains taxpayer names; do not infer a current 2026 parcel inventory from older eligible-year language; and do not present delinquent balances, penalties, interest totals, or later tax-deed values as tax-lien opening/minimum bids.',source:'https://glaciercountymt.gov/departments/treasurer/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Glacier County row already present")
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
    print("Added Montana Glacier County tax-lien market")


if __name__ == "__main__":
    main()
