#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Iowa County"

ROW = r'''{state:'Iowa — Iowa County',product:'Tax Sale Certificate / property-tax lien',schedule:'Annual electronic tax sale is held on the third Monday in June. The 2026 annual sale therefore occurred in June; verify any adjourned/current availability directly with the Iowa County Treasurer.',availability:'2026 annual sale passed — verify current tax-sale certificate availability directly with Iowa County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa County states that redemption from tax sale requires 2% interest per month under Iowa law. This is certificate/redemption interest and does not mean the investor immediately owns the property.',bid:'https://iowacounty.iowa.gov/treasurer/tax_sale/',canadian:'Foreign/non-U.S. bidder eligibility is not clearly stated on the county public page. Confirm current registration, taxpayer-ID, payment, and documentation requirements with Iowa County Treasurer before attempting to bid.',itin:'Do not assume an ITIN alone satisfies bidder requirements. Verify current taxpayer-ID/document requirements directly with Iowa County Treasurer.',online:'Yes — Iowa County states the annual tax sale is held electronically',otc:'County-specific. Verify any adjourned or public-bidder certificate availability directly with the Treasurer; do not infer current inventory from delinquent-tax or tax inquiry pages.',deed:'A tax-sale certificate is a lien interest, not immediate property ownership. Any later deed requires the separate Iowa statutory notice/redemption process.',special:'MARKET-LEVEL ONLY. Iowa County publishes tax-sale and tax-sale-certificate inquiry resources, but no current unrestricted machine-readable 2026 parcel feed was verified for safe republication. Do not bulk republish owner/taxpayer names, fabricate parcel inventory or opening bids, treat delinquent tax balances as opening bids, or substitute Iowa County Sheriff foreclosure sales for Treasurer tax-sale certificates.',source:'https://iowacounty.iowa.gov/treasurer/tax_sale/'}'''


def find_row_bounds(text: str):
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        return None
    candidates = [p for p in (text.find("},", start), text.find("}\n", start)) if p >= 0]
    if not candidates:
        raise SystemExit("Could not find end of Iowa County Iowa market row")
    end = min(candidates) + 1
    return start, end


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        if text[start:end] == ROW:
            print("Iowa County Iowa canonical row already present")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Iowa County Iowa tax-lien market row")
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
    print("Added Iowa County Iowa tax-lien market")


if __name__ == "__main__":
    main()
