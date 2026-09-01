#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Putnam County"

ROW = r'''{state:'Florida — Putnam County',product:'Tax certificate / property-tax lien',schedule:'Annual tax-certificate sale is held on or before June 1. Putnam County Tax Collector conducts the sale online through RealAuction; verify the current annual notice and inventory before bidding.',availability:'Annual sale cycle; official county-held certificates are also available through Putnam County\'s RealTaxLien portal when inventory exists',maxReturn:'18%/yr statutory max',interest:'Florida reverse auction. Putnam County states bidding starts at 18% and is bid down in 0.25% increments until the certificate is sold to the lowest bidder.',bid:'https://putnamtax.com/services/other-services/tax-services/property-tax/',canadian:'No Putnam-specific foreign-bidder eligibility rule was identified in the official county material reviewed. Verify current registration, taxpayer-identification, withholding, funding and payment requirements with the Tax Collector / RealAuction before bidding.',itin:'Verify current taxpayer-identification and withholding requirements directly with Putnam County Tax Collector / RealAuction; do not assume an ITIN alone guarantees eligibility.',online:'Yes — annual sale through RealAuction. County-held certificates are directed to Putnam County\'s official RealTaxLien portal.',otc:'YES when county-held inventory is available — Putnam County Tax Collector directs purchasers to its official county-held tax-certificate portal.',deed:'A tax certificate is a lien and does not convey ownership. Putnam County states that after the statutory waiting period, an unredeemed certificate holder may initiate a separate tax-deed application process.',special:'Do not mix Putnam tax certificates with tax-deed property sales or ordinary property-tax payments. The Tax Collector explicitly warns that paying taxes is not purchasing a tax certificate or the property.',source:'https://putnamtax.com/services/other-services/tax-services/property-tax/'}'''


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
        raise SystemExit("Found Putnam marker but could not locate row start")

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
        raise SystemExit("Found Putnam marker but could not locate row end")

    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Putnam row repair escaped rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Putnam County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Putnam County tax-lien market row")
        return

    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Florida Putnam County tax-lien market")


if __name__ == "__main__":
    main()
