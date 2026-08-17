#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Adams County"

ROW = r'''{state:'Colorado — Adams County',product:'Tax lien / Tax Lien Sale Certificate of Purchase',schedule:'Adams County holds an annual internet tax-lien sale. As of Aug 17, 2026, the county’s dedicated tax-lien page still displays its 2025 live-sale dates and says current-year sale information is posted in mid-October; the county tax calendar separately describes the annual online sale window as Oct 7–Nov 6. Verify the final 2026 dates when Adams publishes its current-year notice.',availability:'2026 schedule pending official current-year notice',maxReturn:'2026 rate not yet published; 2025 was 14%/yr',interest:'Colorado sets the statutory redemption interest rate annually. Adams County states the 2025 rate was 14%. The guide does not reuse that value as the 2026 rate until Adams or the state publishes the 2026 rate. Premium/bonus bids do not earn interest and are not returned.',bid:'https://adamscountyco.gov/our-county/elected-officials/treasurer-public-trustee/treasurer-division/tax-lien-sale/',canadian:'The official Adams County materials reviewed do not clearly establish eligibility for non-U.S. persons. Confirm bidder registration and tax-document requirements directly with the Treasurer before planning to participate.',itin:'Current official materials reviewed do not state whether an ITIN or foreign tax form is accepted; verify directly with Adams County.',online:'YES — Adams County states its tax-lien sale is an internet tax sale.',otc:'YES — Adams County publishes a County Held Lien List and an Unredeemed Tax Lien List. Availability changes as liens are redeemed or assigned.',deed:'A tax-lien certificate is not property ownership. Under Colorado’s current Treasurer’s Deed process, the later option for Treasurer’s Deed is sold through a separate public auction rather than automatically conveying the property to the lienholder.',special:'Keep this annual tax-lien/certificate market separate from Adams County Public Trustee foreclosure auctions and from the later Treasurer’s Deed option auction. The county explicitly says a tax-sale purchaser receives a recorded lien and no right of possession.',source:'https://adamscountyco.gov/our-county/elected-officials/treasurer-public-trustee/treasurer-division/tax-lien-sale/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Adams County row already present")
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
    print("Added Colorado Adams County tax-lien market")


if __name__ == "__main__":
    main()
