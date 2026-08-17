#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Larimer County"

ROW = r'''{state:'Colorado — Larimer County',product:'Tax lien / Tax Lien Sale Certificate',schedule:'Larimer County’s 2026 annual tax-lien sale is scheduled for <span class="schedule-date">Nov 19, 2026</span> at the Larimer County Fairgrounds. The county says an advertised-property Excel list will be posted beginning the first week of October and updated nightly through the sale.',availability:'Upcoming — Nov 19, 2026',maxReturn:'2026 rate set Sep 1; 2025 was 14%/yr',interest:'Colorado sets the investor interest rate each September 1. Larimer states the 2025 rate was 14% and the 2026 rate will be set September 1, 2026. Premium bids do not earn interest and are not refunded on redemption.',bid:'https://www.larimer.gov/treasurer/thirdparty/liens/sale',canadian:'Larimer requires tax-lien investors to complete IRS Form W-9 and be at least 18. The official instructions reviewed do not establish eligibility for non-U.S. persons; confirm directly with the Treasurer before planning to participate.',itin:'Official registration instructions require a completed W-9. The county does not state that an ITIN or foreign tax form is accepted as a substitute; verify with the Treasurer.',online:'NO — Larimer’s 2026 sale is scheduled as an in-person sale at the county fairgrounds.',otc:'Assignments of existing liens are processed beginning in January after the tax-lien sale; this is a certificate transfer process, not a county-held OTC inventory promise.',deed:'Buying the tax lien does not buy the property. After the statutory period, an eligible certificate holder may apply for the separate Treasurer’s Deed process; Colorado’s current process uses a public auction rather than automatically issuing the property to the lienholder.',special:'This row is the annual tax-lien sale, not the later Treasurer’s Deed auction. Larimer requires bidders to be at least 18 and to provide a W-9. The 2026 statutory interest rate is not yet published, so the guide does not reuse 2025’s 14% as the 2026 return.',source:'https://www.larimer.gov/treasurer/thirdparty/liens/sale'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Larimer County row already present")
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
    print("Added Colorado Larimer County tax-lien market")


if __name__ == "__main__":
    main()
