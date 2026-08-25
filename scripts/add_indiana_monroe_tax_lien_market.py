#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Indiana — Monroe County 2026"

ROW = r'''{state:'Indiana — Monroe County 2026',product:'Tax sale certificate / property-tax lien',schedule:'Monroe County\'s official 2026 tax-lien auction is <span class="schedule-date">Wednesday, October 7, 2026</span>, with online bidding from 10:00 AM to 5:00 PM through ZeusAuction.',availability:'Upcoming — official 2026 sale date published; certified property list may be viewed on county sites or requested digitally, but no owner-linked bulk list is republished here',interest:'Indiana tax-sale purchaser returns are governed by the statutory redemption framework rather than a simple APR. Verify Indiana Code 6-1.1-24 and 6-1.1-25 plus Monroe County\'s current bidder rules for the exact certificate, redemption amount, notice duties, and deadlines.',bid:'https://www.in.gov/counties/monroe/Departments/auditor/tax-sale-faqs/',canadian:'Not confirmed — verify current Monroe County/ZeusAuction bidder-registration and taxpayer-document requirements before participating.',itin:'Do not assume an ITIN or W-8 alone is accepted; verify Monroe County/ZeusAuction\'s current registration and tax-form requirements.',online:'YES — Monroe County states its annual tax-lien auction uses ZeusAuction; 2026 open bidding is October 7 from 10:00 AM to 5:00 PM.',otc:'NO — Monroe County states it does not offer certificates for properties not sold at the annual tax sale.',deed:'Purchaser receives a tax-sale certificate/lien first. If the certificate is not redeemed after the statutory redemption period, the buyer may separately petition the court for a tax title deed; title is not immediate.',special:'MARKET-LEVEL SUMMARY ONLY. Monroe County says the certified lien list can be sent digitally or viewed on county/auction sites, but the guide does not bulk republish owner/taxpayer names or freeze a changing certified list as guaranteed auction inventory. Do not fabricate parcel rows or opening/minimum bids, bypass ZeusAuction registration controls, or substitute Sheriff/judicial foreclosure sales for the Treasurer/Auditor tax-lien auction.',source:'https://www.in.gov/counties/monroe/Departments/auditor/tax-sale-faqs/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        row_re = re.compile(
            rf"\{{state:'{re.escape(MARKER)}'.*?\}}(?=\s*,|\s*\n\];)",
            re.S,
        )
        updated, count = row_re.subn(ROW, text, count=1)
        if count != 1:
            raise SystemExit(f"Could not uniquely refresh {MARKER}")
        INDEX.write_text(updated, encoding="utf-8")
        print("Refreshed Monroe County Indiana tax-lien market")
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
    print("Added Monroe County Indiana tax-lien market")


if __name__ == "__main__":
    main()
