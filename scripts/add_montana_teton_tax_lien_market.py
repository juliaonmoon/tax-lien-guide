#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Teton County"

ROW = r'''{state:'Montana — Teton County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Teton County administers delinquent real-property taxes and tax-lien sale redemptions, but no current 2026 bulk assignable-inventory feed has been verified for safe republication, so no property-level rows are added.',availability:'Teton County processes tax-lien sale redemptions under Montana law. Verify current assignment availability, required notice and payment directly with the County Treasurer before relying on an assignment opportunity.',maxReturn:'10%/yr statutory delinquent-tax interest',interest:'Teton County states delinquent property taxes incur a 2% penalty plus interest at 5/6 of 1% per month (10% annualized). A tax-lien assignment/certificate is distinct from a later deed proceeding.',bid:'https://tetoncountymt.gov/treasurer/property-tax-department/',canadian:'Foreign-assignee eligibility is not clearly established in the accessible county guidance; verify identity, payment, notice and tax-document requirements directly with the Teton County Treasurer.',itin:'No specific foreign-assignee taxpayer-ID rule was verified from the accessible county material; confirm directly with the Treasurer.',online:'No verified online tax-lien bidding platform. The county website provides tax information, but this guide does not treat general tax-payment systems as tax-lien auction platforms.',otc:'Potentially — Montana law provides for assignment of county-held tax-lien interests; current Teton County inventory and assignment timing must be verified with the Treasurer.',deed:'A tax-lien assignment is not immediate property ownership. Teton County separately processes redemptions and issuance of deeds under Montana’s statutory framework.',special:'MARKET-LEVEL ONLY. Teton County’s official Treasurer pages verify delinquent-tax administration, tax-lien sale redemptions and the county’s 2% penalty plus 5/6 of 1% monthly interest. Do not infer a current 2026 assignable parcel inventory, do not bulk collect owner/taxpayer names, and do not present delinquent balances or later deed values as tax-lien opening/minimum bids.',source:'https://tetoncountymt.gov/treasurer/property-tax-department/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Teton County row already present")
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
    print("Added Montana Teton County tax-lien market")


if __name__ == "__main__":
    main()
