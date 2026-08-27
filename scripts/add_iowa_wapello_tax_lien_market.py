#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Wapello County"

ROW = r'''{state:'Iowa — Wapello County',product:'Tax Sale Certificate of Purchase / property-tax lien',schedule:'2026 annual online public tax sale was held on the third Monday in June through GovEase. Wapello County may also conduct public-bidder/adjourned handling when delinquencies remain.',availability:'2026 annual sale passed — verify any current public-bidder or adjourned availability directly with Wapello County Treasurer',maxReturn:'2%/month redemption interest',interest:'Wapello County states that 2% interest per month accrues on the outstanding tax-sale amount during redemption, subject to Iowa law. This is certificate/redemption interest, not immediate ownership of the property.',bid:'https://www.wapellocounty.org/treasurer/tax_sale/',canadian:'Foreign/non-U.S. bidder eligibility is not clearly stated on the county page. Confirm current GovEase registration, taxpayer-ID, and payment requirements directly with the Treasurer before registering.',itin:'Do not assume an ITIN alone satisfies bidder requirements. Verify current taxpayer-ID/document requirements with Wapello County Treasurer and GovEase.',online:'Yes — annual public tax sale is online through GovEase',otc:'Unsold delinquencies may proceed to Public Bidder Sale under Iowa law; verify current availability with the Treasurer rather than inferring inventory from the annual publication.',deed:'A tax-sale purchase does not transfer ownership. Wapello County states the certificate generally must remain unpaid for 1 year 9 months before the investor may start the separate 90-day deed-notice process.',special:'MARKET-LEVEL ONLY. Wapello County publishes qualifying unpaid parcels through its official publication and makes an updated nightly list available to registered GovEase bidders. Do not bypass bidder registration, bulk republish owner/taxpayer names, fabricate parcel inventory or opening bids, treat delinquent tax amounts as opening bids, or substitute Wapello County Sheriff foreclosure sales for the Treasurer tax-sale certificate market.',source:'https://www.wapellocounty.org/treasurer/tax_sale/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start >= 0:
        # Restore the canonical county-authored market row before validation.
        # Shared presentation normalizers may rewrite comparison fields later,
        # so marker presence alone is not a sufficient idempotency check.
        end = text.find("}\n", start)
        comma = text.find("},", start)
        if comma >= 0 and (end < 0 or comma < end):
            end = comma + 1
        elif end >= 0:
            end += 1
        else:
            raise SystemExit("Could not find end of existing Wapello County row")
        existing = text[start:end]
        if existing == ROW:
            print("Iowa Wapello County canonical row already present")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Iowa Wapello County tax-lien market row")
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
    print("Added Iowa Wapello County tax-lien market")


if __name__ == "__main__":
    main()
