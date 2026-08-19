#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Dallas County"

ROW = r'''{state:'Iowa — Dallas County',product:'Tax sale certificate / property-tax lien',schedule:'2026 annual Dallas County tax sale was held on June 15, 2026. The Treasurer publishes an official 2026 Delinquent Tax List (XLS) and administers the sale under Iowa Code Chapter 446.',availability:'2026 annual sale passed; verify any subsequent/public-bidder activity with the Dallas County Treasurer',maxReturn:'2%/month redemption interest',interest:'Dallas County states redemption requires the amount for which the parcel was sold plus 2% interest per month, with additional amounts potentially accruing. Do not treat delinquent-tax amounts or sheriff-sale judgment amounts as tax-lien opening bids.',bid:'https://www.dallascountyiowa.gov/252/Tax-Sale',canadian:'Dallas County requires bidder registration and taxpayer-identification documentation. Confirm current non-U.S.-bidder eligibility and documentation directly with the Treasurer before funding.',itin:'The county publishes a W-9 form for bidder tax identification; do not assume an ITIN/W-8 pathway is accepted without Treasurer confirmation.',online:'Verify current auction format with the Treasurer; the official 2026 page confirms the annual sale date and delinquent-tax list but should control over any older instructions.',otc:'Subsequent/public-bidder availability is governed by Iowa law and county procedure; verify current status directly with the Treasurer.',deed:'A tax-sale certificate is a lien and does not itself convey property ownership. Any later tax deed follows Iowa statutory redemption and notice procedures and is distinct from Dallas County Sheriff mortgage-foreclosure sales.',special:'Dallas County publishes an official 2026 Delinquent Tax List in XLS format. Automated retrieval currently encounters a redirect loop from the county document endpoint, so this guide adds the county at market level only and does not fabricate parcel rows. Sheriff foreclosure listings are explicitly excluded from the tax-lien dataset.',source:'https://www.dallascountyiowa.gov/252/Tax-Sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Dallas County row already present")
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
    print("Added Iowa Dallas County tax-lien market")


if __name__ == "__main__":
    main()
