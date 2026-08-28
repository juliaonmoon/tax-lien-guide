#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Santa Cruz County"

ROW = r'''{state:'Arizona — Santa Cruz County',product:'Tax lien / Certificate of Purchase',schedule:'Santa Cruz County held its 2026 online tax-lien sale on February 10, 2026 through RealAuction. The Treasurer states the tax-lien sale is held annually in February; use the current official Treasurer/auction publication for the exact next sale date and parcel list.',availability:'The 2026 annual auction has passed. Registered Certificate of Purchase buyers may purchase over-the-counter delinquent taxes from April 1 through December 31; the Treasurer says the delinquent-tax list is updated monthly during that period. Current parcel-specific availability must be verified from the official county list.',maxReturn:'16%/yr statutory max',interest:'Santa Cruz County states bidding starts at 16% and is bid down in 1% increments; 0% bids are allowed. The purchased lien earns the accepted bid rate, not an automatically guaranteed 16%.',bid:'https://www.santacruzcountyaz.gov/317/Treasurer',canadian:'County registration and tax-document requirements must be confirmed before funding. Do not assume foreign-bidder eligibility from another Arizona county.',itin:'Santa Cruz County states registered Certificate of Purchase buyers submit investor information and IRS tax documentation. Foreign bidders should confirm acceptable taxpayer-identification documents directly with the Treasurer.',online:'YES — Santa Cruz County states the annual tax-lien auction is online through RealAuction.',otc:'YES — registered Certificate of Purchase buyers may purchase over-the-counter delinquent taxes April 1–December 31; the county says its delinquent-tax list is updated monthly during that period. Do not infer that any specific certificate is currently available.',deed:'A tax-lien purchase is a Certificate of Purchase, not property ownership, possession, or a right to enter/contact the property owner. The county states investors may initiate foreclosure proceedings only after the statutory waiting period and recommends using an attorney for that process.',special:'The county explicitly warns that advertised parcels may be removed before auction after payment and that published amounts can change due to interest, penalties, fees, partial payments, or prior certificates. Market-level only: do not bulk republish owner/taxpayer names or fabricate parcel inventory, opening/minimum bids, amounts due, current OTC availability, property characteristics, or legal outcomes. Keep tax-lien Certificates of Purchase distinct from any later foreclosure/deed process.',source:'https://www.santacruzcountyaz.gov/317/Treasurer'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Santa Cruz marker but could not locate row start")
    row_end = text.find("}\n", marker_pos)
    if row_end < 0:
        row_end = text.find("},\n", marker_pos)
        if row_end < 0:
            raise SystemExit("Found Santa Cruz marker but could not locate row end")
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Arizona Santa Cruz County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Arizona Santa Cruz County tax-lien market row")
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
    print("Added Arizona Santa Cruz County tax-lien market")


if __name__ == "__main__":
    main()
