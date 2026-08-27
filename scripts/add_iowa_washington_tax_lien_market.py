#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Washington County"

ROW = r'''{state:'Iowa — Washington County',product:'Tax sale certificate / property-tax lien',schedule:'Washington County held its 2026 annual tax sale at 9:00 a.m. on June 15, 2026. Registration and bidding were conducted online through the county-designated Iowa Tax Auction system; adjourned sales may be held afterward if parcels remain available.',availability:'2026 annual June sale passed; verify current adjourned-sale or certificate availability with Washington County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa tax-sale certificates accrue 2% interest per month during redemption under the applicable Iowa tax-sale rules. A Tax Sale Certificate of Purchase is a lien interest and does not itself convey ownership of the real estate.',bid:'https://www.washingtoncounty.iowa.gov/319/Tax-Sale-Information',canadian:'Washington County bidder registration requires compliance with county and Iowa eligibility rules. Confirm current identification, payment, residency/tax-document, and registration requirements directly with the Treasurer and auction system before bidding.',itin:'Washington County requires qualifying bidders/certificate holders to have a Social Security number or federal tax identification number and to complete the required tax-sale registration documents; verify current requirements directly with the county.',online:'Yes — Washington County states annual-sale registration and bidding are conducted online through the county-designated Iowa Tax Auction system.',otc:'Adjourned tax sales may be held during regular office hours if parcels remain available. Verify current certificate inventory directly with the Treasurer rather than inferring it from the June publication.',deed:'The Tax Sale Certificate of Purchase is not a deed. If a qualifying certificate remains unredeemed, the holder must complete the separate statutory notice/redemption process before seeking a tax deed.',special:'MARKET-LEVEL ONLY. Washington County publishes a 2026 tax-sale publication and current terms, but this integration does not bulk republish parcel or taxpayer/owner data. Do not fabricate parcel inventory or opening bids, and do not substitute Sheriff mortgage-foreclosure sales for the Treasurer tax-sale certificate market.',source:'https://www.washingtoncounty.iowa.gov/319/Tax-Sale-Information'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start >= 0:
        # Restore the canonical county-authored row before strict validation.
        # Shared presentation normalization may rewrite comparison fields later,
        # so marker presence alone is not a sufficient idempotency check.
        end = text.find("}\n", start)
        comma = text.find("},", start)
        if comma >= 0 and (end < 0 or comma < end):
            end = comma + 1
        elif end >= 0:
            end += 1
        else:
            raise SystemExit("Could not find end of existing Washington County row")
        existing = text[start:end]
        if existing == ROW:
            print("Iowa Washington County canonical row already present")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Iowa Washington County tax-lien market row")
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
    print("Added Iowa Washington County tax-lien market")


if __name__ == "__main__":
    main()
