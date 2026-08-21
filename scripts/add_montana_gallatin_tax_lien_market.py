#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Gallatin County"

ROW = r'''{state:'Montana — Gallatin County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Gallatin County documents the real-property tax-lien and assignment process and states that a parcel lien list is made available to interested parties. A safely ingestible current 2026 bulk parcel list was not verified in this refresh, so no property rows are published here.',availability:'Lien assignments generally become available after the first working day in August; verify current 2026 availability with the Treasurer',maxReturn:'10%/yr statutory delinquent-tax interest',interest:'Gallatin County states delinquent real-property taxes accrue 5/6 of 1% per month (10% annualized). A third party may take an assignment by paying the delinquent taxes, penalty, interest and costs after following Montana notice and assignment requirements.',bid:'https://www.gallatinmt.gov/679/Delinquent-Taxes-Tax-Liens-and-Assignmen',canadian:'Current foreign-bidder eligibility is not clearly established in the public county guidance; verify identity, payment and notice requirements directly with the Treasurer before attempting an assignment.',itin:'The accessible county guidance does not establish a specific U.S. taxpayer-ID rule for foreign assignees; verify directly with the Treasurer.',online:'Assignment requests may be submitted electronically under the county priority policy, but this is not an online reverse auction.',otc:'YES — unpaid county-held real-property tax liens may be assigned after statutory notice and county procedures; availability changes as taxpayers redeem.',deed:'A tax-lien assignment is not property ownership. Montana tax deed is a later statutory process if the lien remains unredeemed.',special:'MARKET-LEVEL ONLY until Gallatin County exposes a current 2026 parcel lien list in a clearly redistributable, safely machine-readable form. Do not scrape taxpayer names, infer parcel records from tax-deed/foreclosure data, or treat delinquent amounts as opening bids. Gallatin uses an assignment-priority process rather than a Florida-style interest-rate auction.',source:'https://www.gallatinmt.gov/679/Delinquent-Taxes-Tax-Liens-and-Assignmen'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Gallatin County row already present")
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
    print("Added Montana Gallatin County tax-lien market")


if __name__ == "__main__":
    main()
