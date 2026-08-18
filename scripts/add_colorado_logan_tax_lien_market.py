#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Logan County"

ROW = r'''{state:'Colorado — Logan County',product:'Tax lien / Certificate of Purchase',schedule:'Annual tax-lien sale <span class="schedule-date">Nov 19, 2026</span>. Logan County states that parcels not sold during the auction remain open for purchase through the Treasurer from 3:00 p.m. Nov 19 through close of business Nov 24, 2026 before being struck off to the county.',availability:'Upcoming — Nov 19, 2026; limited post-sale Treasurer availability through Nov 24',maxReturn:'14% per year for the 2026 certificate',interest:'Logan County states that the 2026 tax-lien interest rate is 14% per annum and remains fixed for the life of the certificate. Premium bids are not refundable and do not earn interest.',bid:'https://www.logancountyco.gov/208/Tax-Liens-Sale',canadian:'The county requires IRS tax reporting information and a W-9 for standard registration. A non-U.S.-person pathway is not clearly published; verify eligibility directly with the Treasurer before funding.',itin:'A W-9 and U.S. tax ID / SSN are described in the published bidder rules. The reviewed page does not establish a W-8/ITIN pathway for foreign bidders.',online:'No — the published 2026 sale is held at the Logan County Courthouse in Sterling, Colorado.',otc:'Limited — unsold parcels remain open for purchase at the Treasurer from 3:00 p.m. Nov 19 through Nov 24, 2026, then are struck off to the county.',deed:'A successful bidder receives a tax-lien Certificate of Purchase, not ownership or possession. Any later Treasurer\'s Deed process is separate and subject to Colorado statutory procedures.',special:'Open bidding is by premium above taxes, penalty, interest and costs. The premium is not returned and earns no interest, so the certificate\'s 14% statutory rate is not the same as the investor\'s net return when a premium is paid.',source:'https://www.logancountyco.gov/208/Tax-Liens-Sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Logan County row already present")
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
    print("Added Colorado Logan County tax-lien market")


if __name__ == "__main__":
    main()
