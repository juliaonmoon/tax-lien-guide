#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
LABEL = "Kentucky — county certificate sales"
ROW = r"""{state:'Kentucky — county certificate sales',product:'Certificate of delinquency / property-tax lien',schedule:'County clerks sell certificates beginning in mid-July through late October; Kentucky DOR published the 2026 county sale-date list on July 9, 2026',availability:'Active season — county dates vary',interest:'Certificates represent liens; Kentucky states interest accrues at 1% per month before sale, while third-party purchaser collections are governed by state statutes/regulations and fee limits',bid:'https://revenue.ky.gov/Property/Pages/Third-Party-Purchaser.aspx',canadian:'Possible only if current state and county registration requirements are met; verify directly before participating',itin:'State registration is required for purchasers above statutory thresholds; confirm taxpayer-ID documentation with Kentucky DOR and the county clerk',online:'County-specific; each clerk sets its own sale and registration process',otc:'County-specific; unsold/available certificates depend on the clerk and sale process',deed:'The purchaser receives a lien/certificate, not immediate ownership; collection/foreclosure steps are governed by Kentucky law',special:'For 2026, Kentucky requires state registration for purchasers planning to buy more than 3 certificates in a county, more than 5 statewide, or invest more than $10,000; state registration must be effective before participation and counties also have separate registration.',source:'https://revenue.ky.gov/Property/Pages/Third-Party-Purchaser.aspx'}"""


def main():
    html = INDEX.read_text(encoding="utf-8")
    if LABEL in html:
        print("Kentucky tax-lien market already present")
        return
    anchor = "const visible=Object.fromEntries"
    pos = html.find(anchor)
    if pos < 0:
        raise SystemExit("Could not find rows-array anchor")
    rows_end = html.rfind("];", 0, pos)
    if rows_end < 0:
        raise SystemExit("Could not find rows array end")
    prefix = ",\n" if not html[:rows_end].rstrip().endswith(",") else "\n"
    html = html[:rows_end] + prefix + ROW + "\n" + html[rows_end:]
    html = html.replace("Updated August 13, 2026", "Updated August 14, 2026")
    INDEX.write_text(html, encoding="utf-8")
    print("Added Kentucky certificate-of-delinquency market")


if __name__ == "__main__":
    main()
