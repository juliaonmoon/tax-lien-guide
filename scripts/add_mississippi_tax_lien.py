#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
LABEL = "Mississippi — DeSoto County"
ROW = r"""{state:'Mississippi — DeSoto County',product:'Redeemable county tax sale interest',schedule:'DeSoto County holds its annual tax sale on the last Monday in August; in 2026 that is Aug 31',availability:'Upcoming — Aug 31, 2026',interest:'Winning bidder purchases the delinquent-tax interest; redemption amounts and statutory charges are administered through the Chancery Clerk. Verify current sale terms before bidding.',bid:'https://www.desotocountyms.gov/690/Tax-Sale-Information',canadian:'County/platform-specific; verify GovEase registration, payment and tax-document requirements before registering',itin:'Verify current bidder tax-ID requirements with DeSoto County / GovEase',online:'YES — DeSoto County states the annual tax sale uses GovEase for online bidding',otc:'No standing OTC certificate list identified; Mississippi tax-forfeited land is a separate Secretary of State process',deed:'The tax-sale purchaser does not receive immediate title. DeSoto County states unredeemed tax-sale property can mature so the purchaser may obtain a tax deed after the redemption process.',special:'Mississippi DOR states counties hold annual tax sales for delinquent property, generally on the first Monday in April or last Monday in August. Treat this as a redeemable tax-sale interest, not an immediate deed purchase.',source:'https://www.desotocountyms.gov/690/Tax-Sale-Information'}"""


def main():
    html = INDEX.read_text(encoding="utf-8")
    if LABEL in html:
        print("Mississippi DeSoto tax-lien market already present")
        return
    anchor = "const visible=Object.fromEntries"
    anchor_pos = html.find(anchor)
    if anchor_pos < 0:
        raise SystemExit("Could not find rows-array anchor")
    rows_end = html.rfind("];", 0, anchor_pos)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")
    insertion = (",\n" if not html[:rows_end].rstrip().endswith(",") else "\n") + ROW + "\n"
    html = html[:rows_end] + insertion + html[rows_end:]
    html = html.replace("Updated August 13, 2026", "Updated August 14, 2026")
    INDEX.write_text(html, encoding="utf-8")
    print("Added Mississippi DeSoto County tax-lien market")


if __name__ == "__main__":
    main()
