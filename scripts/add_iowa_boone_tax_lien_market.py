#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Boone County"

ROW = r'''{state:'Iowa — Boone County',product:'Tax sale certificate / property-tax lien',schedule:'Boone County administers an annual tax sale in June under Iowa Code Chapter 446. The Treasurer says delinquent parcels are advertised in June and offered through an open competitive bidding process. Verify the current 2026 adjourned/public-bidder availability directly with the Treasurer.',availability:'2026 annual June sale passed; verify current adjourned/public-bidder certificate availability with Boone County Treasurer',maxReturn:'2%/month redemption interest',interest:'Boone County states redemption requires the amount for which the parcel was sold plus 2% interest per month, with additional qualifying amounts potentially accruing. A tax-sale certificate is a lien interest, not immediate ownership.',bid:'https://www.boonecounty.iowa.gov/treasurer/tax_sale/',canadian:'County and auction-platform bidder-registration rules apply. Confirm current eligibility, identification, payment, and tax-document requirements before registering.',itin:'Verify Boone County and the county-designated Iowa tax auction bidder tax-identification requirements; do not assume an ITIN alone establishes eligibility.',online:'Boone County directs bidders to its county-designated Iowa Tax Auction registration process; verify current sale/adjourned-sale format with the Treasurer.',otc:'Iowa public-bidder or adjourned-sale availability is county-specific. Verify live availability with Boone County Treasurer; do not infer inventory from delinquent balances or newspaper advertisements.',deed:'The tax-sale certificate is a lien interest, not ownership. Boone County states that if the lien is not redeemed within the period specified by Iowa law, the purchaser may later initiate separate proceedings to obtain a tax deed.',special:'MARKET-LEVEL ONLY. Boone County advertises delinquent parcels and makes lists available through the Treasurer/publication process, but this integration does not bulk republish parcel or owner/taxpayer data. Do not fabricate parcel listings or opening bids, and do not substitute Boone County Sheriff mortgage-foreclosure sales for the Treasurer tax-sale certificate market.',source:'https://www.boonecounty.iowa.gov/treasurer/tax_sale/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start >= 0:
        # Restore the canonical county-authored market row before validation.
        # Shared presentation normalizers may rewrite display wording later, so
        # merely checking for MARKER is not sufficient for an idempotent repair.
        end = text.find("}\n", start)
        comma = text.find("},", start)
        if comma >= 0 and (end < 0 or comma < end):
            end = comma + 1
        elif end >= 0:
            end += 1
        else:
            raise SystemExit("Could not find end of existing Boone County row")
        existing = text[start:end]
        if existing == ROW:
            print("Iowa Boone County canonical row already present")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Iowa Boone County tax-lien market row")
        return

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before = text[:end]
    after = text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Iowa Boone County tax-lien market")


if __name__ == "__main__":
    main()
