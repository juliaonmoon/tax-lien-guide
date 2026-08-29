#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Chaffee County"

ROW = r'''{state:'Colorado — Chaffee County',product:'Tax lien certificate / Certificate of Purchase',schedule:'MARKET-LEVEL ONLY — Chaffee County publishes general tax-lien investment rules, but the official Treasurer page currently says “Nothing at this time” under Tax Lien Sale Purchase and Issuance of Treasurer Deed. A current 2026 sale-specific date/list was not published when checked <span class="schedule-date">Aug 29, 2026</span>.',availability:'2026 sale-specific date/list pending official Treasurer publication',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Chaffee County explains that the annual certificate rate is set at nine percentage points above the Federal discount rate as of September 1 and is fixed for the life of the certificate. Do not carry a prior-year rate into 2026 before the current rate is officially set/published.',bid:'https://search.chaffeecounty.org/Treasurer',canadian:'The current public Treasurer page does not clearly publish foreign-bidder eligibility. Confirm registration, payment, identity and tax-document requirements directly with the Chaffee County Treasurer before funding.',itin:'Not clearly published for foreign bidders on the current Treasurer page; verify taxpayer-identification requirements directly with the county.',online:'Current 2026 auction format is not published on the official page reviewed; verify the current Treasurer notice when posted.',otc:'The current official page reviewed does not clearly publish a standing over-the-counter assignment inventory. Do not assume unsold annual-sale liens are directly purchasable without Treasurer confirmation.',deed:'A tax-lien purchase creates a Certificate of Purchase/lien, not ownership or possession. Chaffee County separately describes the later Treasurer’s Deed application process after the statutory period; that deed stage is distinct from the original tax-lien purchase.',special:'MARKET-LEVEL ONLY until Chaffee County publishes a current 2026 tax-lien sale notice/list that can be safely and unambiguously ingested. Do not substitute Public Trustee mortgage foreclosures, Treasurer’s Deed rows, owner-name data, prior-year sale details, or fabricated parcel/opening-bid data. Do not fabricate parcel inventory, opening/minimum bids, payoff amounts, current availability, property characteristics, redemption/deed outcomes, or bulk owner/taxpayer data.',source:'https://search.chaffeecounty.org/Treasurer'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Chaffee County marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Chaffee County marker but could not locate row end")
    return row_start, min(endings) + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Chaffee County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Chaffee County tax-lien market row")
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
    print("Added Colorado Chaffee County tax-lien market")


if __name__ == "__main__":
    main()
