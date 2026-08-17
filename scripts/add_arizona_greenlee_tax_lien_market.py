#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Greenlee County"

ROW = r'''{state:'Arizona — Greenlee County',product:'Tax lien / Certificate of Purchase',schedule:'Greenlee County holds its tax-lien sale each February. The County published a 2026 tax-lien sale notice on February 4, 2026; the 2026 annual sale has passed. The Treasurer also publishes an official over-the-counter tax-lien listing page. Verify current inventory and the next sale date directly with the Treasurer.',availability:'2026 annual sale passed — official OTC lien listings available',maxReturn:'16%/yr max',interest:'Arizona tax-lien certificates are awarded through interest-rate bidding subject to the state statutory ceiling of 16% simple interest per year; the actual winning certificate rate may be lower.',bid:'https://greenlee.az.gov/team/treasurer/',canadian:'Greenlee requires bidder registration and a Social Security Number or Tax ID number on its bidder form. Foreign-bidder eligibility is not stated as a simple rule; confirm acceptable taxpayer-identification documentation and payment requirements with the Treasurer before participating.',itin:'Bidder registration requires an SSN or Tax ID number. Confirm whether an ITIN or other foreign taxpayer ID is accepted before registering.',online:'NO for the annual sale — Greenlee states the February tax-lien sale is held at the Treasurer’s Office in Clifton.',otc:'YES — the Treasurer publishes an official Over The Counter tax-lien listing page. Inventory changes, so verify the current official list before purchase.',deed:'A Certificate of Purchase is a tax lien, not immediate ownership or possession. Foreclosure of the right to redeem is a later court process under Arizona law.',special:'Greenlee County explicitly states that it also holds a separate property tax-deed sale. This row covers only the Treasurer tax-lien sale and OTC lien certificates; tax-deeded property sales are a different product.',source:'https://greenlee.az.gov/tax-lien-sale-faq/'}'''


def add_greenlee():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Arizona Greenlee County row already present")
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
    print("Added Arizona Greenlee County tax-lien market")


def main():
    add_greenlee()
    # Keep the newly verified Colorado market in the recurring refresh without
    # creating a second data-writing workflow. This script is already an
    # explicit recurring market-publisher step in refresh-properties.yml.
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "add_colorado_arapahoe_tax_lien_market.py")],
        check=True,
    )


if __name__ == "__main__":
    main()
