#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Howard County"

ROW = r'''{state:'Maryland — Howard County',product:'Tax Sale Certificate / property-tax lien',schedule:'2026 Howard County property tax sale was June 10, 2026. The official county tax-sale portal opened May 15, registration opened May 21, and registration closed June 3, 2026. Verify the next current-year notice before participating.',availability:'Annual county tax sale. Howard County advertises delinquent properties before the sale and operates a dedicated official tax-sale portal. This guide does not republish a stale post-sale parcel inventory; verify current availability directly with the Department of Finance tax-sale portal.',maxReturn:'18%/yr county redemption rate; owner-occupied residential rate subject to Maryland statutory cap',interest:'Howard County Code §20.141 sets an 18% annual redemption interest rate. Maryland Tax-Property §14-820 separately caps the redemption rate for owner-occupied residential property, so certificate-specific treatment must be verified.',bid:'https://taxsale.howardcountymd.gov/Public/Home.aspx',canadian:'County-specific. Howard County requires bidder registration and tax/payment documentation. Verify current eligibility and registration requirements directly with the Department of Finance before attempting to participate.',itin:'Do not assume an ITIN alone satisfies Howard County bidder eligibility. Verify current taxpayer-ID, registration, payment, and documentation requirements directly with the official tax-sale office.',online:'YES — Howard County operates a dedicated online tax-sale portal for registration, property viewing, and bidding.',otc:'No general over-the-counter inventory is assumed. Verify any post-sale certificate availability or assignments directly with Howard County; do not infer availability from an expired sale list.',deed:'The successful bidder receives a tax-sale certificate and lien, not immediate ownership. Any later court action to foreclose the owner\'s right of redemption is a separate legal stage and is not treated as a tax-deed sale listing here.',special:'MARKET-LEVEL ONLY. Howard County has a legitimate 2026 tax-certificate sale and a public tax-sale portal, but this row does not bulk republish owner/taxpayer names or a stale post-sale parcel inventory. Do not fabricate parcel listings or opening bids, treat assessed value or delinquent balance as a bid, or substitute Sheriff judicial-foreclosure or other deed/foreclosure sales for Howard County tax-sale certificates.',source:'https://taxsale.howardcountymd.gov/Public/Home.aspx'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Howard County Maryland row already present")
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
    print("Added Howard County Maryland tax-lien market")


if __name__ == "__main__":
    main()
