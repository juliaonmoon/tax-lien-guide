#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Citrus County"

ROW = r'''{state:'Florida — Citrus County',product:'Tax certificate / first-priority property-tax lien',schedule:'2026 annual internet tax-certificate sale began June 1, 2026 at 8:30 a.m. ET. Verify current county-held inventory and future sale notices with the Citrus County Tax Collector.',availability:'2026 annual sale passed; county-held certificates may be available through the official LienHub process',maxReturn:'18%/yr statutory max',interest:'Florida reverse auction. Citrus County explains that bidding starts at 18% and the bidder willing to accept the lowest interest rate wins; interest on redeemed certificates is computed under Florida law and certificate terms.',bid:'https://www.citrustc.us/services/tax-certificate-information/',canadian:'No Citrus-specific foreign-bidder eligibility rule was found in the official county pages reviewed. Verify current registration, taxpayer-identification, withholding and payment requirements with the Tax Collector / LienHub before funding.',itin:'Verify current taxpayer-identification and withholding requirements with the Citrus County Tax Collector / official auction platform; do not assume an ITIN alone guarantees eligibility.',online:'Yes — Citrus County states its tax-certificate sale is conducted through LienHub.',otc:'YES — Citrus County states county-held certificates can be purchased through LienHub, subject to current inventory and Florida restrictions such as certain low-value homestead certificates.',deed:'A tax certificate is a first lien, not ownership. Citrus County states certificates are subject to tax-deed application only after the statutory waiting period; tax-deed auctions are conducted separately by the Clerk.',special:'Do not confuse Citrus County tax certificates with tax-deed property sales. The Tax Collector sells liens; the Clerk conducts tax-deed auctions. Keep county-held certificate inventory separate from deed/foreclosure listings.',source:'https://www.citrustc.us/services/tax-certificate-information/'}'''


def ensure_citrus():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Citrus County row already present")
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
    print("Added Florida Citrus County tax-lien market")


def main():
    ensure_citrus()
    # Keep Clay County in the recurring Florida publication path. This child
    # appender is idempotent and the downstream county-filter/recount steps
    # still run after this workflow stage.
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "add_florida_clay_tax_lien_market.py")],
        check=True,
        cwd=ROOT,
    )


if __name__ == "__main__":
    main()
