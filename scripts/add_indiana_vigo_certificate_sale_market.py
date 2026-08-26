#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Indiana — Vigo County 2026 Commissioners’ Certificate Sale"

ROW = r'''{state:'Indiana — Vigo County 2026 Commissioners’ Certificate Sale',product:'Commissioners’ tax-sale certificate / property-tax lien',schedule:'Vigo County’s official 2026 Commissioners’ Certificate Sale was scheduled for <span class="schedule-date">March 25, 2026</span> at 10:00 AM local time, with the county notice allowing a switch to the official ZeusAuction electronic format if local officials elected to do so.',availability:'Completed — March 25, 2026; verify any later county-held certificate availability directly with Vigo County/SRI',interest:'This is a Commissioners’ Certificate Sale after properties failed to receive sufficient bids at the preceding county tax sale. The official notice states redemption includes 10% of the certificate sale price plus 10% annual interest on qualifying subsequent taxes/special assessments paid by the purchaser; this is not a simple guaranteed APR on the entire investment.',bid:'https://www.vigocounty.in.gov/egov/documents/1769177825_36315.pdf',canadian:'Not confirmed — verify current Vigo County/SRI bidder eligibility and taxpayer-document requirements before participating in any future certificate sale.',itin:'Do not assume an ITIN or W-8 alone is accepted; verify current Vigo County/SRI registration requirements.',online:'POSSIBLE — the official notice states the March 25, 2026 sale could switch to ZeusAuction at local officials’ discretion; verify the county/SRI notice for the actual format used.',otc:'Not inferred. Any county-held certificate assignment or later disposition must be verified as a separate official Vigo County process.',deed:'A Commissioners’ Certificate Sale sells a certificate/lien interest, not immediate ownership. Any later deed requires the applicable Indiana redemption, notice, and deed procedures.',special:'MARKET-LEVEL SUMMARY ONLY. This is specifically a Vigo County Commissioners’ Certificate Sale, not the ordinary annual Treasurer tax sale and not a Sheriff/judicial foreclosure. The official publication contains parcel IDs, owner names, descriptions, and published certificate-sale minimum prices; this guide does not bulk republish owner/taxpayer names or freeze that completed 2026 list as current inventory. Do not substitute Sheriff foreclosure or Commissioners’ deed-sale properties.',source:'https://www.vigocounty.in.gov/egov/documents/1769177825_36315.pdf'}'''


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
        print("Refreshed Vigo County Indiana Commissioners certificate-sale market")
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
    print("Added Vigo County Indiana Commissioners certificate-sale market")


if __name__ == "__main__":
    main()
