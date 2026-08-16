#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Miami-Dade County"

ROW = r'''{state:'Florida — Miami-Dade County',product:'Tax certificate / first-priority property-tax lien',schedule:'Miami-Dade County holds its annual tax-certificate sale on June 1. The official 2026 sale began June 1, 2026 for unpaid 2025 real-estate taxes.',availability:'2026 annual sale passed — monitor official Tax Collector for current certificate availability',maxReturn:'18%/yr max',interest:'Florida tax certificates are awarded to the investor accepting the lowest interest rate. Florida law caps certificate interest at 18% per year; actual winning rates may be lower.',bid:'https://www.mdctaxcollector.gov/services/tax-certificate-sales',canadian:'Foreign-bidder eligibility, payment funding, and U.S. tax-document requirements should be confirmed directly with the Miami-Dade County Tax Collector before registration.',itin:'Verify current taxpayer-identification and withholding requirements with the Tax Collector before participating.',online:'The Tax Collector publishes the annual tax-certificate sale and current participation information online; verify the current auction platform and registration rules on the official page.',otc:'Do not assume OTC inventory. Use only certificate availability explicitly published by the Miami-Dade County Tax Collector or its official sale platform.',deed:'A tax certificate is a lien, not ownership. A holder may submit a separate tax-deed application after 22 months; the Miami-Dade Clerk of Court conducts any later tax-deed sale.',special:'Miami-Dade explicitly warns that a tax certificate does not transfer ownership or title and that earnings depend on redemption. Florida law also restricts certificate-holder contact with owners during the statutory period.',source:'https://www.mdctaxcollector.gov/services/tax-certificate-sales'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Miami-Dade County row already present")
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
    print("Added Florida Miami-Dade County tax-lien market")


if __name__ == "__main__":
    main()
