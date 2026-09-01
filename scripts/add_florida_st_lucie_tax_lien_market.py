#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — St. Lucie County"

ROW = r'''{state:'Florida — St. Lucie County',product:'Tax certificate / first-priority property-tax lien',schedule:'St. Lucie County conducts its annual electronic tax-certificate sale on or shortly before June 1; the bidding site generally opens about three weeks before the sale.',availability:'Annual sale / county-held certificates available after the sale while inventory remains',maxReturn:'18%/yr statutory max',interest:'Reverse auction: the certificate is awarded to the bidder accepting the lowest interest rate. Certificates receiving no bids are struck to St. Lucie County at 18%. Florida redemption rules include a 5% minimum return in many redemptions unless the winning bid was 0%; verify certificate-specific treatment before bidding.',bid:'https://tcslc.com/205/Delinquent-Property-Taxes',canadian:'The general county information does not publish a simple foreign-bidder eligibility rule. Confirm current bidder-registration, U.S. tax-document and banking requirements with the St. Lucie County Tax Collector / official auction platform before funding.',itin:'Verify current taxpayer-identification and withholding requirements with the Tax Collector / official auction platform; do not assume an ITIN alone guarantees eligibility.',online:'Yes — St. Lucie County states the annual tax-certificate sale is conducted electronically through LienHub.',otc:'YES — certificates not purchased at the annual sale are struck to the county and can be purchased online on a first-come basis at 18%, subject to current inventory.',deed:'A tax certificate is a lien, not ownership. After the statutory waiting period, an eligible certificate holder may apply for a separate tax-deed process; the Clerk then conducts the real-property auction if the taxes remain unpaid.',special:'St. Lucie County explicitly states that the tax-certificate sale is not a sale of land. Keep certificate investing separate from the later tax-deed auction, and verify current parcel, redemption, bankruptcy, title and certificate status before bidding.',source:'https://tcslc.com/205/Delinquent-Property-Taxes'}'''


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
        raise SystemExit("Found St. Lucie marker but could not locate row start")

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
        raise SystemExit("Found St. Lucie marker but could not locate row end")

    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("St. Lucie row repair escaped rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida St. Lucie County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida St. Lucie County tax-lien market row")
        return

    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Florida St. Lucie County tax-lien market")


if __name__ == "__main__":
    main()
