#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Delta County"

ROW = r'''{state:'Colorado — Delta County',product:'Tax lien certificate',schedule:'Delta County states that its annual tax lien sale is held online on the first Thursday in November. The official Annual Sales page currently still shows 2025 sale specifics; do not infer a 2026 parcel list, sale-specific rate, opening bid, or availability until the Treasurer publishes the current 2026 material.',availability:'2026 annual sale follows the county’s published first-Thursday-in-November schedule, but the current official page still shows 2025 sale-specific information and no current 2026 delinquent parcel list/rate',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Delta County states that tax-lien certificate interest is set at 9 percentage points above the Federal Reserve discount rate in effect on September 1 each year. The 2026 certificate rate is therefore pending until that rate-setting point and official publication.',bid:'https://deltacountyco.gov/141/Annual-Sales',canadian:'The public county page does not clearly publish foreign-bidder eligibility. Confirm registration, identity, payment, and U.S. tax-document requirements directly with the Delta County Treasurer before funding.',itin:'Not clearly published for foreign bidders on the current tax-lien page; verify taxpayer-identification requirements directly with the Treasurer.',online:'Yes — Delta County states the annual tax lien sale is held online through its linked auction platform.',otc:'County-owned/struck-off inventory is handled separately by the county. Do not assume annual-sale parcels remain purchasable after the auction; use only current official county-owned-property or strike-off information.',deed:'Buying the tax lien creates a Certificate of Purchase, not ownership of the property. Delta County separately explains that after the statutory holding period a lien holder may apply for a Treasurer’s Deed; that later deed process is distinct from the original tax-lien sale.',special:'MARKET-LEVEL ONLY until Delta County publishes a current 2026 delinquent tax-sale list/rate source that can be safely and unambiguously ingested. Do not substitute Public Trustee foreclosure rows, Treasurer’s Deed auction rows, county-owned real-estate sale rows, owner-name data, an older 2025 lien list, or fabricated parcel/opening-bid data. Do not fabricate parcel inventory, opening/minimum bids, payoff amounts, current availability, property characteristics, redemption/deed outcomes, or bulk owner/taxpayer data.',source:'https://deltacountyco.gov/141/Annual-Sales'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Delta County marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Delta County marker but could not locate row end")
    return row_start, min(endings) + 1


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

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Colorado Delta County tax-lien market")


if __name__ == "__main__":
    main()
