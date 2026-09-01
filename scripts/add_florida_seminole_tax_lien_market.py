#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
SEMINOLE_MARKER = "Florida — Seminole County"
OSCEOLA_MARKER = "Florida — Osceola County"

SEMINOLE_ROW = r'''{state:'Florida — Seminole County',product:'Tax certificate / first lien',schedule:'Seminole County states its 2026 online tax-certificate sale took place June 1, 2026. Delinquent real-estate taxes are advertised before the sale and the auction is hosted through LienHub.',availability:'2026 annual sale passed — monitor the official Tax Collector / LienHub pages for current certificate information and future sale notices',maxReturn:'18%/yr statutory max',interest:'Competitive reverse bidding starts at 18% and decreases. The winning bidder pays the delinquent taxes and receives a tax certificate creating a first lien on the parcel; the actual certificate rate may be lower than 18%.',bid:'https://seminolecounty.tax/services/property-taxes/delinquent-taxes/',canadian:'Seminole County requires bidder registration through LienHub. Foreign-bidder eligibility and acceptable taxpayer-identification/banking documentation are not stated as a simple county rule; confirm current requirements with the Tax Collector before participating.',itin:'Verify current taxpayer-identification requirements with the Tax Collector / auction platform before registering; do not assume an ITIN alone guarantees eligibility.',online:'YES — Seminole County states the 2026 tax-certificate sale is hosted online through LienHub.',otc:'County-held certificates can exist under Florida law, including certificates automatically struck to the county in specified cases. Use the current official county/LienHub records rather than assuming inventory is available.',deed:'A tax certificate is a first lien, not ownership. If eligible and still unpaid after the statutory waiting period, a certificate holder may apply for a separate tax-deed process; any later property auction is distinct from the original lien sale.',special:'Seminole County states certificates are auctioned individually by parcel. Low-value homestead parcels and properties in litigation may be automatically struck to the county and not offered to bidders at the annual sale.',source:'https://seminolecounty.tax/services/property-taxes/delinquent-taxes/'}'''

OSCEOLA_ROW = r'''{state:'Florida — Osceola County',product:'Tax certificate / first-priority lien',schedule:'Osceola County states that its public online tax-certificate sale is held on or before June 1 each year for unpaid real-estate taxes. The current official information page does not state a separate exact 2026 sale date, so the guide does not invent one.',availability:'2026 annual sale passed — county-held certificates may be available; verify current inventory on the official Tax Collector site',maxReturn:'18%/yr statutory max',interest:'Competitive reverse bidding begins at 18% and the certificate is awarded to the bidder accepting the lowest annual interest rate. Certificates bid at 0% earn no interest.',bid:'https://osceolataxcollector.org/tax-certificate-information/',canadian:'The official county page explains the sale mechanics but does not publish a simple foreign-bidder eligibility rule. Confirm current registration, payment and tax-document requirements with the Tax Collector / LienHub before participating.',itin:'The county notes that certificate interest is taxable and reports interest on IRS Form 1099-INT. Verify current taxpayer-identification requirements directly with the Tax Collector / auction platform before registering.',online:'YES — Osceola County states tax certificates are sold through LienHub.',otc:'YES — Osceola County publishes county-held certificates for purchase. The official page states the purchase price is face value plus 1.5% interest per month from June 1 of the certificate year plus the purchase fee; the assigned certificate then bears 18% annual interest.',deed:'A tax certificate is a first-priority lien and does not convey title. If it remains unredeemed after the statutory waiting period, the certificate holder may apply for a separate tax-deed process; the Clerk conducts the later property auction.',special:'Osceola explicitly warns that buying a certificate does not permit entry onto the property or owner harassment/contact. Florida law restricts certificate-holder contact intended to encourage or demand payment during the statutory period.',source:'https://osceolataxcollector.org/tax-certificate-information/'}'''


def find_rows_bounds(text: str):
    rows_start = text.find("const rows=[")
    if rows_start < 0:
        raise SystemExit("Could not find rows array")
    rows_end = text.find("\n];", rows_start)
    if rows_end < 0:
        raise SystemExit("Could not find end of rows array")
    return rows_start, rows_end


def find_row_bounds(text: str, marker: str, label: str):
    rows_start, rows_end = find_rows_bounds(text)
    marker_pos = text.find(marker, rows_start, rows_end)
    if marker_pos < 0:
        return None

    row_start = text.rfind("{state:", rows_start, marker_pos + 1)
    if row_start < rows_start:
        raise SystemExit(f"Found {label} marker but could not locate row start")

    candidates = [
        pos for pos in (
            text.find("},\n", marker_pos, rows_end),
            text.find("}\n", marker_pos, rows_end),
        ) if pos >= 0
    ]
    if candidates:
        row_end = min(candidates) + 1
    elif text.startswith("}", rows_end - 1):
        row_end = rows_end
    else:
        raise SystemExit(f"Found {label} marker but could not locate row end")

    if not (rows_start <= row_start < row_end <= rows_end):
        raise SystemExit(f"{label} row repair escaped rows array")
    return row_start, row_end


def ensure_row(text: str, marker: str, row: str, label: str):
    bounds = find_row_bounds(text, marker, label)
    if bounds:
        start, end = bounds
        existing = text[start:end]
        if existing == row:
            return text, False, "canonical"
        return text[:start] + row + text[end:], True, "restored"

    _, rows_end = find_rows_bounds(text)
    before, after = text[:rows_end], text[rows_end:]
    insertion = "\n" + row if before.rstrip().endswith(',') else ",\n" + row
    return before + insertion + after, True, "added"


def main():
    text = INDEX.read_text(encoding="utf-8")
    text, changed_seminole, seminole_action = ensure_row(
        text, SEMINOLE_MARKER, SEMINOLE_ROW, "Florida Seminole County"
    )
    text, changed_osceola, osceola_action = ensure_row(
        text, OSCEOLA_MARKER, OSCEOLA_ROW, "Florida Osceola County"
    )

    if not changed_seminole and not changed_osceola:
        print("Florida Seminole and Osceola County rows already canonical")
        return

    INDEX.write_text(text, encoding="utf-8")
    if changed_seminole:
        print(f"{seminole_action.title()} Florida Seminole County tax-lien market row")
    if changed_osceola:
        print(f"{osceola_action.title()} Florida Osceola County tax-lien market row")


if __name__ == "__main__":
    main()
