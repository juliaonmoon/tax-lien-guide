#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Indiana — Randolph County 2026"

ROW = r'''{state:'Indiana — Randolph County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Randolph County conducts tax-certificate sales annually. The current official county pages confirm the tax-sale certificate process and direct investors to SRI for current available tax-lien properties; a specific 2026 annual-sale date is not currently published on the county tax-sale page, so the guide does not invent one.',availability:'Current market confirmed — verify the live SRI/county property list and current sale notice before bidding',interest:'Indiana tax-sale purchaser returns are governed by statutory redemption rather than a simple APR. Randolph County states the owner generally has up to 12 months to redeem the certificate by paying delinquent taxes, interest, and required legal fees. Verify the current county/SRI packet and Indiana Code 6-1.1-24 and 6-1.1-25 for the exact certificate, redemption amount, notice duties, and deadlines.',bid:'https://www.in.gov/counties/randolph/departments/treasurer/tax-certificate-sales/',canadian:'Not confirmed — verify current Randolph County/SRI bidder-registration and U.S. taxpayer-document requirements directly before participating.',itin:'Do not assume an ITIN or W-8 alone is accepted; verify Randolph County/SRI current registration and tax-form requirements.',online:'Randolph County uses SRI for tax-certificate sales and links investors to SRI for current available tax-lien properties and bidding information. Do not bypass SRI registration controls.',otc:'Not confirmed for the annual tax sale. Randolph County separately describes Commissioners Certificate Sales for real estate that did not sell in an annual tax sale; that is a distinct sale path and must not be represented as the annual Treasurer tax sale.',deed:'Purchaser receives a Tax Sale Certificate/lien, not the real estate. If the certificate is not redeemed within the statutory period, the certificate holder may later petition for a tax sale deed; title is not immediate.',special:'MARKET-LEVEL SUMMARY ONLY. Randolph County directs investors to SRI for current available tax-lien properties, but the guide does not bulk republish owner/taxpayer names, freeze a changing SRI list as guaranteed inventory, infer parcel-level opening/minimum bids, or substitute Commissioners Certificate Sale or Sheriff/judicial foreclosure records for the annual tax-certificate sale.',source:'https://www.in.gov/counties/randolph/departments/treasurer/tax-certificate-sales/'}'''


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
        print("Refreshed Randolph County Indiana tax-lien market")
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
    print("Added Randolph County Indiana tax-lien market")


if __name__ == "__main__":
    main()
