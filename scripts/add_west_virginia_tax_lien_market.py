#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "West Virginia — State Auditor sales"

ROW = r'''{state:'West Virginia — State Auditor sales',product:'Tax lien / delinquent land sale',schedule:'County sheriffs publish delinquent real estate by <span class="schedule-date">September 10</span>; unredeemed property is certified to the State Auditor on <span class="schedule-date">October 31</span>. The Auditor then certifies sale lists March 1–August 1 and holds the county courthouse auction within 90 days of certification.',availability:'Upcoming / Auditor schedule',interest:'Highest eligible bid; minimum is the taxes, interest and charges due. This is not a fixed-rate certificate market, so verify the current Auditor auction terms before bidding.',bid:'https://www.wvsao.gov/CountyCollections/DelinquentProperties',canadian:'Possible only if current registration rules are satisfied; business entities must be authorized to do business in West Virginia',itin:'Verify current State Auditor registration and taxpayer-ID requirements before bidding',online:'No — current statute describes public auction at the county courthouse',otc:'YES — property left unsold after auction may later be sold by the Auditor without another public auction or additional advertising',deed:'After an approved sale, purchaser must follow the statutory deed process; the tax-lien purchase is not immediate clear ownership',special:'CURRENT LAW WARNING: older West Virginia guides describing the sheriff selling tax liens in November are outdated. §11A-3-5 was repealed. Current law certifies delinquent property to the State Auditor, who conducts the annual auction. Entity bidders must also be properly registered with the WV Secretary of State.',source:'https://code.wvlegislature.gov/11A-3-45/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("West Virginia row already present")
        return

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before = text[:end]
    after = text[end:]
    if before.rstrip().endswith(','):
        insertion = "\n" + ROW
    else:
        insertion = ",\n" + ROW
    text = before + insertion + after
    INDEX.write_text(text, encoding="utf-8")
    print("Added West Virginia State Auditor tax-lien market")


if __name__ == "__main__":
    main()
