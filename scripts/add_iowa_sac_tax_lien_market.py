#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Sac County"

ROW = r'''{state:'Iowa — Sac County',product:'Tax Sale Certificate of Purchase / property-tax lien',schedule:'Annual tax sale takes place in June. Sac County states delinquent parcels are advertised in June and offered through an open competitive bidding process under Iowa Code Chapter 446; verify any current or adjourned availability directly with the Treasurer.',availability:'Annual June sale — verify current/adjourned certificate availability directly with Sac County Treasurer',maxReturn:'2%/month redemption interest',interest:'Sac County states Iowa tax-sale redemptions pay 2% interest per month. This is certificate/redemption interest, not ownership of the property.',bid:'https://www.saccountyiowa.gov/treasurer/property_tax/',canadian:'County-specific. Confirm current registration, taxpayer-ID/tax-form, residency, payment, and bidder eligibility directly with Sac County before attempting to bid.',itin:'Do not assume an ITIN alone satisfies bidder eligibility. Verify current taxpayer-ID and tax-form requirements directly with Sac County Treasurer.',online:'YES — Sac County directs bidders to Iowa Tax Auction for registration and online bidding.',otc:'County-specific. Sac County notes adjourned tax sales may be held when parcels remain available; verify current inventory directly with the Treasurer and do not infer availability from older lists.',deed:'A tax-sale certificate is a lien interest and does not itself convey title. Any later tax deed requires the separate Iowa statutory notice/redemption process.',special:'MARKET-LEVEL ONLY. Sac County officially confirms its annual June Treasurer tax sale, online bidder registration, and 2%/month redemption interest, but no unrestricted machine-readable current parcel feed was verified for safe republication. Do not bulk republish owner/taxpayer names, fabricate parcel inventory or opening bids, treat delinquent-tax amounts as opening bids, bypass bidder-registration controls, or substitute Sheriff mortgage-foreclosure sales for Treasurer tax-sale certificates.',source:'https://www.saccountyiowa.gov/treasurer/property_tax/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Sac County Iowa row already present")
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
    print("Added Sac County Iowa tax-lien market")


if __name__ == "__main__":
    main()
