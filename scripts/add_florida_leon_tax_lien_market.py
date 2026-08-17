#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Leon County"

ROW = r'''{state:'Florida — Leon County',product:'Tax lien certificate',schedule:'Annual online tax-certificate sale. Leon County held the 2026 sale on June 1, 2026; bidding opened May 1, 2026. The Tax Collector also publishes current certificate lists, including county-held certificates.',availability:'2026 annual sale passed — county-held certificates may be available from the official Tax Collector list',maxReturn:'18%/yr statutory max',interest:'Reverse auction: bids start at 18% and move downward in 0.25% increments. The lowest accepted rate wins. Leon County notes that a zero-percent bid earns no interest and that Florida redemption rules can produce a statutory minimum-interest result in some nonzero-bid redemptions.',bid:'https://www.leontaxcollector.net/Services/Property-Taxes/Annual-Tax-Sale',canadian:'Foreign bidders are permitted if they satisfy Leon County registration and tax-document requirements. The county specifically publishes W-8/ITIN guidance for foreign bidders.',itin:'Leon County states that foreign bidders must have an ITIN, complete online registration, and submit an original W-8 with supporting documentation. Verify current requirements before funding.',online:'YES — Leon County conducts the annual tax-certificate sale online.',otc:'YES — Leon County publishes county-held certificates available for purchase through its official Tax Collector certificate-list/purchase pages. Inventory changes over time.',deed:'A certificate is a first-priority lien and conveys no property rights. After the statutory waiting period, an eligible certificate holder may apply for a tax deed; any later deed auction is conducted separately by the Clerk.',special:'Leon County explicitly warns that the certificate sale is NOT a sale of land. For homestead property reaching a later tax-deed sale, Florida law can add one-half of assessed value to the opening bid. Keep the tax-lien certificate market separate from the later tax-deed auction.',source:'https://www.leontaxcollector.net/Services/Property-Taxes/Annual-Tax-Sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Leon County row already present")
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
    # Keep Monroe County on the same serialized recurring Florida publication path.
    # The Monroe appender is idempotent and uses only official county-published rules.
    runpy.run_path(str(ROOT / "scripts" / "add_florida_monroe_tax_lien_market.py"), run_name="__main__")
