#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Carbon County"

ROW = r'''{state:'Montana — Carbon County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Carbon County Treasurer manages property-tax accounts, and current county records show Treasurer tax-lien notice activity. No verified current 2026 bulk assignable-inventory feed was found for safe republication, so no property-level rows are added.',availability:'County-administered Montana tax-lien assignment framework — verify current eligible county-held liens, assignment timing, exact payoff amount, and notice requirements directly with the Carbon County Treasurer.',maxReturn:'10%/yr statutory delinquent-tax interest; 2% delinquency penalty applies under Montana law',interest:'Montana delinquent real-property taxes draw interest at 5/6 of 1% per month (10% annualized), plus a statutory 2% delinquency penalty. Montana law provides for assignment of county-held tax-lien rights to third parties after required notice and payment.',bid:'https://carbonmt.gov/departments/treasurer/',canadian:'Foreign-assignee eligibility is not clearly established in the accessible Carbon County guidance; verify identity, payment, notice, and tax-document requirements directly with the Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online reverse-auction process. Montana tax-lien assignments are county-administered rather than Florida-style interest-rate auctions.',otc:'Potentially — Montana law permits assignment of county-held tax-lien rights, but Carbon County does not expose a verified current 2026 bulk assignable-inventory feed. Verify eligible liens and payoff amounts directly with the Treasurer.',deed:'A tax-lien assignment/certificate is not immediate property ownership. A later tax deed is a separate statutory stage after redemption and notice requirements.',special:'MARKET-LEVEL ONLY. Carbon County current records confirm Treasurer tax-lien notice activity, but no safe current bulk assignable-inventory feed was verified. Do not bulk republish owner/taxpayer data; do not infer a 2026 parcel inventory from the general property-tax search or notice expenses; and do not present delinquent balances, penalties, interest totals, or later tax-deed values as tax-lien opening/minimum bids.',source:'https://carbonmt.gov/departments/treasurer/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Carbon County row already present")
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
    print("Added Montana Carbon County tax-lien market")


if __name__ == "__main__":
    main()
