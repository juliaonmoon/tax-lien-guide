#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Carter County"

ROW = r'''{state:'Montana — Carter County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Carter County states that each August 1, prior-year delinquent real-estate taxes receive a lien and those liens are available for sale to the general public. No current 2026 bulk lien inventory has been verified for safe republication, so no property-level rows are added.',availability:'Seasonal / county-administered — verify the current assignable lien inventory and purchase procedure directly with the Carter County Treasurer.',maxReturn:'10%/yr statutory delinquent-tax interest; county guidance also states a 2% delinquency penalty',interest:'Carter County states delinquent taxes carry a 2% penalty plus 5/6 of 1% interest per month (10% annualized). Verify the exact assignment payoff and treatment of penalty, interest and costs with the Treasurer before purchase.',bid:'https://cartercountymt.gov/departments/treasurer.php',canadian:'Foreign-bidder eligibility is not clearly established in the accessible county guidance; verify identity, payment, notice and tax-document requirements directly with the Carter County Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online reverse-auction process. Carter County describes county-administered lien sales/assignments rather than a Florida-style interest-rate auction.',otc:'Potentially — Carter County says real-estate tax liens are available for sale to the general public after attachment; verify current inventory directly with the Treasurer.',deed:'A tax lien is not immediate property ownership. Carter County separately references tax deeds; any later deed process remains a distinct statutory stage subject to Montana redemption and notice requirements.',special:'MARKET-LEVEL ONLY. Do not infer a current 2026 parcel inventory from the county tax system, do not bulk collect owner/taxpayer names, and do not present delinquent balances or later tax-deed values as tax-lien opening/minimum bids.',source:'https://cartercountymt.gov/departments/treasurer.php'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Carter County row already present")
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
    print("Added Montana Carter County tax-lien market")


if __name__ == "__main__":
    main()
