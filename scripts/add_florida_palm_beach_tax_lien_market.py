#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Palm Beach County"

ROW = r'''{state:'Florida — Palm Beach County',product:'Tax certificate / first-priority property-tax lien',schedule:'Palm Beach County holds an annual tax-certificate sale for unpaid prior-year real-estate taxes. Under the official Tax Collector guidance, the sale is held 60 days after delinquency or June 1, whichever is later; county-held certificates may remain purchasable afterward.',availability:'2026 annual sale passed — county-held certificates may be available',maxReturn:'18%/yr max',interest:'Competitive tax-certificate bidding determines the investor rate. Palm Beach County states that county-held certificates accrue 18% annual interest (1.5% per month); annual-sale certificates are subject to Florida competitive-bid rules.',bid:'https://www.pbctax.gov/taxes/property-tax/tax-certificates-and-deeds/',canadian:'Foreign-bidder eligibility and U.S. tax-document requirements should be confirmed directly with the Palm Beach County Constitutional Tax Collector and RealAuction before registration or purchase.',itin:'Verify current taxpayer-identification and withholding documentation requirements with the Tax Collector before bidding or purchasing county-held certificates.',online:'YES for auction registration — the official Palm Beach County page directs tax-certificate buyers to RealAuction; county-held purchases may also be completed through the Tax Collector using its published procedures.',otc:'YES — certificates not purchased at the annual sale are struck to the county and may be purchased after issuance and before a tax-deed application, subject to current availability and county confirmation.',deed:'A tax certificate is an enforceable lien, not ownership. If delinquent taxes remain unpaid for the statutory period, the certificate holder may file a separate Tax Deed Application; the resulting tax-deed sale is conducted separately by the Clerk & Comptroller.',special:'Palm Beach County explicitly distinguishes tax certificates from tax deeds. County-held certificates accrue 18% annual interest, and buyers are instructed to research the current county-held list and confirm certificate status with the Tax Collector before purchase.',source:'https://www.pbctax.gov/taxes/property-tax/tax-certificates-and-deeds/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Palm Beach County row already present")
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
    print("Added Florida Palm Beach County tax-lien market")


if __name__ == "__main__":
    main()
