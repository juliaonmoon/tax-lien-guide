#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Plymouth County"

ROW = r'''{state:'Iowa — Plymouth County',product:'Tax Sale Certificate of Purchase / property-tax lien',schedule:'Annual tax sale is held on the third Monday in June; the 2026 occurrence was June 15, 2026 (passed). Verify any adjourned/current availability directly with the Plymouth County Treasurer.',availability:'2026 annual sale passed — verify any adjourned/current certificate availability directly with Plymouth County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa Code §447.1 provides 2% interest per month on redemption, counting each fraction of a month as a whole month. This is tax-sale certificate/redemption interest, not ownership of the property.',bid:'https://plymouthcountyiowa.gov/departments/treasurer/',canadian:'Foreign/non-U.S. bidder eligibility is not clearly established by the public county page. Confirm current registration, taxpayer-ID/tax-form, residency, payment, and bidder requirements directly with Plymouth County before attempting to bid.',itin:'Do not assume an ITIN alone satisfies bidder eligibility. Verify current taxpayer-ID and tax-form requirements directly with Plymouth County Treasurer.',online:'Current public county page does not clearly establish the 2026 bidding format; verify directly with the Treasurer.',otc:'County-specific. Verify any adjourned sale or county-held certificate availability directly with Plymouth County Treasurer; do not infer current inventory.',deed:'A tax sale certificate is a lien interest and does not itself convey title. Any later tax deed requires the separate Iowa statutory notice/redemption process.',special:'MARKET-LEVEL ONLY. Plymouth County confirms the annual Treasurer tax-sale program, but no current unrestricted machine-readable 2026 parcel feed was verified for safe republication. Do not bulk republish owner/taxpayer names, fabricate parcel inventory or opening bids, treat delinquent-tax amounts as opening bids, or substitute Sheriff mortgage-foreclosure sales for Treasurer tax-sale certificates.',source:'https://plymouthcountyiowa.gov/departments/treasurer/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Plymouth County Iowa row already present")
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
    print("Added Plymouth County Iowa tax-lien market")


if __name__ == "__main__":
    main()
