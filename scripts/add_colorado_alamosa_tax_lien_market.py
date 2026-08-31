#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Alamosa County"

ROW = r'''{state:'Colorado — Alamosa County',product:'County-held tax lien / Certificate of Purchase assignment',schedule:'Alamosa County’s official Treasurer page states the 2026 Tax Lien Sale will be held on <span class="schedule-date">October 21, 2026</span>. Separately, county-held liens from prior annual tax-lien sales may be assigned to investors; the official county-held list currently linked by the Treasurer is dated <span class="schedule-date">August 24, 2026</span> and the county says that list is updated quarterly.',availability:'2026 annual tax-lien sale scheduled for October 21, 2026. County-held assignments are separately available subject to the Treasurer’s current inventory and payoff total; the linked research list is not proof that any particular lien remains available at the moment of purchase.',maxReturn:'Variable annual statutory rate; county materials say tax-lien interest varies by year. Do not infer a specific 2026 rate without the current sale publication or certificate terms.',interest:'Alamosa County states tax-lien interest varies from year to year. Use the rate published for the applicable certificate/sale year; do not reuse a prior-year rate as a current rate.',bid:'https://www.alamosacounty.org/198/Treasurer-Public-Trustee',canadian:'The public annual-sale and county-held assignment materials reviewed do not clearly publish foreign-bidder eligibility. Verify registration, identity, payment, and tax-document requirements directly with the Treasurer before funding.',itin:'Not clearly published in the official materials reviewed; verify current taxpayer-identification requirements with the Treasurer.',online:'The county publishes tax-lien information and county-held inventory online. Verify the current annual-sale bidding method and registration instructions on the Treasurer’s official sale materials before participating.',otc:'YES — official county-held tax liens may be assigned to outside investors. The county says assignment requires the current tax-lien amount, accrued interest, and the statutory Treasurer fee; because the public list omits amounts due and changes over time, contact the Treasurer for the current total and availability.',deed:'A county-held assignment or annual-sale certificate is a tax lien, not ownership or access to the property. The county states the owner redemption period is three years from the original tax-lien sale date; after statutory requirements are met, a certificate holder may pursue the separate Treasurer’s Deed process. Do not present a lien purchase as an automatic transfer of real estate.',special:'MARKET-LEVEL ONLY. Keep the annual tax-lien sale, county-held lien assignment, and later Treasurer’s Deed process distinct. The official county-held list does not publish amounts due. Do not fabricate parcel-level opening/minimum bids, current payoff totals, availability, ownership/property characteristics, redemption outcomes, or deed outcomes, and do not bulk republish owner/taxpayer names.',source:'https://www.alamosacounty.org/198/Treasurer-Public-Trustee'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Alamosa County marker but could not locate row start")

    candidates = []
    for terminator in ("},\n", "}\n", "},\r\n", "}\r\n"):
        pos = text.find(terminator, marker_pos)
        if pos >= 0:
            candidates.append((pos, terminator))
    if not candidates:
        raise SystemExit("Found Alamosa County marker but could not locate row end")

    row_end, terminator = min(candidates, key=lambda item: item[0])
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
