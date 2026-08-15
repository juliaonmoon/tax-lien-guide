#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Pinal County"

ROW = r'''{state:'Arizona — Pinal County',product:'Tax lien / Certificate of Purchase',schedule:'Pinal County holds its online tax-lien sale each February for prior-year delinquent real-property taxes. The 2026 annual sale has passed; verify the Treasurer tax-lien site for the next published sale date and current parcel list.',availability:'2026 annual sale passed — monitor next February sale',maxReturn:'16%/yr max',interest:'Arizona tax-lien certificates are awarded through interest-rate bidding subject to the state statutory ceiling of 16% simple interest per year; the actual winning certificate rate may be lower.',bid:'https://treasurer.pinal.gov/',canadian:'Foreign-bidder eligibility is not stated as a simple rule on the public Treasurer pages. Confirm current registration, federal-tax-ID and U.S.-funds requirements with the Pinal County Treasurer before participating.',itin:'Pinal County bidder tools require federal identification information. Confirm which taxpayer-identification documents are accepted for a foreign individual or entity before registering.',online:'YES — Pinal County states that its February Tax Lien Sale is conducted online.',otc:'Do not assume unsold certificates are currently available over the counter; verify any assignment or subsequent-tax options directly with the Treasurer.',deed:'The purchaser receives a tax-lien Certificate of Purchase, not possession or immediate title. Arizona law allows a later judicial foreclosure action only after the statutory waiting period and required notice.',special:'Pinal County also handles state-deeded and proprietary-property sales through separate processes. This row covers the Treasurer tax-lien certificate auction only.',source:'https://treasurer.pinal.gov/faq.aspx'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Arizona Pinal County row already present")
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
    print("Added Arizona Pinal County tax-lien market")


if __name__ == "__main__":
    main()
