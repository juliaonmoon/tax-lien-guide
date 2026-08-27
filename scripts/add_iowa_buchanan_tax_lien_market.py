#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Iowa — Buchanan County"

ROW = r'''{state:'Iowa — Buchanan County',product:'Tax Sale Certificate of Purchase / property-tax lien',schedule:'2026 annual online tax sale was Monday, June 15, 2026. Buchanan County Treasurer administers the sale under Iowa tax-sale law; verify any current adjourned or county-held availability directly with the Treasurer.',availability:'2026 annual sale completed June 15 — verify current adjourned/county-held certificate availability directly with Buchanan County Treasurer',maxReturn:'2%/month redemption interest',interest:'Iowa tax-sale redemptions accrue 2% interest per month. This is certificate/redemption interest, not ownership of the underlying property.',bid:'https://buchanancountyiowa.org/tax-sales/',canadian:'County-specific. Confirm current registration, taxpayer-ID/tax-form, residency, payment, and bidder eligibility directly with Buchanan County before attempting to bid.',itin:'Do not assume an ITIN alone satisfies bidder eligibility. Verify current W-9/taxpayer-ID and bidder requirements directly with Buchanan County Treasurer.',online:'YES — Buchanan County identifies the annual tax sale as online and directs bidders to the county-designated Iowa tax-auction platform.',otc:'County-specific. Verify current adjourned or county-held certificate availability directly with the Treasurer; do not infer current inventory from an older delinquent-tax list.',deed:'A tax-sale certificate is a lien interest and does not itself convey title. Any later tax deed requires the separate Iowa statutory notice/redemption process.',special:'MARKET-LEVEL ONLY. Buchanan County officially confirms its June 15, 2026 online Treasurer tax sale and publishes tax-sale rules, but no unrestricted machine-readable current parcel feed was verified for safe republication. Do not bulk republish owner/taxpayer names, fabricate parcel inventory or opening bids, treat delinquent-tax amounts as opening bids, bypass bidder-registration controls, or substitute Sheriff mortgage-foreclosure sales for Treasurer tax-sale certificates.',source:'https://buchanancountyiowa.org/tax-sales/'}'''


def row_end(text: str, start: int) -> int:
    candidates = []
    for token in ("},\n", "}\n];"):
        pos = text.find(token, start)
        if pos >= 0:
            candidates.append(pos)
    if not candidates:
        raise SystemExit("Could not find end of Buchanan County market row")
    return min(candidates)


def main():
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start >= 0:
        end = row_end(text, start)
        current = text[start:end + 1]
        if current == ROW:
            print("Buchanan County Iowa canonical row already present")
            return
        INDEX.write_text(text[:start] + ROW + text[end + 1:], encoding="utf-8")
        print("Restored canonical Buchanan County Iowa tax-lien market row")
        return

    rows_start = text.find("const rows=[")
    if rows_start < 0:
        raise SystemExit("Could not find rows array")
    rows_end = text.find("\n];", rows_start)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")

    before = text[:rows_end]
    after = text[rows_end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Buchanan County Iowa tax-lien market")


if __name__ == "__main__":
    main()
