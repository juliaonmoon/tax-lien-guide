#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Richland County"

ROW = r'''{state:'Montana — Richland County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Richland County Treasurer administers delinquent real-property taxes under Montana\'s tax-lien framework. The county provides an official tax-inquiry system, but no current 2026 bulk lien-assignment inventory has been verified for safe republication, so no property-level rows are added.',availability:'Montana law permits county-held tax-lien interests to be assigned to third parties after the statutory notice/payment process. Verify current Richland County assignment availability directly with the Treasurer before attempting an assignment.',maxReturn:'10%/yr statutory delinquent-tax interest',interest:'Montana delinquent real-property taxes draw interest at 5/6 of 1% per month (10% annualized), plus the applicable statutory penalty. A tax-lien assignee pays delinquent taxes, penalties, interest, costs and any applicable assignment fees under Montana law.',bid:'https://www.richland.org/treasurer.html',canadian:'Foreign-assignee eligibility is not clearly established in the accessible Richland County guidance; verify identity, payment, notice and tax-document requirements directly with the Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online reverse-auction process. The county provides online tax inquiries, but that system must not be treated as a bulk lien-sale feed.',otc:'Potentially — Montana law provides for assignment of county-held tax-lien interests to third parties. Current Richland inventory and assignment timing must be verified directly with the Treasurer.',deed:'A tax-lien assignment is not immediate property ownership. A later tax deed, if redemption and statutory notice requirements are satisfied, is a separate stage.',special:'MARKET-LEVEL ONLY. Do not infer a current 2026 assignable parcel inventory from the county tax-inquiry system, do not bulk collect owner/taxpayer names, and do not present delinquent balances or later tax-deed values as tax-lien opening/minimum bids.',source:'https://www.richland.org/treasurer.html'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Richland County row already present")
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
    print("Added Montana Richland County tax-lien market")


if __name__ == "__main__":
    main()
