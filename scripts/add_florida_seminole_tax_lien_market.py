#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Seminole County"

ROW = r'''{state:'Florida — Seminole County',product:'Tax certificate / first lien',schedule:'Seminole County states its 2026 online tax-certificate sale took place June 1, 2026. Delinquent real-estate taxes are advertised before the sale and the auction is hosted through LienHub.',availability:'2026 annual sale passed — monitor the official Tax Collector / LienHub pages for current certificate information and future sale notices',maxReturn:'18%/yr statutory max',interest:'Competitive reverse bidding starts at 18% and decreases. The winning bidder pays the delinquent taxes and receives a tax certificate creating a first lien on the parcel; the actual certificate rate may be lower than 18%.',bid:'https://seminolecounty.tax/services/property-taxes/delinquent-taxes/',canadian:'Seminole County requires bidder registration through LienHub. Foreign-bidder eligibility and acceptable taxpayer-identification/banking documentation are not stated as a simple county rule; confirm current requirements with the Tax Collector before participating.',itin:'Verify current taxpayer-identification requirements with the Tax Collector / auction platform before registering; do not assume an ITIN alone guarantees eligibility.',online:'YES — Seminole County states the 2026 tax-certificate sale is hosted online through LienHub.',otc:'County-held certificates can exist under Florida law, including certificates automatically struck to the county in specified cases. Use the current official county/LienHub records rather than assuming inventory is available.',deed:'A tax certificate is a first lien, not ownership. If eligible and still unpaid after the statutory waiting period, a certificate holder may apply for a separate tax-deed process; any later property auction is distinct from the original lien sale.',special:'Seminole County states certificates are auctioned individually by parcel. Low-value homestead parcels and properties in litigation may be automatically struck to the county and not offered to bidders at the annual sale.',source:'https://seminolecounty.tax/services/property-taxes/delinquent-taxes/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Seminole County row already present")
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
    print("Added Florida Seminole County tax-lien market")


if __name__ == "__main__":
    main()
