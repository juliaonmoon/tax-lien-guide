#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Alachua County"

ROW = r'''{state:'Florida — Alachua County',product:'Tax certificate / first lien',schedule:'Alachua County holds its tax-certificate sale on or before June 1 each year. The Tax Collector states the sale is conducted online through LienHub.',availability:'Annual sale cycle — monitor the official Tax Collector / LienHub pages for current certificate and county-held inventory',maxReturn:'18%/yr statutory max',interest:'Competitive reverse bidding starts at 18% and bids downward. The certificate is awarded to the bidder accepting the lowest rate. Alachua County states that non-zero certificates receive at least 5% interest until accrued interest exceeds 5%; zero-interest bids earn zero.',bid:'https://www.alachuacollector.com/property-taxes/',canadian:'Bidder registration is handled through the official online tax-certificate platform. The county page does not publish a simple foreign-bidder eligibility rule; confirm current identity, tax-document and banking requirements before funding.',itin:'Verify current taxpayer-identification requirements with the Tax Collector / LienHub before registering; do not assume an ITIN alone guarantees eligibility.',online:'YES — Alachua County states its tax-certificate sale is conducted online through LienHub.',otc:'YES — certificates receiving no bids are struck to the county. Eligible county-held certificates may later be purchased from the Tax Collector on a first-come, first-served basis and carry 18% interest.',deed:'A tax certificate is an enforceable first lien, not ownership. After the statutory waiting period, an eligible certificate holder may apply for the separate tax-deed process; if not redeemed, the property may then be sold at a public tax-deed auction.',special:'Alachua County explicitly distinguishes tax certificates from tax deeds. Certificates are valid for seven years from issuance; verify current parcel status, redemption, bankruptcy and sale terms from official county records before bidding.',source:'https://www.alachuacollector.com/property-taxes/'}'''


def find_rows_bounds(text: str):
    rows_start = text.find("const rows=[")
    if rows_start < 0:
        raise SystemExit("Could not find rows array")
    rows_end = text.find("\n];", rows_start)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")
    return rows_start, rows_end


def find_row_bounds(text: str):
    rows_start, rows_end = find_rows_bounds(text)
    marker_pos = text.find(MARKER, rows_start, rows_end)
    if marker_pos < 0:
        return None

    row_start = text.rfind("{state:", rows_start, marker_pos + 1)
    if row_start < rows_start:
        raise SystemExit("Found Alachua County marker but could not locate row start")

    candidates = [
        pos for pos in (
            text.find("},\n", marker_pos, rows_end),
            text.find("}\n", marker_pos, rows_end),
        ) if pos >= 0
    ]
    if candidates:
        row_end = min(candidates) + 1
    elif text.startswith("}", rows_end - 1):
        row_end = rows_end
    else:
        raise SystemExit("Found Alachua County marker but could not locate row end")

    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Alachua County row repair escaped rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Alachua County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Alachua County tax-lien market row")
        return

    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Florida Alachua County tax-lien market")


if __name__ == "__main__":
    main()
