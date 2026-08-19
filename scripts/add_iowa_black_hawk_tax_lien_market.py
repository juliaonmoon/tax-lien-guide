#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Black Hawk County"

ROW = r'''{state:'Iowa — Black Hawk County',product:'Tax sale certificate / property-tax lien',schedule:'Annual tax sale is held in June under Iowa law. Black Hawk County publishes delinquent-tax sale information and an adjourned tax-sale list through the Treasurer; verify the current sale/adjourned-sale status before bidding.',availability:'Annual June sale / adjourned-sale status is county-specific; verify the current official Black Hawk County Treasurer listing',maxReturn:'2%/month redemption interest',interest:'Iowa tax-sale certificates accrue 2% per month redemption interest under Iowa law. The certificate is a lien interest, not immediate ownership; later deed rights require the separate statutory notice/redemption process.',bid:'https://www.blackhawkcounty.iowa.gov/334/Delinquencies',canadian:'County registration and tax-identification requirements apply. Confirm current bidder eligibility directly with the Black Hawk County Treasurer before funding.',itin:'Verify current Black Hawk County bidder tax-ID and registration requirements; do not assume an ITIN alone guarantees eligibility.',online:'Verify current Black Hawk County sale format and registration instructions with the Treasurer.',otc:'Black Hawk County publishes an Adjourned Tax Sale List when applicable; availability changes as taxes are paid or parcels otherwise leave sale status.',deed:'A tax-sale certificate creates a lien and does not itself convey title. A tax deed, if eventually available after Iowa statutory notice and redemption requirements, is a separate later stage.',special:'MARKET-LEVEL ONLY. Black Hawk County explicitly prohibits commercial redistribution of data from its site. This project therefore does not ingest, republish, or bulk-copy the county delinquent/adjourned parcel list. Do not substitute sheriff-foreclosure listings, owner-name data, or fabricated parcel rows.',source:'https://www.blackhawkcounty.iowa.gov/334/Delinquencies'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Iowa Black Hawk County row already present")
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
    print("Added Iowa Black Hawk County tax-lien market (market-level only; redistribution restriction preserved)")


if __name__ == "__main__":
    main()
