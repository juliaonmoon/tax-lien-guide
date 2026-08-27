#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Marion County"

ROW = r'''{state:'Iowa — Marion County',product:'Tax Sale Certificate of Purchase / property-tax lien',schedule:'2026 annual online tax sale was June 15, 2026 (third Monday in June). Marion County also permits adjourned/public-bidder handling when delinquent parcels remain.',availability:'2026 annual sale passed — verify any current adjourned/public-bidder availability with Marion County Treasurer',maxReturn:'2%/month redemption interest',interest:'Marion County states that tax-sale certificates accrue 2% interest per month during the redemption period. This is certificate/redemption interest, not immediate ownership of the property.',bid:'https://www.marioncountyiowa.gov/treasurer/tax_sale/',canadian:'2026 registration requires an online W-9. Foreign/non-U.S. bidder eligibility is not clearly stated on the county page; confirm taxpayer-identification eligibility directly with the Treasurer before registration.',itin:'Do not assume an ITIN alone satisfies Marion County bidder requirements. The county requires the online tax-auction registration process and W-9; verify current tax-ID requirements directly with the Treasurer.',online:'Yes — annual sale conducted online through Iowa Tax Auction',otc:'Unpaid parcels may move to adjourned/public-bidder handling under Iowa law; verify current inventory directly with the Treasurer rather than inferring it from the May/June publication.',deed:'A Certificate of Purchase does not transfer ownership. Marion County states an investor generally must wait at least 1 year 9 months before starting the separate notice process for a tax sale deed.',special:'MARKET-LEVEL ONLY. Marion County publishes an official 2026 Tax Sale Publication List, but it is a newspaper-style PDF containing taxpayer names and mixed public-notice content rather than a clean machine-readable inventory. Do not bulk republish owner/taxpayer names, do not treat published delinquent amounts as opening bids, and do not substitute Sheriff mortgage-foreclosure sales for the Treasurer tax-sale certificate market.',source:'https://www.marioncountyiowa.gov/treasurer/tax_sale/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start >= 0:
        # Restore the canonical county-authored row before strict validation.
        # Shared presentation normalizers may rewrite display wording later,
        # so marker presence alone is not an idempotent repair guarantee.
        end = text.find("}\n", start)
        comma = text.find("},", start)
        if comma >= 0 and (end < 0 or comma < end):
            end = comma + 1
        elif end >= 0:
            end += 1
        else:
            raise SystemExit("Could not find end of existing Marion County row")
        existing = text[start:end]
        if existing == ROW:
            print("Iowa Marion County canonical row already present")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Iowa Marion County tax-lien market row")
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
    print("Added Iowa Marion County tax-lien market")


if __name__ == "__main__":
    main()
