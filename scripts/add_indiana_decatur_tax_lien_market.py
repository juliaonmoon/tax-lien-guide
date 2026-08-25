#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Indiana — Decatur County 2026"

ROW = r'''{state:'Indiana — Decatur County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Decatur County officially publishes a 2026 Tax Sale — Second Advertisement through the County Auditor. The county page confirms the current 2026 Treasurer/Auditor tax-sale process, but the guide does not infer an auction date or parcel eligibility beyond the current official notice.',availability:'Current 2026 tax-sale market confirmed — verify the latest Decatur County Auditor advertisement and Treasurer/SRI materials before bidding because parcels and amounts may change before sale',interest:'Indiana tax-sale purchaser returns are governed by statutory redemption rather than a simple APR. Verify the current Decatur County sale notice and Indiana Code 6-1.1-24 and 6-1.1-25 for minimum-bid components, redemption amounts, notice duties, and deadlines.',bid:'https://decaturcounty.in.gov/auditor/',canadian:'Not confirmed — verify current Decatur County bidder-registration and U.S. taxpayer-document requirements directly before participating.',itin:'Do not assume an ITIN or W-8 alone is accepted; verify current Decatur County sale-registration and tax-form requirements.',online:'Auction format is not inferred from the county landing page. Use the current official 2026 advertisement and any county-designated vendor instructions; do not bypass registration controls.',otc:'Not confirmed for the annual Treasurer tax sale. Do not treat later county-held certificate, Commissioners sale, or deed disposition paths as identical to the annual tax-certificate sale.',deed:'The Treasurer tax sale is a tax-sale certificate/lien process; title is not immediate. Any later tax deed requires separate Indiana statutory redemption, notice, and deed procedures.',special:'MARKET-LEVEL SUMMARY ONLY. Decatur County publishes a current 2026 Tax Sale — Second Advertisement, but the guide does not bulk republish owner/taxpayer names, freeze an advertised list as guaranteed current inventory, infer parcel-level opening/minimum bids, or substitute Decatur County Sheriff/judicial foreclosure sales for the Treasurer tax sale.',source:'https://decaturcounty.in.gov/auditor/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        row_re = re.compile(
            rf"\{{state:'{re.escape(MARKER)}'.*?\}}(?=\s*,|\s*\n\];)",
            re.S,
        )
        updated, count = row_re.subn(ROW, text, count=1)
        if count != 1:
            raise SystemExit(f"Could not uniquely refresh {MARKER}")
        INDEX.write_text(updated, encoding="utf-8")
        print("Refreshed Decatur County Indiana tax-lien market")
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
    print("Added Decatur County Indiana tax-lien market")


if __name__ == "__main__":
    main()
