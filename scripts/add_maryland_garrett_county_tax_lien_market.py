#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Garrett County"

ROW = r'''{state:'Maryland — Garrett County',product:'Tax Sale Certificate / property-tax lien',schedule:'Garrett County opened bidding for its 2026 online tax sale on May 18, 2026, with bidding closing in batches on May 22, 2026. Registration closed May 15.',availability:'MARKET-LEVEL ONLY. Garrett County directed bidders to its official online tax-sale system for the regularly updated property list. This guide does not republish the completed-sale parcel list as current inventory.',maxReturn:'Current 2026 certificate redemption rate not independently verified; confirm with Garrett County before bidding',interest:'Purchasers receive a certificate of sale / tax lien rather than immediate ownership. Garrett County official sale terms describe a later court foreclosure of the right of redemption as a separate stage. This guide does not carry an older published county redemption rate forward as the 2026 rate without current confirmation.',bid:'https://www.garrettcountymd.gov/financial-services/billing-collections/news/2026-05/2026-tax-sale-registration-now-open',canadian:'Foreign-bidder eligibility is not clearly established by the current county page. Verify current bidder registration and tax-identification requirements directly with Garrett County before attempting to participate.',itin:'The county requires online registration, but this guide does not infer whether an ITIN, SSN, EIN, or other identifier satisfies current registration requirements.',online:'Yes — Garrett County states the 2026 sale was conducted through its official online Maryland tax-sale portal.',otc:'No current over-the-counter inventory is claimed from the county source reviewed for this market.',deed:'A successful bidder receives a Certificate of Sale / property-tax lien, not immediate title. A later Circuit Court foreclosure of the right of redemption and deed issuance are separate legal stages subject to statutory requirements.',special:'MARKET-LEVEL ONLY. Do not bulk republish owner/taxpayer names, treat the completed 2026 auction list as current inventory, fabricate opening bids from assessments or delinquent balances, or substitute judicial foreclosure/deed-sale records for Garrett County tax-sale certificates.',source:'https://www.garrettcountymd.gov/financial-services/billing-collections/news/2026-05/2026-tax-sale-registration-now-open'}'''


def row_bounds(text: str):
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        return None
    comma_end = text.find("},", start)
    array_end = text.find("}\n];", start)
    candidates = []
    if comma_end >= 0:
        candidates.append(comma_end + 1)
    if array_end >= 0:
        candidates.append(array_end + 1)
    if not candidates:
        raise SystemExit("Could not find end of Garrett County Maryland row")
    return start, min(candidates)


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Garrett County Maryland canonical row already present")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Garrett County Maryland tax-lien market row")
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
    print("Added Garrett County Maryland tax-lien market")


if __name__ == "__main__":
    main()
