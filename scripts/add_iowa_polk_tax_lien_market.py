#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Polk County"

ROW = r'''{state:'Iowa — Polk County',product:'Tax sale certificate / property-tax lien',schedule:'2026 annual Polk County property-tax sale was held online on June 15, 2026. Polk County states the annual sale is conducted to collect delinquent property taxes; verify current adjourned/public-bidder activity with the Treasurer.',availability:'2026 annual sale passed; verify current county tax-sale status and any subsequent/public-bidder activity with the Polk County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa tax-sale certificates accrue redemption interest under Iowa Code chapter 447. Polk County conducts its annual tax sale under Iowa Code chapter 446. Do not treat the delinquent-tax amount or later tax-deed values as an auction opening bid.',bid:'https://www.polkcountyiowa.gov/treasurer/information-for-tax-sale-buyers/',canadian:'Polk County requires bidder registration and tax-identification documentation. Confirm current eligibility, tax-ID and registration requirements directly with the Treasurer before funding.',itin:'Verify current Polk County and Iowa bidder tax-identification requirements; do not assume an ITIN alone guarantees eligibility.',online:'Yes — Polk County states the June 15, 2026 annual tax sale used an online bidding process.',otc:'County/public-bidder or subsequent-sale availability is governed by Iowa law and county procedure; verify current Polk County inventory/status directly with the Treasurer.',deed:'A tax-sale certificate creates a lien and does not itself convey ownership. A tax deed, if eventually available after the statutory redemption and notice process, is a separate later stage under Iowa law.',special:'The complete 2026 available-property list was published through the county\'s designated newspaper rather than a verified county machine-readable bulk file. This row is therefore market-level only; the project must not fabricate parcel listings or scrape restricted owner data.',source:'https://www.polkcountyiowa.gov/treasurer/news/2026-property-tax-sale-takes-place-june-15/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Polk County row already present")
        return

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before = text[:end]
    after = text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Iowa Polk County tax-lien market")


if __name__ == "__main__":
    main()
