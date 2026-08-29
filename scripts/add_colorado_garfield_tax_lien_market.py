#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Garfield County"

ROW = r'''{state:'Colorado — Garfield County',product:'Tax lien certificate',schedule:'Garfield County states that its annual tax lien sale is held in early November each year, with the delinquent-account listing advertised and posted online in late September and throughout October. A current 2026 sale-specific list/date was not yet published on the official pages reviewed.',availability:'2026 annual sale expected in early November under the county’s published annual schedule; verify the current Treasurer notice/list when posted',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Garfield County explains that the tax-lien certificate earns the county/state-set annual redemption rate on the lien principal; premium bids above the minimum do not earn interest and are not refunded on redemption. Do not carry an older year’s published rate into 2026 before the current rate is officially posted.',bid:'https://www.garfieldcountyco.gov/treasurer/faqs/',canadian:'The current public county pages do not clearly publish foreign-bidder eligibility. Confirm registration, payment, identity, and U.S. tax-document requirements directly with the Garfield County Treasurer before funding.',itin:'Not clearly published for foreign bidders on the current tax-lien pages; verify taxpayer-identification requirements directly with the Treasurer.',online:'Current 2026 auction format was not yet clearly published on the official pages reviewed; use the Treasurer’s current tax-lien sale notice when posted.',otc:'Garfield County’s current public pages reviewed do not clearly publish a standing over-the-counter assignment program. Do not assume unsold annual-sale liens remain directly purchasable without current Treasurer confirmation.',deed:'Buying the tax lien creates a certificate/lien, not ownership or possession of the property. Garfield County separately documents the later Treasurer’s Deed option/public-auction process under newer Colorado law; that later deed auction is distinct from the original tax-lien sale.',special:'MARKET-LEVEL ONLY until Garfield County publishes a current 2026 delinquent tax-lien sale list and sale-specific terms that can be safely and unambiguously ingested. Do not substitute Public Trustee mortgage-foreclosure rows, Treasurer’s Deed auction rows, owner-name data, an older lien list/rate, or fabricated parcel/opening-bid data.',source:'https://www.garfieldcountyco.gov/treasurer/faqs/'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Garfield County marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Garfield County marker but could not locate row end")
    return row_start, min(endings) + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Garfield County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Garfield County tax-lien market row")
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
    print("Added Colorado Garfield County tax-lien market")


if __name__ == "__main__":
    main()
