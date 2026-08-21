#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Lewis and Clark County"

ROW = r'''{state:'Montana — Lewis and Clark County',product:'Tax lien assignment / assignment certificate',schedule:'MARKET-LEVEL ONLY — Lewis and Clark County documents the delinquent-tax lien assignment process, but a current 2026 bulk lien inventory that is clearly appropriate for automated republication was not verified. The Treasurer pauses tax-sale assignment business during November and May.',availability:'County-held real-property tax liens may be assigned under Montana law; current inventory and timing must be verified directly with the Lewis and Clark County Treasurer',maxReturn:'10%/yr statutory delinquent-tax interest',interest:'Lewis and Clark County states delinquent property taxes incur a 2% penalty plus interest at 5/6 of 1% per month (10% annualized). Interested purchasers should review Montana tax-lien assignment law before buying an assignment.',bid:'https://www.lccountymt.gov/Government/Clerk-and-Recorder-Treasurer/Tax-Information',canadian:'Current foreign-bidder eligibility is not clearly established in the public county guidance; verify identity, payment, notice, and tax-document requirements directly with the Treasurer before attempting an assignment.',itin:'The accessible county guidance does not establish a specific U.S. taxpayer-ID rule for foreign assignees; verify directly with the Treasurer.',online:'No verified online reverse auction. Lewis and Clark County describes tax-sale assignments handled through the Treasurer under Montana statutory procedures.',otc:'YES — county-held tax liens may be assigned to interested purchasers under the Treasurer\'s statutory assignment process; current availability changes as taxpayers redeem.',deed:'A tax-lien assignment certificate is not immediate property ownership. Lewis and Clark County separately issues tax deeds after the later statutory process.',special:'MARKET-LEVEL ONLY. Do not bulk republish owner names from tax-record or pending-assignment materials, infer a 2026 parcel inventory from older notices, or treat delinquent tax balances as opening bids. Tax-lien assignments and tax deeds are separate stages.',source:'https://www.lccountymt.gov/Government/Clerk-and-Recorder-Treasurer/Tax-Information'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        print("Montana Lewis and Clark County row already present")
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
    print("Added Montana Lewis and Clark County tax-lien market")


if __name__ == "__main__":
    main()
