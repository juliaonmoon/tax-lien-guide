#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Hernando County"

ROW = r'''{state:'Florida — Hernando County',product:'Tax certificate / property-tax lien',schedule:'Hernando County states that the annual tax-certificate sale for unpaid property taxes must be held by the end of May. The Tax Collector handles the certificate sale; the Clerk states that it is conducted online through LienHub.',availability:'Annual sale cycle; verify the current sale notice, inventory and any county-held / post-sale availability with the Hernando County Tax Collector and official LienHub portal.',maxReturn:'18%/yr statutory max',interest:'Hernando County states that the certificate is sold to the registered bidder willing to accept the lowest redemption interest rate, which may range from 0% to 18%.',bid:'https://hernandoclerk.com/additional-services/tax-deeds/',canadian:'No Hernando-specific foreign-bidder eligibility rule was identified in the official county material reviewed. Verify current registration, taxpayer-identification, withholding, funding and payment requirements with the Tax Collector / official auction platform before bidding.',itin:'Verify current taxpayer-identification and withholding requirements directly with the Hernando County Tax Collector / LienHub; do not assume an ITIN alone guarantees eligibility.',online:'Yes — Hernando County states the tax-certificate sale is held online through LienHub.',otc:'County-held / post-sale certificate availability is Tax Collector-specific; verify current official inventory rather than assuming unsold certificates are continuously available.',deed:'A tax certificate represents a tax lien and does not convey title. Hernando County states that if a certificate remains unredeemed for the statutory period, the certificate holder may begin a separate tax-deed process; the Clerk then conducts the property auction.',special:'Do not mix Hernando tax certificates with tax-deed listings or tax-deed base bids. The Tax Collector handles certificate liens; the Clerk separately conducts tax-deed property auctions. Tax-deed opening/base bids are not tax-certificate minimum bids.',source:'https://hernandoclerk.com/additional-services/tax-deeds/'}'''


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
        raise SystemExit("Found Hernando County marker but could not locate row start")

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
        raise SystemExit("Found Hernando County marker but could not locate row end")

    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit("Hernando County row repair escaped rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Hernando County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Hernando County tax-lien market row")
        return

    _, end = find_rows_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Florida Hernando County tax-lien market")


if __name__ == "__main__":
    main()
