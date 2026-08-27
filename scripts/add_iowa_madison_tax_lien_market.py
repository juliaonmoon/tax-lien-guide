#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Madison County"

ROW = r'''{state:'Iowa — Madison County',product:'Tax sale certificate / property-tax lien',schedule:'Madison County Treasurer states that its electronic tax sale is held on the third Monday in June. The 2026 annual sale cycle has passed; verify any adjourned or county-held certificate availability directly with the Treasurer.',availability:'2026 annual sale cycle passed; verify current adjourned or county-held certificate availability with Madison County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa Code §447.1 provides redemption interest of 2% per month, counting each fraction of a month as a whole month. The tax-sale certificate is a lien interest, not immediate ownership; any deed requires the separate statutory notice and redemption process.',bid:'https://madisoncountytreasurer.iowa.gov/',canadian:'County bidder-registration and tax-identification rules apply. Confirm current eligibility and required documentation directly with Madison County Treasurer before attempting to bid.',itin:'Verify current Madison County bidder tax-identification requirements; do not assume an ITIN alone establishes eligibility.',online:'Yes — Madison County Treasurer states that the tax sale is held electronically on the third Monday in June.',otc:'Adjourned-sale or county-held certificate availability is county-specific. Verify current inventory with Madison County Treasurer; do not infer availability from delinquent-tax balances, real-estate lookup results, or prior-year lists.',deed:'The tax-sale certificate does not convey title. If the certificate remains unredeemed, a deed can arise only after the separate Iowa statutory notice/redemption process.',special:'MARKET-LEVEL ONLY. Madison County documents an electronic Treasurer tax-sale certificate process, but no current machine-readable 2026 parcel inventory was verified for safe republication. Do not bulk republish owner/taxpayer names, do not fabricate parcel listings or opening bids, and do not substitute Madison County Sheriff mortgage-foreclosure sales for the Treasurer tax-sale certificate market.',source:'https://madisoncountytreasurer.iowa.gov/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")

    if MARKER in text:
        start = text.index("{state:'Iowa — Madison County'")
        end = text.find("},\n", start)
        suffix_len = 1
        if end < 0:
            end = text.find("}\n", start)
        if end < 0:
            end = text.find("}\r\n", start)
        if end < 0:
            raise SystemExit("Could not locate end of existing Madison County row")
        end += suffix_len
        current = text[start:end]
        if current == ROW:
            print("Iowa Madison County canonical row already present")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Repaired Iowa Madison County tax-lien market row to canonical county-authored output")
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
    print("Added Iowa Madison County tax-lien market")


if __name__ == "__main__":
    main()
