#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Clayton County"

ROW = r'''{state:'Iowa — Clayton County',product:'Tax sale certificate / property-tax lien',schedule:'Clayton County states that its annual tax sale is held on the third Monday of June at 1:00 PM. The 2026 annual cycle has therefore passed; verify any adjourned or county-held certificate availability directly with the Treasurer.',availability:'2026 annual sale cycle passed; verify current adjourned or county-held certificate availability with Clayton County Treasurer',maxReturn:'2%/month redemption interest',interest:'Clayton County states that tax-sale certificates redeem at 2% interest per month, counting each fraction of a month as a whole month. A tax-sale certificate is a lien interest, not immediate ownership; any deed requires the separate statutory notice and redemption process.',bid:'https://claytoncountyia.gov/resources/property_tax/',canadian:'County bidder-registration and tax-identification rules apply. Confirm current eligibility and required documentation directly with Clayton County Treasurer before attempting to bid.',itin:'Verify current Clayton County bidder tax-identification requirements; do not assume an ITIN alone establishes eligibility.',online:'County-specific for the current sale cycle; verify current bidding method with the Treasurer rather than relying on older sale instructions.',otc:'County-held or adjourned-sale availability is county-specific. Verify current inventory with Clayton County Treasurer; do not infer availability from delinquent-tax balances or prior-year lists.',deed:'The tax-sale certificate does not convey title. If the certificate remains unredeemed, a deed can arise only after the separate Iowa statutory notice/redemption process.',special:'MARKET-LEVEL ONLY. Clayton County documents the annual Treasurer tax-sale certificate process and 2% monthly redemption interest, but no current machine-readable 2026 parcel inventory was verified for safe republication. Do not bulk republish owner/taxpayer names, do not fabricate parcel listings or opening bids, and do not substitute Clayton County Sheriff mortgage-foreclosure sales for the Treasurer tax-sale certificate market.',source:'https://claytoncountyia.gov/resources/property_tax/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")

    if MARKER in text:
        start = text.index("{state:'Iowa — Clayton County'")
        end = text.find("},\n", start)
        suffix_len = 1
        if end < 0:
            end = text.find("}\n", start)
        if end < 0:
            end = text.find("}\r\n", start)
        if end < 0:
            raise SystemExit("Could not locate end of existing Clayton County row")
        end += suffix_len
        current = text[start:end]
        if current == ROW:
            print("Iowa Clayton County canonical row already present")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Repaired Iowa Clayton County tax-lien market row to canonical county-authored output")
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
    print("Added Iowa Clayton County tax-lien market")


if __name__ == "__main__":
    main()
