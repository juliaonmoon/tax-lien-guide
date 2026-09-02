#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Eagle County"

ROW = r'''{state:'Colorado — Eagle County',product:'Tax lien / Certificate of Purchase',schedule:'MARKET-LEVEL ONLY — Eagle County official tax-account records document properties paid by Tax Lien Sale, and official Treasurer records separately document later Treasurer’s Deed public auctions. A current 2026 tax-lien sale date/list was not verified, so no 2026 parcel rows or sale date are inferred.',availability:'2026 tax-lien sale details pending official publication',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Colorado tax-lien certificate interest is set under state law. Eagle County official records show tax-lien-sale certificates and redeemed liens; no prior-year certificate rate is carried forward as a 2026 return.',bid:'https://propertytax.eaglecounty.us/PropertyTaxSearch/',canadian:'Foreign-bidder eligibility is not clearly published in the current official county materials; verify registration and taxpayer-ID requirements directly with the Eagle County Treasurer.',itin:'Current public materials do not clearly state foreign taxpayer-ID eligibility; verify directly with the Treasurer before funding.',online:'Current 2026 tax-lien auction platform/rules were not verified; check Eagle County Treasurer materials when the 2026 sale is posted.',otc:'County-held/assignment availability is not clearly published for 2026; verify directly with the Treasurer.',deed:'A tax-lien Certificate of Purchase is not immediate ownership. Eagle County separately conducts the later public-auction process for a Certificate of Option for Treasurer’s Deed after the statutory process.',special:'MARKET-LEVEL ONLY until Eagle County publishes current 2026 tax-lien sale details in a form that can be safely ingested. Do not substitute Public Trustee mortgage foreclosures, Treasurer’s Deed auction rows, owner-name data, prior-year parcel lists, or deed-auction amounts for tax-lien listings. Do not fabricate parcel inventory, opening/minimum bids, payoff amounts, current availability, property characteristics, redemption/deed outcomes, or bulk owner/taxpayer data.',source:'https://propertytax.eaglecounty.us/PropertyTaxSearch/'}'''


def rows_array_bounds(text: str):
    rows_start = text.find("const rows=[")
    if rows_start < 0:
        raise SystemExit("Could not find rows array")
    rows_end = text.find("\n];", rows_start)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")
    return rows_start, rows_end


def find_row_bounds(text: str):
    rows_start, rows_end = rows_array_bounds(text)
    marker_pos = text.find(MARKER, rows_start, rows_end)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", rows_start, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Eagle County marker but could not locate row start inside rows array")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + len("\n];"))
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Eagle County marker but could not locate row end inside rows array")
    row_end = min(endings)
    if row_end >= rows_end + len("\n];"):
        raise SystemExit("Refusing Eagle County repair outside rows array")
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Eagle County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Eagle County tax-lien market row")
        return

    _, end = rows_array_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Colorado Eagle County tax-lien market")


if __name__ == "__main__":
    main()
