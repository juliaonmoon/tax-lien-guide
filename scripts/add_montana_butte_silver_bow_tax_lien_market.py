#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Butte-Silver Bow"

ROW = r'''{state:'Montana — Butte-Silver Bow',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Butte-Silver Bow explicitly administers third-party tax-lien assignments under Montana law. No current 2026 bulk lien-assignment inventory has been verified for safe republication, so no property-level rows are added.',availability:'Tax-lien assignment business is administered by the Butte-Silver Bow Treasurer. The county states it does not conduct assignment business during November and May; verify current availability directly with the Treasurer.',maxReturn:'10%/yr statutory delinquent-tax interest',interest:'Montana delinquent real-property taxes draw interest at 5/6 of 1% per month (10% annualized), plus the statutory penalty. An assignee pays the delinquent taxes, penalties, interest, costs and assignment fee under the Montana tax-lien assignment process.',bid:'https://co.silverbow.mt.us/2090/Delinquent-Tax-Process',canadian:'Foreign-assignee eligibility is not clearly established in the accessible county guidance; verify identity, payment, notice and tax-document requirements directly with the Butte-Silver Bow Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online reverse-auction process. This is a statutory tax-lien assignment market, not a deed auction or Florida-style rate auction.',otc:'Potentially — the Treasurer administers assignment of county-held tax-lien interests to interested persons; current inventory and timing must be verified directly with the county.',deed:'A tax-lien assignment is not immediate property ownership. Butte-Silver Bow separately publishes tax-deed auctions after the statutory redemption/notice process.',special:'MARKET-LEVEL ONLY. Do not infer a current 2026 parcel inventory from general property/tax systems, do not bulk collect owner/taxpayer names, and do not substitute tax-deed auction parcels or tax-deed opening bids for tax-lien assignments.',source:'https://co.silverbow.mt.us/2090/Delinquent-Tax-Process'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Butte-Silver Bow row already present")
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
    print("Added Montana Butte-Silver Bow tax-lien market")


if __name__ == "__main__":
    main()
