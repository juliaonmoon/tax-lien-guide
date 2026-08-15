#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Ohio — Franklin County"

ROW = r'''{state:'Ohio — Franklin County',product:'Tax lien certificate portfolio',schedule:'Franklin County conducts an annual tax-lien certificate sale generally between late October and early November. The county says sale details are posted in early September. The most recently published specific sale date on the official buyer-information page is November 3, 2025, so verify the 2026 notice before relying on a date.',availability:'Annual bulk sale; 2026 specific date not yet published on the county buyer-information page',interest:'Ohio tax-certificate rates are governed by Ohio Revised Code Chapter 5721. The certificate rate may range from 0% up to 18% depending on sale structure and county terms. Franklin County uses a negotiated bulk sale, so do not assume the statutory maximum is the actual return.',bid:'https://treasurer.franklincountyohio.gov/Delinquent-Taxes/Tax-Lien-Sale/Buyer-Information',canadian:'Franklin County explicitly states the sale is a multi-million-dollar bulk portfolio and is not designed for individual investors. Prospective purchasers must satisfy county registration, financial-verification, tax-ID and deposit requirements.',itin:'The county requires IRS Form W-9 and taxpayer-identification information plus financial verification; do not assume an ITIN by itself makes a bidder eligible.',online:'The county publishes buyer information and provides the property list electronically by email before the sale, but the tax liens are sold as one negotiated portfolio rather than individual online lots.',otc:'Franklin County explicitly says it does not sell over-the-counter tax liens.',deed:'Purchasing the certificate does not give immediate ownership. Franklin County states the owner has at least one year to redeem before foreclosure can ordinarily begin, subject to Ohio law and exceptions such as vacant-and-abandoned property.',special:'Important suitability warning: Franklin County says all available liens are auctioned as a single block worth several million dollars, individual certificates are not sold, and the program is not designed for individual investors. The county also states that a list of included properties is made available electronically in September and changes as owners pay before sale.',source:'https://treasurer.franklincountyohio.gov/Delinquent-Taxes/Tax-Lien-Sale/Buyer-Information'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Ohio Franklin County tax-lien row already present")
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
    print("Added Ohio Franklin County tax-lien market")


if __name__ == "__main__":
    main()
