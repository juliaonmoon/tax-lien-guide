#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Navajo County"

ROW = r'''{state:'Arizona — Navajo County',product:'Tax lien / Certificate of Purchase',schedule:'Annual electronic tax-lien sale. Navajo County held the 2026 sale on February 11, 2026 through RealAuction; bidding opened February 3, 2026.',availability:'2026 annual auction passed — monitor county Treasurer for the next sale and any lien-purchase inventory',maxReturn:'16%/yr statutory max',interest:'Arizona tax liens are awarded to the bidder accepting the lowest interest rate, subject to the state statutory ceiling. The lien earns the bid rate rather than an automatically guaranteed 16%.',bid:'https://www.navajocountyaz.gov/459/February-Lien-Sale-Instructions',canadian:'Navajo County uses online bidder registration through RealAuction. Foreign bidders should confirm current taxpayer-identification and payment requirements with the Treasurer/auction provider before registering.',itin:'County/auction registration requirements should be verified directly before bidding; do not assume a foreign bidder can substitute documents without county confirmation.',online:'YES — Navajo County states its tax-lien sale is electronic through RealAuction.',otc:'County lien-purchase inquiries may identify certificates available outside the annual auction; availability is parcel-specific and should be confirmed with the Treasurer.',deed:'A tax-lien purchase is a Certificate of Purchase, not immediate ownership. Navajo County states certificate holders seeking a judgment deed are responsible for the court process.',special:'The county warns that advertised parcels may be removed before sale because taxes are paid or because of bankruptcy and that advertised tax amounts may omit interest, penalties, fees, partial payments, or prior certificates that must be bought out. Keep this tax-lien market distinct from any tax-deed or other foreclosure sale.',source:'https://www.navajocountyaz.gov/459/February-Lien-Sale-Instructions'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Arizona Navajo County row already present")
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
    print("Added Arizona Navajo County tax-lien market")


if __name__ == "__main__":
    main()
