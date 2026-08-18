#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Hernando County"

ROW = r'''{state:'Florida — Hernando County',product:'Tax certificate / property-tax lien',schedule:'Annual tax-certificate sale must be held by the end of May. Hernando County Clerk states the sale is conducted online through LienHub; verify the Tax Collector for the current annual sale notice and inventory.',availability:'Annual sale cycle; verify current county-held / post-sale availability with the Hernando County Tax Collector and official LienHub portal',maxReturn:'18%/yr statutory max',interest:'Florida reverse auction. Hernando County states the certificate is sold to the registered bidder willing to accept the lowest redemption interest rate, which may range from 0% to 18%.',bid:'https://hernandoclerk.com/additional-services/tax-deeds/',canadian:'No Hernando-specific foreign-bidder eligibility rule was identified in the official county material reviewed. Verify current registration, taxpayer-identification, withholding, funding and payment requirements with the Tax Collector / official auction platform before bidding.',itin:'Verify current taxpayer-identification and withholding requirements directly with the Hernando County Tax Collector / LienHub; do not assume an ITIN alone guarantees eligibility.',online:'Yes — Hernando County states the tax-certificate sale is held online through LienHub.',otc:'County-held / post-sale certificate availability is Tax Collector-specific; verify current official inventory rather than assuming unsold certificates are continuously available.',deed:'A tax certificate is a lien and does not convey title. Hernando County states that if a certificate remains unredeemed for the statutory period, the certificate holder may begin a separate tax-deed process; the Clerk then conducts the property auction.',special:'Do not mix Hernando tax certificates with tax-deed listings or tax-deed base bids. The Tax Collector sells liens; the Clerk separately conducts tax-deed property auctions. Tax-deed opening/base bids are not tax-certificate minimum bids.',source:'https://hernandoclerk.com/additional-services/tax-deeds/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Hernando County row already present")
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
    print("Added Florida Hernando County tax-lien market")


if __name__ == "__main__":
    main()
