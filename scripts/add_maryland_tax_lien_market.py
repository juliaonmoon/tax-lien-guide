#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Montgomery County"

ROW = r'''{state:'Maryland — Montgomery County',product:'Property tax lien / certificate of sale',schedule:'Montgomery County holds its public sealed-bid tax lien sale annually on the second Monday in June. The 2026 sale was June 8, 2026; the County states the next sale will be June 7, 2027.',availability:'2026 sale passed — next sale June 7, 2027',interest:'For the June 8, 2026 sale, Montgomery County states redemption interest was 6% annually for owner-occupied property and 20% annually for non-owner-occupied property, calculated daily. Verify the rate stated on each future certificate.',bid:'https://www.montgomerycountymd.gov/tax-sale-information-procedures',canadian:'The sale is open to the public, but foreign bidders should confirm current payment, certificate-name, tax-document and legal requirements directly with Montgomery County before participating',itin:'The published 2026 procedures require bidder identity/contact information but do not state a specific taxpayer-ID requirement; verify current requirements with the County for future sales',online:'Bids are sealed; Montgomery County accepts bids during the sale window by email, courier/mail, or in person. It is not a conventional live online auction.',otc:'NO — Montgomery County states it does not sell tax liens over the counter; unsold parcels return to the tax rolls',deed:'The purchaser receives a certificate of sale, not immediate ownership. The owner retains a right of redemption until finally foreclosed by Circuit Court order. A deed follows only after the statutory foreclosure-of-redemption process and court judgment.',special:'Montgomery County warns that tax sales are complex and that liens may later be invalid or void. The County sells the lien, not the property. The 2026 sale used bid factors tied to full cash value and could require a high-bid premium.',source:'https://www.montgomerycountymd.gov/tax-sale-information-procedures'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Maryland Montgomery County row already present")
        return

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before = text[:end]
    after = text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Maryland Montgomery County tax-lien market")


if __name__ == "__main__":
    main()
