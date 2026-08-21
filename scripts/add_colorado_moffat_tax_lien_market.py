#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Moffat County"

ROW = r'''{state:'Colorado — Moffat County',product:'Tax lien / Certificate of Purchase',schedule:'MARKET-LEVEL ONLY — Moffat County officially documents an annual Treasurer tax-lien certificate sale, but the latest clearly accessible county sale publication located during this refresh is the 2024 notice. No exact 2026 sale date or 2026 parcel list is inferred from that older notice.',availability:'2026 sale-specific date/list pending official publication',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Moffat County’s official prior sale notice states redemption interest is attached to the tax-lien certificate and that a Treasurer’s Deed is a later process after the statutory period. Colorado’s annual certificate rate changes by year, so the older published 15% rate is not carried forward to 2026.',bid:'https://moffatcounty.colorado.gov/sites/moffatcounty/files/24TaxLienList.pdf',canadian:'Current 2026 foreign-bidder eligibility is not clearly published in the accessible county materials; verify registration, payment, and taxpayer-ID requirements directly with the Moffat County Treasurer.',itin:'Current public materials reviewed do not establish 2026 foreign taxpayer-ID requirements; verify directly with the Treasurer before registration.',online:'2026 format pending official publication; do not assume the format from the older county notice.',otc:'County-held/assignment availability for 2026 is not clearly published in the accessible official materials; verify directly with the Treasurer.',deed:'A tax-lien certificate is not ownership. Moffat County’s official notice describes Treasurer’s Deed as a later process if the lien remains unredeemed through the statutory period.',special:'MARKET-LEVEL ONLY until Moffat County publishes current 2026 sale-specific details in a safely ingestible form. Do not reuse the 2024 parcel list, owner-name data, mailing addresses, the prior 15% redemption rate, Public Trustee foreclosure records, or Treasurer’s Deed auction values as current 2026 tax-lien listings or opening bids.',source:'https://moffatcounty.colorado.gov/sites/moffatcounty/files/24TaxLienList.pdf'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Moffat County row already present")
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
