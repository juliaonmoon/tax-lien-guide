#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Adams County"

ROW = r'''{state:'Colorado — Adams County',product:'Tax lien / Tax Lien Sale Certificate of Purchase',schedule:'Adams County’s official Treasurer page now lists 2026 internet tax-lien registration for <span class="schedule-date">October 19–30, 2026</span> and the live tax sale for <span class="schedule-date">October 26–November 6, 2026</span>. The county says its delinquent-tax list is scheduled for newspaper publication September 24, October 1, and October 8, 2026; dates remain subject to change.',availability:'2026 annual internet sale scheduled for October 26–November 6, 2026 — use the county auction site/current official Treasurer page for actual sale inventory and status.',maxReturn:'2026 redemption rate not yet stated on the official county tax-lien page reviewed Aug 28, 2026; do not reuse the 2025 14% rate as a 2026 rate.',interest:'Colorado sets the redemption interest rate for tax-lien certificates under state law. Adams County’s current page does not state a 2026 redemption rate yet. Premium/bonus bids are not returned and do not earn interest; verify the current published rate before bidding.',bid:'https://adamscountyco.gov/our-county/elected-officials/treasurer-public-trustee/treasurer-division/tax-lien-sale/',canadian:'The official Adams County materials reviewed do not clearly establish eligibility for non-U.S. persons. Confirm bidder registration, identity, and tax-document requirements directly with the Treasurer before planning to participate.',itin:'Current official materials reviewed do not state whether an ITIN or foreign tax form is accepted; verify directly with Adams County.',online:'YES — Adams County states its 2026 tax-lien sale is an internet tax sale.',otc:'Adams County publishes County Held Lien and Unredeemed Tax Lien lists. These lists change as liens are redeemed or assigned; do not treat a historical list as proof that a lien remains available.',deed:'A Tax Lien Sale Certificate of Purchase is a lien and does not convey possession, use, improvement, access, or immediate ownership. Adams County describes a separate Treasurer’s Deed process for an eligible unredeemed certificate after the statutory period; do not present a tax-lien purchase as a property purchase.',special:'Keep the annual Treasurer tax-lien sale separate from Public Trustee foreclosure auctions and from the later Treasurer’s Deed process. Market-level only: do not bulk republish owner/taxpayer names or fabricate parcel inventory, opening/minimum bids, amounts due, current lien availability, property characteristics, redemption outcomes, or deed outcomes. Use the current official Treasurer/auction publication for sale-specific facts.',source:'https://adamscountyco.gov/our-county/elected-officials/treasurer-public-trustee/treasurer-division/tax-lien-sale/'}'''


def find_row_bounds(text: str):
    marker_pos = text.find(MARKER)
    if marker_pos < 0:
        return None
    row_start = text.rfind("{state:", 0, marker_pos + 1)
    if row_start < 0:
        raise SystemExit("Found Adams County marker but could not locate row start")
    row_end = text.find("}\n", marker_pos)
    if row_end < 0:
        row_end = text.find("},\n", marker_pos)
        if row_end < 0:
            raise SystemExit("Found Adams County marker but could not locate row end")
    return row_start, row_end + 1


def main():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == ROW:
            print("Colorado Adams County row already canonical")
            return
        INDEX.write_text(text[:start] + ROW + text[end:], encoding="utf-8")
        print("Restored canonical Colorado Adams County tax-lien market row")
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
    print("Added Colorado Adams County tax-lien market")


if __name__ == "__main__":
    main()
