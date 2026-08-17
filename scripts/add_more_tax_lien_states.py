#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

NEW_ROWS = r"""
{state:'Alabama — state-held inventory',product:'Tax sale certificate assignment / tax deed',schedule:'Annual county auctions are usually the first Monday in May; state-held delinquent inventory is published and updated weekly',availability:'Open now',interest:'State-held purchase amount includes delinquent tax, fees, costs and 12% annual interest; verify certificate redemption terms before purchase',bid:'https://www.revenue.alabama.gov/property-tax/tax-delinquent-property-and-land-sales/',canadian:'Verify ALDOR application and tax-document requirements before applying',itin:'Verify current tax-ID requirements with ALDOR',online:'State-held price quote application is online; county auction format varies',otc:'YES — state-held delinquent inventory by county',deed:'If state held the certificate less than 3 years, purchaser receives an assignment; over 3 years, a tax deed is issued',special:'Neither a certificate assignment nor a tax deed guarantees clear title. ALDOR advises purchasers to investigate title and legal issues before purchase.',source:'https://www.revenue.alabama.gov/property-tax/tax-delinquent-property-and-land-sales/'},
{state:'Nebraska — county tax sales',product:'Tax sale certificate / tax lien',schedule:'Annual county public sale begins the first Monday in March; 2026 statewide delinquent list was published in February',availability:'Passed',interest:'Purchaser pays taxes, delinquent interest and costs; bidding rules are announced by the county treasurer',bid:'https://revenue.nebraska.gov/PAD/real-property/nebraska-delinquent-real-property-list',canadian:'County-specific; verify bidder registration rules with the county treasurer',itin:'County-specific; verify current registration and tax-document requirements',online:'Varies by county',otc:'Unsold parcels may be sold privately by the county treasurer after the public sale under Nebraska law',deed:'Certificate holder must follow statutory notice and deed/foreclosure procedures; timing differs for certain vacant/abandoned property',special:'Nebraska changed delinquent-property sale procedures in 2025, and a 2026 law preserves prior rules for some certificates sold from 2022 through May 7, 2025. Use current statutes for the certificate date.',source:'https://revenue.nebraska.gov/PAD/real-property/nebraska-delinquent-real-property-list'},
{state:'Arizona — Coconino County OTC liens',product:'Tax lien certificate',schedule:'Arizona county tax-lien sales are held annually; Coconino also publishes an over-the-counter certificate list during the year',availability:'Open now — Coconino OTC list published for August 2026',interest:'Arizona tax-lien certificates use interest bidding at the annual sale; over-the-counter/state-held certificate terms should be verified with the county before purchase',bid:'https://www.coconino.az.gov/376/Tax-Liens',canadian:'Verify bidder registration, payment and tax-document requirements directly with the county treasurer',itin:'County-specific; confirm current taxpayer-ID requirements before registration',online:'Coconino annual sale uses an online auction; OTC certificates can be researched from the county tax-lien page',otc:'YES — Coconino publishes a current over-the-counter tax-lien certificate list',deed:'Buying the certificate does not buy the property; judicial foreclosure of the right to redeem is a later legal process if statutory conditions are met',special:'The county explicitly warns buyers to research each property. Tax-lien certificates are liens, not deeds, and title/property condition still require independent due diligence.',source:'https://www.coconino.az.gov/376/Tax-Liens'},
{state:'Colorado — Jefferson County',product:'Tax lien certificate',schedule:'2026 Jefferson County tax-lien auction is scheduled for November 2026; registration starts in October',availability:'Upcoming — November 2026',interest:'Certificate interest is set under Colorado law; Jefferson County states the 2025 tax-lien rate was 14%. Premium bids do not earn interest and are not refunded on redemption.',bid:'https://www.jeffco.us/2438/Internet-Sale-Information',canadian:'Jefferson County requires a U.S. taxpayer ID number to register, so confirm eligibility before planning to bid',itin:'U.S. taxpayer ID required by Jefferson County for bidder registration',online:'YES — Jefferson County uses an online public auction through SRI / Zeus Auction',otc:'County-specific; Jefferson County primarily describes its annual online auction',deed:'The lien is not ownership. After the statutory period, a lien holder may pursue the current treasurer-deed process, which changed under Colorado law effective June 1, 2026.',special:'Jefferson County explicitly states that the asset purchased is the tax lien, not the property. Colorado changed treasurer-deed procedures effective June 1, 2026, so older guides may be outdated.',source:'https://www.jeffco.us/3154/Tax-Lien-Sale'},
{state:'Colorado — Weld County',product:'Tax lien / Tax Lien Sale Certificate',schedule:'Weld County’s next annual online tax-lien sale is November 5, 2026. The county says the advertised property list is posted on RealAuction about three weeks before the sale and updated daily until sale day.',availability:'Upcoming — November 5, 2026',interest:'Colorado redemption interest is set each September 1 at nine percentage points above the federal discount rate, rounded up. Weld County has not yet published the 2026 rate on its official sale page; premium bids do not earn interest.',bid:'https://www.weld.gov/Government/Departments/Treasurer-Public-Trustee/Treasurer/Tax-Lien-Sale-Information',canadian:'Official county material reviewed does not clearly state foreign-bidder eligibility. Confirm registration, taxpayer-ID, withholding and payment requirements directly with Weld County Treasurer / RealAuction before funding.',itin:'The official county page does not establish that an ITIN alone is sufficient; verify current taxpayer-identification requirements with Weld County Treasurer / RealAuction.',online:'YES — Weld County conducts the tax-lien sale online through RealAuction.',otc:'County-held availability is not clearly described on the current sale page; verify directly with the Treasurer before assuming an OTC assignment is available.',deed:'Buying a tax lien does not buy the property. Certificates issued after January 1, 2026 expire after seven years. After the statutory holding period, an eligible lien holder may apply for the separate public Treasurer’s Deed auction process.',special:'Weld County explicitly labels its tax-lien auction site as NOT the foreclosure or Treasurer’s Deed sale. Under Colorado’s 2026 law changes, the later deed stage is a separate public auction; do not treat a lien certificate as ownership or a deed.',source:'https://www.weld.gov/Government/Departments/Treasurer-Public-Trustee/Treasurer/Tax-Lien-Sale-Information'},
{state:'Iowa — county tax sales',product:'Tax sale certificate / property-tax lien',schedule:'County tax sales are held annually on the third Monday in June; counties may hold adjourned sales afterward',availability:'2026 annual sale passed; monitor county adjourned/public-bidder sales',interest:'Iowa county guidance states redemption interest on tax-sale certificates is 2% per month; verify certificate-specific rules and later costs before bidding',bid:'https://www.iowa.gov/how-do-i-pay-property-taxes',canadian:'County-specific registration rules apply; confirm eligibility and documentation with the county treasurer before registration',itin:'County-specific; confirm taxpayer-ID and bidder-registration requirements with the county treasurer',online:'Many counties conduct the annual tax sale electronically; format and registration are county-specific',otc:'County/public-bidder or adjourned-sale availability varies by county',deed:'Buying delinquent taxes creates a lien/certificate, not immediate ownership. Deed proceedings require the statutory notice and redemption process.',special:'Iowa Code Chapter 446 governs tax sales. County treasurer pages should be used for the current sale list, registration rules and deadlines.',source:'https://www.legis.iowa.gov/law/iowaCode/sections?codeChapter=446'}
""".strip()

OLD_COLORADO = "{state:'Colorado — Jefferson County',product:'Tax lien certificate',schedule:'Registration starts <span class=\"schedule-date\">Oct 2026</span>; auction <span class=\"schedule-date\">Nov 2026</span>',availability:'Upcoming',interest:'Statutory rate; 2025 sale rate was 14%',bid:'https://www.jeffco.us/2438/Internet-Sale-Information',canadian:'Restricted by U.S. taxpayer-ID rule; confirm whether ITIN qualifies',itin:'U.S. taxpayer ID required',online:'Yes — SRI / Zeus Auction',otc:'County-held liens exist; contact Treasurer for list',deed:'Treasurer’s deed application after 3 years',special:'Winning bidders may pay a PREMIUM. Premium earns no interest and is not refunded, reducing effective yield.',source:'https://www.jeffco.us/2432/Pre-Sale-Procedures'},"
OLD_IOWA = "{state:'Iowa — county tax sales',product:'Tax sale certificate',schedule:'Generally third Monday in June; Johnson County was <span class=\"schedule-date\">Jun 15, 2026</span>',availability:'Passed',interest:'Iowa statutory tax-sale return rules',bid:'https://johnsoncountyiowa.gov/treasurer/tax-sale-information',canadian:'Verify county registration and tax-ID rules',itin:'Tax ID generally required for bidder registration',online:'Often county/in-person rather than one statewide portal',otc:'County-specific',deed:'Strict notice/deed deadlines after statutory waiting period',special:'Procedural deadlines are important; missing required notices can impair the certificate.',source:'https://johnsoncountyiowa.gov/treasurer/tax-sale-information'},"


def row_for(label: str) -> str:
    return next(r for r in NEW_ROWS.split("\n") if label in r)


def main():
    html = INDEX.read_text(encoding="utf-8")
    changed = False

    replacements = {
        OLD_COLORADO: row_for("Colorado — Jefferson County"),
        OLD_IOWA: row_for("Iowa — county tax sales") + ",",
    }
    for old, new in replacements.items():
        if old in html:
            html = html.replace(old, new, 1)
            changed = True

    # Repair the separator if a prior refresh replaced the final NEW_ROWS item in-place.
    iowa = row_for("Iowa — county tax sales")
    broken = iowa + "\n{state:'Illinois — county tax sales'"
    fixed = iowa + ",\n{state:'Illinois — county tax sales'"
    if broken in html:
        html = html.replace(broken, fixed, 1)
        changed = True

    wanted = [
        "Alabama — state-held inventory",
        "Nebraska — county tax sales",
        "Arizona — Coconino County OTC liens",
        "Colorado — Jefferson County",
        "Colorado — Weld County",
        "Iowa — county tax sales",
    ]
    missing_rows = []
    for row in NEW_ROWS.split("\n"):
        labels = [x for x in wanted if x in row]
        if labels and labels[0] not in html:
            missing_rows.append(row)

    if missing_rows:
        anchor = "const visible=Object.fromEntries"
        anchor_pos = html.find(anchor)
        if anchor_pos < 0:
            raise SystemExit("Could not find rows-array anchor in index.html")
        rows_end = html.rfind("];", 0, anchor_pos)
        if rows_end < 0:
            raise SystemExit("Could not find end of rows array")
        insertion = (",\n" if not html[:rows_end].rstrip().endswith(",") else "\n") + "\n".join(missing_rows) + "\n"
        html = html[:rows_end] + insertion + html[rows_end:]
        changed = True

    if not changed:
        print("Verified tax-lien market rows already current")
        return

    html = html.replace("Updated August 13, 2026", "Updated August 14, 2026")
    INDEX.write_text(html, encoding="utf-8")
    print("Refreshed verified tax-lien market rows")


if __name__ == "__main__":
    main()
