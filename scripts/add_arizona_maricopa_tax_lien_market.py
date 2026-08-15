#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Maricopa County"

ROW = r'''{state:'Arizona — Maricopa County',product:'Tax lien / Certificate of Purchase',schedule:'Maricopa County conducts an annual tax-lien sale and also maintains a Treasurer Tax Assignment portal for eligible certificate assignments. Verify the current assignment inventory and annual-sale dates directly with the Treasurer before funding.',availability:'Tax Assignment portal available — inventory/eligibility changes over time',interest:'Arizona delinquent real-property tax accrues at a statutory 16% simple rate. Tax-lien auction bidding can reduce the investor rate below that ceiling; assignment terms should be verified for the specific certificate.',bid:'https://treasurer.maricopa.gov/TaxAssignment/instructions',canadian:'Registration and tax-document requirements are controlled by the Treasurer. Foreign bidders should confirm current eligibility and taxpayer-identification requirements before attempting to purchase or receive an assignment.',itin:'Confirm current taxpayer-ID requirements with the Maricopa County Treasurer Tax Lien Department before registration or assignment.',online:'YES — Maricopa County operates an online Treasurer Tax Assignment portal; annual-sale procedures should be verified separately.',otc:'Assignment-style availability exists through the Treasurer Tax Assignment system when eligible certificates are offered; do not assume every unsold lien is available.',deed:'A Certificate of Purchase is a lien, not immediate ownership. Arizona foreclosure rights arise only after statutory waiting, notice and court requirements are satisfied.',special:'Do not confuse tax-lien Certificates of Purchase with Maricopa County tax-deeded land sales. The county also sells separate state-held tax-deeded parcels; those are a different product and process.',source:'https://treasurer.maricopa.gov/TaxAssignment/instructions'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Arizona Maricopa County row already present")
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
    print("Added Arizona Maricopa County tax-lien market")


if __name__ == "__main__":
    main()
