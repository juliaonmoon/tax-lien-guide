#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Pinal County"

ROW = r'''{state:'Arizona — Pinal County',product:'Tax lien / Certificate of Purchase',schedule:'Pinal County holds an online tax-lien sale each February for prior-year delinquent real-property taxes. The Treasurer states that delinquent taxes are offered for purchase at the February Tax Lien Sale; use the current Treasurer/auction publication for the exact next sale date and parcel list.',availability:'Annual February auction; county-held certificates not sold at auction are described in the Treasurer tax-sale booklet as generally available online approximately the first week of March through the end of December, subject to current parcel-specific availability.',maxReturn:'16%/yr statutory max',interest:'Pinal County describes tax-lien certificates as interest-rate bids subject to Arizona\'s 16% simple annual ceiling; the actual winning certificate rate may be lower. Verify the certificate-specific rate before relying on a return figure.',bid:'https://treasurer.pinal.gov/',canadian:'Pinal County uses online bidder registration and federal identification information. Foreign bidders should confirm current taxpayer-identification, tax-form and U.S.-funds requirements with the Treasurer/auction provider before participating.',itin:'The bidder application references SSN/EIN-linked federal identification. Do not assume an alternative foreign-bidder document is accepted without direct confirmation from Pinal County/its auction provider.',online:'YES — Pinal County states its February tax-lien sale is conducted online.',otc:'County guidance says county-held certificates not sold at auction are generally offered online approximately the first week of March through the end of December, but availability is parcel-specific and can change. Do not infer that any particular certificate is currently available.',deed:'The purchaser receives a tax-lien Certificate of Purchase, not possession or immediate title. Pinal County states that the certificate does not permit entry or possession; foreclosure rights arise only after the statutory waiting period and required legal process.',special:'Keep the Treasurer tax-lien certificate process separate from Pinal County\'s distinct state-deeded/proprietary-property and personal-property sale processes. Market-level only: do not bulk republish owner/taxpayer names or fabricate parcel inventory, opening/minimum bids, amounts due, current availability, property characteristics, or legal outcomes. Use only current official Treasurer/auction publication for parcel-specific sale data.',source:'https://treasurer.pinal.gov/faq.aspx'}'''


def find_row_bounds(text: str):
    rows_start = text.find("const rows=[")
    if rows_start < 0:
        raise SystemExit("Could not find rows array")
    rows_end = text.find("\n];", rows_start)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")

    marker_pos = text.find(MARKER, rows_start, rows_end)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", rows_start, marker_pos + 1)
    if row_start < rows_start:
        raise SystemExit("Found Pinal marker but could not locate row start")

    # Include the array-closing sequence in the bounded search so Pinal can be
    # repaired safely even when it is the final row. Choose the nearest valid
    # separator style rather than allowing a farther terminator to consume
    # following rows.
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Pinal marker but could not locate row end")

    row_end = min(endings) + 1
    if row_start < rows_start or row_end > rows_end + 1:
        raise SystemExit("Refusing to repair Pinal row outside rows array")
    return row_start, row_end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Arizona Pinal County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Arizona Pinal County tax-lien market row")
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
