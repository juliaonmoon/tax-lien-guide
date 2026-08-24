#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Worcester County"

ROW = r'''{state:'Maryland — Worcester County',product:'Tax Sale Certificate / property-tax lien',schedule:'Worcester County held its 2026 online tax sale through RealAuction from May 13, 2026 at 10:00 a.m. through May 15, 2026 at 1:00 p.m. Eastern time.',availability:'Annual online tax-lien certificate sale. Worcester County also publishes over-the-counter liens from the 2025 and 2026 tax sales; verify the current county list before acting because liens can be redeemed or otherwise resolved.',maxReturn:'10%/yr county redemption rate',interest:'Worcester County states that tax-sale lien certificates earn 10% annual interest on the amount paid at sale for taxes, water and wastewater charges, and costs of sale. This return applies to the certificate/lien, not immediate ownership of the real property.',bid:'https://www.worcestermd.gov/departments/treasurer/sale',canadian:'County-specific. The 2026 annual sale required RealAuction registration. Do not assume foreign-bidder eligibility; verify current taxpayer-ID, registration, payment, and tax-document requirements directly with Worcester County.',itin:'Do not assume an ITIN alone establishes bidder eligibility. Verify Worcester County\'s current registration and tax-document requirements before participating.',online:'YES — the 2026 annual tax sale was conducted online through RealAuction.',otc:'YES — the county currently publishes an Over the Counter Lien from Tax Sale 2025 & 2026 resource. Current availability changes with redemption and other account activity; use the county\'s current official list.',deed:'The county sells a tax-sale certificate/lien. The property owner retains title unless the purchaser later completes the separate court foreclosure-of-the-right-of-redemption process and obtains title.',special:'MARKET-LEVEL ONLY. Worcester County publishes current 2026 tax-sale and over-the-counter lien information, but this guide does not bulk republish owner/taxpayer names from property lists, does not treat delinquent balances or assessments as fabricated opening bids, and does not substitute later foreclosure/title records for the original tax-lien certificate.',source:'https://www.worcestermd.gov/departments/treasurer/sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Worcester County Maryland row already present")
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
    print("Added Worcester County Maryland tax-lien market")


if __name__ == "__main__":
    main()
