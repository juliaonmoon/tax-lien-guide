#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Liberty County"

ROW = r'''{state:'Montana — Liberty County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Liberty County administers delinquent real-property taxes under Montana’s tax-lien framework. The county property-tax page references pending tax liens, but no current 2026 bulk assignable-inventory feed has been verified for safe republication, so no property-level rows are added.',availability:'Montana law permits county-held property-tax liens to be assigned to third parties after the statutory notice/payment process. Verify current Liberty County assignment availability directly with the Treasurer.',maxReturn:'10%/yr statutory delinquent-tax interest',interest:'Montana delinquent real-property taxes draw interest at 5/6 of 1% per month (10% annualized), plus the statutory 2% penalty. A tax-lien assignment remains distinct from a later tax-deed proceeding.',bid:'https://www.libertycountymt.gov/tax-dates',canadian:'Foreign-assignee eligibility is not clearly established in the accessible county guidance; verify identity, payment, notice and tax-document requirements directly with the Liberty County Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online reverse-auction process. Liberty County provides online property-tax information/payment, but this guide does not treat that system as a tax-lien bidding platform.',otc:'Potentially — Montana law provides for assignment of county-held tax-lien interests to third parties; current Liberty County inventory and timing must be verified with the Treasurer.',deed:'A tax-lien assignment is not immediate property ownership. A later tax-deed process is a separate statutory stage after redemption and notice requirements.',special:'MARKET-LEVEL ONLY. Liberty County’s current property-tax page is used only to verify county tax administration and pending-tax-lien context; assignment authority and interest mechanics come from Montana law. Do not infer a current 2026 parcel inventory from the county tax-search system, do not bulk collect owner/taxpayer names, and do not present delinquent balances or later tax-deed values as tax-lien opening/minimum bids.',source:'https://www.libertycountymt.gov/tax-dates'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Liberty County row already present")
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
    print("Added Montana Liberty County tax-lien market")


if __name__ == "__main__":
    main()
