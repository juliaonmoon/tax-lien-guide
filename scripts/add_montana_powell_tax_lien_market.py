#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Powell County"

ROW = r'''{state:'Montana — Powell County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Powell County Treasurer publishes current tax-assignment guidance and makes delinquent-tax lists available through the Treasurer. No current 2026 bulk assignable-inventory feed was verified for safe republication, so no parcel rows are inferred from the county delinquent-tax notice.',availability:'County-administered tax-lien assignments are first come, first served after required notice. Powell County states assignment business is paused during the tax-season months of November and May; verify current availability and payoff directly with the Treasurer.',maxReturn:'10%/yr statutory delinquent-tax interest; 2% delinquency penalty applies under Montana law',interest:'Montana delinquent real-property taxes draw 5/6 of 1% interest per month (10% annualized), plus the statutory delinquency penalty. Powell County separately charges an assignment fee and requires the assignee to follow the statutory owner-notice process.',bid:'https://www.powellcountymt.gov/media/5056',canadian:'Foreign-assignee eligibility is not clearly established in the accessible Powell County guidance; verify identity, payment, notice, and tax-document requirements directly with the Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online reverse-auction process. Powell County describes first-come, first-served county-administered tax-lien assignments.',otc:'Potentially — Powell County states that if taxes remain unpaid after required notice, an interested party may purchase the county tax lien by paying the delinquent taxes, county fee, and providing proof of notice/certified mailing. Verify currently assignable liens directly with the Treasurer.',deed:'A tax-lien assignment is not immediate property ownership. Powell County explicitly treats tax-deed action as a later, separate legal process that the investor must handle under Montana law.',special:'MARKET-LEVEL ONLY. Powell County makes delinquent-tax lists available and publishes tax-assignment procedures, but the current public delinquent notice includes taxpayer names and is not used here as a bulk republication feed. Do not bulk republish owner/taxpayer data; do not infer a 2026 assignable parcel inventory from the general delinquent-tax list; and do not present delinquent balances, county fees, penalties, interest totals, sheriff-sale amounts, or later tax-deed values as tax-lien opening/minimum bids.',source:'https://www.powellcountymt.gov/media/5056'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Powell County row already present")
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
    print("Added Montana Powell County tax-lien market")


if __name__ == "__main__":
    main()
