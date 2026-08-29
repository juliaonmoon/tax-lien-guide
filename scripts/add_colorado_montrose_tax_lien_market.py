#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Montrose County"

ROW = r'''{state:'Colorado — Montrose County',product:'Tax lien / Certificate of Purchase',schedule:'MARKET-LEVEL ONLY — Montrose County publishes official Tax Sale Procedures and a Delinquent Tax Sale List, but the public pages reviewed do not clearly publish a current 2026 sale date/rate. Keep 2026 sale specifics pending until the Treasurer posts them.',availability:'2026 date pending official publication',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Colorado tax-lien certificate interest is set annually under state law. Montrose County has not clearly published a current 2026 certificate rate on the accessible official pages reviewed, so no prior-year rate is carried forward.',bid:'https://www.montrosecounty.net/217/Delinquent-Tax-Sale-List',canadian:'The current public Treasurer pages do not clearly publish foreign-bidder eligibility. Verify current registration and taxpayer-document requirements directly with Montrose County before funding.',itin:'Not clearly published on the accessible current tax-sale pages; verify current taxpayer-identification requirements with the Treasurer.',online:'Current 2026 auction format is not clearly published on the accessible official pages reviewed; verify with the Treasurer.',otc:'Montrose County publishes Tax Lien Certificate Assignment materials, but current assignable inventory/terms should be verified directly with the Treasurer.',deed:'A tax-lien Certificate of Purchase is not immediate property ownership. Montrose County separately publishes Treasurer\'s Deed public-auction procedures, which are a later and distinct process.',special:'MARKET-LEVEL ONLY until Montrose County publishes clearly current 2026 sale-specific rules/listing data that can be safely ingested. Do not substitute Public Trustee mortgage-foreclosure rows, Treasurer\'s Deed auction rows, owner-name data, or foreclosure/deed opening bids for tax-lien listings.',source:'https://www.montrosecounty.net/QuickLinks.aspx?CID=12'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Montrose County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Montrose County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Montrose County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Montrose County tax-lien market row")
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
    print("Added Colorado Montrose County tax-lien market")


if __name__ == "__main__":
    main()
