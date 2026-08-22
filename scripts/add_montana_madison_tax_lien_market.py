#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Madison County"

ROW = r'''{state:'Montana — Madison County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Madison County Treasurer publishes current tax-lien assignment guidance and a Notice of Pending Assignment form. No current 2026 bulk assignable-lien inventory was verified for safe republication, so no parcel rows are inferred.',availability:'County-administered tax-lien assignments may be purchased in person or by mail after the statutory notice process; Madison County uses first-come/earliest-postmark rules with a random tie-break process when needed. Verify current lien availability directly with the Treasurer before sending payment or notices.',maxReturn:'10%/yr statutory delinquent-tax interest; 2% delinquency penalty applies under Montana law',interest:'Montana delinquent real-property taxes draw 5/6 of 1% interest per month (10% annualized), plus the statutory 2% delinquency penalty. Madison County requires the statutory owner-notice paperwork before an assignment can be issued.',bid:'https://madisoncountymt.gov/214/Tax-Lien-Assignment-Information',canadian:'Foreign-assignee eligibility is not clearly established in the accessible Madison County guidance; verify identity, payment, notice, and tax-document requirements directly with the Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online reverse-auction process. Madison County describes in-person or mail tax-lien purchases administered by the Treasurer.',otc:'YES — county-administered assignment process. Madison County says tax-lien purchases can be made in person or by mail, subject to current availability and statutory notice requirements.',deed:'A tax-lien assignment is not immediate property ownership. A later tax-deed process is a separate statutory stage and should not be confused with the initial lien assignment.',special:'MARKET-LEVEL ONLY. Madison County publishes tax-lien assignment procedures, but no current 2026 bulk assignable-parcel feed was verified for safe republication. Do not infer parcel inventory from general tax records; do not bulk republish owner/taxpayer names; and do not present delinquent balances, penalties, interest totals, sheriff-sale amounts, or later tax-deed values as tax-lien opening/minimum bids.',source:'https://madisoncountymt.gov/214/Tax-Lien-Assignment-Information'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Madison County row already present")
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
    print("Added Montana Madison County tax-lien market")


if __name__ == "__main__":
    main()
