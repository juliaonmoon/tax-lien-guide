#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Marshall County"

ROW = r'''{state:'Iowa — Marshall County',product:'Tax Sale Certificate of Purchase / property-tax lien',schedule:'Iowa Code §446.7 requires the annual county tax sale on the third Monday in June unless the Treasurer designates another June date for good cause; in 2026 that statutory date was June 15. Marshall County confirms it conducts the annual tax sale for delinquent property taxes.',availability:'2026 annual sale passed; verify any adjourned sale or other current availability directly with Marshall County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa Code §447.1 provides 2% interest per month on redemption of qualifying tax-sale certificates, counting each fraction of a month as a full month. This is a tax-sale certificate/lien interest, not immediate ownership of the property.',bid:'https://www.marshallcountyia.gov/460/Property-Tax',canadian:'County registration and tax-document requirements are not clearly published for foreign bidders on the current public page. Confirm current eligibility directly with Marshall County Treasurer before registering.',itin:'Do not assume an ITIN alone is sufficient. Verify current taxpayer-identification and bidder-registration requirements directly with Marshall County Treasurer.',online:'Marshall County confirms it conducts the annual tax sale; the current public page does not clearly publish the 2026 auction platform or a current bidder portal, so verify the active procedure with the Treasurer.',otc:'County-specific. Iowa law permits adjourned tax-sale procedures, but do not infer current Marshall County inventory from delinquent balances or prior publications.',deed:'A tax-sale certificate does not itself convey title. A later tax deed requires the separate Iowa statutory notice and redemption process.',special:'MARKET-LEVEL ONLY. Marshall County confirms an annual Treasurer tax sale, but no current machine-readable 2026 parcel inventory suitable for safe republication was verified. Do not fabricate parcel listings or opening bids, do not bulk republish owner/taxpayer names, and do not substitute Sheriff mortgage-foreclosure sales for the Treasurer tax-sale certificate market.',source:'https://www.marshallcountyia.gov/460/Property-Tax'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Marshall County row already present")
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
    print("Added Iowa Marshall County tax-lien market")


if __name__ == "__main__":
    main()
