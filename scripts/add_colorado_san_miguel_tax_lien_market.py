#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — San Miguel County"

ROW = r'''{state:'Colorado — San Miguel County',product:'Tax lien certificate / Certificate of Purchase',schedule:'San Miguel County’s current Treasurer page announces its annual online tax-lien sale for October 27 at 10:00 a.m. MDT through GovEase. The extracted official page does not print a year beside that date, so verify the current-year sale notice and parcel list before bidding.',availability:'Annual online sale announced for October 27; current-year parcel list/rules should be verified on the official Treasurer/GovEase notice',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Colorado tax-lien certificate interest is set annually under state law. San Miguel County’s page confirms investors earn interest on purchased tax liens; do not carry a prior-year percentage into 2026 before the current rate is officially set/published.',bid:'https://sanmiguelcountyco.gov/261/Tax-Lien-Sale',canadian:'The current county page does not clearly publish foreign-bidder eligibility. Confirm GovEase registration, identity, payment and U.S. tax-document requirements before funding.',itin:'Not clearly published for foreign bidders on the current county page; verify taxpayer-identification requirements with San Miguel County/GovEase.',online:'Yes — San Miguel County says the annual tax-lien sale is online through GovEase.',otc:'County-held tax liens that are not purchased at the annual sale may be available to the public. The county page currently states there are no county-held tax liens available.',deed:'Buying a tax lien does not transfer ownership or possession. San Miguel County separately maintains Treasurer Deed procedures, which are a later stage distinct from the original tax-lien purchase.',special:'MARKET-LEVEL ONLY until San Miguel County publishes a current-year parcel list in a form that can be safely and unambiguously ingested. Do not substitute Public Trustee mortgage foreclosures, Treasurer Deed records, owner-name data, prior-year parcel lists, or fabricated opening-bid amounts.',source:'https://sanmiguelcountyco.gov/261/Tax-Lien-Sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado San Miguel County row already present")
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
    print("Added Colorado San Miguel County tax-lien market")


if __name__ == "__main__":
    main()
