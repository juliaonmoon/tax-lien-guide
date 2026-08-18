#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Douglas County"

ROW = r'''{state:'Colorado — Douglas County',product:'Tax lien / tax sale certificate',schedule:'Douglas County maintains official tax-lien sale and Treasurer records. As of Aug 17, 2026, the county has not published a clearly accessible 2026 annual tax-lien sale date/list on its public pages, so the 2026 schedule is marked pending rather than inferred from prior-year records.',availability:'2026 annual sale date/list pending official publication',maxReturn:'2026 rate not yet set; Colorado rate is set after Sep 1',interest:'Colorado sets the annual tax-lien redemption rate after September 1. Douglas County has not yet published a 2026 rate, so this guide does not carry forward a prior-year rate.',bid:'https://www.douglas.co.us/treasurer/',canadian:'The reviewed Douglas County public materials do not clearly establish a non-U.S.-person/W-8 bidder pathway. Verify current registration and taxpayer-ID requirements directly with the Treasurer before funding.',itin:'Current public Douglas County materials reviewed do not clearly state whether an ITIN/W-8 is accepted for a non-U.S. bidder; verify with the Treasurer.',online:'Current-year auction format should be verified from the Treasurer\'s official sale instructions when posted.',otc:'County-held/assignment availability must be verified from current Douglas County Treasurer records; do not infer availability from older sale certificates.',deed:'A tax-sale certificate/tax lien is not immediate property ownership. Douglas County separately publishes Treasurer\'s Deed process materials after the statutory lien/redemption process.',special:'Douglas County records include Tax Sale Certificates and Treasurer\'s Certificates of Purchase. Keep those lien instruments separate from Public Trustee mortgage foreclosures and later Treasurer\'s Deed proceedings. The guide deliberately leaves the 2026 sale date and return rate pending until officially published.',source:'https://www.douglas.co.us/file-category/treasurer-documents/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Douglas County row already present")
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
    print("Added Colorado Douglas County tax-lien market")


if __name__ == "__main__":
    main()
