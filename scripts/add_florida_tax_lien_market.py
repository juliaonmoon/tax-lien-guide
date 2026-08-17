#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Pinellas County"

ROW = r'''{state:'Florida — Pinellas County',product:'Tax certificate / first-priority property-tax lien',schedule:'Pinellas County conducts its tax certificate sale online each year on or before June 1. The County published its 2026 Tax Certificate Sale for May 30, 2026.',availability:'2026 annual sale passed — county-held certificates become available for purchase on the first business day of September',interest:'Reverse auction: bidders compete by accepting the lowest interest rate. Pinellas County states certificates with no bids are struck to the County at 18%, the maximum rate allowed by Florida law. Actual investor yield depends on the winning bid rate and redemption timing.',bid:'https://pinellastaxcollector.gov/property-tax/tax-certificate-and-tax-deed/',canadian:'The County describes the sale as open to registered bidders through LienHub, but bidders must satisfy current registration, payment and U.S. tax-reporting requirements. Foreign bidders should confirm eligibility directly with the Tax Collector before participating.',itin:'Pinellas County states registered bidders must provide a federal taxpayer identification number or Social Security number; confirm whether an ITIN is accepted before bidding.',online:'YES — Pinellas County states the annual tax certificate sale is conducted online through LienHub using a reverse-auction format.',otc:'YES — certificates not sold at the annual sale are struck to Pinellas County and may be purchased through LienHub beginning the first business day of September.',deed:'A tax certificate is a lien, not ownership of the property. If the taxes remain unpaid, a certificate holder may apply for a tax deed after two years from the date of delinquency; the property can then proceed through a separate public tax-deed process if it is not redeemed.',special:'Pinellas County explicitly warns investors to research certificates before bidding. A certificate conveys no immediate property rights. Certificates generally remain valid for seven years from issuance unless redeemed or otherwise resolved.',source:'https://pinellastaxcollector.gov/property-tax/tax-certificate-and-tax-deed/'}'''


def add_pinellas():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Pinellas County row already present")
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
    print("Added Florida Pinellas County tax-lien market")


def main():
    add_pinellas()
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "add_florida_marion_tax_lien_market.py")],
        check=True,
    )


if __name__ == "__main__":
    main()
