#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Boulder County"

ROW = r'''{state:'Colorado — Boulder County',product:'Tax lien / Tax Lien Sale Certificate of Purchase',schedule:'Boulder County holds an annual real-property tax-lien sale. As of Aug 28, 2026, the official tax-lien page still shows the Nov 14, 2025 real-property sale and has not published a 2026 real-property sale date or list. The county says the auction list is published close to the sale and updated weekly once posted.',availability:'2026 real-property tax-lien sale schedule/list not yet published on the official county page; verify the county page before treating any parcel or date as current.',maxReturn:'2026 rate not yet published; 2025 was 14%/yr',interest:'Colorado sets the redemption interest rate each September. Boulder County states the 2025 rate was 14% per annum. Premium bids do not earn interest and are not returned, so the guide does not treat premium as principal or reuse the 2025 rate as the 2026 rate.',bid:'https://bouldercounty.gov/property-and-land/treasurer/taxes/tax-lien-sale/',canadian:'Boulder County requires bidder registration with a Social Security or Tax ID number and a completed signed IRS W-9. The reviewed official materials do not establish a W-8/non-U.S.-person alternative, so foreign eligibility should be confirmed directly with the Treasurer before planning to bid.',itin:'Official FAQ requires a Social Security or Tax ID number plus signed IRS W-9; it does not state whether an ITIN alone or W-8 is accepted for a non-U.S. bidder.',online:'No — the official FAQ describes an in-person sale at the Boulder County Courthouse unless the county publishes a different 2026 format.',otc:'NO — Boulder County explicitly states it does not offer tax lien certificates over the counter.',deed:'The certificate is a lien, not ownership. Beginning three years after purchase, a lienholder may apply for a separate public auction for a Certificate of Option for Treasurer’s Deed, subject to statutory notice and redemption.',special:'MARKET-LEVEL ONLY. Keep the annual Treasurer tax-lien sale separate from Boulder County Public Trustee mortgage-foreclosure sales and from the later Treasurer’s Deed auction. The county explicitly states a tax-lien investor receives no right, title, interest, possession, or inspection right in the property. Do not fabricate parcel inventory, opening/minimum bids, lien/payoff amounts, current availability, ownership/property characteristics, redemption outcomes, or deed outcomes, and do not bulk republish owner/taxpayer names.',source:'https://bouldercounty.gov/property-and-land/treasurer/taxes/tax-lien-sale/'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Boulder County marker but could not locate row start")
    row_end = text.find("}\n", marker_pos)
    if row_end < 0:
        row_end = text.find("},\n", marker_pos)
        if row_end < 0:
            raise SystemExit("Found Boulder County marker but could not locate row end")
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Boulder County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Boulder County tax-lien market row")
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
    print("Added Colorado Boulder County tax-lien market")


if __name__ == "__main__":
    main()
