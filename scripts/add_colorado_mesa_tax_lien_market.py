#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Mesa County"

ROW = r'''{state:'Colorado — Mesa County',product:'Tax lien / tax certificate',schedule:'Mesa County conducts its tax-lien sale online each fall. As of Aug 17, 2026, the official Treasurer page still shows the Oct 22, 2025 sale and has not published a 2026 sale date/property list, so the guide marks the 2026 schedule as pending official publication.',availability:'2026 schedule/list pending official publication',maxReturn:'2026 rate not yet set; Colorado rate is set after Sep 1',interest:'Colorado sets the tax-lien redemption rate each year at nine percentage points above the federal discount rate as of September 1, rounded as provided by law. Mesa County states its 2025 rate was 14%. Premium bids do not earn interest and are not returned, so the guide does not reuse the 2025 rate as the 2026 rate.',bid:'https://www.mesacounty.us/departments-and-services/treasurer/tax-sale-information',canadian:'Mesa County requires online registration and a deposit through RealAuction. The reviewed official bidder pages do not establish a non-U.S.-person/W-8 pathway; foreign eligibility should be confirmed directly with the Treasurer before funding.',itin:'Official bidder materials reviewed do not clearly state whether an ITIN/W-8 is accepted for a non-U.S. bidder; verify directly with Mesa County before registration.',online:'Yes — Mesa County uses RealAuction for its tax-lien sale.',otc:'County-held/assignment availability is not represented as continuously open in the reviewed 2026 official material; verify current inventory with the Treasurer rather than assuming OTC availability.',deed:'The tax-lien certificate is not property ownership. A holder may apply for the separate Treasurer’s Deed process after the statutory three-year period, subject to notice, redemption and public-auction procedures.',special:'Minimum starting bid equals the unpaid taxes, interest, penalties and fees. Premium bidding may be used, but premium does not earn interest and is not returned. Keep the annual tax-lien sale separate from Mesa County’s later Treasurer’s Deed/public-auction process.',source:'https://www.mesacounty.us/departments-and-services/treasurer/tax-sale-information'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Mesa County row already present")
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
    print("Added Colorado Mesa County tax-lien market")


if __name__ == "__main__":
    main()
