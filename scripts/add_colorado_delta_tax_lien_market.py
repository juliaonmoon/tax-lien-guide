#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Delta County"

ROW = r'''{state:'Colorado — Delta County',product:'Tax lien certificate',schedule:'Delta County states that its annual tax lien sale is held online on the first Thursday in November. The county page reviewed still shows 2025 sale specifics; verify the Treasurer’s current 2026 notice/list before bidding.',availability:'2026 annual sale follows the county’s first-Thursday-in-November schedule, but current 2026 sale-specific list/rate was not yet published on the official page reviewed',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Delta County states that tax-lien certificate interest is set at 9 percentage points above the Federal Reserve discount rate in effect on September 1 each year. The 2026 certificate rate is therefore pending until the county/state rate is set and published.',bid:'https://deltacountyco.gov/141/Annual-Sales',canadian:'The public county page does not clearly publish foreign-bidder eligibility. Confirm registration, identity, payment, and U.S. tax-document requirements directly with the Delta County Treasurer before funding.',itin:'Not clearly published for foreign bidders on the current tax-lien page; verify taxpayer-identification requirements directly with the Treasurer.',online:'Yes — Delta County states the annual tax lien sale is held online through its linked auction platform.',otc:'County-owned/struck-off inventory is handled separately by the county. Do not assume annual-sale parcels remain purchasable after the auction; use only the current official county-owned property or strike-off information.',deed:'Buying the tax lien creates a Certificate of Purchase, not ownership of the property. Delta County separately explains that after the statutory holding period a lien holder may apply for a Treasurer’s Deed; the later deed/public-auction process is distinct from the original tax-lien sale.',special:'MARKET-LEVEL ONLY until Delta County publishes a current 2026 delinquent tax-sale list/rate source that can be safely and unambiguously ingested. Do not substitute Public Trustee foreclosure rows, Treasurer’s Deed auction rows, county-owned real-estate sale rows, owner-name data, an older 2025 lien list, or fabricated parcel/opening-bid data.',source:'https://deltacountyco.gov/141/Annual-Sales'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Delta County row already present")
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
