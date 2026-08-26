#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Indiana — Lake County 2026"

ROW = r'''{state:'Indiana — Lake County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Lake County\'s official 2026 Treasurer Tax Sale page lists an online sale window of September 4-8, 2026. The statutory notice dated July 29, 2026 states the electronic auction begins September 4, 2026 at 5:30 PM local time and properties begin closing in batches September 7, 2026.',availability:'Current 2026 Treasurer Tax Sale notice and public property listing are published. Verify the live Lake County and ZeusAuction listings before bidding because parcels can be withdrawn, paid, corrected, or otherwise become ineligible before or during the sale.',interest:'Indiana tax-sale purchaser returns are governed by statutory redemption, not a simple advertised APR. Verify the current Lake County Treasurer Tax Sale information and Indiana Code 6-1.1-24 and 6-1.1-25 for redemption amounts, notice duties, deadlines, and tax-deed procedures.',bid:'https://www.lakecountyin.gov/departments/auditor-taxsales/lake-county-treasurer-tax-sale',canadian:'Not confirmed — verify Lake County\'s current registration, tax-form, entity-document, and bidder-eligibility requirements directly before participating.',itin:'Do not assume an ITIN, W-8, or foreign registration is accepted. The 2026 county notice requires bidders to complete IRS Form W-9 and applicable registration statements; verify current county and auction-platform requirements before participating.',online:'Yes — Lake County states the 2026 Treasurer Tax Sale is conducted entirely online through ZeusAuction. Registration for the 2026 sale ran July 22-August 14, 2026.',otc:'This row covers the annual Treasurer Tax Sale. Lake County separately runs a Commissioners Tax Sale for parcels that did not sell at the Treasurer sale; keep that certificate-sale process distinct from the annual Treasurer sale and from Sheriff/judicial foreclosure sales.',deed:'Buying at the Treasurer Tax Sale does not give immediate ownership. Indiana law provides a redemption period and separate statutory notice and tax-deed procedures before a purchaser may receive title.',special:'MARKET-LEVEL SUMMARY ONLY. Lake County publishes a current 2026 notice and a public property listing, but this guide does not bulk republish owner/taxpayer names, freeze dynamic inventory as guaranteed availability, or copy parcel-level minimum bids without a dedicated current-source ingestion and validation path. The county expressly states minimum bids are prescribed by law and may change before the auction. Use the official county page and live auction listing for parcel-specific amounts and eligibility.',source:'https://www.lakecountyin.gov/departments/auditor-taxsales/lake-county-treasurer-tax-sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        row_re = re.compile(
            rf"\{{state:'{re.escape(MARKER)}'.*?\}}(?=\s*,|\s*\n\];)",
            re.S,
        )
        updated, count = row_re.subn(ROW, text, count=1)
        if count != 1:
            raise SystemExit(f"Could not uniquely refresh {MARKER}")
        INDEX.write_text(updated, encoding="utf-8")
        print("Refreshed Lake County Indiana tax-lien market")
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
    print("Added Lake County Indiana tax-lien market")


if __name__ == "__main__":
    main()
