#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Duval County"

ROW = r'''{state:'Florida — Duval County',product:'Tax certificate / first-priority property-tax lien',schedule:'2026 Duval County Tax Certificate Sale: <span class="schedule-date">May 27, 2026</span> (passed). Registration opened May 8, 2026. County-held certificates from prior sales may remain available.',availability:'Passed / county-held certificates may remain',maxReturn:'18%/yr statutory max',interest:'Direct reverse bid: bidder accepting the lowest interest rate wins. Florida statutory maximum is 18%; bids may go to 0%. Duval states a minimum 5% return applies to certificates redeemed early under the applicable Florida rule.',bid:'https://taxcollector.jacksonville.gov/taxes/property-taxes/tax-sale%2C-certificates%2C-and-tax-deeds',canadian:'Duval requires a U.S. Tax Identification Number and completed IRS W-9 for bidder registration, so a foreign individual should confirm eligibility/documentation with the Tax Collector before planning to bid.',itin:'TIN required for registration; Duval says the registration name must match official tax-ID records and interest is reported on Form 1099-INT.',online:'YES — official 2026 sale uses LienHub',otc:'YES — Duval says unsold county-held certificates from previous years can be purchased through its LienHub county-held process.',deed:'Certificate must generally be held for at least two years before a tax-deed application. A tax certificate is not ownership; Duval Clerk separately manages tax-deed sales.',special:'Duval explicitly warns that a tax certificate is a lien, not a sale of real property or a direct means to acquire the property. Homestead liens are not subject to the tax-certificate sale. Do not mix Duval tax certificates with the separate Clerk tax-deed auction.',source:'https://taxcollector.jacksonville.gov/taxes/property-taxes/tax-sale%2C-certificates%2C-and-tax-deeds'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Duval County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Duval County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Duval County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Duval County tax-lien market row")
        return

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Florida Duval County tax-lien market")


if __name__ == "__main__":
    main()
