#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

NEW_ROWS = r"""
{state:'Alabama — state-held inventory',product:'Tax sale certificate assignment / tax deed',schedule:'Annual county auctions are usually the first Monday in May; state-held delinquent inventory is published and updated weekly',availability:'Open now',interest:'State-held purchase amount includes delinquent tax, fees, costs and 12% annual interest; verify certificate redemption terms before purchase',bid:'https://www.revenue.alabama.gov/property-tax/tax-delinquent-property-and-land-sales/',canadian:'Verify ALDOR application and tax-document requirements before applying',itin:'Verify current tax-ID requirements with ALDOR',online:'State-held price quote application is online; county auction format varies',otc:'YES — state-held delinquent inventory by county',deed:'If state held the certificate less than 3 years, purchaser receives an assignment; over 3 years, a tax deed is issued',special:'Neither a certificate assignment nor a tax deed guarantees clear title. ALDOR advises purchasers to investigate title and legal issues before purchase.',source:'https://www.revenue.alabama.gov/property-tax/tax-delinquent-property-and-land-sales/'},
{state:'Nebraska — county tax sales',product:'Tax sale certificate / tax lien',schedule:'Annual county public sale begins the first Monday in March; 2026 statewide delinquent list was published in February',availability:'Passed',interest:'Purchaser pays taxes, delinquent interest and costs; bidding rules are announced by the county treasurer',bid:'https://revenue.nebraska.gov/PAD/real-property/nebraska-delinquent-real-property-list',canadian:'County-specific; verify bidder registration rules with the county treasurer',itin:'County-specific; verify current registration and tax-document requirements',online:'Varies by county',otc:'Unsold parcels may be sold privately by the county treasurer after the public sale under Nebraska law',deed:'Certificate holder must follow statutory notice and deed/foreclosure procedures; timing differs for certain vacant/abandoned property',special:'Nebraska changed delinquent-property sale procedures in 2025, and a 2026 law preserves prior rules for some certificates sold from 2022 through May 7, 2025. Use current statutes for the certificate date.',source:'https://revenue.nebraska.gov/PAD/real-property/nebraska-delinquent-real-property-list'},
{state:'Arizona — Coconino County OTC liens',product:'Tax lien certificate',schedule:'Arizona county tax-lien sales are held annually; Coconino also publishes an over-the-counter certificate list during the year',availability:'Open now — Coconino OTC list published for August 2026',interest:'Arizona tax-lien certificates use interest bidding at the annual sale; over-the-counter/state-held certificate terms should be verified with the county before purchase',bid:'https://www.coconino.az.gov/376/Tax-Liens',canadian:'Verify bidder registration, payment and tax-document requirements directly with the county treasurer',itin:'County-specific; confirm current taxpayer-ID requirements before registration',online:'Coconino annual sale uses an online auction; OTC certificates can be researched from the county tax-lien page',otc:'YES — Coconino publishes a current over-the-counter tax-lien certificate list',deed:'Buying the certificate does not buy the property; judicial foreclosure of the right to redeem is a later legal process if statutory conditions are met',special:'The county explicitly warns buyers to research each property. Tax-lien certificates are liens, not deeds, and title/property condition still require independent due diligence.',source:'https://www.coconino.az.gov/376/Tax-Liens'}
""".strip()


def main():
    html = INDEX.read_text(encoding="utf-8")
    wanted = ["Alabama — state-held inventory", "Nebraska — county tax sales", "Arizona — Coconino County OTC liens"]
    if all(x in html for x in wanted):
        print("Alabama, Nebraska and Arizona already present")
        return

    # Add only rows that are not already present so this remains idempotent.
    rows = []
    for row in NEW_ROWS.split("\n"):
        if "Alabama — state-held inventory" in row and "Alabama — state-held inventory" in html:
            continue
        if "Nebraska — county tax sales" in row and "Nebraska — county tax sales" in html:
            continue
        if "Arizona — Coconino County OTC liens" in row and "Arizona — Coconino County OTC liens" in html:
            continue
        rows.append(row)
    if not rows:
        print("No new tax-lien market rows")
        return

    anchor = "const visible=Object.fromEntries"
    anchor_pos = html.find(anchor)
    if anchor_pos < 0:
        raise SystemExit("Could not find rows-array anchor in index.html")
    rows_end = html.rfind("];", 0, anchor_pos)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")
    insertion = (",\n" if not html[:rows_end].rstrip().endswith(",") else "\n") + "\n".join(rows) + "\n"
    html = html[:rows_end] + insertion + html[rows_end:]
    html = html.replace("Updated August 13, 2026", "Updated August 14, 2026")
    INDEX.write_text(html, encoding="utf-8")
    print("Added verified tax-lien market rows")


if __name__ == "__main__":
    main()
