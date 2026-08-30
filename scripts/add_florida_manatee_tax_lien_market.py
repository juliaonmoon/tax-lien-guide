#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Manatee County"

ROW = r'''{state:'Florida — Manatee County',product:'Tax certificate / first-priority property-tax lien',schedule:'Annual tax-certificate sale is conducted on or before June 1. The official Tax Collector page publishes a 2026 Tax Sale Calendar of Events, bidder materials, a tax-data research file, and a county-held certificate list.',availability:'2026 annual sale passed — county-held certificates available subject to current official list',maxReturn:'18%/yr statutory max',interest:'Florida reverse-auction structure applies: certificates are awarded to the bidder accepting the lowest interest rate, subject to the 18% statutory maximum. Certificates not purchased at the annual sale default to the county.',bid:'https://www.taxcollector.com/services/property-tax/tax-certs.cfm',canadian:'County-held purchase instructions require IRS taxpayer documentation and ACH authorization. Non-U.S. bidders should confirm acceptable tax documentation and banking eligibility directly with the Tax Collector before attempting to purchase.',itin:'Official county-held instructions require a W-9. A foreign bidder should not assume a W-9 is appropriate; confirm the acceptable IRS form / taxpayer-identification documentation with the Tax Collector before participation.',online:'Sale documents and research files are published online; county-held purchases are initiated from the official list and completed with forms/payment instructions from the Tax Collector.',otc:'YES — certificates not purchased through the annual tax-certificate sale default to Manatee County and the Tax Collector states they can be purchased at any time, subject to the current county-held list and completion of required forms.',deed:'A tax certificate is a lien rather than title. A later tax-deed application and tax-deed sale are separate statutory processes.',special:'Use the official current county-held list and research file rather than assuming old inventory remains available. Do not treat a tax-certificate purchase as ownership of, or a right to enter, the underlying property. Do not substitute tax-deed inventory or deed-sale opening bids for tax-certificate data.',source:'https://www.taxcollector.com/services/property-tax/tax-certs.cfm'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Manatee County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Manatee County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Manatee County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Manatee County tax-lien market row")
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
    print("Added Florida Manatee County tax-lien market")


if __name__ == "__main__":
    main()
