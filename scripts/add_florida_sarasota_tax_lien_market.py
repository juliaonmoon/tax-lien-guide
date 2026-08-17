#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Sarasota County"

ROW = r'''{state:'Florida — Sarasota County',product:'Tax certificate / first lien',schedule:'2026 tax-certificate sale for 2025 taxes; Sarasota County conducts the annual sale online through LienHub. Florida law requires the sale on or before June 1.',availability:'2026 annual sale passed; official unsold county-held certificates may be available after reconciliation on a first-come-first-served basis',maxReturn:'18%/yr statutory max',interest:'Reverse auction starts at 18% and bids downward. Sarasota states that a certificate generally earns at least 5% until accrued interest exceeds 5%, except a 0% winning bid earns 0%. County-held unsold certificates are offered at 18%.',bid:'https://www.sarasotataxcollector.gov/services/tax-services/property-tax/tax-cert-sale',canadian:'The county page does not publish a simple foreign-bidder rule. Confirm current LienHub registration, identity, banking and tax-document requirements before funding.',itin:'Verify current taxpayer-identification requirements with Sarasota County / LienHub; do not assume an ITIN alone guarantees eligibility.',online:'Yes — Sarasota County states the tax-certificate sale is conducted online through LienHub and bidders must pre-register.',otc:'YES — certificates without a bid are struck to the County at 18% and may be purchased first-come-first-served after annual-sale reconciliation, subject to the current official list.',deed:'A tax certificate is a lien, not ownership. After the statutory waiting period, an eligible certificate holder may file a separate tax-deed application; the Clerk conducts any later property auction.',special:'Sarasota explicitly separates the tax-certificate investment from the later tax-deed sale. The certificate has a seven-year life, subject to bankruptcy-related extensions; verify current certificate status, redemption, title and parcel details before bidding.',source:'https://www.sarasotataxcollector.gov/services/tax-services/property-tax/tax-cert-sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Florida Sarasota County row already present")
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
    print("Added Florida Sarasota County tax-lien market")


if __name__ == "__main__":
    main()
