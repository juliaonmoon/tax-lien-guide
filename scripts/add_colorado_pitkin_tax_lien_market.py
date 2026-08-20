#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Pitkin County"

ROW = r'''{state:'Colorado — Pitkin County',product:'Tax lien certificate / Certificate of Purchase',schedule:'Online tax-lien sale <span class="schedule-date">Nov 5, 2026</span>; registration/sale site opens Oct 5, 2026 and the delinquent-property list is expected on the sale site and in the Aspen Daily News beginning Oct 13',availability:'Upcoming — Nov 5, 2026',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Pitkin County states simple interest accrues at 9 percentage points above the Federal Discount rate as of September 1 each year, rounded to the nearest full percent, and stays fixed for the life of the certificate. The county currently lists the 2026 sale interest rate as to be determined.',bid:'https://pitkincounty.com/333/Tax-Lien-Sale',canadian:'The current public Treasurer page does not clearly publish foreign-bidder eligibility. Confirm registration, payment, identity and tax-document requirements directly with Pitkin County before funding.',itin:'Not clearly published for foreign bidders on the current Treasurer page; verify taxpayer-identification requirements directly with the county.',online:'YES — Pitkin County states the Nov 5, 2026 sale will be online at pitkin.coloradotaxsale.com',otc:'The current 2026 Treasurer page reviewed does not clearly publish a standing over-the-counter assignment inventory. Do not assume unsold liens are directly purchasable without Treasurer confirmation.',deed:'A tax-lien Certificate of Purchase is not property ownership. Pitkin County separately documents a later Treasurer’s Deed public-auction process after the statutory period; that deed auction is distinct from the original tax-lien sale.',special:'MARKET-LEVEL ONLY until Pitkin County publishes its 2026 delinquent-property list in October and the list is verified as safely ingestible. The tax-lien starting bid is taxes, interest and fees owed; premium bids do not earn interest and are not returned on redemption. Do not substitute Treasurer’s Deed auctions, Public Trustee foreclosures, owner-name data, or fabricated parcel/opening-bid data.',source:'https://pitkincounty.com/333/Tax-Lien-Sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Pitkin County row already present")
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
    print("Added Colorado Pitkin County tax-lien market")


if __name__ == "__main__":
    main()
