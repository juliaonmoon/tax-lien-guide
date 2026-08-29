#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Broomfield County"

ROW = r'''{state:'Colorado — Broomfield County',product:'Property tax lien / Certificate of Purchase',schedule:'MARKET-LEVEL ONLY — Broomfield says its tax-lien sale is a public auction held each year, usually in November. The official site still exposes the 2025 delinquent list/results; a 2026 sale-specific list/date was not yet published when checked <span class="schedule-date">Aug 29, 2026</span>.',availability:'Upcoming — exact 2026 date/list pending official publication',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Broomfield states the certificate rate is nine percentage points above the applicable Federal Reserve discount rate on September 1 and remains fixed for the life of the certificate. The county page currently cites 15% for certificates sold in 2024, so no 2026 rate is inferred.',bid:'https://www.broomfield.org/814/Tax-Lien-Sale-Information',canadian:'The public tax-lien page says anyone except city/county employees and their immediate families may purchase liens, but its registration instructions require a W-9 with an SSN or EIN. Do not infer foreign-bidder eligibility from the general wording; verify current identity and U.S. tax-document requirements directly with the Treasurer before funding.',itin:'Not clearly published for foreign bidders on the current tax-lien page; verify current U.S. taxpayer-identification requirements with the Treasurer.',online:'Current tax-lien rules and historical delinquent lists/results are published online; confirm the 2026 sale format with the Treasurer when the current notice is posted.',otc:'YES — Broomfield says liens not sold at the annual sale are held by the county and are normally available for purchase from the Treasurer, subject to current inventory.',deed:'Buying the tax lien does not grant property rights. Broomfield states most liens have a three-year redemption period; any later deed process is separate and very few liens reach deed.',special:'MARKET-LEVEL ONLY until Broomfield publishes a current 2026 delinquent tax-lien list. Do not substitute Public Trustee mortgage-foreclosure rows, owner-name data, the 2025 delinquent list, or foreclosure/deed bid amounts for 2026 tax-lien listings. Do not fabricate parcel inventory, opening/minimum bids, payoff amounts, current county-held availability, property characteristics, redemption/deed outcomes, or bulk owner/taxpayer data. Premium bids do not earn interest and are not refunded on redemption.',source:'https://www.broomfield.org/814/Tax-Lien-Sale-Information'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Broomfield County marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Broomfield County marker but could not locate row end")
    return row_start, min(endings) + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Broomfield County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Broomfield County tax-lien market row")
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
