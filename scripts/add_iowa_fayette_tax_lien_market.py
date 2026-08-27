#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Fayette County"

ROW = r'''{state:'Iowa — Fayette County',product:'Tax Sale Certificate of Purchase / property-tax lien',schedule:'Fayette County Treasurer administers Iowa tax sales and currently publishes tax-sale terms/delinquent-tax materials. A current 2026 parcel publication suitable for safe bulk republication was not verified on the county page reviewed.',availability:'MARKET-LEVEL ONLY — verify current tax-sale or adjourned-sale availability directly with Fayette County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa tax-sale certificates redeem with 2% interest per month under Iowa Code Chapter 447. This is certificate/redemption interest, not immediate ownership of the property.',bid:'https://fayettecounty.iowa.gov/departments/treasurer/',canadian:'County terms do not clearly state foreign-bidder eligibility. Confirm registration, taxpayer-identification and payment requirements directly with Fayette County Treasurer before bidding.',itin:'Do not assume an ITIN alone is sufficient. Verify current taxpayer-identification and bidder-registration requirements directly with the Treasurer.',online:'Current 2026 auction format was not clearly published on the county Treasurer page reviewed; verify directly with the county before registration.',otc:'Adjourned-sale or county-held availability is county-specific. Do not infer current inventory from older delinquent-tax lists; verify directly with the Treasurer.',deed:'A tax-sale certificate does not itself convey title. If a parcel is not redeemed, a later tax deed requires the separate Iowa statutory notice and redemption process.',special:'MARKET-LEVEL ONLY. Fayette County currently confirms Treasurer tax-sale administration but does not expose a verified current machine-readable 2026 parcel feed suitable for bulk republication. Do not fabricate parcel listings or opening bids, do not bulk republish owner/taxpayer names, and do not substitute Sheriff mortgage-foreclosure sales for the Treasurer tax-sale certificate market.',source:'https://fayettecounty.iowa.gov/departments/treasurer/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")

    if MARKER in text:
        start = text.index("{state:'Iowa — Fayette County'")
        end = text.find("},\n", start)
        suffix_len = 1
        if end < 0:
            end = text.find("}\n", start)
        if end < 0:
            end = text.find("}\r\n", start)
        if end < 0:
            raise SystemExit("Could not locate end of existing Fayette County row")
        end += suffix_len
        current = text[start:end]
        if current == ROW:
            print("Iowa Fayette County canonical row already present")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Repaired Iowa Fayette County tax-lien market row to canonical county-authored output")
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
    print("Added Iowa Fayette County tax-lien market")


if __name__ == "__main__":
    main()
