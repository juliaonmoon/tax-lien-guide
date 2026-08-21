#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Archuleta County"

ROW = r'''{state:'Colorado — Archuleta County',product:'Tax lien / Certificate of Purchase',schedule:'MARKET-LEVEL ONLY — Archuleta County officially conducts Treasurer tax-lien sales and publishes delinquent-tax sale lists, but the currently indexed official publication is not a verified 2026 list. No 2026 parcel rows or sale date are inferred.',availability:'2026 details pending official publication',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Colorado tax-lien certificate interest is set under state law. Archuleta County administers tax liens and a later separate Treasurer’s Deed process; no prior-year certificate rate is carried forward as a 2026 return.',bid:'https://www.archuletacounty.org/301/Treasurer-Deeds',canadian:'Foreign-bidder eligibility is not clearly published in the current official county materials; verify registration and taxpayer-ID requirements directly with the Archuleta County Treasurer.',itin:'Current public materials do not clearly state foreign taxpayer-ID eligibility; verify directly with the Treasurer before funding.',online:'Archuleta County has used an internet tax-lien auction for its published sale lists; verify the current 2026 auction platform/rules when posted.',otc:'County-held or assignment availability is not clearly published for 2026; verify directly with the Treasurer.',deed:'A tax-lien Certificate of Purchase is not immediate ownership. Archuleta County separately administers Treasurer’s Deed applications after the statutory holding period.',special:'MARKET-LEVEL ONLY until Archuleta County publishes a current 2026 delinquent tax-lien list in a form that can be safely ingested. Do not substitute Public Trustee mortgage foreclosures, Treasurer’s Deed rows, owner-name data, prior-year parcel lists, or deed-auction amounts for tax-lien listings.',source:'https://www.archuletacounty.org/301/Treasurer-Deeds'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Archuleta County row already present")
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
    print("Added Colorado Archuleta County tax-lien market")


if __name__ == "__main__":
    main()
