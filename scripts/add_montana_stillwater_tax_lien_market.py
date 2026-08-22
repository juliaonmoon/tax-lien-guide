#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Stillwater County"

ROW = r'''{state:'Montana — Stillwater County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Stillwater County Treasurer publishes a 2026 delinquent-tax report plus official property-tax assignment guidance and assignment-list resources. The assignment list includes taxpayer names and is not republished here; no current 2026 bulk assignable-inventory feed was verified for safe republication.',availability:'County-administered Montana tax-lien assignment framework — verify currently assignable county-held liens, notice timing, payoff amount, and assignment requirements directly with the Stillwater County Treasurer.',maxReturn:'10%/yr statutory delinquent-tax interest; 2% delinquency penalty applies under Montana law',interest:'Montana delinquent real-property taxes draw interest at 5/6 of 1% per month (10% annualized), plus a statutory 2% delinquency penalty. Stillwater County publishes property-tax assignment guidance and assignment-list resources.',bid:'https://www.stillwatercountymt.gov/248/Treasurer',canadian:'Foreign-assignee eligibility is not clearly established in the accessible Stillwater County guidance; verify identity, payment, notice, and tax-document requirements directly with the Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online reverse-auction process. Montana tax-lien assignments are county-administered rather than Florida-style interest-rate auctions.',otc:'Potentially — Stillwater County publishes property-tax assignment guidance and assignment-list resources, but the public assignment list includes taxpayer names and is not used as a bulk republication feed here. Verify currently assignable liens directly with the Treasurer.',deed:'A tax-lien assignment/certificate is not immediate property ownership. A later tax deed is a separate statutory stage after redemption and notice requirements.',special:'MARKET-LEVEL ONLY. Stillwater County publishes a current delinquent-tax report and tax-assignment resources, but the assignment list includes taxpayer names and no safe current 2026 bulk assignable-inventory feed was verified. Do not bulk republish owner/taxpayer data; do not infer a parcel inventory from the general delinquent-tax report; and do not present delinquent balances, penalties, interest totals, or later tax-deed values as tax-lien opening/minimum bids.',source:'https://www.stillwatercountymt.gov/248/Treasurer'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Stillwater County row already present")
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
    print("Added Montana Stillwater County tax-lien market")


if __name__ == "__main__":
    main()
