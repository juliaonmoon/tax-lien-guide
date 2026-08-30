#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Palm Beach County"

ROW = r'''{state:'Florida — Palm Beach County',product:'Tax certificate / enforceable first property-tax lien',schedule:'Palm Beach County holds an annual tax-certificate sale for unpaid prior-year real-estate taxes. The Constitutional Tax Collector states the sale must be held 60 days after delinquency or June 1, whichever is later; county-held certificates may remain purchasable afterward while eligible.',availability:'2026 annual sale passed — current county-held certificates may be available through the Constitutional Tax Collector, subject to live status confirmation',maxReturn:'18%/yr statutory max',interest:'Competitive tax-certificate bidding determines the investor rate. Palm Beach County states that county-held certificates accrue 18% annual interest (1.5% per month); annual-sale certificates are sold through the competitive certificate-sale process.',bid:'https://www.pbctax.gov/taxes/property-tax/tax-certificates-and-deeds/',canadian:'Foreign-bidder eligibility and U.S. tax-document requirements should be confirmed directly with the Palm Beach County Constitutional Tax Collector and RealAuction before registration or purchase.',itin:'Verify current taxpayer-identification and withholding-document requirements with the Tax Collector before bidding or purchasing county-held certificates; do not infer eligibility from another Florida county.',online:'YES for annual auction registration — the official Palm Beach County page directs certificate buyers to RealAuction. County-held certificates may be purchased using the Tax Collector’s published methods and may also appear in supplemental sales.',otc:'YES — certificates not purchased during the annual certificate sale are struck to the county and may be purchased after issuance and before a tax-deed application, subject to current certificate status.',deed:'A tax certificate is an enforceable first lien, not ownership. If delinquent taxes remain unpaid for the statutory period, an eligible certificate holder may file a separate Tax Deed Application; any resulting tax-deed property sale is conducted separately by the Clerk & Comptroller.',special:'Palm Beach County explicitly distinguishes tax certificates from tax deeds. Preserve that terminology: do not present a certificate as ownership, and do not substitute later tax-deed inventory or tax-deed opening/minimum bids for tax-certificate data. Research the current county-held list and confirm certificate status with the Constitutional Tax Collector before purchase.',source:'https://www.pbctax.gov/taxes/property-tax/tax-certificates-and-deeds/'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Palm Beach County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Palm Beach County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Palm Beach County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Palm Beach County tax-lien market row")
        return

    start = text.find("const rows=[")
    if start < 0:
        raise SystemExit("Could not find rows array")
    end = text.find("\n];", start)
    if end < 0:
        raise SystemExit("Could not find end of rows array")

    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Florida Palm Beach County tax-lien market")


if __name__ == "__main__":
    main()
