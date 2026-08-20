#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Fremont County"

ROW = r'''{state:'Colorado — Fremont County',product:'Tax lien certificate',schedule:'Fremont County publishes official Property Tax Lien Sale information and annual Tax Lien Sale Lists. The latest sale list currently posted on the official county page is for 2025; a 2026 sale date/list was not yet published on the source reviewed, so verify the current Treasurer notice before bidding.',availability:'2026 annual-sale date/list not yet published on the official county tax-lien page reviewed; monitor Fremont County Treasurer for the current notice',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Colorado tax-lien certificate interest is set under state law for the applicable sale year. Fremont County has not yet published a 2026 certificate rate on the official tax-lien page reviewed, so no current-year rate is inferred.',bid:'https://fremontcountyco.gov/treasurer/tax-lien-sale-information',canadian:'The public tax-lien page does not clearly state foreign-bidder eligibility. Confirm identity, payment, W-9/tax-document, and registration requirements directly with the Fremont County Treasurer before funding.',itin:'Not clearly published for foreign bidders on the current tax-lien page; verify taxpayer-identification requirements directly with the Treasurer.',online:'The official page publishes tax-lien sale information and lists; current 2026 auction format/registration should be verified from the Treasurer rather than inferred from older sale materials.',otc:'County-held or assignment availability is not clearly stated on the current official tax-lien page reviewed; verify directly with the Treasurer rather than assuming inventory.',deed:'A tax-lien certificate is not property ownership. Fremont County separately publishes Treasurer’s Deed information: after the statutory holding period, a later public auction for the option for Treasurer’s Deed is a distinct process. Public Trustee mortgage-foreclosure listings are also separate and must not be treated as tax-lien inventory.',special:'MARKET-LEVEL ONLY until Fremont County publishes a current 2026 sale/list source that can be safely and unambiguously ingested. Do not substitute Public Trustee foreclosure rows, Treasurer’s Deed auction rows, owner-name data, an older 2025 lien list, or fabricated parcel/opening-bid data.',source:'https://fremontcountyco.gov/treasurer/tax-lien-sale-information'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Fremont County row already present")
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
    print("Added Colorado Fremont County tax-lien market")


if __name__ == "__main__":
    main()
