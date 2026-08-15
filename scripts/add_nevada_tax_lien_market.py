#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Nevada — Clark County"

ROW = r'''{state:'Nevada — Clark County',product:'Special-assessment lien Certificate of Sale',schedule:'Clark County conducts certificate sales for delinquent special assessments four times per year. Assessment Management Group, the county-linked assessment administrator, currently lists the next Clark County sale for September 24, 2026. Verify the parcel list when it is posted approximately three weeks before sale.',availability:'Periodic in-person certificate sale; current published Clark County sale date: September 24, 2026',interest:'Clark County states the certificate earns simple interest at 1% per month (12% per year) on the certificate sale price while outstanding, with monthly interest also applying to eligible subsequent payments made by the certificate holder.',bid:'https://www.clarkcountynv.gov/government/elected_officials/county_treasurer/certificate-sale',canadian:'Registration is in person shortly before the sale and requires government-issued photo ID. Winning purchasers must complete a W-9, so non-U.S. bidders should confirm tax-ID and withholding requirements with Clark County before relying on eligibility.',itin:'Clark County requires a completed W-9 from a winning buyer. Do not assume an ITIN or foreign tax status alone satisfies the county or IRS requirements; confirm directly before bidding.',online:'No. Clark County says purchasers must be physically present to register and participate in the certificate sale.',otc:'Potential follow-up availability exists: if a certificate remains unsold after the winning buyer and alternates fail to pay, it may first be sold at the Treasurer window; if still unsold it is issued to Clark County and may later be sold over the counter for the sale amount plus 1% per month while the County holds it.',deed:'This is a lien certificate, not immediate ownership. Clark County states the redemption period is generally 120 days, or 2 years when a permanent residential dwelling or other significant permanent improvement existed on the property at sale. After the applicable redemption period, a certificate holder must complete statutory notice and other requirements before requesting a deed.',special:'Important distinction: this is a delinquent SPECIAL-ASSESSMENT lien certificate under Nevada law, not Clark County’s separate real-property tax deed auction. The purchaser acquires only the assessment lien and has no right to enter or use the property during the redemption period. Clark County uses a randomized buyer-number selection process rather than an interest-rate bidding auction.',source:'https://www.clarkcountynv.gov/government/elected_officials/county_treasurer/faqs'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Nevada Clark County assessment-lien row already present")
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
    print("Added Nevada Clark County special-assessment lien market")


if __name__ == "__main__":
    main()
