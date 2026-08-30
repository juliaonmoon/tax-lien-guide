#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Leon County"

ROW = r'''{state:'Florida — Leon County',product:'Tax lien certificate',schedule:'Annual online tax-certificate sale held June 1 each year. Leon County publishes the advertised items in early to mid-May and also publishes current certificate lists, including county-held certificates.',availability:'2026 annual sale passed — current county-held certificates are available only from the official Leon County Tax Collector certificate list/purchase pages and inventory changes over time',maxReturn:'18%/yr statutory max',interest:'Reverse auction: valid bids range from 0% to 18% in 0.25% increments, and the certificate is awarded to the bidder accepting the lowest interest rate. Leon County states that a redeemed certificate generally receives a statutory 5% minimum-interest result except a 0% bid, which earns no interest.',bid:'https://www.leontaxcollector.net/Services/property-taxes/Tax-Sale-Information',canadian:'Leon County states that any person may register to bid. Foreign bidders must satisfy the Tax Collector’s current registration and U.S. tax-document requirements before participating.',itin:'Leon County requires certificate issuance under the taxpayer information supplied on IRS Form W-9 or W-8 for foreign bidders. Verify the current identification/withholding documentation directly with the Tax Collector before funding; do not assume an ITIN alone guarantees eligibility.',online:'YES — Leon County conducts the annual tax-certificate sale online.',otc:'YES — certificates not sold at the annual sale are issued to the county and Leon County publishes current county-held certificate lists and a purchase process. Use only the current official list; do not infer inventory.',deed:'A tax certificate is a first-priority lien and conveys no property rights. After the statutory waiting period an eligible certificate holder may apply for a tax deed; any later tax-deed sale is a separate property process.',special:'Leon County explicitly states that tax certificates convey no property rights. Preserve tax-certificate-vs-tax-deed terminology, do not treat a certificate as ownership, and do not substitute later tax-deed inventory or deed-sale opening/minimum bids for tax-certificate data.',source:'https://www.leontaxcollector.net/Services/property-taxes/Tax-Sale-Information'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Leon County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Leon County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Leon County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Leon County tax-lien market row")
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
    print("Added Florida Leon County tax-lien market")


if __name__ == "__main__":
    main()
