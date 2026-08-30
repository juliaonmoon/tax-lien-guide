#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Miami-Dade County"

ROW = r'''{state:'Florida — Miami-Dade County',product:'Tax certificate / property-tax lien',schedule:'Miami-Dade County holds its annual tax-certificate sale beginning on or before June 1. The official Tax Collector states that the 2026 annual sale began June 1, 2026 for unpaid 2025 real-estate taxes.',availability:'2026 annual sale passed — monitor the official Tax Collector for current certificate availability or any explicitly published county-held inventory',maxReturn:'18%/yr statutory max',interest:'Florida tax certificates are awarded through reverse bidding to the investor accepting the lowest interest rate, subject to Florida’s statutory 18% annual cap; actual winning rates and redemption returns may be lower.',bid:'https://www.mdctaxcollector.gov/services/tax-certificate-sales',canadian:'Foreign-bidder eligibility, payment funding, and U.S. tax-document requirements should be confirmed directly with the Miami-Dade County Tax Collector before registration.',itin:'Verify current taxpayer-identification and withholding requirements with the Tax Collector before participating; do not assume an ITIN alone guarantees eligibility.',online:'The Tax Collector publishes the annual tax-certificate sale and current participation information online. Use only the current official Tax Collector page or its explicitly linked official sale system for registration and inventory.',otc:'Do not assume OTC or county-held inventory. Use only certificate availability explicitly published by the Miami-Dade County Tax Collector or its official sale platform.',deed:'A tax certificate is a lien, not ownership. A certificate holder may later apply for a tax deed after the statutory waiting period; the application and any later public tax-deed sale are separate processes, and the Miami-Dade Clerk of the Court conducts the tax-deed sale.',special:'Miami-Dade explicitly states that a tax certificate represents a lien on unpaid real-estate taxes. Preserve certificate-vs-deed terminology, do not treat certificates as property ownership, and do not substitute tax-deed inventory or deed-sale opening/minimum bids for tax-certificate data.',source:'https://www.mdctaxcollector.gov/services/tax-certificate-sales'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Miami-Dade County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Miami-Dade County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Miami-Dade County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Miami-Dade County tax-lien market row")
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
    print("Added Florida Miami-Dade County tax-lien market")


if __name__ == "__main__":
    main()
