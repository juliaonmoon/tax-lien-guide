#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Lake County"

ROW = r'''{state:'Florida — Lake County',product:'Tax certificate / property-tax lien',schedule:'Annual tax-certificate sale for delinquent real-property taxes. Florida law generally requires the tax collector to begin the sale on or before June 1 (or the later statutory deadline); verify Lake County\'s current sale notice and registration details with the Lake County Tax Collector.',availability:'2026 annual certificate sale passed; verify current county-held certificate availability with the Lake County Tax Collector',maxReturn:'18%/yr statutory max',interest:'Florida tax certificates carry a statutory maximum of 18% per year. Florida law permits electronic certificate sales and awards certificates under the state\'s tax-certificate bidding rules; verify Lake County\'s current auction terms before bidding.',bid:'https://floridarevenue.com/property/Pages/HOME.aspx',canadian:'No Lake County-specific foreign-bidder rule was verified from the official public pages reviewed. Confirm current taxpayer-identification, withholding, payment and registration requirements with the Lake County Tax Collector before funding.',itin:'Verify current taxpayer-identification and withholding requirements with the Lake County Tax Collector; do not assume an ITIN alone guarantees eligibility.',online:'County-specific. Florida DOR publishes the current county tax-certificate-sale information; verify Lake County\'s current auction method with the Tax Collector.',otc:'County-held certificate availability is county-specific; verify current Lake County inventory directly with the Tax Collector.',deed:'A tax certificate is a lien, not ownership. Lake County Clerk states that tax certificates are sold annually by the Tax Collector; only after at least two years, and upon a qualifying certificateholder application, can a separate tax-deed sale be conducted by the Clerk.',special:'Do not confuse Lake County tax certificates with tax-deed property auctions. The Tax Collector sells the lien certificate; the Clerk separately conducts tax-deed sales after the statutory process. Do not substitute tax-deed inventory or deed-sale opening bids for tax-certificate data.',source:'https://www.lakecountyclerkfl.gov/departments/records-administrative-services/official-records/tax-deeds/'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Lake County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Lake County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Lake County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Lake County tax-lien market row")
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
    print("Added Florida Lake County tax-lien market")


if __name__ == "__main__":
    main()
