#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — El Paso County"

ROW = r'''{state:'Colorado — El Paso County',product:'Tax lien / Tax Lien Sale Certificate of Purchase',schedule:'El Paso County conducts one annual online tax-lien sale through RealAuction. As of Aug 28, 2026, the Treasurer\'s official page publishes the 2025-property-tax (payable in 2026) delinquent-tax advertisement dates as Sep 16, Sep 23 and Sep 30, 2026, but does not yet publish a 2026 auction date or the 2026 redemption-interest rate.',availability:'2026 delinquent-tax publication dates are officially posted; exact 2026 auction date, sale inventory and redemption rate remain pending official publication.',maxReturn:'2026 rate not yet published; do not carry forward the 2025 14%/yr rate',interest:'Colorado sets the redemption rate each year at nine percentage points above the federal discount rate in effect on September 1. El Paso County states the 2025 tax-lien-sale rate was 14% annually (1.17% monthly). Premium/bonus bids are not part of the redemption amount and do not earn interest, so the guide does not treat them as interest-bearing principal or reuse the 2025 rate as a 2026 return.',bid:'https://treasurer.elpasoco.com/tax-lien-sale/',canadian:'Foreign-bidder eligibility is not clearly established in the official county material reviewed. El Paso County reports interest on redeemed certificates to the IRS and issues 1099 forms, so non-U.S. bidders should confirm registration, taxpayer-ID, withholding and payment requirements directly with the Treasurer / RealAuction before funding.',itin:'Official public instructions do not establish that an ITIN alone is sufficient. Verify current taxpayer-identification and withholding requirements directly with El Paso County Treasurer / RealAuction.',online:'YES — El Paso County states its annual Tax Lien Sale is conducted online through RealAuction.',otc:'CONDITIONAL — unsold tax liens are struck off to the County and may be available for assignment after Treasurer review; not every county-held lien is eligible. Do not treat the existence of a county-held list as proof that any specific lien is currently assignable.',deed:'A Tax Lien Sale Certificate of Purchase is a lien, not ownership or a right of possession. After the statutory redemption period, an eligible certificate holder may enter the separate Treasurer’s Deed/public-auction process; a deed is not automatic.',special:'MARKET-LEVEL ONLY. Keep El Paso County’s annual tax-lien sale separate from Public Trustee foreclosure sales and from the later Treasurer’s Deed/public-auction process. The county explicitly says buying a tax lien gives no ownership, possession, use, improvement or access rights. Do not fabricate parcel inventory, opening/minimum bids, lien/payoff amounts, current county-held availability, ownership/property characteristics, redemption outcomes, or deed outcomes, and do not bulk republish owner/taxpayer names.',source:'https://treasurer.elpasoco.com/tax-lien-sale/'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found El Paso County marker but could not locate row start")
    row_end = text.find("}\n", marker_pos)
    if row_end < 0:
        row_end = text.find("},\n", marker_pos)
        if row_end < 0:
            raise SystemExit("Found El Paso County marker but could not locate row end")
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado El Paso County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado El Paso County tax-lien market row")
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
    print("Added Colorado El Paso County tax-lien market")


if __name__ == "__main__":
    main()
