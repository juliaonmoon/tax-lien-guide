#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Sioux County"

ROW = r'''{state:'Iowa — Sioux County',product:'Tax Sale Certificate of Purchase / property-tax lien',schedule:'The 2026 annual tax sale was held Monday, June 15, 2026 at 10:00 AM. Bids were placed online through the county-designated IowaTaxAuction system. Verify any adjourned/current availability directly with the Sioux County Treasurer.',availability:'2026 annual sale passed — verify any adjourned/current certificate availability directly with Sioux County Treasurer',maxReturn:'2%/month redemption interest',interest:'Sioux County purchaser terms state redemption includes 2% interest per month, with each fraction of a month counted as a whole month. This is tax-sale certificate/redemption interest; the certificate does not convey title to the property.',bid:'https://www.iowatreasurers.org/index.php?idCounty=84&module=treashome',canadian:'Foreign/non-U.S. bidder eligibility is not clearly established by the public 2026 county page. Registration used online bidding and tax documentation; confirm current residency, W-9/taxpayer-ID, payment, and bidder requirements directly with Sioux County before attempting to bid.',itin:'Do not assume an ITIN alone satisfies bidder eligibility. Verify current taxpayer-ID and tax-form requirements directly with Sioux County Treasurer.',online:'Yes — 2026 bids were placed online through the county-designated IowaTaxAuction system',otc:'County-specific. Sioux County states an adjourned tax sale may be held on a later business day when bidders are present and parcels remain. Do not infer current inventory or bypass bidder registration.',deed:'A Tax Sale Certificate of Purchase is a lien interest and does not convey title. Any later tax deed requires the separate Iowa statutory notice/redemption process.',special:'MARKET-LEVEL ONLY. No current unrestricted machine-readable Sioux County 2026 parcel feed was verified for safe republication. Do not bypass bidder registration, bulk republish owner/taxpayer names, fabricate parcel inventory or opening bids, treat delinquent-tax amounts as opening bids, or substitute Sioux County Sheriff mortgage-foreclosure sales for Treasurer tax-sale certificates.',source:'https://www.iowatreasurers.org/index.php?idCounty=84&module=treashome'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start >= 0:
        # Restore the canonical county-authored market row before validation.
        # Shared presentation normalizers may rewrite display wording later, so
        # merely checking for MARKER is not sufficient for an idempotent repair.
        end = text.find("}\n", start)
        comma = text.find("},", start)
        if comma >= 0 and (end < 0 or comma < end):
            end = comma + 1
        elif end >= 0:
            end += 1
        else:
            raise SystemExit("Could not find end of existing Sioux County row")
        existing = text[start:end]
        if existing == ROW:
            print("Iowa Sioux County canonical row already present")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Iowa Sioux County tax-lien market row")
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
    print("Added Sioux County Iowa tax-lien market")


if __name__ == "__main__":
    main()
