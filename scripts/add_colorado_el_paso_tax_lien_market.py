#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — El Paso County"

ROW = r'''{state:'Colorado — El Paso County',product:'Tax lien / Tax Lien Sale Certificate of Purchase',schedule:'El Paso County conducts one annual online tax-lien sale through RealAuction. The Treasurer says delinquent-tax lists are published each September; the exact 2026 auction date and 2026 redemption rate were not yet posted on the official county page as of Aug 17, 2026.',availability:'2026 annual sale upcoming; exact date/rate pending official publication',maxReturn:'2026 rate set Sep 1; 2025 was 14%/yr',interest:'Colorado sets the redemption rate each year at nine percentage points above the federal discount rate in effect on September 1. El Paso County states the 2025 rate was 14% annually (1.17% monthly). Premium/bonus bids are not part of the redemption amount and do not earn interest.',bid:'https://treasurer.elpasoco.com/tax-lien-sale/',canadian:'Foreign-bidder eligibility is not clearly stated in the official county material reviewed. El Paso County reports interest on redeemed certificates to the IRS and issues 1099 forms, so non-U.S. bidders should confirm registration, taxpayer-ID, withholding and payment requirements directly with the Treasurer / RealAuction before funding.',itin:'Official public instructions do not establish that an ITIN alone is sufficient. Verify current taxpayer-identification and withholding requirements directly with El Paso County Treasurer / RealAuction.',online:'YES — El Paso County states its annual Tax Lien Sale is conducted online through RealAuction.',otc:'YES — unsold tax liens are struck off to the County and may be available for assignment. The Treasurer publishes a County Held Tax Liens list; not every county-held lien is necessarily eligible for assignment.',deed:'A Tax Lien Sale Certificate of Purchase is not ownership. The original lien generally has a three-year redemption period. Under Colorado’s newer Treasurer’s Deed procedure, an eligible certificate holder may later apply for a separate public auction process rather than receiving a deed automatically.',special:'Keep El Paso County’s annual tax-lien sale separate from its later Treasurer’s Deed/public-auction process. The county explicitly says buying a tax lien gives no ownership, possession, use or access rights. The 2026 redemption rate should remain unknown until the official September 1 rate is published; do not reuse the 2025 14% figure as a guaranteed 2026 return.',source:'https://treasurer.elpasoco.com/tax-lien-sale/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado El Paso County row already present")
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
    print("Added Colorado El Paso County tax-lien market")


if __name__ == "__main__":
    main()
