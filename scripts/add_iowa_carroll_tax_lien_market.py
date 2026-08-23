#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Carroll County"

ROW = r'''{state:'Iowa — Carroll County',product:'Tax Sale Certificate of Purchase / property-tax lien',schedule:'Annual Treasurer tax sale is held on the third Monday in June at 10:00 a.m. Carroll County requires participants to register with the Treasurer by 4:30 p.m. on the Thursday before the sale; verify the current year notice before participating.',availability:'Annual June sale — verify current adjourned or county-held certificate availability directly with Carroll County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa Code 2026 §447.1 provides 2% interest per month on tax-sale redemption amounts, counting each fraction of a month as a full month. This is certificate/redemption interest, not ownership of the property.',bid:'https://www.carrollcountyiowa.gov/pview.aspx?catid=0&id=21053',canadian:'County-specific. Confirm current registration, taxpayer-ID/tax-form, residency, payment, and bidder eligibility directly with Carroll County Treasurer before attempting to participate.',itin:'Do not assume an ITIN alone satisfies bidder eligibility. Verify current taxpayer-ID and registration requirements directly with Carroll County Treasurer.',online:'NO current online-sale claim from the county source. Carroll County currently states the annual tax sale is held at the Treasurer\'s Office; verify the current-year notice because procedures may change.',otc:'County-specific. Verify any adjourned or county-held certificate availability directly with the Treasurer; do not infer current inventory from an older delinquent-tax list.',deed:'A tax-sale certificate is a lien interest and does not itself convey title. Any later tax deed requires the separate Iowa statutory notice and redemption process.',special:'MARKET-LEVEL ONLY. Carroll County officially confirms it conducts the annual tax sale for delinquent taxes and publishes the recurring third-Monday-in-June schedule, but no unrestricted machine-readable current parcel feed was verified for safe republication. Do not bulk republish owner/taxpayer names, fabricate parcel inventory or opening bids, treat delinquent-tax amounts as opening bids, bypass registration controls, or substitute Sheriff mortgage-foreclosure sales for Treasurer tax-sale certificates.',source:'https://www.carrollcountyiowa.gov/pview.aspx?catid=0&id=20971'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Carroll County Iowa row already present")
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
    print("Added Carroll County Iowa tax-lien market")


if __name__ == "__main__":
    main()
