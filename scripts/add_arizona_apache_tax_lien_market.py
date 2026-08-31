#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Apache County"

ROW = r'''{state:'Arizona — Apache County',product:'Tax lien / Certificate of Purchase',schedule:'Apache County holds its annual online tax-lien auction each February. The official 2026 notice scheduled the electronic sale for February 18, 2026. After the annual sale, investors should rely on the Treasurer for any currently available unsold-lien process rather than assuming inventory remains available.',availability:'2026 annual auction passed — check the Apache County Treasurer for current official availability',maxReturn:'16%/yr statutory max',interest:'Arizona tax liens may be bid down from the statutory 16% annual rate; Apache County states investors may bid down the interest rate or bid a premium. Actual certificate yield depends on the winning bid and redemption timing.',bid:'https://www.apachecountyaz.gov/treasurer',canadian:'Apache County publishes purchaser/registration instructions for its tax-lien sale. A non-U.S. bidder should confirm directly with the Treasurer whether foreign registration and the appropriate IRS taxpayer documentation are accepted before funding or bidding.',itin:'Do not assume a U.S.-person tax form applies to a foreign bidder. Confirm the current taxpayer-identification and withholding documentation accepted by Apache County/its official auction provider.',online:'YES — the official 2026 public notice states the annual tax-lien auction was electronic through the county-linked RealAuction site.',otc:'CHECK OFFICIAL SOURCE — do not fabricate or infer current unsold-lien inventory; contact the Treasurer for any post-auction availability and exact amount/fees.',deed:'The purchase is a tax lien / Certificate of Purchase, not an immediate deed or ownership interest. Any later foreclosure/deed process is legally distinct and must follow Arizona law.',special:'Market-level only. Do not bulk republish owner/taxpayer names from county records. Do not fabricate parcel inventory, opening/minimum bids, or current OTC availability. Certificate purchasers do not obtain immediate ownership or possession rights. Preserve the distinction between the tax-lien certificate sale and any later foreclosure/deed process.',source:'https://www.apachecountyaz.gov/treasurer'}'''


def find_row_bounds(text: str, start: int, end: int):
    marker_pos = text.find(MARKER, start, end)
    if marker_pos < 0:
        return None

    row_start = text.rfind("{state:", start, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Apache County marker but could not locate row start")

    # index.html contains multiple valid row-separator styles. Choose the
    # nearest valid terminator instead of testing one style first; otherwise a
    # later `}\n` can be selected ahead of a nearer `},\n`, deleting rows in
    # between when this publisher repairs a stale Apache row.
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Apache County marker but could not locate row end")

    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    bounds = find_row_bounds(text, start, end)
    if bounds:
        row_start, row_end = bounds
        existing = text[row_start:row_end]
        if existing == ROW:
            print("Arizona Apache County canonical row already present")
            return
        INDEX.write_text(text[:row_start] + ROW + text[row_end:], encoding="utf-8")
        print("Restored canonical Arizona Apache County tax-lien market row")
        return

    before = text[:end]
    after = text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Arizona Apache County tax-lien market")


if __name__ == "__main__":
    main()
