#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Mohave County"

ROW = r'''{state:'Arizona — Mohave County',product:'Tax lien / Certificate of Purchase',schedule:'Mohave County operates an annual online tax-lien sale and also accepts over-the-counter assignment requests for county/state-held liens from <span class="schedule-date">April 15–November 30</span> each year. The current Treasurer page identifies the 2026 tax-lien sale but does not publish a reliable sale date in the page text; verify the official auction portal before relying on a date.',availability:'OTC assignments open Apr 15–Nov 30; annual auction date county-published',maxReturn:'16%/yr max',interest:'Arizona tax-lien certificates are subject to the statutory 16% simple annual ceiling. At the annual auction, the actual certificate rate may be bid down; assignment terms should be verified for the specific lien.',bid:'https://www.mohave.gov/departments/treasurer/tax-liens/tax-lien-sale/',canadian:'Mohave County explicitly provides W-8BEN instructions for people living outside the United States when requesting tax-lien assignments. Confirm current bidder-number, payment and tax-document requirements before participating.',itin:'Foreign assignment applicants are directed to complete W-8BEN rather than assuming a U.S. SSN. Confirm whether any additional taxpayer-identification documentation is required for the annual RealAuction sale.',online:'YES for the annual auction — Mohave County identifies RealAuction as the auction vendor. OTC assignments use the Treasurer assignment-request process.',otc:'YES — assignment requests for state/county-held tax liens are accepted April 15 through November 30, first come/first served, subject to current availability and county review.',deed:'A tax-lien certificate or assignment is a lien, not immediate ownership. Judicial foreclosure of the right to redeem is a later court process under Arizona law; county guidance also warns that liens expire after the statutory period if foreclosure is not commenced.',special:'Do not confuse Mohave tax liens with the separate Tax Deed Auction/OTC Tax Deed program. The Treasurer tax-lien program sells or assigns liens; the Clerk of the Board tax-deed program sells real property already deeded to the State.',source:'https://www.mohave.gov/departments/treasurer/tax-liens/assignment-requests-for-state-liens/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Arizona Mohave County row already present")
        return

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before = text[:end]
    after = text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Arizona Mohave County tax-lien market")


if __name__ == "__main__":
    main()
