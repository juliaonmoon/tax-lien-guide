#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Wyoming — Carbon County"

ROW = r'''{state:'Wyoming — Carbon County',product:'Tax lien / Certificate of Purchase',schedule:'Carbon County held its 2026 delinquent-tax sale on <span class="schedule-date">August 10, 2026</span> for delinquent 2025 property taxes; monitor the Treasurer page for the next annual sale and current list.',availability:'Passed — monitor next sale',interest:'Purchasers receive a 3% penalty on the amount purchased plus statutory 15% annual interest from the sale date; eligible subsequent taxes paid by the certificate holder also earn 15%.',bid:'https://carboncountywy.gov/1161/Tax-Sale-Information',canadian:'In-person purchaser rules apply; confirm current identity, taxpayer-document and payment requirements directly with the Carbon County Treasurer before planning to attend',itin:'County page does not state a foreign-bidder rule; confirm current taxpayer-ID/W-9 requirements directly with the Treasurer',online:'No — 2026 sale was held in person in Rawlins',otc:'County may hold liens it cannot sell; verify any later assignment availability directly with the Treasurer',deed:'Certificate holder may apply for a tax deed no earlier than 4 years after the sale if the property remains unredeemed and statutory notice requirements are satisfied.',special:'The Treasurer explicitly states that the tax sale sells the county tax lien, not the property. A Certificate of Purchase is issued. The certificate does not give immediate ownership or possession rights.',source:'https://carboncountywy.gov/1161/Tax-Sale-Information'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Wyoming Carbon County row already present")
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
    print("Added Wyoming Carbon County tax-lien market")


if __name__ == "__main__":
    main()
