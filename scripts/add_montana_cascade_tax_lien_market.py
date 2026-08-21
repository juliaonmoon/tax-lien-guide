#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Cascade County"

ROW = r'''{state:'Montana — Cascade County',product:'Tax lien assignment / certificate',schedule:'MARKET-LEVEL ONLY — Cascade County administers property-tax lien assignments and redemptions. A current 2026 county-held tax-lien inventory that is clearly safe to bulk republish was not verified, so no property-level lien rows are published here.',availability:'County-held lien assignments are handled by the Treasurer under Montana law; contact the Treasurer for current assignable inventory and procedures',maxReturn:'10%/yr statutory delinquent-tax interest',interest:'Montana delinquent-property-tax interest is 10% annualized. Cascade County documents tax-lien assignment procedures and redemptions; this is not a reverse-auction interest-rate market.',bid:'https://www.cascadecountymt.gov/274/Property-Tax',canadian:'Current foreign-bidder eligibility is not clearly established in the public county guidance; verify identity, payment, notice, and tax-document requirements directly with the Treasurer.',itin:'The accessible county guidance does not publish a specific foreign-assignee taxpayer-ID rule; verify directly with the Treasurer before funding an assignment.',online:'No verified public 2026 reverse-auction portal. Cascade County provides nightly-updated public parcel/tax information, but lien assignments are administered through the Treasurer.',otc:'Potentially yes — county-held tax liens may be assigned under Montana procedures; current inventory must be confirmed with the Treasurer.',deed:'A tax-lien assignment is not immediate property ownership. A tax deed is a later statutory process after the redemption/notice requirements are satisfied.',special:'MARKET-LEVEL ONLY. Do not bulk republish taxpayer/owner names, infer a 2026 lien inventory from the county parcel-search system, or substitute Cascade tax-deed auction parcels/opening bids for tax-lien assignments. The county separately administers tax-deed proceedings.',source:'https://www.cascadecountymt.gov/302/Treasurers-Office'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Cascade County row already present")
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
    print("Added Montana Cascade County tax-lien market")


if __name__ == "__main__":
    main()
