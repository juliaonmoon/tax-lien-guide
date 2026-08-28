#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Graham County"

ROW = r'''{state:'Arizona — Graham County',product:'Tax lien / Certificate of Purchase',schedule:'Annual in-person tax-lien sale is held each February; the official 2026 sale was February 25, 2026. State-owned liens not sold at auction may be purchased later by assignment when the Treasurer\'s current Active Certificate Report shows Investor ID 1.',availability:'2026 annual auction passed — check the current official Active Certificate Report for state-owned assignment liens',maxReturn:'16%/yr statutory max',interest:'Graham County states competitive bidding is based on the least interest rate accepted by the bidder, with 16% as the maximum; state-owned liens available by assignment carry 16% interest. Actual yield depends on the certificate rate and redemption timing.',bid:'https://www.graham.az.gov/360/Tax-Lien-Information',canadian:'County registration requires bidder and taxpayer-identification information. A non-U.S. bidder should confirm directly with the Treasurer which foreign taxpayer documentation is accepted before participating.',itin:'Do not assume a U.S.-person tax form applies to a foreign bidder. Confirm the current taxpayer-identification and withholding documentation accepted by Graham County before funding or bidding.',online:'NO — Graham County states the annual sale is held in person; telephone and mail bids are not accepted.',otc:'YES, BY ASSIGNMENT WHEN OFFICIALLY LISTED — parcels not sold at the annual sale are assigned to the state. Only certificates shown with Investor ID 1 on the county\'s current Active Certificate Report should be treated as available for assignment; obtain the current total due from the Treasurer.',deed:'A tax-lien purchase is a Certificate of Purchase, not an immediate deed or ownership interest. Any later foreclosure/Treasurer\'s-deed process is legally distinct and must follow Arizona law.',special:'Market-level summary only. Do not bulk republish owner/taxpayer names from county records. Do not fabricate parcel inventory, opening/minimum bids, current assignment availability, or amounts due. Graham County separately operates tax-deed processes; keep those distinct from this tax-lien Certificate of Purchase market.',source:'https://www.graham.az.gov/362/Tax-Sale-Lien-Guidelines'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    marker_pos = text.find(MARKER, start, end)
    if marker_pos >= 0:
        row_start = text.rfind("{state:", start, marker_pos + 1)
        if row_start < 0:
            raise SystemExit("Could not find Graham row start")
        row_end = text.find("}\n", marker_pos, end)
        if row_end < 0:
            row_end = text.find("},\n", marker_pos, end)
            if row_end < 0:
                raise SystemExit("Could not find Graham row end")
        row_end += 1
        existing = text[row_start:row_end]
        if existing == ROW:
            print("Arizona Graham County canonical row already present")
            return
        INDEX.write_text(text[:row_start] + ROW + text[row_end:], encoding="utf-8")
        print("Restored canonical Arizona Graham County tax-lien market row")
        return

    before = text[:end]
    after = text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Arizona Graham County tax-lien market")


if __name__ == "__main__":
    main()
