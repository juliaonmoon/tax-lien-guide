#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Indiana — Hancock County 2026"

ROW = r'''{state:'Indiana — Hancock County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Hancock County’s 2026 online Tax Sale is Friday, <span class="schedule-date">September 18, 2026</span>, beginning at 10:00 AM Eastern through SRI / ZeusAuction. The county also separately references Tax Certificate Sales for delinquent-property liens.',availability:'Upcoming — September 18, 2026',interest:'Indiana tax-sale purchaser returns are governed by statutory redemption rather than a simple APR. Hancock County directs bidders to Indiana Code 6-1.1-24 and 6-1.1-25; verify the current redemption calculation and parcel-specific amounts before bidding.',bid:'https://www.hancockin.gov/606/Tax-Sale',canadian:'Not confirmed — verify current Hancock County/SRI bidder-registration and U.S. taxpayer-document requirements before participating.',itin:'Do not assume an ITIN or W-8 alone is accepted; verify current SRI/Hancock County registration requirements.',online:'YES — Hancock County says the September 18, 2026 sale is online through SRI / ZeusAuction.',otc:'Not established by the current county page. Any later Tax Certificate Sale or county disposition must be treated as a separate county process and verified independently.',deed:'The county sells liens through the tax-sale/certificate process. A tax deed is not immediate; purchasers must satisfy Indiana redemption, notice, and deed procedures after the statutory redemption period.',special:'MARKET-LEVEL SUMMARY ONLY. Hancock County says the current sale is online and directs bidders to SRI. Do not bulk republish owner/taxpayer names, freeze a changing auction list as guaranteed inventory, infer parcel-level opening/minimum bids, bypass registration controls, or substitute Hancock County Sheriff foreclosure properties for Treasurer tax-sale certificates.',source:'https://www.hancockin.gov/606/Tax-Sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        row_re = re.compile(
            rf"\{{state:'{re.escape(MARKER)}'.*?\}}(?=\s*,|\s*\n\];)",
            re.S,
        )
        updated, count = row_re.subn(ROW, text, count=1)
        if count != 1:
            raise SystemExit(f"Could not uniquely refresh {MARKER}")
        INDEX.write_text(updated, encoding="utf-8")
        print("Refreshed Hancock County Indiana tax-lien market")
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
    print("Added Hancock County Indiana tax-lien market")


if __name__ == "__main__":
    main()
