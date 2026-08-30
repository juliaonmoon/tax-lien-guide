#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Flagler County"

ROW = r'''{state:'Florida — Flagler County',product:'Tax certificate / enforceable first lien',schedule:'Flagler County states that its tax-certificate sale for delinquent real-estate taxes begins on or before June 1 each year. County-held certificates are unavailable while the annual sale is being prepared and become available again beginning July 1.',availability:'County-held certificates may be available now — verify current inventory through the official Tax Collector / LienHub page',maxReturn:'18%/yr statutory max',interest:'Competitive reverse bidding begins at 18% and decreases in 0.25% increments. The certificate is awarded to the bidder accepting the lowest rate; 0% bids earn no interest. County-held certificates carry 18% interest.',bid:'https://www.flaglertax.gov/tax-certificate-information/',canadian:'The official county pages explain sale mechanics but do not publish a simple foreign-bidder eligibility rule. Confirm current registration, taxpayer-identification, banking and payment requirements with the Tax Collector / LienHub before participating.',itin:'Verify current taxpayer-identification requirements with the Tax Collector / LienHub before registering; do not assume an ITIN alone guarantees eligibility.',online:'YES — Flagler County directs investors to its online tax-certificate vendor and uses LienHub for county-held certificate purchases.',otc:'YES — certificates receiving no bids are struck to the county and may be purchased through LienHub on a first-come, first-served basis. Flagler states county-held certificates become available beginning July 1 after the annual sale cycle.',deed:'A tax certificate is an enforceable first lien, not a purchase of the property. A separate tax-deed application may be initiated after the statutory waiting period; the later property auction is conducted separately by the Clerk of Court.',special:'Flagler explicitly distinguishes certificates/liens from tax-deed property sales and warns purchasers to research the property before buying a certificate. Do not treat certificate purchase as a right to occupy or enter the property.',source:'https://www.flaglertax.gov/tax-certificate-information/'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Flagler County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Flagler County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Flagler County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Flagler County tax-lien market row")
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
    print("Added Florida Flagler County tax-lien market")


if __name__ == "__main__":
    main()
