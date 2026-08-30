#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Citrus County"

ROW = r'''{state:'Florida — Citrus County',product:'Tax certificate / first-priority property-tax lien',schedule:'Citrus County states that its annual tax-certificate sale for delinquent real-estate taxes begins on or before June 1. The Tax Collector currently links to 2026 sale information from its property-tax page, but that linked detail page is unavailable; verify the current annual notice before bidding.',availability:'The 2026 annual sale period has passed; county-held certificates may be available through the official LienHub process, subject to current inventory and Florida restrictions.',maxReturn:'18%/yr statutory max',interest:'Florida reverse auction. Citrus County explains that the tax-certificate sale is conducted through LienHub; Florida certificate bidding is rate-based and the certificate remains a lien rather than ownership. Verify the current county auction instructions before bidding.',bid:'https://www.citrustc.us/services/tax-certificate-information/',canadian:'No Citrus-specific foreign-bidder eligibility rule was found in the official county pages reviewed. Verify current registration, taxpayer-identification, withholding and payment requirements with the Tax Collector / LienHub before funding.',itin:'Verify current taxpayer-identification and withholding requirements with the Citrus County Tax Collector / official auction platform; do not assume an ITIN alone guarantees eligibility.',online:'Yes — Citrus County states its tax-certificate sale is conducted through LienHub.',otc:'YES — Citrus County states county-held certificates can be purchased through LienHub, subject to current inventory and Florida restrictions such as certain low-value homestead certificates.',deed:'A tax certificate is a first lien, not ownership. Citrus County states certificates are subject to tax-deed application only after the statutory waiting period; any later tax-deed auction is a separate property-sale process.',special:'MARKET-LEVEL ONLY unless Citrus County publishes a current tax-certificate parcel list in a form that can be safely and unambiguously ingested. Do not substitute tax-deed auction rows, foreclosure rows, owner-name data, or tax-deed opening/minimum bids for tax-certificate listings.',source:'https://www.citrustc.us/services/tax-certificate-information/'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Citrus County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Citrus County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Citrus County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Citrus County tax-lien market row")
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
    print("Added Florida Citrus County tax-lien market")


if __name__ == "__main__":
    main()
