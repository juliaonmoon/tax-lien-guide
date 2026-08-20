#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Colorado — Morgan County"

ROW = r'''{state:'Colorado — Morgan County',product:'Tax lien certificate',schedule:'Morgan County’s official property-tax calendar confirms an online real-estate tax-lien sale process. The latest calendar currently published on the county site lists the 2025 sale as <span class="schedule-date">Nov 18–20, 2025</span>; a 2026 sale date was not yet published on the official calendar reviewed, so verify the current Treasurer notice before bidding.',availability:'2026 annual-sale date not yet published on the official county calendar reviewed; monitor Morgan County Treasurer for the current notice',maxReturn:'Variable annual statutory rate; 2026 rate pending',interest:'Colorado tax-lien certificate interest is set under state law for the applicable sale year. Morgan County’s currently published calendar does not state a 2026 certificate rate, so no current-year rate is inferred.',bid:'https://morgancounty.colorado.gov/property-tax-calendar',canadian:'The public county calendar does not state foreign-bidder eligibility. Confirm identity, payment, and tax-document requirements directly with the Morgan County Treasurer before funding.',itin:'Not clearly published on the official calendar reviewed; verify current taxpayer-identification requirements with the Treasurer.',online:'Yes — Morgan County’s official calendar describes an online real-estate tax-lien sale with online registration.',otc:'County-held or assignment availability is not clearly stated on the official calendar reviewed; verify directly with the Treasurer rather than assuming inventory.',deed:'A tax-lien certificate is not the same as the county’s separate Public Trustee mortgage-foreclosure process or a later Treasurer’s Deed stage. Do not treat Public Trustee foreclosure listings as tax-lien inventory.',special:'MARKET-LEVEL ONLY until Morgan County publishes a current 2026 sale/list source that can be safely and unambiguously ingested. The project does not substitute Public Trustee foreclosure rows, infer a 2026 interest rate, or fabricate parcel/opening-bid data.',source:'https://morgancounty.colorado.gov/property-tax-calendar'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Colorado Morgan County row already present")
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
    print("Added Colorado Morgan County tax-lien market")


if __name__ == "__main__":
    main()
