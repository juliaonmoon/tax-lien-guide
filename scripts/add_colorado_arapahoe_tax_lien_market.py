#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Arapahoe County"

ROW = r'''{state:'Colorado — Arapahoe County',product:'Tax lien / Certificate of Purchase',schedule:'Arapahoe County states that its 2025 delinquent-tax lien sale will be held online on <span class="schedule-date">Nov 5, 2026</span>. The county expects the 2026 sale files in early to mid-October and also publishes county-held certificates available for purchase.',availability:'Upcoming — Nov 5, 2026',maxReturn:'2026 rate set Sep 1; 2025 was 14%/yr',interest:'Colorado redemption interest is set annually on September 1 at nine percentage points above the federal discount rate. Arapahoe states the 2025 tax-lien sale rate was 14%. Premium bidding determines the winning lien; do not treat premium as interest-bearing principal.',bid:'https://files.arapahoeco.gov/your_county/county_departments/treasurer/tax_lien_sale/index.php',canadian:'Foreign-bidder eligibility is not clearly stated. Arapahoe says online registration generates an IRS W-9 for the county, so non-U.S. persons should confirm acceptable tax documentation and eligibility with the Treasurer before funding.',itin:'County instructions describe W-9 based registration; acceptable ITIN/foreign taxpayer documentation is not clearly stated. Verify with the Treasurer.',online:'YES — Arapahoe conducts the tax-lien auction online through its official tax-sale site.',otc:'YES — the Treasurer publishes a County Held Certificates Available for Purchase file; inventory changes and should be verified from the official page.',deed:'A tax-lien Certificate of Purchase is not immediate ownership. For real property, Arapahoe states the lien generally must be at least 3 years old before the holder may begin the Treasurer’s Deed process. Colorado changed the later deed/public-auction procedure effective June 1, 2026.',special:'This row covers the Treasurer tax-lien sale, not a later Treasurer’s Deed/public auction. Arapahoe warns that tax liens may not be first or only liens and bidders must perform their own due diligence. The 2026 redemption rate is not published until September 1; do not substitute the 2025 14% rate as a guaranteed 2026 rate.',source:'https://files.arapahoeco.gov/your_county/county_departments/treasurer/tax_lien_sale/tax_lien_sale_information.php'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Arapahoe County row already present")
        return

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Colorado Arapahoe County tax-lien market")


if __name__ == "__main__":
    main()
