#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Charles County"

ROW = r'''{state:'Maryland — Charles County',product:'Tax Sale Certificate / property-tax lien',schedule:'Charles County held its 2026 tax sale on May 12, 2026. The county conducts its tax sale annually in May; verify the current notice before participating.',availability:'Annual county tax-lien certificate sale. Charles County states that property not sold at tax sale is purchased by the County and is not offered over the counter; the County does not provide an OTC tax-sale property list.',maxReturn:'12%/yr county redemption rate',interest:'Charles County states that interest paid on delinquent taxes, fees, advertising, and miscellaneous costs paid on the day of tax sale is 1% per month, or 12% per year. Subsequent taxes paid by the purchaser do not earn interest under the published county process.',bid:'https://www.charlescountymd.gov/government/fiscal-and-administrative-services/treasury-taxes/your-taxes',canadian:'County-specific. Charles County requires tax-sale bidder registration and a completed IRS Form W-9. Do not assume Canadian or other foreign eligibility; verify current taxpayer-identification and registration requirements directly with the Treasury Division.',itin:'Do not assume an ITIN alone satisfies Charles County bidder eligibility because the published process requires a W-9 at registration. Verify current tax-ID and entity eligibility directly with the County before attempting to participate.',online:'YES — Charles County uses an online tax-sale platform for registration and bidding.',otc:'NO — Charles County states that property not sold at tax sale is purchased by the County and may not be purchased over the counter directly from the County.',deed:'The purchaser receives a tax-sale certificate/lien, not immediate ownership. The owner retains a right of redemption; any later court action to foreclose that right is a separate legal stage.',special:'MARKET-LEVEL ONLY. Charles County conducts a legitimate annual tax-lien certificate sale, but this guide does not bulk republish owner/taxpayer names or a stale parcel inventory. Do not fabricate parcel listings or opening bids, treat delinquent balances or assessed values as bids, or substitute Sheriff judicial-foreclosure or later deed/title proceedings for the original tax-sale certificate.',source:'https://www.charlescountymd.gov/government/fiscal-and-administrative-services/treasury-taxes/your-taxes'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Charles County Maryland row already present")
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
    print("Added Charles County Maryland tax-lien market")


if __name__ == "__main__":
    main()
