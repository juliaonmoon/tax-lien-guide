#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Illinois — Stark County"

ROW = r'''{state:'Illinois — Stark County',product:'Delinquent real-estate tax sale / tax certificate',schedule:'Stark County publishes its 2026 delinquent real-estate tax sale for October 28, 2026 at 1:00 PM, with tax-sale registration due October 14, 2026. Verify the county notice before participating because dates can change.',availability:'2026 sale published — October 28, 2026',interest:'Illinois uses a lowest-penalty bid. Under 35 ILCS 200/21-215, no accepted penalty bid may exceed 9% of the tax or special assessment amount. Redemption amounts and timing are governed by the Property Tax Code.',bid:'https://www.starkco.illinois.gov/departments/treasurer',canadian:'County-specific registration and payment rules apply; verify identification, tax-form and payment requirements directly with the Stark County Treasurer before attempting to register',itin:'Do not assume an ITIN alone is sufficient; follow the current county registration packet and Illinois statutory requirements',online:'The Stark County Treasurer page is the official source for its current tax-sale date and registration information; verify whether the current sale is in-person, electronic, or uses a vendor before bidding',otc:'Illinois counties may handle unsold or forfeited taxes through separate statutory processes; do not assume a general OTC inventory without a current county notice',deed:'The tax buyer purchases the delinquent taxes and receives tax-sale rights/certificate, not immediate ownership. Illinois generally provides a redemption period; 35 ILCS 200/21-350 currently provides 2.5 years for many properties, with a shorter 1-year period for certain vacant, commercial, industrial, and 7+ unit properties.',special:'Illinois Department of Revenue states that, outside Cook County, counties generally hold tax sales annually. Stark County currently lists October 28, 2026 for its 2025 delinquent real-estate tax sale. Always verify the county registration packet, final delinquent list, redemption class, and current law.',source:'https://www.starkco.illinois.gov/departments/treasurer'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Illinois Stark County tax-lien row already present")
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
    print("Added Illinois Stark County tax-lien market")


if __name__ == "__main__":
    main()
