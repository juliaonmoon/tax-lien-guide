#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Fremont County"

ROW = r'''{state:'Colorado — Fremont County',product:'Tax lien certificate',schedule:'Fremont County publishes official Property Tax Lien Sale information and annual Tax Lien Sale Lists. The latest sale list currently posted on the official county page is for 2025; a 2026 sale date/list was not yet published on the source reviewed, so verify the current Treasurer notice before bidding.',availability:'2026 annual-sale date/list not yet published on the official county tax-lien page reviewed; monitor Fremont County Treasurer for the current notice',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Colorado tax-lien certificate interest is set under state law for the applicable sale year. Fremont County has not yet published a 2026 certificate rate on the official tax-lien page reviewed, so no current-year rate is inferred.',bid:'https://fremontcountyco.gov/treasurer/tax-lien-sale-information',canadian:'The public tax-lien page does not clearly state foreign-bidder eligibility. Confirm identity, payment, W-9/tax-document, and registration requirements directly with the Fremont County Treasurer before funding.',itin:'Not clearly published for foreign bidders on the current tax-lien page; verify taxpayer-identification requirements directly with the Treasurer.',online:'The official page publishes tax-lien sale information and lists; current 2026 auction format/registration should be verified from the Treasurer rather than inferred from older sale materials.',otc:'County-held or assignment availability is not clearly stated on the current official tax-lien page reviewed; verify directly with the Treasurer rather than assuming inventory.',deed:'A tax-lien certificate is not property ownership. Fremont County separately publishes Treasurer’s Deed information: after the statutory holding period, a later public auction for the option for Treasurer’s Deed is a distinct process. Public Trustee mortgage-foreclosure listings are also separate and must not be treated as tax-lien inventory.',special:'MARKET-LEVEL ONLY until Fremont County publishes a current 2026 sale/list source that can be safely and unambiguously ingested. Do not substitute Public Trustee foreclosure rows, Treasurer’s Deed auction rows, owner-name data, an older 2025 lien list, or fabricated parcel/opening-bid data.',source:'https://fremontcountyco.gov/treasurer/tax-lien-sale-information'}'''


def rows_bounds(text: str):
    rows_start = text.find("const rows=[")
    if rows_start < 0:
        raise SystemExit("Could not find rows array")
    rows_end = text.find("\n];", rows_start)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")
    return rows_start, rows_end


def find_row_bounds(text: str, rows_start: int, rows_end: int):
    marker_pos = text.find(MARKER, rows_start, rows_end)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", rows_start, marker_pos + 1)
    if row_start < rows_start:
        raise SystemExit("Found Fremont County marker but could not locate row start inside rows array")
    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + 3)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Fremont County marker but could not locate row end inside rows array")
    return row_start, min(endings) + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    rows_start, rows_end = rows_bounds(text)
    bounds = find_row_bounds(text, rows_start, rows_end)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Fremont County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Fremont County tax-lien market row")
        return

    before, after = text[:rows_end], text[rows_end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Colorado Fremont County tax-lien market")


if __name__ == "__main__":
    main()
