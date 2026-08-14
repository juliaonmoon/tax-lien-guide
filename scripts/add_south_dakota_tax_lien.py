#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
LABEL = "South Dakota — Stanley County"
ROW = r"""{state:'South Dakota — Stanley County',product:'Tax certificate',schedule:'Annual county tax-certificate sale on the third Monday in December; in 2026 that is <span class="schedule-date">Dec 21, 2026</span>',availability:'Upcoming',interest:'Lowest annual interest-rate bid wins; South Dakota law caps a valid bid at 10% per year',bid:'https://www.stanleycountysd.gov/departments/treasurer/',canadian:'County-specific; confirm bidder eligibility, payment method and documentation with the Stanley County Treasurer before bidding',itin:'County-specific; confirm taxpayer-ID requirements directly with the Treasurer',online:'No — Stanley County describes the statutory county treasurer sale; verify the current sale notice before attending',otc:'Potentially — South Dakota law allows private sale of unsold tax certificates, but counties may sell certificates only if the county commission has waived the statutory prohibition',deed:'A tax certificate is not immediate ownership. South Dakota tax-deed proceedings generally cannot begin sooner than 3 years after the tax sale, with additional notice/redemption requirements.',special:'South Dakota generally prohibits counties from selling tax certificates unless the county commission adopts a waiver. Stanley County states its Treasurer conducts the annual certificate sale, but investors should verify the current-year county resolution and sale notice before bidding.',source:'https://www.stanleycountysd.gov/departments/treasurer/'}"""


def main():
    html = INDEX.read_text(encoding="utf-8")
    if LABEL in html:
        print("South Dakota tax-lien market already present")
        return

    anchor = "const visible=Object.fromEntries"
    anchor_pos = html.find(anchor)
    if anchor_pos < 0:
        raise SystemExit("Could not find rows-array anchor in index.html")
    rows_end = html.rfind("];", 0, anchor_pos)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")

    prefix = ",\n" if not html[:rows_end].rstrip().endswith(",") else "\n"
    html = html[:rows_end] + prefix + ROW + "\n" + html[rows_end:]
    html = html.replace("Updated August 13, 2026", "Updated August 14, 2026")
    INDEX.write_text(html, encoding="utf-8")
    print("Added South Dakota — Stanley County tax-certificate market")


if __name__ == "__main__":
    main()
