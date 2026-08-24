#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Prince George's County"

ROW = r'''{state:'Maryland — Prince George\'s County',product:'Tax Sale Certificate / property-tax lien',schedule:'Prince George\'s County held its 2026 internet-based tax sale on May 11, 2026. The 2026 assignment sale for certificates left unsold began June 10, 2026 after the county posted its assignment list.',availability:'Annual Internet-based sealed-bid tax-lien certificate sale using the high-bid-premium method. Unsold 2026 certificates may be purchased through the county assignment-sale process while the official list remains available. Verify current availability directly with the county before acting.',maxReturn:'2026 redemption rate: 10%/yr owner-occupied; 20%/yr non-principal residence or unimproved parcel',interest:'Beginning with the FY2026 sale, Prince George\'s County states 10% per annum for owner-occupied property and heirs of deceased owners, and 20% per annum for non-principal residences and unimproved parcels. High-bid premium amounts do not earn interest and are not part of certificate yield.',bid:'https://taxsale.princegeorgescountymd.gov/',canadian:'County-specific. The 2026 auction required online registration, ACH funding, and an IRS W-9. Do not assume a non-U.S. bidder qualifies; verify current taxpayer-ID and banking requirements directly with Prince George\'s County.',itin:'Do not assume an ITIN alone satisfies bidder eligibility. The 2026 registration required a completed IRS W-9 and U.S.-dollar ACH/bank information; verify current county rules before participating.',online:'YES — the annual tax-lien certificate auction is Internet-based. The post-sale assignment process is handled separately under the county\'s published instructions.',otc:'YES, when county-owned/unsold certificates are listed. For 2026, assignment-sale requests began June 10 and certificates were offered at tax value on a first-come, first-served basis under county instructions. Availability changes as certificates are assigned or redeemed.',deed:'The purchaser receives a certificate of sale / tax lien, not immediate ownership. The owner retains title unless and until the right of redemption is later foreclosed and a deed is issued through the separate legal process.',special:'MARKET-LEVEL ONLY. Prince George\'s County publishes current tax-sale and assignment information, but the property lists contain owner information and change as accounts are paid, redeemed, or assigned. This guide does not bulk republish owner/taxpayer names, does not treat assessed value or delinquent balances as fabricated opening bids, and does not substitute later foreclosure/deed records for tax-sale certificates.',source:'https://taxsale.princegeorgescountymd.gov/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Prince George's County Maryland row already present")
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
    print("Added Prince George's County Maryland tax-lien market")


if __name__ == "__main__":
    main()
