#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Audubon County"

ROW = r'''{state:'Iowa — Audubon County',product:'Tax Sale Certificate of Purchase / property-tax lien',schedule:'2026 Treasurer tax sale was June 15, 2026 at 9:00 a.m. at the Audubon County Courthouse. Registration deadline was June 11, 2026 at 4:00 p.m.; verify the current-year Treasurer notice before participating.',availability:'Annual June sale — verify any adjourned sale, assignments, or county-held certificate availability directly with Audubon County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa tax-sale certificates redeem with 2% interest per month under the Iowa statutory redemption framework. This is certificate/redemption interest, not ownership of the property.',bid:'https://www.iowatreasurers.org/treshome.php?idCounty=05',canadian:'County-specific. Confirm current bidder registration, W-9/taxpayer-ID, residency, payment, and eligibility requirements directly with Audubon County Treasurer before attempting to participate.',itin:'Do not assume an ITIN alone satisfies bidder eligibility. The official 2026 Treasurer page links a W-9 form; verify current taxpayer-ID and registration requirements directly with the Treasurer.',online:'NO current online-sale claim from the official 2026 Treasurer page. The 2026 sale is listed at the Audubon County Courthouse; verify current-year procedures because they may change.',otc:'County-specific. Verify current adjourned-sale, assignment, or county-held certificate availability directly with the Treasurer; do not infer current inventory from an older delinquent-tax list.',deed:'A Tax Sale Certificate of Purchase is a lien interest and does not itself convey title. Any later tax deed requires the separate Iowa statutory notice and redemption process.',special:'MARKET-LEVEL ONLY. Audubon County officially confirms a June 15, 2026 Treasurer tax sale and registration deadline, but no unrestricted machine-readable current parcel feed was verified for safe republication. Do not bulk republish owner/taxpayer names, fabricate parcel inventory or opening bids, treat delinquent-tax amounts as opening bids, bypass registration controls, or substitute Sheriff mortgage-foreclosure sales for Treasurer tax-sale certificates.',source:'https://www.auduboncountyia.gov/county-information/treasurer.aspx'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Audubon County Iowa row already present")
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
    print("Added Audubon County Iowa tax-lien market")


if __name__ == "__main__":
    main()
