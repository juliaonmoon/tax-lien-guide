#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Chickasaw County"

ROW = r'''{state:'Iowa — Chickasaw County',product:'Tax Sale Certificate of Purchase / property-tax lien',schedule:'Annual online Treasurer tax sale held June 15, 2026; adjourned tax sales may follow on business days when bidders are present and parcels remain available.',availability:'2026 annual sale passed; verify current adjourned-sale or assignment availability directly with Chickasaw County Treasurer',maxReturn:'2%/month redemption interest',interest:'Chickasaw County states redemption includes 2% interest per month on the amount for which the parcel was sold, with each fraction of a month counted as a whole month. Iowa Code Chapter 447 governs redemption. This is certificate/redemption interest, not immediate ownership of the property.',bid:'https://chickasawcounty.iowa.gov/treasurer/2024_tax_sale/',canadian:'Current county terms require bidder registration and tax documentation; foreign-bidder eligibility is not clearly stated. Confirm eligibility directly with Chickasaw County Treasurer before registering.',itin:'Do not assume an ITIN alone is sufficient. Verify current taxpayer-identification and bidder-registration requirements directly with the Treasurer.',online:'Yes — Chickasaw County states bidders place bids online through the county-designated Iowa tax auction system.',otc:'Adjourned tax sales may be held after the annual sale when bidders are present and parcels remain. Verify current inventory directly with the Treasurer; do not infer availability from delinquent balances.',deed:'A tax-sale certificate does not itself convey title. If a parcel is not redeemed, a later deed requires the separate Iowa statutory notice and redemption process.',special:'MARKET-LEVEL ONLY. Chickasaw County publishes detailed 2026 tax-sale terms, but this guide does not bulk republish taxpayer/owner names or infer a current parcel inventory from the annual publication. Do not fabricate parcel listings or opening bids, and do not substitute Sheriff mortgage-foreclosure sales for the Treasurer tax-sale certificate market.',source:'https://chickasawcounty.iowa.gov/treasurer/2024_tax_sale/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Chickasaw County row already present")
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
    print("Added Iowa Chickasaw County tax-lien market")


if __name__ == "__main__":
    main()
