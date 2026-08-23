#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Mahaska County"

ROW = r'''{state:'Iowa — Mahaska County',product:'Tax Sale Certificate of Purchase / property-tax lien',schedule:'Annual Treasurer tax sale under Iowa Code Chapter 446; current county site confirms the Treasurer administers tax-sale/redemption activity, but a current 2026 parcel publication suitable for safe bulk republication was not verified.',availability:'MARKET-LEVEL ONLY — verify current tax-sale or adjourned-sale availability directly with Mahaska County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa tax-sale certificates redeem with 2% interest per month under Iowa Code Chapter 447. This is certificate/redemption interest, not immediate ownership of the property.',bid:'https://mahaskacountyia.gov/treasurer/',canadian:'County terms do not clearly state foreign-bidder eligibility. Confirm registration, taxpayer-identification and payment requirements directly with Mahaska County Treasurer before bidding.',itin:'Do not assume an ITIN alone is sufficient. Verify current taxpayer-identification and bidder-registration requirements directly with the Treasurer.',online:'Current auction format was not clearly published on the county Treasurer page reviewed; verify directly with the county before registration.',otc:'County-held tax-sale certificates and tax-sale redemptions exist in county records, but current assignable inventory is not safely inferred from older records. Verify directly with the Treasurer.',deed:'A tax-sale certificate does not itself convey title. If a parcel is not redeemed, a later tax deed requires the separate Iowa statutory notice and redemption process.',special:'MARKET-LEVEL ONLY. Mahaska County currently confirms Treasurer tax-sale/redemption administration but does not expose a verified current machine-readable 2026 parcel feed suitable for bulk republication. Do not fabricate parcel listings or opening bids, do not bulk republish owner/taxpayer names, and do not substitute Sheriff mortgage-foreclosure sales or county tax-deed disposal auctions for the Treasurer tax-sale certificate market.',source:'https://mahaskacountyia.gov/treasurer/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Mahaska County row already present")
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
    print("Added Iowa Mahaska County tax-lien market")


if __name__ == "__main__":
    main()
