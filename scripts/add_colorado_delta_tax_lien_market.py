#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Delta County"

ROW = r'''{state:'Colorado — Delta County',product:'Tax lien certificate',schedule:'Delta County officially states that its annual online tax-lien sale is held on the first Thursday in November beginning at 8:00 a.m. MST. Under that standing published rule, the 2026 sale date is <span class="schedule-date">November 5, 2026</span>. The county page still shows 2025 sale-specific registration/list details, so no 2026 parcel inventory, registration window, sale-specific rate, opening bid, or availability is inferred until the Treasurer publishes the current 2026 material.',availability:'Upcoming — November 5, 2026 under the county’s standing first-Thursday-in-November rule; current 2026 delinquent parcel list and registration details are still pending official publication',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Delta County states that tax-lien certificate interest is set at 9 percentage points above the Federal Reserve discount rate in effect on September 1 each year. The 2026 certificate rate is therefore pending until that rate-setting point and official publication.',bid:'https://deltacountyco.gov/141/Annual-Sales',canadian:'The public county page does not clearly publish foreign-bidder eligibility. Confirm registration, identity, payment, and U.S. tax-document requirements directly with the Delta County Treasurer before funding.',itin:'Not clearly published for foreign bidders on the current tax-lien page; verify taxpayer-identification requirements directly with the Treasurer.',online:'Yes — Delta County states the annual tax lien sale is held online through its linked auction platform.',otc:'County-owned/struck-off inventory is handled separately by the county. Do not assume annual-sale parcels remain purchasable after the auction; use only current official county-owned-property or strike-off information.',deed:'Buying the tax lien creates a Certificate of Purchase, not ownership of the property. Delta County separately explains that after the statutory holding period a lien holder may apply for a Treasurer’s Deed; that later deed process is distinct from the original tax-lien sale.',special:'MARKET-LEVEL ONLY until Delta County publishes a current 2026 delinquent tax-sale list/rate source that can be safely and unambiguously ingested. Do not substitute Public Trustee foreclosure rows, Treasurer’s Deed auction rows, county-owned real-estate sale rows, owner-name data, an older 2025 lien list, or fabricated parcel/opening-bid data. Do not fabricate parcel inventory, opening/minimum bids, payoff amounts, current availability, property characteristics, redemption/deed outcomes, or bulk owner/taxpayer data.',source:'https://deltacountyco.gov/141/Annual-Sales'}'''


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
    if row_start < rows_start:
        raise SystemExit("Found Delta County marker but could not locate row start inside rows array")
    endings = []
    search_end = rows_end + len("\n];")
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, search_end)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Delta County marker but could not locate row end inside rows array")
    row_end = min(endings) + 1
    if row_start < rows_start or row_end > search_end:
        raise SystemExit("Refusing Delta County repair outside rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Delta County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Delta County tax-lien market row")
        return

    _, end = rows_array_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Colorado Delta County tax-lien market")


if __name__ == "__main__":
    main()
