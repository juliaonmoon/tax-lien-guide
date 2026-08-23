#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Mills County"

ROW = r'''{state:'Iowa — Mills County',product:'Tax Sale Certificate of Purchase / property-tax lien',schedule:'Mills County held its 2026 annual online tax sale on June 15, 2026. The Treasurer states that adjourned tax sales may be held on later business days when bidders are present and parcels remain available.',availability:'2026 annual sale passed; verify current adjourned-sale or assignment availability directly with Mills County Treasurer',maxReturn:'2%/month redemption interest',interest:'Mills County states that redemption includes the Tax Sale Certificate of Purchase amount plus 2% interest per month. The certificate is a tax-sale lien interest, not immediate ownership of the property.',bid:'https://www.millscountyiowa.gov/246/Tax-Sale-Information',canadian:'The 2026 Mills County packet requires online registration, a completed W-9, and bidder eligibility under county/Iowa rules. Do not assume foreign eligibility; confirm current identification and tax-document requirements directly with the Treasurer before registering.',itin:'The 2026 packet requires a W-9 and applicable U.S. taxpayer identification information. Verify current eligibility directly with Mills County; an ITIN alone should not be assumed sufficient.',online:'Yes — the June 15, 2026 sale used the county-designated Iowa Tax Auction system. Verify any current adjourned-sale procedure with the Treasurer.',otc:'Mills County states adjourned sales may occur after the annual sale when parcels remain. Treat current availability as county-specific and do not infer inventory from delinquent balances or prior publications.',deed:'A Tax Sale Certificate of Purchase does not itself convey title. A later Treasurer’s Deed requires the separate Iowa statutory notice and redemption process.',special:'MARKET-LEVEL ONLY. This integration uses Mills County’s official 2026 tax-sale packet and Treasurer guidance but does not bulk republish parcel or owner/taxpayer records. Do not fabricate parcel listings or opening bids, and do not substitute Mills County Sheriff levy/foreclosure sales for the Treasurer tax-sale certificate market.',source:'https://www.millscountyiowa.gov/246/Tax-Sale-Information'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Mills County row already present")
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
    print("Added Iowa Mills County tax-lien market")


if __name__ == "__main__":
    main()
