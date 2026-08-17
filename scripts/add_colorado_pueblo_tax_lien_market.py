#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Pueblo County"

ROW = r'''{state:'Colorado — Pueblo County',product:'Tax lien / tax certificate',schedule:'Pueblo County operates tax-lien sales through the Treasurer. As of Aug 17, 2026, the county\'s current public tax-lien page still points to 2025 sale materials; the 2026 annual sale date/list is therefore marked pending official publication. Pueblo also publishes a separate nightly-updated county-held lien list.',availability:'County-held liens available; 2026 annual sale date/list pending',maxReturn:'2026 rate not yet set; Colorado rate is set after Sep 1',interest:'Colorado sets the annual tax-lien redemption rate after September 1 under state law. Pueblo County has not yet published the 2026 rate, so the guide does not carry forward a prior-year rate.',bid:'https://county.pueblo.org/treasurers-department/2025-tax-lien-sale-information',canadian:'The reviewed Pueblo County pages do not clearly establish a non-U.S.-person/W-8 bidder pathway. Verify current registration and tax-ID requirements directly with the Treasurer before funding.',itin:'Official Pueblo bidder materials reviewed do not clearly state whether an ITIN/W-8 is accepted for a non-U.S. bidder; verify with the Treasurer.',online:'Annual sale format should be verified from the current-year Treasurer instructions before bidding.',otc:'YES — Pueblo County publishes a nightly-updated official county-held lien list with a downloadable CSV.',deed:'A tax-lien certificate is not property ownership. Pueblo separately administers Treasurer\'s Deed applications and Treasurer\'s Deed auctions after the statutory process.',special:'Use the Treasurer\'s tax-lien and county-held-lien sources for lien investing. Do not confuse them with Pueblo County Public Trustee mortgage foreclosures or with the separate Treasurer\'s Deed auction schedule.',source:'https://county.pueblo.org/treasurers-department/county-held-properties'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Pueblo County row already present")
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
    print("Added Colorado Pueblo County tax-lien market")


if __name__ == "__main__":
    main()
