#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Marion County"

ROW = r'''{state:'Florida — Marion County',product:'Tax certificate / enforceable first lien',schedule:'Marion County conducts its annual tax-certificate sale on or before June 1. The Tax Collector publishes official bidder materials, sale-calendar information, delinquent-property notices, and online tax-certificate services.',availability:'2026 annual sale passed — official county-held certificate purchase tools remain available subject to current inventory',maxReturn:'18%/yr statutory max',interest:'Reverse auction: Marion County states bids begin at 18% and progress downward, with the certificate issued to the lowest interest-rate bidder. Actual return depends on the winning rate and redemption timing.',bid:'https://www.mariontax.com/tax-certificate-deed-sales',canadian:'Marion County describes the tax-certificate sale as open to participants, but foreign-bidder registration, banking and U.S. tax-document requirements should be confirmed directly with the Tax Collector before funding.',itin:'Verify current taxpayer-identification requirements with the Marion County Tax Collector / official sale system; do not assume an ITIN alone guarantees eligibility.',online:'Official Marion County online services include the tax-certificate sale, held-certificate management, tax-deed application, and purchase of county-held certificates.',otc:'YES — Marion County provides an official online Purchase County Held Certificates service. Inventory is dynamic; use only the current official system/data.',deed:'A tax certificate is an enforceable first lien, not ownership. If statutory conditions are later met, a tax-deed application and tax-deed sale are separate processes handled through the Clerk.',special:'Preserve tax-certificate terminology and use only current official certificate-sale or county-held-certificate information. Do not treat certificate records as property ownership, and do not substitute tax-deed inventory or deed-sale opening/minimum bids for tax-certificate data.',source:'https://www.mariontax.com/tax-certificate-deed-sales'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Marion County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Marion County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Marion County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Marion County tax-lien market row")
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
    print("Added Florida Marion County tax-lien market")


if __name__ == "__main__":
    main()
