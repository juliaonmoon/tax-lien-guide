#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Broomfield County"

ROW = r'''{state:'Colorado — Broomfield County',product:'Property tax lien / Certificate of Purchase',schedule:'MARKET-LEVEL ONLY — Broomfield says delinquent taxes are normally advertised in October and the tax-lien sale is held in early November. The official site still exposes the 2025 delinquent list/results; a 2026 sale-specific list/date was not yet published when checked <span class="schedule-date">Aug 20, 2026</span>.',availability:'Upcoming — exact 2026 date/list pending official publication',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Broomfield states the certificate rate is nine percentage points above the applicable Federal Reserve discount rate on September 1 and remains fixed for the life of the certificate. The county page currently cites 15% for certificates sold in 2024, so no 2026 rate is inferred.',bid:'https://www.broomfield.org/814/Tax-Lien-Sale-Information',canadian:'The public tax-lien page does not clearly publish foreign-bidder eligibility. Verify current registration and tax-document requirements directly with the Treasurer before funding.',itin:'Not clearly published on the current tax-lien page; verify current U.S. taxpayer-identification requirements with the Treasurer.',online:'Current tax-lien rules and historical delinquent lists/results are published online; confirm the 2026 sale format with the Treasurer when the current notice is posted.',otc:'YES — Broomfield says liens not sold at the annual sale are held by the county and are normally available for purchase from the Treasurer, subject to current inventory.',deed:'Buying the tax lien does not grant property rights. Broomfield states most liens have a three-year redemption period; any later deed process is separate and very few liens reach deed.',special:'MARKET-LEVEL ONLY until Broomfield publishes a current 2026 delinquent tax-lien list. Do not substitute Public Trustee mortgage-foreclosure rows, owner-name data, the 2025 delinquent list, or foreclosure/deed bid amounts for 2026 tax-lien listings. Premium bids do not earn interest and are not refunded on redemption.',source:'https://www.broomfield.org/814/Tax-Lien-Sale-Information'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Broomfield County row already present")
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
    print("Added Colorado Broomfield County tax-lien market")


if __name__ == "__main__":
    main()
