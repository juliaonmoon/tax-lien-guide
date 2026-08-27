#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Queen Anne's County"
SOURCE_MARKER = "Maryland — Queen Anne\\'s County"

ROW = r'''{state:'Maryland — Queen Anne\'s County',product:'Tax Sale Certificate / property-tax lien',schedule:'Queen Anne\'s County held its 2026 online tax sale on May 19, 2026. The county currently lists the next annual tax sale as May 18, 2027.',availability:'MARKET-LEVEL ONLY. The county publishes tax-sale information and an over-the-counter certificate PDF, but changing/paid accounts are not frozen here as guaranteed current inventory; verify availability and purchase amount with the Treasury Division.',maxReturn:'10%/yr county redemption rate',interest:'Queen Anne\'s County Resolution 26-01 sets the redemption interest rate at 10% a year for all properties beginning with the May 2026 tax sale.',bid:'https://www.qac.org/598/Tax-Sale',canadian:'Not evaluated in this guide.',itin:'Not evaluated in this guide.',online:'The annual tax sale is held online. The county states that the online property list is updated weekly before the sale.',otc:'The county publishes an Available Over-the-Counter Tax Sale Certificates PDF. Registration is required, business purchasers must be registered and in good standing in Maryland, and the Treasury Division must be contacted for the amount needed to purchase a certificate.',deed:'The county sells tax sale certificates for delinquent charges; this is a lien/certificate interest, not an immediate deed or property ownership. Redemption and any later foreclosure of the right of redemption are separate legal stages.',special:'MARKET-LEVEL ONLY. Do not bulk republish owner/taxpayer names, present a completed or changing list as guaranteed current inventory, fabricate parcel/opening-bid or OTC purchase amounts, treat assessed/delinquent balances as bids, bypass bidder-registration requirements, or substitute deed/foreclosure records for Queen Anne\'s County tax-sale certificates.',source:'https://www.qac.org/598/Tax-Sale'}'''


def _find_existing_row(text: str):
    starts = [
        text.find("{state:'Maryland — Queen Anne\\'s County'"),
        text.find("{state:'Maryland — Queen Anne's County'"),
    ]
    starts = [s for s in starts if s >= 0]
    if not starts:
        return None
    start = min(starts)
    candidates = [p for p in (text.find("},", start), text.find("}\n", start)) if p >= 0]
    if not candidates:
        raise SystemExit("Could not find end of Queen Anne's County row")
    end = min(candidates) + 1
    return start, end


def main():
    text = INDEX.read_text(encoding="utf-8")
    existing = _find_existing_row(text)
    if existing:
        start, end = existing
        current = text[start:end]
        if current == ROW:
            print("Queen Anne's County Maryland canonical row already present")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Queen Anne's County Maryland tax-lien market row")
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
    print("Added Queen Anne's County Maryland tax-lien market")


if __name__ == "__main__":
    main()
