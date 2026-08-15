#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Hillsborough County"

ROW = r'''{state:'Florida — Hillsborough County',product:'Tax certificate / first-priority property-tax lien',schedule:'Hillsborough County conducts an annual tax-certificate sale on or before June 1. The official 2026 sale was May 30, 2026; county-held certificates may remain available after the sale.',availability:'2026 annual sale passed — county-held certificates may be available',maxReturn:'18%/yr max',interest:'Online reverse auction: bidding begins at 18% and is bid down in 0.25% increments; the lowest accepted rate wins. Certificates receiving no bids are issued to the county at 18%.',bid:'https://www.hillstaxfl.gov/taxes/tax-certificate/',canadian:'Foreign-bidder eligibility and U.S. tax-document requirements should be confirmed directly with the Hillsborough County Tax Collector before registration.',itin:'Verify current taxpayer-identification and withholding requirements with the Tax Collector before bidding or purchasing county-held certificates.',online:'YES — Hillsborough County describes the annual tax-certificate sale as an online auction; current registration is linked from the official Tax Collector page.',otc:'YES — county-held certificates that were not purchased at the annual sale may be purchased after the sale through LienHub while still available.',deed:'A tax certificate is a lien, not ownership. If the owner does not redeem, a certificate holder may apply for a separate tax-deed process after the statutory waiting period; the deed sale is a different product.',special:'Hillsborough County explicitly states that tax certificates convey no property rights. Certificates are valid for seven years, and the Tax Collector warns purchasers to research the property and certificate before investing.',source:'https://www.hillstaxfl.gov/tax-certificate-process/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Hillsborough County row already present")
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
    print("Added Florida Hillsborough County tax-lien market")


if __name__ == "__main__":
    main()
