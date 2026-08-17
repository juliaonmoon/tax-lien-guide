#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Brevard County"

ROW = r'''{state:'Florida — Brevard County',product:'Tax certificate / first lien',schedule:'Brevard County states that its annual tax-certificate sale for delinquent real-estate taxes begins on or before June 1 each year.',availability:'Annual sale cycle — monitor the official Brevard County Tax Collector / LienHub pages for current sale and certificate inventory',maxReturn:'18%/yr statutory max',interest:'Florida tax certificates use reverse bidding from the statutory maximum rate. The winning bidder accepts the lowest interest rate; verify the current Brevard sale rules and certificate-specific rate before bidding.',bid:'https://www.brevardtaxcollector.com/services/tax-certificate-information/',canadian:'The county does not publish a simple foreign-bidder eligibility rule on its general information page. Confirm current registration, identity, banking and tax-document requirements with the Tax Collector / official auction platform before funding.',itin:'Verify current taxpayer-identification requirements with the Tax Collector / official auction platform; do not assume an ITIN alone guarantees eligibility.',online:'Brevard County links taxpayers and investors to LienHub for tax-certificate services; verify the current auction registration page and deadlines through the official Tax Collector site.',otc:'County-held / post-sale certificate availability is inventory-dependent. Use only the current official Tax Collector or LienHub inventory; do not infer availability from old sale lists.',deed:'A tax certificate is a first lien, not ownership. Brevard County states that a certificate may become eligible for a separate tax-deed application after two years, subject to Florida law and current certificate status.',special:'Brevard County explicitly describes a tax certificate as a valid first lien on taxable property. Keep the tax-certificate purchase separate from any later tax-deed sale and verify redemption, bankruptcy, title and parcel status before bidding.',source:'https://www.brevardtaxcollector.com/services/tax-certificate-information/'}'''


def add_brevard():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Brevard County row already present")
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
    print("Added Florida Brevard County tax-lien market")


def main():
    add_brevard()
    # Keep St. Lucie in the same recurring Florida publication path. This runs
    # even when Brevard is already present, so a rebuilt index cannot silently
    # drop St. Lucie on a later refresh.
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "add_florida_st_lucie_tax_lien_market.py")],
        check=True,
    )


if __name__ == "__main__":
    main()
