#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Cochise County"

ROW = r'''{state:'Arizona — Cochise County',product:'Tax lien / Certificate of Purchase',schedule:'Arizona law requires county tax-lien sales to be held in February. Cochise County states that its exact annual tax-lien sale date is posted on the Treasurer page before February; do not invent a future date when the current notice is not posted.',availability:'Cochise County publishes an Available Tax Liens map/list that the Treasurer says is updated nightly. Treat availability as live and parcel-specific; verify the Treasurer list immediately before attempting a purchase.',maxReturn:'16%/yr statutory ceiling',interest:'Arizona tax liens are awarded to the purchaser who pays the full delinquent amount and accepts the lowest interest rate, subject to the statutory ceiling. Actual certificate rates may therefore be below 16%.',bid:'https://www.cochise.az.gov/439/Treasurer',canadian:'No simple foreign-bidder eligibility rule is stated on the official Cochise sources used for this row. Confirm bidder registration, taxpayer-identification, payment, and participation requirements directly with the Treasurer before participating.',itin:'The official sources reviewed do not state a simple ITIN/SSN rule. Confirm acceptable taxpayer-identification documentation directly with the Treasurer.',online:'Annual sale platform: Cochise Treasurer Parcel Inquiry states the county uses RealAuction for its annual tax sale. Separately, the current Treasurer page says available/back-tax liens cannot be purchased online and funds must be sent or mailed to the Treasurer. Do not conflate the annual auction with ongoing available-lien purchases.',otc:'Ongoing available liens are officially published and the Treasurer Parcel Inquiry describes an ongoing CP sale during the year. Use the county’s current Available Tax Liens list and Treasurer instructions; do not treat a stale snapshot as guaranteed inventory.',deed:'This is a sale/assignment of a real-property tax lien evidenced by a Certificate of Purchase, not an immediate sale of the property. Cochise County states that a certificate holder must pursue judicial foreclosure for issuance of a Treasurer deed.',special:'Market-level summary only. Cochise County says its Available Tax Liens map/list is updated nightly and directs buyers to Treasurer Parcel Inquiry for parcel research. Do not bulk aggregate owner/taxpayer names. Do not fabricate parcel availability, purchase amounts, opening/minimum bids, interest rates, or ownership outcomes. Verify each parcel and current instructions directly with the Treasurer before acting.',source:'https://www.cochise.az.gov/439/Treasurer'}'''


def rows_array_bounds(text: str):
    rows_start = text.find("const rows=[")
    if rows_start < 0:
        raise SystemExit("Could not find rows array")
    rows_end = text.find("\n];", rows_start)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")
    return rows_start, rows_end


def find_row_bounds(text: str):
    rows_start, rows_end = rows_array_bounds(text)
    marker_pos = text.find(MARKER, rows_start, rows_end)
    if marker_pos < 0:
        return None

    row_start = text.rfind("{state:", rows_start, marker_pos + 1)
    if row_start < rows_start:
        raise SystemExit("Found Cochise County marker but could not locate row start inside rows array")

    endings = []
    for token in ("},\n", "}\n,", "}\n];"):
        pos = text.find(token, marker_pos, rows_end + len("\n];"))
        if pos >= 0:
            endings.append(pos)
    if not endings:
        raise SystemExit("Found Cochise County marker but could not locate row end inside rows array")

    row_end = min(endings)
    if row_end >= rows_end + len("\n];"):
        raise SystemExit("Refusing Cochise County repair outside rows array")
    return row_start, row_end + 1


def add_cochise():
    text = INDEX.read_text(encoding="utf-8")
    bounds = find_row_bounds(text)
    if bounds:
        row_start, row_end = bounds
        existing = text[row_start:row_end]
        if existing == ROW:
            print("Arizona Cochise County canonical row already present")
            return
        INDEX.write_text(text[:row_start] + ROW + text[row_end:], encoding="utf-8")
        print("Restored canonical Arizona Cochise County tax-lien market row")
        return

    _, end = rows_array_bounds(text)
    before, after = text[:end], text[end:]
    insertion = "\n" + ROW if before.rstrip().endswith(',') else ",\n" + ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")
    print("Added Arizona Cochise County tax-lien market")


def main():
    add_cochise()


if __name__ == "__main__":
    main()
