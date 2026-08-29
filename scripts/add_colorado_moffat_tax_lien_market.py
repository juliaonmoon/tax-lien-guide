#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Moffat County"

ROW = r'''{state:'Colorado — Moffat County',product:'Tax lien / Certificate of Purchase',schedule:'MARKET-LEVEL ONLY — Moffat County officially documents an annual Treasurer tax-lien certificate sale. The latest clearly accessible county sale publication located during this refresh is the 2025 notice, which states the 2025 tax-lien sale was November 6, 2025. No exact 2026 sale date or 2026 parcel list is inferred from that prior-year notice.',availability:'2026 sale-specific date/list pending official publication',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Moffat County’s official 2025 sale notice states a 14% redemption interest rate for liens sold at the November 6, 2025 sale. Colorado’s certificate rate changes by sale year, so that prior-year rate is not carried forward to 2026.',bid:'https://moffatcounty.colorado.gov/sites/moffatcounty/files/25TaxSale_0.pdf',canadian:'Current 2026 foreign-bidder eligibility is not clearly published in the accessible county materials; verify registration, payment, and taxpayer-ID requirements directly with the Moffat County Treasurer.',itin:'Current public materials reviewed do not establish 2026 foreign taxpayer-ID requirements; verify directly with the Treasurer before registration.',online:'2026 format pending official publication; do not assume the format from the prior-year county notice.',otc:'County-held/assignment availability for 2026 is not clearly published in the accessible official materials; verify directly with the Treasurer.',deed:'A tax-lien certificate is not ownership. Treasurer’s Deed is a later statutory process if a lien remains unredeemed; do not confuse tax-lien certificates with Public Trustee mortgage foreclosures.',special:'MARKET-LEVEL ONLY until Moffat County publishes current 2026 sale-specific details in a safely ingestible form. Do not reuse the 2025 parcel list, assessed-owner or mailing-address data, the prior-year 14% redemption rate, Public Trustee foreclosure records, or Treasurer’s Deed values as current 2026 tax-lien listings, rates, or opening bids.',source:'https://moffatcounty.colorado.gov/sites/moffatcounty/files/25TaxSale_0.pdf'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Moffat County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Moffat County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Moffat County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Moffat County tax-lien market row")
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
    print("Added Colorado Moffat County tax-lien market")


if __name__ == "__main__":
    main()
