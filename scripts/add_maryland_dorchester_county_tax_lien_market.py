#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Maryland — Dorchester County"

ROW = r'''{state:'Maryland — Dorchester County',product:'Tax Sale Certificate / property-tax lien',schedule:'Dorchester County\'s official page states that its 2026 annual online Tax Sale began May 18, 2026 at 12:00 PM ET and ended May 19, 2026 at 12:00 PM ET. The 2026 sale is completed; verify the county Treasury page for the next annual sale rather than treating a past list as current inventory.',availability:'MARKET-LEVEL ONLY. Dorchester County conducts an online tax-sale certificate auction for qualifying delinquent property taxes. Do not treat completed-sale results or historical advertising lists as current inventory.',maxReturn:'10%/yr in the latest official Terms of Sale currently linked by the county (2025); verify the next sale terms before bidding',interest:'The latest official Dorchester County Terms of Sale currently linked on the county page (2025) state that interest on qualifying delinquent taxes and fees, advertising and miscellaneous costs paid on the tax-sale date is 10% per year; subsequent taxes paid by the purchaser do not earn interest. Do not assume that rate or all terms are unchanged for a future sale.',bid:'https://dorchestercountymd.com/departments/finance-treasury/tax-sale/',canadian:'County-specific. The latest official terms currently linked by the county require online registration, ACH payment and a W-9 taxpayer-identification form. Do not assume Canadian or other foreign-bidder eligibility; verify current registration, tax-ID and banking requirements directly with Dorchester County.',itin:'Do not assume an ITIN alone satisfies Dorchester County registration. The latest official terms currently linked require a W-9; verify the next sale\'s taxpayer-identification requirements with the Treasury Division.',online:'YES for the completed 2026 sale — the official county page states that the auction ran online May 18–19, 2026. Verify the format of the next sale.',otc:'NO current OTC inventory claimed. Do not infer over-the-counter availability from completed sale results or county-owned-property records.',deed:'A successful bidder purchases a Certificate of Sale / tax-sale lien, not immediate possession or title. Redemption remains possible until the right of redemption is finally foreclosed; any later deed/title transfer requires the separate statutory process and payment of any remaining balance.',special:'MARKET-LEVEL ONLY. Do not bulk republish owner/taxpayer names from sale lists or results, present completed 2026 results as live inventory, fabricate a future sale date or opening/minimum bid, substitute assessment or delinquent-bill amounts for the Collector\'s auction amount, or conflate tax-sale certificates with a later deed/foreclosure proceeding.',source:'https://dorchestercountymd.com/departments/finance-treasury/tax-sale/'}'''


def main():
    text = INDEX.read_text(encoding="utf-8")
    count = text.count(MARKER)
    if count > 1:
        raise SystemExit(f"Refusing to update duplicate Dorchester rows: {count}")

    if count == 1:
        start = text.find("{state:'" + MARKER + "'")
        if start < 0:
            raise SystemExit("Dorchester marker exists outside expected market row")
        end = text.find("\n", start)
        if end < 0:
            raise SystemExit("Could not find end of Dorchester market row")
        old = text[start:end]
        comma = "," if old.rstrip().endswith(",") else ""
        replacement = ROW + comma
        if old == replacement:
            print("Dorchester County Maryland row already current")
            return
        INDEX.write_text(text[:start] + replacement + text[end:], encoding="utf-8")
        print("Updated Dorchester County Maryland tax-lien market")
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
    print("Added Dorchester County Maryland tax-lien market")


if __name__ == "__main__":
    main()
