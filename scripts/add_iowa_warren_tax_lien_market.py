#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Warren County"

ROW = r'''{state:'Iowa — Warren County',product:'Tax sale certificate / property-tax lien',schedule:'Warren County publishes a dedicated 2026 Tax Sale page and an official 2026 Tax Sale Publication List. Verify current Treasurer notices for any adjourned/public-bidder activity before bidding.',availability:'2026 annual tax-sale materials published; verify current certificate/adjourned-sale status with Warren County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa tax-sale certificates are governed by Iowa Code chapters 446 and 447. Warren County states that delinquent taxes may result in a tax-sale certificate; the certificate is a lien and does not itself convey ownership. Do not treat published delinquent-tax amounts as opening/minimum bids unless Warren County explicitly labels them that way.',bid:'https://www.warrencountyia.gov/government/county-government/treasurer/tax-sale/',canadian:'County bidder-registration and tax-identification rules apply. Confirm current Warren County eligibility and documentation requirements directly with the Treasurer before attempting registration.',itin:'Verify current Warren County and Iowa bidder tax-identification requirements; do not assume an ITIN alone establishes eligibility.',online:'Verify the current 2026 Warren County Tax Sale Information and bidder documents from the Treasurer before registration.',otc:'Iowa law provides for continued/adjourned and public-bidder procedures, but current Warren County availability must be verified from the Treasurer rather than inferred.',deed:'A tax-sale certificate creates a lien and does not itself convey ownership. A tax deed is a separate later stage after Iowa statutory redemption, notice, and deed requirements.',special:'MARKET-LEVEL ONLY. Warren County publishes an official 2026 property list, but the PDF is a multi-column publication whose machine-readable text layers do not safely recover the complete real-estate item set: three official item markers are absent from every tested text layer and many extracted dollar amounts conflict across columns. Do not fabricate, infer, or republish property-level rows until a complete legitimate source or unambiguous extraction path is available. Owner/taxpayer names must not be bulk-published.',source:'https://www.warrencountyia.gov/government/county-government/treasurer/tax-sale/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Warren County row already present")
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
    print("Added Iowa Warren County tax-lien market")


if __name__ == "__main__":
    main()
