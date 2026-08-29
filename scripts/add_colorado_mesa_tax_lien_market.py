#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Mesa County"

ROW = r'''{state:'Colorado — Mesa County',product:'Tax lien / tax certificate',schedule:'Mesa County conducts its tax-lien sale online each fall. As of Aug 29, 2026, the official Treasurer material reviewed still does not publish a 2026 annual tax-lien sale date or 2026 advertised-property list, so the guide leaves the 2026 schedule pending official publication rather than inferring it from prior years.',availability:'2026 schedule/list pending official publication; do not infer parcel inventory or current availability from prior-year material',maxReturn:'2026 rate not yet set; Colorado rate is set after Sep 1',interest:'Colorado sets the tax-lien redemption rate each year based on the statutory September 1 benchmark. Mesa County states its 2025 rate was 14%. Premium bids do not earn interest and are not returned, so the guide does not reuse the 2025 rate as the 2026 rate.',bid:'https://www.mesacounty.us/departments-and-services/treasurer/tax-sale-information',canadian:'Mesa County requires online registration and a deposit through RealAuction. The reviewed official bidder material does not establish a non-U.S.-person/W-8 pathway; foreign eligibility should be confirmed directly with the Treasurer before funding.',itin:'Official bidder materials reviewed do not clearly state whether an ITIN/W-8 is accepted for a non-U.S. bidder; verify directly with Mesa County before registration.',online:'Yes — Mesa County uses RealAuction for its annual tax-lien sale.',otc:'County-held/assignment availability is not represented as continuously open in the reviewed current official material; verify current inventory with the Treasurer rather than assuming OTC availability.',deed:'The tax-lien certificate is not property ownership. A holder may later use the separate Treasurer’s Deed / Certificate of Option process subject to statutory notice, redemption and public-auction procedures; that later process must not be presented as the annual tax-lien sale.',special:'MARKET-LEVEL ONLY. Minimum starting bid at the annual lien sale is based on delinquent taxes and statutory charges when officially published for the specific sale. Premium bidding may be used, but premium does not earn interest and is not returned. Keep the annual tax-lien certificate sale separate from Mesa County’s later Treasurer’s Deed / Certificate of Option public-auction process and from Public Trustee foreclosure sales. Do not fabricate parcel inventory, opening/minimum bids, lien/payoff amounts, current availability, property or ownership characteristics, redemption/deed outcomes, or bulk owner/taxpayer data.',source:'https://www.mesacounty.us/departments-and-services/treasurer/tax-sale-information'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Mesa County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Mesa County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Mesa County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Mesa County tax-lien market row")
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
