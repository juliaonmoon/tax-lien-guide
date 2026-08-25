#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Broward County"

ROW = r'''{state:'Florida — Broward County',product:'Tax certificate / first-priority tax lien',schedule:'Broward County sells delinquent-property tax certificates through the Tax Collector; the county explains that unpaid property taxes lead to a tax-certificate sale in June. Verify the current annual certificate-sale calendar on the official Tax Collector page before bidding.',availability:'Annual tax-certificate market; verify current certificate-sale and county-held availability with Broward County Tax Collector',maxReturn:'Up to 18%/yr statutory maximum; actual certificate rate is determined by Florida reverse bidding',interest:'Florida tax certificates earn the bid interest rate subject to the statutory 18% annual maximum. Broward County distinguishes the certificate investment from the later tax-deed property auction; verify current certificate-specific auction rules before funding.',bid:'https://www.broward.org/RecordsTaxesTreasury/taxcollector/Pages/TaxCertificateSale.aspx',canadian:'Foreign-bidder eligibility and tax-document requirements are not clearly published on the county tax-certificate page; verify directly with Broward County Tax Collector before registration or funding.',itin:'Taxpayer-identification requirements for non-U.S. bidders are not clearly stated on the public county certificate page; verify with the Tax Collector.',online:'Broward County maintains an official tax-certificate sale process; verify the current auction platform and registration instructions on the county page.',otc:'Do not assume county-held inventory is available. Verify current unsold/county-held certificate procedures directly with the Tax Collector.',deed:'A tax certificate is an investment/lien and does not convey ownership. After the statutory holding period, an eligible certificate holder may apply for a tax deed; the later tax-deed auction is a separate property sale.',special:'MARKET-LEVEL ONLY until Broward County publishes a current tax-certificate parcel list in a form that can be safely and unambiguously ingested. Do not substitute Broward tax-deed auction rows, foreclosure-sale rows, owner-name data, or tax-deed opening bids for tax-certificate listings.',source:'https://www.broward.org/RecordsTaxesTreasury/taxcollector/Pages/TaxCertificateSale.aspx'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start >= 0:
        end = text.find("}", start)
        if end < 0:
            raise SystemExit("Could not find end of existing Broward County row")
        INDEX.write_text(text[:start] + ROW + text[end + 1 :], encoding="utf-8")
        print("Refreshed Florida Broward County tax-lien market")
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
    print("Added Florida Broward County tax-lien market")


if __name__ == "__main__":
    main()
