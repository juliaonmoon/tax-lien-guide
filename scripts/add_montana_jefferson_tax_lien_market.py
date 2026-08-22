#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Jefferson County"

ROW = r'''{state:'Montana — Jefferson County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Jefferson County Treasurer explicitly administers delinquent-tax assignments and directs interested purchasers to Montana tax-lien law. No current 2026 bulk assignable-lien inventory was verified for safe republication, so no parcel rows are inferred.',availability:'County-administered delinquent-tax assignments may be purchased subject to current availability and Montana statutory procedures. Jefferson County does not accept tax assignments during the tax-season months of November and May; verify current availability directly with the Treasurer.',maxReturn:'10%/yr statutory delinquent-tax interest; 2% delinquency penalty applies under Montana law',interest:'Montana delinquent real-property taxes draw 5/6 of 1% interest per month (10% annualized), plus the statutory 2% delinquency penalty. Jefferson County directs interested purchasers to Montana Title 15 tax-lien law and its post-2016 assignment framework.',bid:'https://jeffersoncounty-mt.gov/staging/8993/treasurer/',canadian:'Foreign-assignee eligibility is not clearly established in the accessible Jefferson County guidance; verify identity, payment, notice, and tax-document requirements directly with the Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online reverse-auction process. Jefferson County describes Treasurer-administered delinquent-tax assignments rather than a competitive lien auction.',otc:'YES — county-administered assignment process, subject to current availability and statutory requirements. Jefferson County specifically notes that assignments are not accepted during November and May.',deed:'A delinquent-tax assignment is a lien interest, not immediate property ownership. Jefferson County separately directs users to the tax-deed process, which is a later statutory stage.',special:'MARKET-LEVEL ONLY. Jefferson County confirms a delinquent-tax assignment process but does not expose a verified current 2026 bulk assignable-parcel feed suitable for republication. Do not infer inventory from the general property-tax search; do not bulk republish owner/taxpayer names; and do not present delinquent balances, penalties, sheriff-sale amounts, or later tax-deed values as tax-lien opening/minimum bids.',source:'https://jeffersoncounty-mt.gov/staging/8993/treasurer/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Jefferson County row already present")
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
    print("Added Montana Jefferson County tax-lien market")


if __name__ == "__main__":
    main()
