#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Clay County"

ROW = r'''{state:'Florida — Clay County',product:'Tax certificate / property-tax lien',schedule:'Annual Florida tax-certificate sale for delinquent real-estate taxes; Clay County Clerk confirms the Tax Collector sells the certificate before any later tax-deed proceeding. Verify the current annual sale notice and registration window with the Clay County Tax Collector / official sale platform.',availability:'Annual certificate sale; verify current county-held / unsold certificate availability with the Tax Collector',maxReturn:'18%/yr statutory max',interest:'Florida reverse-auction rules apply: the statutory certificate rate can be bid down from 18%. Do not treat the statutory maximum as the rate an investor will necessarily receive.',bid:'https://clayclerk.com/departments/recording/tax-deeds/',canadian:'No Clay County-specific foreign-bidder eligibility rule was found in the official public material reviewed. Verify current bidder registration, tax-ID, withholding, funding, and residency requirements before participating.',itin:'Verify current taxpayer-identification requirements with the Clay County Tax Collector / official auction platform; do not assume an ITIN alone establishes eligibility.',online:'The Clerk confirms later tax-deed sales are online; verify the current tax-certificate auction channel directly with the Tax Collector before bidding.',otc:'County-held certificate availability is not asserted here without a current official Clay County inventory source; verify directly with the Tax Collector.',deed:'A tax certificate is a lien, not ownership. Clay County Clerk states a certificate is held for at least two years before the holder may request the separate tax-deed sale process; the Clerk conducts the later property auction.',special:'Keep the products separate: the Tax Collector sells the delinquent-tax certificate/lien; the Clerk later conducts a tax-deed property sale if statutory conditions are met. Opening bids shown for tax-deed cases are deed-sale amounts and must not be presented as tax-certificate bids.',source:'https://clayclerk.com/departments/recording/tax-deeds/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Clay County row already present")
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
    print("Added Florida Clay County tax-lien market")


if __name__ == "__main__":
    main()
