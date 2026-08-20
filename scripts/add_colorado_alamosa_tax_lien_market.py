#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Alamosa County"

ROW = r'''{state:'Colorado — Alamosa County',product:'County-held tax lien / Certificate of Purchase assignment',schedule:'County-held liens are available by assignment from the Treasurer; the official list reviewed is dated <span class="schedule-date">June 18, 2026</span> and the county says it is updated quarterly. Verify annual-sale dates separately with the Treasurer.',availability:'Open now — county-held assignments, subject to current inventory',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Colorado tax-lien interest is set under state law for each sale year. Alamosa does not publish a 2026 rate on the county-held-lien page reviewed here, so no current-year rate is inferred.',bid:'https://www.alamosacounty.org/324/County-Held-Tax-Liens',canadian:'The public county-held assignment page does not publish a foreign-bidder eligibility rule. Verify identity and tax-document requirements directly with the Treasurer before funding.',itin:'Not clearly published on the county-held assignment page; verify current taxpayer-identification requirements with the Treasurer.',online:'Research/list access is online; assignment/payment procedure should be confirmed with the Treasurer.',otc:'YES — official county-held tax liens may be assigned to investors. The county says the list is updated quarterly; contact the Treasurer for the current amount due.',deed:'An assignment is a tax lien, not ownership or access to the property. If the county has held the lien for at least three years, the assignee may be eligible to apply for a Treasurer\'s Deed; otherwise the investor must wait until the statutory holding period is met.',special:'The official county-held list does not publish amounts due. Do not treat a parcel on the list as having a known opening/minimum bid; contact the Treasurer for the current assignment total. Tax-lien purchase and later Treasurer\'s Deed are separate stages.',source:'https://www.alamosacounty.org/324/County-Held-Tax-Liens'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Alamosa County row already present")
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
