#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Harrison County"

ROW = r'''{state:'Iowa — Harrison County',product:'Tax Sale Certificate of Purchase / property-tax lien',schedule:'2026 annual tax sale was June 15, 2026 (passed), with online bidding. Verify any adjourned/current availability directly with the Harrison County Treasurer.',availability:'2026 annual sale passed — verify any adjourned/current certificate availability directly with Harrison County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa Code §447.1 provides 2% interest per month on redemption, counting each fraction of a month as a whole month. This is certificate/redemption interest, not ownership of the property.',bid:'https://www.iowatreasurers.org/treshome.php?idCounty=43',canadian:'County-specific. Confirm current registration, taxpayer-ID/tax-form, residency, payment, and bidder eligibility directly with Harrison County before attempting to bid.',itin:'Do not assume an ITIN alone satisfies bidder eligibility. Verify current taxpayer-ID and tax-form requirements directly with Harrison County Treasurer.',online:'YES — Harrison County states 2026 bidders placed bids online.',otc:'County-specific. Verify any adjourned sale or county-held certificate availability directly with Harrison County Treasurer; do not infer current inventory.',deed:'A Tax Sale Certificate of Purchase is a lien interest and does not itself convey title. Any later tax deed requires the separate Iowa statutory notice/redemption process.',special:'MARKET-LEVEL ONLY. Harrison County officially confirms its June 15, 2026 Treasurer tax sale and online bidding, but no unrestricted machine-readable current parcel feed was verified for safe republication. Do not bulk republish owner/taxpayer names, fabricate parcel inventory or opening bids, treat delinquent-tax amounts as opening bids, bypass bidder-registration controls, or substitute Sheriff mortgage-foreclosure sales for Treasurer tax-sale certificates.',source:'https://www.iowatreasurers.org/treshome.php?idCounty=43'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Harrison County Iowa row already present")
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
    print("Added Harrison County Iowa tax-lien market")


if __name__ == "__main__":
    main()
