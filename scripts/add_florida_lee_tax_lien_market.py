#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Lee County"

ROW = r'''{state:'Florida — Lee County',product:'Tax certificate / first-priority property-tax lien',schedule:'Lee County conducts its annual tax-certificate sale online in May for delinquent real-estate taxes. Certificates not sold at the annual sale may be held by the county and purchased afterward before redemption or execution of a tax deed.',availability:'2026 annual sale passed — county-held certificates may be available',maxReturn:'18%/yr statutory max',interest:'Florida tax-certificate auctions use competitive bidding on the interest rate, subject to the state statutory ceiling. The actual investor return may be bid below the maximum; county-held purchases follow the county\'s published certificate terms.',bid:'https://leetc.com/tax-certificates/',canadian:'Foreign-bidder eligibility, registration, payment, and U.S. tax-document requirements should be confirmed directly with the Lee County Tax Collector and the official auction platform before funding an account.',itin:'Verify current taxpayer-identification and withholding-document requirements with the Lee County Tax Collector before bidding or purchasing a county-held certificate.',online:'YES — Lee County states that the annual tax-certificate sale is conducted online and directs bidders to LienHub.',otc:'YES — Lee County states that certificates not sold at the tax-certificate sale are held by the county and may be purchased afterward before redemption or execution of a tax deed.',deed:'A tax certificate is a lien, not ownership. Lee County states that the holder of an unredeemed certificate may apply for a tax deed after the statutory waiting period; the tax-deed process is separate and does not guarantee title.',special:'Lee County explicitly distinguishes purchase of a tax certificate from purchase of the property. County-held certificate cost includes the certificate face value, accrued interest, and the county\'s published processing fee; buyers should verify current certificate status before purchase.',source:'https://leetc.com/tax-certificates/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Lee County row already present")
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
    print("Added Florida Lee County tax-lien market")


if __name__ == "__main__":
    main()
