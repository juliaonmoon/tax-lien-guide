#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

ROWS = {
    "Indiana — Allen County 2026": r'''{state:'Indiana — Allen County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Allen County\'s official 2026 tax sale is <span class="schedule-date">September 16, 2026</span>. The county currently labels its 2026 Tax Sale List as updated August 20, 2026; eligibility remains dynamic as owners redeem/pay before sale.',availability:'Upcoming — official 2026 list published',interest:'Redemption payments and purchaser return are governed by Indiana Code 6-1.1-24 and 6-1.1-25. Indiana State Board of Accounts guidance describes 110% of the minimum bid for redemption within six months and 115% after six months but before one year, plus 10% annual interest on qualifying amounts above the minimum bid and certain later taxes/assessments. Verify the current county handout for the specific sale.',bid:'https://www.allencounty.in.gov/270/Tax-Sale',canadian:'Not confirmed — verify current Allen County/GovEase bidder-registration and U.S. taxpayer-form requirements before participating',itin:'Do not assume an ITIN alone is sufficient; verify the sale vendor\'s current registration requirements',online:'Allen County publishes current 2026 sale instructions on its official Tax Sale page; verify the linked current-year handout before registering',otc:'NO for the annual tax sale; Allen County notes that certain unsold parcels may later be handled through the county/ACCDC process, which is a different disposition path',deed:'Purchaser receives a tax-sale certificate/lien first. A tax deed is not immediate; statutory redemption and notice procedures apply.',special:'MARKET-LEVEL SUMMARY ONLY. Allen County warns that federal tax liens may survive unless the purchaser separately obtains a federal Certificate of Discharge. Treat the county\'s current list as dynamic because parcels can be removed before sale. Do not bulk republish owner names or treat a prior snapshot as guaranteed current inventory.',source:'https://www.allencounty.in.gov/270/Tax-Sale'}''',
    "Indiana — Lake County 2026": r'''{state:'Indiana — Lake County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Lake County\'s official 2026 electronic tax sale begins <span class="schedule-date">September 4, 2026</span> at 5:30 PM local time, with properties closing in batches beginning September 7, 2026. Registration for this annual sale closed August 14, 2026.',availability:'Upcoming — official 2026 tax-sale notice and public property-list link published',interest:'Indiana redemption mechanics are not a simple APR. Lake County states redemption is 110% of the minimum bid if redeemed within six months or 115% after six months but before one year, plus the purchase-price excess over the minimum bid and 5% annual interest on that excess; qualifying later taxes/assessments paid by the purchaser also earn 5% annual interest. Verify the current county notice and Indiana Code for the exact parcel.',bid:'https://lakecountyin.gov/departments/treasurer/lake-county-tax-sale-notice-2026',canadian:'Annual-auction registration requires IRS Form W-9 and county/vendor approval. A non-U.S. person should not assume W-8 or an ITIN is accepted; verify eligibility directly with Lake County before relying on the auction.',itin:'Do not assume an ITIN alone satisfies the annual-auction W-9 requirement. Business entities must also meet Lake County\'s stated Indiana certificate-of-existence/foreign-registration requirement.',online:'YES — Lake County states the 2026 tax sale is conducted electronically through ZeusAuction. The county also links a public SRI property list; do not bypass auction registration controls.',otc:'NO for the annual tax sale. County-struck certificates and later certificate-sale/disposition processes are legally distinct and should not be treated as the September annual auction.',deed:'Purchaser receives a tax-sale certificate/lien first. A tax deed is not immediate; Lake County states a redemption period applies and later deed procedures are governed separately by Indiana law.',special:'MARKET-LEVEL SUMMARY ONLY. Lake County publishes a current tax-sale notice and a public SRI property-list link, but the county warns that eligibility and minimum bid amounts can change before auction. The statutory minimum bid is based on delinquent/current taxes, penalties, prescribed costs, and certain prior-sale costs. Do not bulk republish owner names, do not infer a stale parcel list as guaranteed auction inventory, and do not confuse Sheriff/judicial foreclosure sales with this Treasurer tax sale.',source:'https://lakecountyin.gov/departments/treasurer/lake-county-tax-sale-notice-2026'}''',
    "Indiana — Porter County 2026": r'''{state:'Indiana — Porter County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Porter County\'s official 2026 Tax Sale will be held online <span class="schedule-date">October 21–22, 2026</span>. The county says additional 2026 sale information will be posted later.',availability:'Upcoming — official 2026 sale dates published; current 2026 parcel results/list not republished here',interest:'Indiana redemption mechanics are statutory penalties/interest rather than a simple APR. Porter County states the standard redemption period after a tax sale is one year; certificate-sale and certain county-held paths use a 120-day redemption period. Verify the current county/SRI handout and Indiana Code 6-1.1-24 and 6-1.1-25 for the exact parcel and sale path.',bid:'https://portercountyin.gov/1036/Tax-SaleCertificate-Sale',canadian:'Not confirmed — verify current Porter County/SRI bidder registration and U.S. taxpayer-form requirements directly before participating.',itin:'Do not assume an ITIN or W-8 alone is accepted; verify the current SRI/Porter County registration requirements.',online:'YES — Porter County states its 2026 Tax Sale will be held online. Use the county page and its official SRI link for current registration and sale details.',otc:'Not a walk-in annual auction. Porter County states unsold tax-sale properties may later be certified to the Board of Commissioners and offered through a separate Certificate Sale, generally in the following spring.',deed:'Purchaser receives a tax-sale certificate/lien first. Porter County separately describes redemption after the tax sale and certificate sale; a tax deed is not immediate.',special:'MARKET-LEVEL SUMMARY ONLY. Porter County Ordinance No. 00-7 states tax-sale results can only be requested in person at the Auditor\'s office and cannot be distributed electronically. Do not bulk republish sale results, owner names, or prior-year parcel lists. Do not infer current 2026 inventory or opening/minimum bids, and do not confuse Sheriff mortgage-foreclosure sales with the Treasurer/Auditor tax sale.',source:'https://portercountyin.gov/1036/Tax-SaleCertificate-Sale'}''',
}


def ensure_row(text: str, marker: str, row: str) -> tuple[str, str]:
    if marker in text:
        row_re = re.compile(
            rf"\{{state:'{re.escape(marker)}'.*?\}}(?=\s*,|\s*\n\];)",
            re.S,
        )
        updated, count = row_re.subn(row, text, count=1)
        if count != 1:
            raise SystemExit(f"Could not uniquely refresh {marker}")
        return updated, "Refreshed"

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before = text[:end]
    after = text[end:]
    insertion = "\n" + row if before.rstrip().endswith(',') else ",\n" + row
    return before + insertion + after, "Added"


def main():
    text = INDEX.read_text(encoding="utf-8")
    actions = []
    for marker, row in ROWS.items():
        text, action = ensure_row(text, marker, row)
        actions.append(f"{action} {marker} tax-lien market")

    INDEX.write_text(text, encoding="utf-8")
    for action in actions:
        print(action)


if __name__ == "__main__":
    main()
