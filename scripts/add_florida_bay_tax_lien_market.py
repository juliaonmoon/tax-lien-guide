#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Bay County"

ROW = r'''{state:'Florida — Bay County',product:'Tax certificate / first-priority tax lien',schedule:'Bay County conducts its electronic tax-certificate sale on or before June 1 each year. For the 2026 cycle, the Tax Collector announced the sale for June 1, 2026.',availability:'2026 annual certificate sale passed; verify current county-held/unredeemed certificate availability with the Tax Collector',maxReturn:'Up to 18%/yr statutory maximum; reverse auction bids the rate down',interest:'Bay County explains that bidders compete by accepting the lowest interest rate. Interest is simple interest from June 1 until redemption; Florida law caps the certificate rate at 18% annually. A statutory minimum return may apply on redemption except for 0% bids; verify certificate-specific treatment before bidding.',bid:'https://baycountyfltax.gov/property-taxes/delinquent-property-taxes/',canadian:'The county page does not clearly publish foreign-bidder eligibility. Verify registration, payment, withholding, and U.S. taxpayer-document requirements before funding.',itin:'Taxpayer-identification requirements are not clearly published for foreign bidders on the county information page; verify with Bay County Tax Collector before registration.',online:'Yes — Bay County states the annual tax-certificate sale is conducted electronically on the internet.',otc:'County-held/unredeemed certificate availability is county-specific; verify current inventory and purchase procedures with the Tax Collector rather than inferring availability.',deed:'A tax certificate is a lien, not ownership. After the statutory period, an eligible certificate holder may apply for tax deed; the Clerk then conducts a separate property auction if the taxes remain unpaid.',special:'MARKET-LEVEL ONLY until Bay County publishes a current tax-certificate parcel list in a form that can be safely and unambiguously ingested. Do not substitute Bay County Clerk tax-deed auction rows, sheriff/mortgage foreclosures, owner-name data, or tax-deed opening bids for tax-certificate listings.',source:'https://baycountyfltax.gov/property-taxes/delinquent-property-taxes/'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Bay County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Bay County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Bay County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Bay County tax-lien market row")
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
    print("Added Florida Bay County tax-lien market")


if __name__ == "__main__":
    main()
