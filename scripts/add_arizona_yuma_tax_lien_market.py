#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Arizona — Yuma County"

ROW = r'''{state:'Arizona — Yuma County',product:'Tax lien / Certificate of Purchase',schedule:'Yuma County held its 2026 tax-lien auction in person on February 17, 2026 for delinquent 2024 real-property taxes. The Treasurer publishes the annual date, bidder forms, and tax-sale booklet on its official tax-lien page.',availability:'2026 annual sale passed — monitor Treasurer for current over-the-counter availability and the next February sale',maxReturn:'16%/yr statutory max',interest:'Arizona tax-lien certificates are subject to the state statutory ceiling of 16% simple annual interest; the actual certificate rate depends on the winning bid and may be lower.',bid:'https://www.yumacountyaz.gov/government/treasurer/tax-lien-information',canadian:'Yuma County\'s 2026 bidder materials require a W-9 and bidder form for the annual sale. That points to U.S.-taxpayer documentation for this sale; foreign bidders should obtain written confirmation from the Treasurer before assuming eligibility.',itin:'The public 2026 sale page specifically provides a W-9 rather than foreign-taxpayer instructions. Do not assume an ITIN/W-8 substitute is accepted without Treasurer confirmation.',online:'NO for the 2026 annual sale — Yuma County states in-person registration and an in-person auction at the Board of Supervisors Auditorium.',otc:'The county calendar explicitly references over-the-counter purchases by tax-lien investors and states it stopped accepting 2023 OTC purchases on February 2, 2026. Current inventory/eligibility is time-sensitive and must be confirmed with the Treasurer.',deed:'A tax-lien certificate is not immediate property ownership. Yuma County separately administers state tax-deeded property sales through the Board of Supervisors, and the county explicitly states that those deed sales are not the Treasurer\'s February tax-lien sale.',special:'Keep the February Treasurer tax-lien auction separate from Yuma County state tax-deeded property auctions. The county warns that tax-sale information may change and directs bidders to confirm the most recent information with the Treasurer.',source:'https://www.yumacountyaz.gov/government/treasurer/tax-lien-information'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Arizona Yuma County row already present")
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
    print("Added Arizona Yuma County tax-lien market")


if __name__ == "__main__":
    main()
