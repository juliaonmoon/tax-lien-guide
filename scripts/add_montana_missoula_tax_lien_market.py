#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Missoula County"

ROW = r'''{state:'Montana — Missoula County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Missoula County documents that tax liens attach on the first business day in August and that third-party investors may purchase outstanding liens in late August. A safely ingestible current 2026 bulk parcel list was not verified in this refresh, so no property rows are published here.',availability:'Late-August third-party assignments under county priority procedures; verify current 2026 availability with the Clerk & Treasurer',maxReturn:'10%/yr statutory delinquent-tax interest',interest:'Missoula County states delinquent taxes incur a 2% penalty plus interest at a 10% annualized rate. Investors may take assignment of outstanding real-property tax liens after following county notice, priority, funding, and assignment requirements.',bid:'https://www.missoulacounty.gov/departments/clerk-treasurer/property-taxes/delinquent-taxes/',canadian:'Current foreign-bidder eligibility is not clearly established in the public county guidance; verify identity, payment, notice, and tax-document requirements directly with the Clerk & Treasurer.',itin:'The accessible county guidance does not establish a specific U.S. taxpayer-ID rule for foreign assignees; verify directly with the Clerk & Treasurer.',online:'Not a reverse auction. Missoula County gives first priority to qualifying electronic assignment submissions that include a parcel-preference list, proof of notice, and sufficient funds.',otc:'YES — outstanding county-held real-property tax liens may be assigned after statutory notice and county procedures; availability changes as taxpayers redeem.',deed:'A tax-lien assignment is not property ownership. Missoula County states taxpayers generally have two to three years from attachment to pay before risking loss of the property; tax deed is a later statutory process.',special:'MARKET-LEVEL ONLY until Missoula County exposes a current 2026 parcel lien list in a clearly redistributable, safely machine-readable form. Do not scrape taxpayer names, infer parcel records from tax-deed/foreclosure data, or treat delinquent amounts as opening bids. Missoula uses a lien-assignment priority process rather than an interest-rate auction.',source:'https://www.missoulacounty.gov/departments/clerk-treasurer/property-taxes/delinquent-taxes/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Missoula County row already present")
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
    print("Added Montana Missoula County tax-lien market")


if __name__ == "__main__":
    main()
