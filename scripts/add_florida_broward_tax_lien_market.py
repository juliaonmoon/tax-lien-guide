#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Florida — Broward County"

ROW = r'''{state:'Florida — Broward County',product:'Tax certificate / first-priority tax lien',schedule:'Broward County states that its public tax-certificate auction is conducted on or before June 1 each year. The advertised unpaid-tax list is normally published on or about May 1 and three times during May; verify the current annual auction calendar before bidding.',availability:'Annual tax-certificate market; use only the current advertised list and current county-held certificate availability published through Broward County Tax Collector / its official auction path',maxReturn:'Up to 18%/yr statutory maximum; actual certificate rate is determined by reverse bidding',interest:'Broward County states that bidding begins at 18% and is bid down; the winning certificate earns the accepted bid rate subject to Florida law. Certificates receiving no bids are struck to the County at 18%.',bid:'https://browardtax.org/faqs/tax-certificate-sale/',canadian:'The current county FAQ says anyone may participate, but registration requires the bidder documentation specified by the Tax Collector, including a federal taxpayer identification number or SSN and matching tax documentation. Do not infer that a particular non-U.S. tax identifier is accepted; verify eligibility and documentation with the Tax Collector before funding.',itin:'The current county FAQ requires a Federal Taxpayer Identification number or Social Security number and matching tax documentation. It does not specifically state that an ITIN by itself satisfies registration, so verify current requirements directly with the Tax Collector / official auction platform.',online:'Broward County states that the tax-certificate sale is an Internet auction and directs bidders to register through LienHub; follow the current Tax Collector page to the official auction/payment path.',otc:'Do not assume county-held inventory is available. Certificates receiving no auction bids may be struck to the County, but current availability and transfer/purchase procedures must be verified from the Tax Collector.',deed:'A tax certificate is an investment/first-priority lien and does not convey property ownership. After the applicable statutory holding period, an eligible certificate holder may apply for a tax deed; a later tax-deed auction is a separate property sale.',special:'MARKET-LEVEL ONLY unless Broward County publishes a current tax-certificate parcel list in a form that can be safely and unambiguously ingested. Do not substitute Broward tax-deed auction rows, foreclosure-sale rows, owner-name data, or tax-deed opening/minimum bids for tax-certificate listings.',source:'https://browardtax.org/faqs/tax-certificate-sale/'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Broward County marker but could not locate row start")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos)
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Broward County marker but could not locate row end")
    row_end = min(endings)
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Florida Broward County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Florida Broward County tax-lien market row")
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
    print("Added Florida Broward County tax-lien market")


if __name__ == "__main__":
    main()
