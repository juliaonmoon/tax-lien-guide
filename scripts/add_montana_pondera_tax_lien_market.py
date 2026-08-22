#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Pondera County"

ROW = r'''{state:'Montana — Pondera County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Pondera County officially sets county costs for tax lien sales, assignments, redemptions and later tax deed sales. No current 2026 bulk assignable-inventory feed has been verified for safe republication, so current availability and timing must be confirmed with the County Treasurer.',availability:'Verify current 2026 tax-lien assignment availability with the Pondera County Treasurer. Do not infer a current parcel list from tax-deed resolutions or prior-year notices.',maxReturn:'10%/yr statutory delinquent-tax interest',interest:'Montana delinquent real-property taxes accrue interest at 5/6 of 1% per month (10% annualized), plus the applicable statutory penalty. Pondera County separately recognizes tax lien sales/assignments, redemptions and tax deed sales.',bid:'https://www.ponderacountymontana.org/',canadian:'Foreign-assignee eligibility is not clearly established in the accessible county guidance; verify identity, notice, payment and tax-document requirements directly with the Pondera County Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online tax-lien bidding platform. Do not treat the county property-tax payment lookup or tax-deed process as a tax-lien auction platform.',otc:'Potentially — Montana law allows assignment of county-held tax-lien rights after required notice and payment. Current Pondera inventory must be verified with the Treasurer.',deed:'A tax-lien assignment/certificate is not immediate ownership. Pondera County separately recognizes the later tax-deed process after statutory redemption and notice requirements.',special:'MARKET-LEVEL ONLY. Pondera County Resolution #18-2023/24 separately sets costs for tax lien sales, assignments, redemptions and tax deed sales. Do not reuse tax-deed parcels, prior-year notices, owner/taxpayer names, delinquent balances, or deed-sale values as current 2026 tax-lien inventory or opening/minimum bids.',source:'https://www.ponderacountymontana.org/_files/ugd/984806_b2f5eb0b39344694a76629b074c12e78.pdf'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Pondera County row already present")
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
    print("Added Montana Pondera County tax-lien market")


if __name__ == "__main__":
    main()
