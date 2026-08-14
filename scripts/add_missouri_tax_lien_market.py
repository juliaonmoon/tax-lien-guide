#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Missouri — Clay County"

ROW = r'''{state:'Missouri — Clay County',product:'Delinquent-tax certificate of purchase / tax lien',schedule:'Clay County\'s 2026 online tax sale is scheduled for <span class="schedule-date">August 24, 2026 at 10:00 AM Central</span>. Registration and the notarized non-delinquency affidavit are due by August 16, 2026. Post-third-sale properties are expected to become available over the counter beginning the week of September 14, 2026.',availability:'Upcoming — August 24, 2026',interest:'Missouri redemption interest is the rate stated in the certificate, capped at 10% annually; interest is not paid on overbid amounts above delinquent taxes and sale costs. Eligible subsequent taxes paid by the purchaser earn 8% annually under state law.',bid:'https://claycountymo.gov/552/Tax-Sale',canadian:'Eligibility is not stated clearly for foreign bidders on the county page; confirm current residency, affidavit, taxpayer-document and payment requirements directly with the Clay County Collector before registering',itin:'County page requires registration and a notarized Statement of Non-Delinquency; confirm any U.S. taxpayer-ID requirement directly with the Collector/GovEase',online:'YES — 2026 sale is online through GovEase',otc:'YES — Clay County says post-third-sale properties will be available over the counter beginning the week of September 14, 2026',deed:'First- and second-offering purchasers generally face a one-year absolute redemption period and must complete statutory title-search and notice requirements before obtaining a Collector\'s Deed.',special:'A tax-sale purchase starts with a certificate of purchase, not immediate possession. Missouri requires title-search/notice steps before deed, and interest on the certificate is capped at 10% annually. Clay County coordinates the due diligence it will accept for deed or redemption reimbursement.',source:'https://claycountymo.gov/552/Tax-Sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Missouri Clay County row already present")
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
    print("Added Missouri Clay County tax-lien market")


if __name__ == "__main__":
    main()
