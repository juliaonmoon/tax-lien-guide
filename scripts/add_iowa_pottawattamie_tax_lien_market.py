#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Pottawattamie County"

ROW = r'''{state:'Iowa — Pottawattamie County',product:'Tax sale certificate / property-tax lien',schedule:'2026 annual Pottawattamie County tax sale was held online on June 15, 2026. The official county terms state the delinquent list was published the week of June 1 and made available on the county-designated auction site after June 1.',availability:'2026 annual sale passed; verify any later public-bidder, assignment, or county-held activity directly with the Pottawattamie County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa tax-sale certificates accrue statutory redemption interest under Iowa law. Pottawattamie County’s 2026 terms govern bid-down ownership percentage, certificate issuance, redemption, assignments, and later deed proceedings. Do not treat the published delinquent amount as a guaranteed opening bid or investment return.',bid:'https://www.pottcounty-ia.gov/treasurer/real_estate/',canadian:'The county requires bidder registration, age 18+, and a completed W-9 for the 2026 sale. Do not assume non-U.S.-person eligibility without direct Treasurer confirmation.',itin:'The official 2026 terms require a W-9 and taxpayer-identification information for bidders; no W-8 pathway is stated in the published rules.',online:'Yes — the official 2026 terms say the sale was online through the county-designated Iowa tax-auction platform.',otc:'Subsequent/public-bidder or county-held certificate activity is governed by Iowa law and county procedure; verify current availability with the Treasurer.',deed:'A tax-sale Certificate of Purchase does not convey title. If a certificate remains unredeemed after the applicable statutory period, the holder may begin the separate notice process toward a Tax Deed.',special:'Market-level only. The official 2026 county terms say parcel data was available through the auction website after June 1, but access requires bidder registration. The pipeline does not bypass registration or fabricate parcel rows. Mortgage-foreclosure or sheriff-sale listings are not substituted for tax-sale certificates.',source:'https://www.pottcounty-ia.gov/treasurer/real_estate/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Pottawattamie County row already present")
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
    print("Added Iowa Pottawattamie County tax-lien market")


if __name__ == "__main__":
    main()
