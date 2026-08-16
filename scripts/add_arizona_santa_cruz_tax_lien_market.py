#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Santa Cruz County"

ROW = r'''{state:'Arizona — Santa Cruz County',product:'Tax lien / Certificate of Purchase',schedule:'Annual tax-lien sale. Santa Cruz County held the 2026 online sale on February 10, 2026 through RealAuction.',availability:'OTC certificates available April 1–December 31 for registered Certificate of Purchase buyers; annual 2026 auction passed',maxReturn:'16%/yr statutory max',interest:'Competitive lowest-rate bidding. Santa Cruz County states bidding starts at 16% and is bid down in 1% increments; 0% bids are allowed. The purchased lien earns the accepted bid rate, not an automatically guaranteed 16%.',bid:'https://www.santacruzcountyaz.gov/317/Treasurer',canadian:'County registration and tax-document requirements must be confirmed before funding. Do not assume foreign-bidder eligibility from another Arizona county.',itin:'Santa Cruz County states registered Certificate of Purchase buyers submit investor information and IRS tax documentation. Foreign bidders should confirm acceptable taxpayer-identification documents directly with the Treasurer.',online:'YES — Santa Cruz County states the annual tax-lien auction is online through RealAuction.',otc:'YES — registered Certificate of Purchase buyers may purchase over-the-counter delinquent taxes April 1–December 31; the county says its delinquent-tax list is updated monthly during that period.',deed:'A tax-lien purchase is a Certificate of Purchase, not property ownership. The county states investors may initiate foreclosure proceedings after the statutory waiting period and recommends using an attorney for that process.',special:'The county explicitly warns that advertised parcels may be removed before auction after payment and that published amounts can change due to interest, penalties, fees, partial payments, or prior certificates. Keep these tax liens distinct from any separate tax-deed or foreclosure property sale.',source:'https://www.santacruzcountyaz.gov/317/Treasurer'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Arizona Santa Cruz County row already present")
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
    print("Added Arizona Santa Cruz County tax-lien market")


if __name__ == "__main__":
    main()
