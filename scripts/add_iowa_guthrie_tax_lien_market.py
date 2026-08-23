#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Guthrie County"

ROW = r'''{state:'Iowa — Guthrie County',product:'Tax Sale Certificate of Purchase / property-tax lien',schedule:'2026 annual Treasurer tax sale was June 15, 2026 at 9:00 a.m. and was conducted online. Verify the current-year Treasurer notice before participating.',availability:'Annual June tax sale; qualifying unpaid parcels are published in the county official publication in late May, and the bidder-site list is updated nightly for registered bidders. Verify any later Public Bidder Sale or other availability directly with Guthrie County Treasurer.',maxReturn:'2%/month redemption interest',interest:'Guthrie County states that tax-sale certificates accrue 2% interest per month during the Iowa redemption period. This is certificate/redemption interest, not ownership of the property.',bid:'https://www.guthriecounty.gov/treasurer/tax_sale/',canadian:'County-specific. Confirm current bidder registration, taxpayer-ID, residency, payment, and eligibility requirements directly with Guthrie County Treasurer before attempting to participate.',itin:'Do not assume an ITIN alone satisfies bidder eligibility. Verify current taxpayer-ID and registration requirements directly with the Treasurer and the county-designated auction system.',online:'YES — Guthrie County states its annual tax sale is held online and its June 15, 2026 calendar entry identifies the county-designated online auction.',otc:'County-specific. Guthrie County states delinquencies remaining unsold after required offerings may enter a Public Bidder Sale. Verify current inventory and procedures directly with the Treasurer; do not infer current availability from an older delinquent-tax publication.',deed:'A tax-sale purchase does not transfer ownership. Guthrie County states taxes must remain unpaid for at least one year and nine months before an investor may begin the separate statutory process that can lead to a tax sale deed.',special:'MARKET-LEVEL ONLY. Guthrie County publishes qualifying unpaid parcels in its official publication and provides a nightly-updated bidder-site list for registered bidders, but no unrestricted machine-readable current parcel feed was verified for safe republication. Do not bulk republish owner/taxpayer names, fabricate parcel inventory or opening bids, treat delinquent-tax amounts as opening bids, bypass registration controls, or substitute Sheriff mortgage-foreclosure sales for Treasurer tax-sale certificates.',source:'https://www.guthriecounty.gov/treasurer/tax_sale/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Guthrie County Iowa row already present")
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
    print("Added Guthrie County Iowa tax-lien market")


if __name__ == "__main__":
    main()
