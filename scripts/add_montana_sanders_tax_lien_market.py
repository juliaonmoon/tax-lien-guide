#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Sanders County"

ROW = r'''{state:'Montana — Sanders County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Sanders County reported mailing 536 pending tax-lien notices in July 2026 and its Treasurer issues real-property tax assignment certificates. No current 2026 bulk assignable-lien inventory has been verified for safe republication, so no property-level rows are added.',availability:'County-administered / seasonal — verify the current assignment window, payoff amount, and available liens directly with the Sanders County Treasurer.',maxReturn:'10%/yr statutory delinquent-tax interest; 2% delinquency penalty applies under Montana law',interest:'Montana delinquent real-property taxes generally draw 5/6 of 1% interest per month (10% annualized) plus a 2% delinquency penalty. Verify the exact assignment amount, accrued interest, penalty, and allowable costs with the Treasurer before purchase.',bid:'https://co.sanders.mt.us/215/Treasurer',canadian:'Foreign-assignee eligibility is not clearly established in the accessible Sanders County guidance; verify identity, payment, notice, and tax-document requirements directly with the Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online reverse-auction process. Sanders County administers real-property tax assignment certificates through the Treasurer rather than a Florida-style interest-rate auction.',otc:'Potentially — county records confirm active tax-lien notices and a Treasurer function that issues and manages real-property tax assignment certificates. Verify current assignable inventory directly with the Treasurer.',deed:'A tax-lien assignment is not immediate property ownership. Sanders County separately issues tax deeds after the applicable Montana redemption/notice process.',special:'MARKET-LEVEL ONLY. Do not infer a current 2026 parcel inventory from the county tax-search system or delinquent-tax PDF, do not bulk collect owner/taxpayer names, and do not present delinquent balances, tax-deed values, or personal-property sheriff-sale amounts as tax-lien opening/minimum bids.',source:'https://co.sanders.mt.us/215/Treasurer'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Sanders County row already present")
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
    print("Added Montana Sanders County tax-lien market")


if __name__ == "__main__":
    main()
