#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Anne Arundel County"

ROW = r'''{state:'Maryland — Anne Arundel County',product:'Tax Sale Certificate / first-lien property-tax lien',schedule:'Anne Arundel County held its 2026 Internet-based tax sale on June 3, 2026, with bidding from 9:00 a.m. to 1:00 p.m. Eastern time.',availability:'Annual Internet-based tax-lien certificate sale. The county also publishes 2026 remaining liens and sale results; verify current availability on the official county Tax Sale page before acting.',maxReturn:'18%/yr county redemption rate',interest:'Anne Arundel County states redemption requires the tax sale price plus interest at 1.5% per month, or 18% per annum, plus qualifying subsequent taxes/charges. The return applies to the tax-lien certificate, not to ownership of the property.',bid:'https://www.aacounty.org/finance/tax-sale',canadian:'County-specific. The 2026 sale required online registration. Do not assume foreign bidder eligibility; verify current taxpayer-ID, payment, and registration requirements directly with Anne Arundel County.',itin:'Do not assume an ITIN alone establishes bidder eligibility. Verify the county\'s current registration and tax-document requirements before participating.',online:'YES — the 2026 tax sale was conducted by Internet-based public auction.',otc:'County publishes a 2026 remaining-liens resource. Availability changes as liens are redeemed or otherwise resolved; use the county\'s current list rather than stale sale inventory.',deed:'Only the tax lien certificate is sold at tax sale, not the property itself. The owner retains ownership unless redemption rights are later foreclosed through the separate court process.',special:'MARKET-LEVEL ONLY. Anne Arundel County publishes current tax-sale, remaining-lien, and result information, but this guide does not bulk republish owner/taxpayer names or treat advertised delinquent balances, assessments, or later foreclosure values as fabricated opening bids. Keep the tax-lien certificate sale distinct from any later foreclosure-of-redemption proceeding.',source:'https://www.aacounty.org/finance/tax-sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Anne Arundel County Maryland row already present")
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
    print("Added Anne Arundel County Maryland tax-lien market")


if __name__ == "__main__":
    main()
