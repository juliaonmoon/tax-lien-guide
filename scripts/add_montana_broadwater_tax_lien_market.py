#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Broadwater County"

ROW = r'''{state:'Montana — Broadwater County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Broadwater County publicly noticed its tax-lien process under MCA 15-17-122, but no current 2026 bulk assignable-inventory feed has been verified for safe republication. Current 2026 assignment availability and timing must be confirmed with the County Treasurer.',availability:'Verify current 2026 tax-lien assignment availability with the Broadwater County Treasurer. The guide does not carry forward the 2025 public-notice auction date as a 2026 sale date.',maxReturn:'10%/yr statutory delinquent-tax interest',interest:'Montana delinquent real-property taxes accrue interest at 5/6 of 1% per month (10% annualized), plus the applicable statutory penalty. A tax-lien assignment/certificate is distinct from a later tax deed.',bid:'https://broadwatercountymt.com/',canadian:'Foreign-assignee eligibility is not clearly established in the accessible county guidance; verify identity, notice, payment and tax-document requirements directly with the Broadwater County Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online tax-lien bidding platform. Do not treat the county property-tax payment lookup as a tax-lien auction platform.',otc:'Potentially — Montana law allows assignment of county-held tax-lien rights after required notice and payment. Current Broadwater inventory must be verified with the Treasurer.',deed:'A tax-lien assignment is not immediate ownership. A tax deed is a later statutory stage after the redemption and notice requirements are satisfied.',special:'MARKET-LEVEL ONLY. Broadwater County’s public tax-lien notice states that the transaction is a sale/assignment of the tax lien on delinquent taxes, not a sale of the property. Do not reuse prior-year parcel lists as current 2026 inventory, do not bulk collect owner/taxpayer names, and do not present delinquent balances or later tax-deed values as tax-lien opening/minimum bids.',source:'https://broadwatercountymt.com/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Broadwater County row already present")
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
    print("Added Montana Broadwater County tax-lien market")


if __name__ == "__main__":
    main()
