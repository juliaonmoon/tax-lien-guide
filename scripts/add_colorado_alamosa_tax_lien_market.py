#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Alamosa County"

ROW = r'''{state:'Colorado — Alamosa County',product:'County-held tax lien / Certificate of Purchase assignment',schedule:'Alamosa County says county-held liens from its annual tax-lien sale may be assigned to investors. The official county-held list currently linked by the Treasurer is dated <span class="schedule-date">August 24, 2026</span> and the county says the list is updated quarterly. The annual tax-lien auction is typically held in November; verify the separate current-year sale page for the exact annual-sale schedule.',availability:'County-held assignments are available subject to the Treasurer’s current inventory and payoff total. The linked county-held list is a research list, not proof that any particular lien remains available at the moment of purchase.',maxReturn:'Variable annual statutory rate; county FAQ says the rate cannot be below 8% per year and is typically 10%–15%, but do not infer a specific 2026 rate without the current sale publication.',interest:'Alamosa County states tax-lien interest varies from year to year. Use the rate published for the applicable certificate/sale year; do not reuse a prior-year rate as a current rate.',bid:'https://www.alamosacounty.org/324/County-Held-Tax-Liens',canadian:'The public county-held assignment materials reviewed do not publish a foreign-bidder eligibility rule. Verify identity, payment, and tax-document requirements directly with the Treasurer before funding.',itin:'Not clearly published on the county-held assignment page; verify current taxpayer-identification requirements with the Treasurer.',online:'Research/list access is online. Alamosa County says its annual tax-lien sale is held online in the fall, while county-held assignment/payment instructions should be confirmed directly with the Treasurer.',otc:'YES — official county-held tax liens may be assigned to outside investors. The county says assignment requires the current tax-lien amount, accrued interest, and the statutory Treasurer fee; because the public list omits amounts due and changes over time, contact the Treasurer for the current total and availability.',deed:'A county-held assignment is a tax lien, not ownership or access to the property. The county states the owner redemption period is three years from the original tax-lien sale date; after the statutory requirements are met, the certificate holder may pursue the separate Treasurer’s Deed process. Current Colorado law adds a later public-auction stage to that deed process, so do not present a lien assignment as an automatic transfer of the real estate.',special:'MARKET-LEVEL ONLY. The official county-held list does not publish amounts due. Do not fabricate parcel-level opening/minimum bids, current payoff totals, availability, ownership/property characteristics, redemption outcomes, or deed outcomes, and do not bulk republish owner/taxpayer names. Keep the annual tax-lien sale, county-held lien assignment, and later Treasurer’s Deed/public-auction process distinct.',source:'https://www.alamosacounty.org/324/County-Held-Tax-Liens'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Alamosa County marker but could not locate row start")
    row_end = text.find("}\n", marker_pos)
    if row_end < 0:
        row_end = text.find("},\n", marker_pos)
        if row_end < 0:
            raise SystemExit("Found Alamosa County marker but could not locate row end")
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Alamosa County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Alamosa County county-held tax-lien market row")
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
    print("Added Colorado Alamosa County county-held tax-lien market")


if __name__ == "__main__":
    main()
