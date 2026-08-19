#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Story County"

ROW = r'''{state:'Iowa — Story County',product:'Tax sale certificate / property-tax lien',schedule:'Story County publishes a dedicated 2026 Tax Sale page and 2026 tax-sale documents. The county states delinquent taxes are published in May/June and are subject to the annual June tax sale. Verify the exact 2026 sale timing and any adjourned/public-bidder activity from the current Treasurer documents before bidding.',availability:'2026 annual sale cycle published; verify current certificate/adjourned-sale status with Story County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa tax-sale certificates are governed by Iowa Code chapters 446 and 447. Story County describes the process as a tax lien followed, only if statutory redemption and later requirements are satisfied, by a possible tax deed. Do not treat delinquent-tax amounts as opening/minimum bids unless Story County explicitly labels them that way.',bid:'https://www.storycountyiowa.gov/487/Tax-Sale',canadian:'County bidder-registration and tax-identification rules apply. Confirm current Story County eligibility and documentation requirements directly with the Treasurer before attempting registration.',itin:'Verify current Story County and Iowa bidder tax-identification requirements; do not assume an ITIN alone establishes eligibility.',online:'Verify the current 2026 Story County Terms and Conditions; the county publishes the authoritative annual bidder documents on its Tax Sale page.',otc:'Iowa law provides for continued/adjourned and public-bidder sale procedures, but current Story County availability must be verified from the Treasurer rather than inferred.',deed:'A tax-sale certificate creates a lien and does not itself convey ownership. A tax deed is a separate later stage after Iowa statutory redemption, notice, and deed requirements.',special:'MARKET-LEVEL ONLY until Story County exposes a verified machine-readable or safely redistributable 2026 parcel list. The project must not fabricate parcel listings, republish restricted owner/taxpayer names, or confuse sheriff foreclosure sales with the Treasurer tax-sale certificate process.',source:'https://www.storycountyiowa.gov/487/Tax-Sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Story County row already present")
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
    print("Added Iowa Story County tax-lien market")


if __name__ == "__main__":
    main()
