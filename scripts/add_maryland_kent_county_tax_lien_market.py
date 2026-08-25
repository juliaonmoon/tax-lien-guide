#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Kent County"

ROW = r'''{state:'Maryland — Kent County',product:'Tax Sale Certificate / property-tax lien',schedule:'Maryland\'s official 2026 tax-sale schedule lists Kent County\'s tax sale for May 21, 2026. Verify future annual dates and any post-sale availability directly with the Kent County Office of Finance.',availability:'MARKET-LEVEL ONLY. Kent County states its tax-sale listing is advertised in the Kent County News rather than supplied as a bidder list by the Office of Finance. This guide does not bulk republish that owner-linked newspaper list or treat the completed 2026 sale list as current inventory.',maxReturn:'Current 2026 certificate redemption rate not independently verified; confirm with Kent County',interest:'Kent County sells real-estate tax-sale certificates. Historical official county guidance states opening bids begin with delinquent taxes plus interest, advertising fees, sale costs and notary fees, and unsold certificates may later be available from the county. Confirm all current 2026 terms directly with the Office of Finance before bidding.',bid:'https://dat.maryland.gov/Pages/Tax-Sale-Schedule.aspx',canadian:'Foreign-bidder eligibility is not clearly established by the current official 2026 schedule. Verify current bidder and tax-identification requirements directly with Kent County.',itin:'Not independently verified; confirm bidder tax-ID requirements with the Kent County Office of Finance.',online:'Current official state schedule confirms the 2026 sale date but does not establish a current online-bidding format for Kent County; verify the current format directly with the county.',otc:'Historical official county guidance says county-held certificates may become available after the annual sale, but current 2026 OTC inventory is not claimed here without a current county list.',deed:'A Kent County tax-sale certificate is a lien/certificate investment, not immediate property ownership. The owner may redeem until the right of redemption is finally barred; any later deed/title stage is separate.',special:'MARKET-LEVEL ONLY. Do not bulk republish owner/taxpayer names from the newspaper advertisement, treat the completed 2026 list as current inventory, fabricate parcel-level opening bids, carry forward an unverified historical redemption rate, or substitute Sheriff/judicial foreclosure or deed-sale records for Kent County tax-sale certificates.',source:'https://dat.maryland.gov/Pages/Tax-Sale-Schedule.aspx'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Kent County Maryland row already present")
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
    print("Added Kent County Maryland tax-lien market")


if __name__ == "__main__":
    main()
