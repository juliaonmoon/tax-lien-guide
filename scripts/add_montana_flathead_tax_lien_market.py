#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Flathead County"

ROW = r'''{state:'Montana — Flathead County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Flathead County officially documents that delinquent real-property taxes become liens and that tax deed is a later separate stage. No current 2026 bulk lien-assignment inventory has been verified for safe republication, so no property-level rows are added.',availability:'Montana law permits county-held tax-lien interests to be assigned to third parties after the required notice and payment process. Verify current Flathead County availability directly with the Treasurer before attempting an assignment.',maxReturn:'10%/yr statutory delinquent-tax interest',interest:'Montana delinquent real-property taxes draw interest at 5/6 of 1% per month (10% annualized), plus the statutory penalty. An assignee pays the delinquent taxes, penalties, interest and costs under the Montana tax-lien assignment process.',bid:'https://flathead.mt.gov/department-directory',canadian:'Foreign-bidder eligibility is not clearly established in the accessible county guidance; verify identity, payment, notice and tax-document requirements directly with the Flathead County Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online reverse-auction process. This is a statutory lien-assignment market, not a Florida-style interest-rate auction.',otc:'Potentially — Montana law provides for assignment of county-held tax-lien interests to third parties; current Flathead inventory and timing must be verified with the Treasurer.',deed:'A tax-lien assignment is not property ownership. Flathead County separately documents that after the statutory period the county may take title by tax deed; deed is a later stage, not the original lien purchase.',special:'MARKET-LEVEL ONLY. Do not infer a current 2026 parcel inventory from the county tax-search system, do not bulk collect owner/taxpayer names, and do not present delinquent balances or later tax-deed values as tax-lien opening/minimum bids.',source:'https://flathead.mt.gov/department-directory'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Flathead County row already present")
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
    print("Added Montana Flathead County tax-lien market")


if __name__ == "__main__":
    main()
