#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Lake County"

ROW = r'''{state:'Montana — Lake County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Lake County publicly documents attachment of delinquent real-property tax liens and that those liens may be assigned to a third party. The currently accessible county notice is not a verified current 2026 bulk parcel list, so no property-level rows are republished here.',availability:'County tax liens may be assigned to third parties after attachment and the required Montana notice/assignment process; verify current 2026 inventory directly with the Lake County Treasurer.',maxReturn:'10%/yr statutory delinquent-tax interest',interest:'Montana law provides delinquent real-property taxes draw interest at 5/6 of 1% per month (10% annualized), plus the statutory penalty. A third party taking an assignment pays the delinquent taxes, penalties, interest and costs under the Montana tax-lien assignment process.',bid:'https://www.lakemt.gov/274/Treasurer',canadian:'Foreign-bidder eligibility is not clearly established in the accessible county guidance; verify identity, payment, notice and tax-document requirements directly with the Treasurer before attempting an assignment.',itin:'The accessible county notice does not establish a specific U.S. taxpayer-ID requirement for foreign assignees; verify directly with the Treasurer.',online:'No verified online reverse-auction process. This is a statutory lien-assignment market, not a Florida-style interest-rate auction.',otc:'YES — county-held real-property tax liens may be assigned to a third party after statutory notice and county procedures; availability changes as taxpayers redeem.',deed:'A tax-lien assignment is not property ownership. A Montana tax deed is a later statutory process if the lien remains unredeemed.',special:'MARKET-LEVEL ONLY. Do not republish the county delinquent list as a current 2026 inventory unless a current, clearly redistributable source is verified. Do not bulk collect owner/taxpayer names, infer parcel rows from tax-deed or foreclosure records, or present delinquent balances as opening/minimum bids.',source:'https://www.lakemt.gov/274/Treasurer'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Lake County row already present")
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
    print("Added Montana Lake County tax-lien market")


if __name__ == "__main__":
    main()
