#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Grand County"

ROW = r'''{state:'Colorado — Grand County',product:'Tax lien / Certificate of Purchase',schedule:'MARKET-LEVEL ONLY — Grand County confirms its tax-lien sale is held online, typically in November. The county page updated Mar 16, 2026 still shows the prior Nov 6, 2025 sale details and does not yet publish a current 2026 sale date/list, so no 2026 parcel rows or sale date are inferred.',availability:'2026 details pending official publication',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Colorado certificate interest is set under state law. Grand County states subsequent taxes earn the same rate as the certificate amount, but the county has not yet published a current 2026 certificate rate, so no prior-year rate is carried forward.',bid:'https://www.co.grand.co.us/129/Tax-Liens',canadian:'Foreign-bidder eligibility is not clearly published on the current county page; verify registration and taxpayer-ID requirements directly with the Grand County Treasurer before funding.',itin:'Current public materials do not clearly state foreign taxpayer-ID eligibility; verify directly with the Treasurer/auction platform.',online:'Yes — Grand County says its tax-lien sale is held online at the county’s official tax-certificate auction site.',otc:'Grand County publishes Tax Lien Assignment information; current assignable inventory must be verified from the Treasurer’s current official materials.',deed:'A tax-lien Certificate of Purchase is not immediate property ownership. Grand County separately administers a later Treasurer’s Deed public-auction process under the post-HB24-1056 rules.',special:'MARKET-LEVEL ONLY until Grand County publishes a current 2026 delinquent tax-lien list in a form that can be safely ingested. Do not substitute Public Trustee foreclosures, Treasurer’s Deed auction rows, owner-name data, prior-year parcel lists, deed-auction opening bids, or fabricated parcel/opening-bid/property data for tax-lien listings.',source:'https://www.co.grand.co.us/129/Tax-Liens'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Grand County marker but could not locate row start")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Grand County marker but could not locate row end")
    return row_start, min(endings) + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Grand County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Grand County tax-lien market row")
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
    print("Added Colorado Grand County tax-lien market")


if __name__ == "__main__":
    main()
