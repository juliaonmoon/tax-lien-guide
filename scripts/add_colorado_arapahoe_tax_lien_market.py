#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Arapahoe County"

ROW = r'''{state:'Colorado — Arapahoe County',product:'Tax lien / Certificate of Purchase',schedule:'Arapahoe County states that its 2025 delinquent-tax lien sale will be held online on <span class="schedule-date">Nov 5, 2026</span>. The county says the annual tax-sale publication is available in October and also links county-held certificates available for purchase.',availability:'Upcoming annual tax-lien sale — Nov 5, 2026. County-held certificates are a separate, changing inventory; verify the official county file before treating any certificate as currently available.',maxReturn:'2026 rate set Sep 1; 2025 was 14%/yr',interest:'Arapahoe County states the redemption interest rate is determined by September 1 each year at nine points above the federal discount rate, and that the 2025 tax-lien sale rate was 14%. Do not reuse 14% as the 2026 rate until the county publishes the applicable 2026 rate. Premium bidding determines the winning lien; do not treat premium as interest-bearing principal.',bid:'https://files.arapahoeco.gov/your_county/county_departments/treasurer/tax_lien_sale/index.php',canadian:'Foreign-bidder eligibility is not clearly stated in the public county instructions. Arapahoe says online registration generates an IRS W-9 for the county, so non-U.S. persons should confirm acceptable tax documentation and eligibility with the Treasurer before funding.',itin:'County instructions describe W-9 based registration; acceptable ITIN/foreign taxpayer documentation is not clearly stated. Verify with the Treasurer.',online:'YES — Arapahoe conducts the tax-lien auction online through its official tax-sale site.',otc:'YES — the Treasurer links a County Held Certificates Available for Purchase file. Inventory changes; the link is a research source, not proof that a particular certificate remains available.',deed:'A tax-lien Certificate of Purchase is not immediate ownership. Arapahoe states that for real property the lien must be at least 3 years old before the purchaser may apply for a Treasurer’s Deed. Keep that later deed process distinct from the annual tax-lien sale and county-held certificate purchases.',special:'MARKET-LEVEL ONLY. This row covers Treasurer tax liens, not a later Treasurer’s Deed/public auction or Public Trustee foreclosure. Arapahoe warns that tax liens may not be first or only liens and bidders must perform their own due diligence. Do not fabricate parcel inventory, opening/minimum bids, lien/payoff amounts, current county-held availability, ownership/property characteristics, redemption outcomes, or deed outcomes, and do not bulk republish owner/taxpayer names.',source:'https://files.arapahoeco.gov/your_county/county_departments/treasurer/tax_lien_sale/tax_lien_sale_information.php'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Arapahoe County marker but could not locate row start")
    row_end = text.find("}\n", marker_pos)
    if row_end < 0:
        row_end = text.find("},\n", marker_pos)
        if row_end < 0:
            raise SystemExit("Found Arapahoe County marker but could not locate row end")
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Arapahoe County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Arapahoe County tax-lien market row")
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
