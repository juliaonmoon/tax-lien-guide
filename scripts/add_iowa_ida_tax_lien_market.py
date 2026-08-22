#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Ida County"

ROW = r'''{state:'Iowa — Ida County',product:'Tax sale certificate / property-tax lien',schedule:'Ida County officially advertised its 2026 annual tax sale for June 15, 2026, with all bids placed online through GovEase. The county publication also states that adjourned tax sales may be held on later business days while parcels remain available and bidders are present.',availability:'2026 annual sale cycle passed; verify any adjourned/public-bidder certificate availability with Ida County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa Code Chapter 447 provides 2% per month redemption interest on qualifying tax-sale certificates. The purchaser receives a tax-sale certificate/lien interest; a deed can arise only after the separate statutory redemption and notice process.',bid:'https://www.iowatreasurers.org/kcfinder/upload/Ida/2026%20Publication%20List%20.pdf',canadian:'County bidder-registration and tax-identification rules apply. Confirm current eligibility and required documentation with Ida County Treasurer and the current auction platform before attempting registration.',itin:'Verify current Ida County bidder tax-identification requirements; do not assume an ITIN alone establishes eligibility.',online:'Yes for the 2026 annual sale — Ida County states all bids were placed online through GovEase.',otc:'The official 2026 notice says adjourned tax sales may be held on business days after the annual sale while parcels remain and bidders are present. Verify current availability directly with the Treasurer; do not infer inventory from the June publication.',deed:'A tax-sale certificate does not transfer ownership. If a parcel is not redeemed within the statutory period, a deed may be issued only after the separate Iowa Code Chapter 447 notice/redemption process.',special:'MARKET-LEVEL ONLY. Ida County publishes an official 2026 delinquent-tax list that includes taxpayer names, real estate, mobile homes, and special assessments. Do not bulk republish owner/taxpayer names, do not infer current inventory from the June publication, do not present delinquent-tax amounts as opening/minimum bids, and do not mix later deed proceedings with the original Treasurer tax-sale certificate process.',source:'https://www.iowatreasurers.org/kcfinder/upload/Ida/2026%20Publication%20List%20.pdf'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Ida County row already present")
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
    print("Added Iowa Ida County tax-lien market")


if __name__ == "__main__":
    main()
