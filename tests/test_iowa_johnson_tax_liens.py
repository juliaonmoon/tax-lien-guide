import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import refresh_iowa_johnson_tax_liens as johnson  # noqa: E402


SAMPLE = """JOHNSON COUNTY DELINQUENT TAX LIST
BGS - BIG GROVE-SOLON
COLTON, DEAN ALAN 0227201001
1) L AND E ESTATES PART TWO
LOT 3 EXC THAT LAND
CONVEYED AS EASEMENT IN BK 3267 PG 449 $3,641.00
DUNN, JOHN E 0216351008
6) AUDITORS PLAT 23
LOT 4 $2,230.00
PUBLIC BIDDER TAX SALE
ICI - IOWA CITY-IOWA CITY
*1910, LLC 1014458004
798) OHL'S SUBDIVISION, RESUBD OF LOT 4
THAT PART OF LOT 4 AS DESC IN BK 2114 PG 289 $616.00
*LIBERTY'S GATE PART ONE LOT OWNERS ASSOCIATION
0611328001
799) LIBERTY'S GATE - PART ONE
OUTLOT A $382.05
MOBILE HOMES
ACEVEDO MIRANDA, ZAID 470339N1478
800) HUNT 1990 Title #52AH00968
Park: WH - WESTERN HILLS Lot C15
WH C15 $202.00
"""


def padded(prefix: str, start: int = 10, stop: int = 710) -> str:
    parts = [prefix]
    for item in range(start, stop):
        parts.append(f"OWNER OMITTED {item:010d}\n{item}) TEST LEGAL DESCRIPTION $10.00")
    parts.append("MOBILE HOMES\nVINOWNER ABC123\n800) MOBILE HOME $100.00")
    return "\n".join(parts)


class JohnsonCountyParserTests(unittest.TestCase):
    def test_parser_emits_only_real_estate_rows(self):
        rows = johnson.parse_real_estate_rows(padded(SAMPLE.split("MOBILE HOMES", 1)[0]), "2026-08-18")
        by_item = {row["sale_item_number"]: row for row in rows}
        self.assertIn("1", by_item)
        self.assertIn("798", by_item)
        self.assertIn("799", by_item)
        self.assertNotIn("800", by_item)
        self.assertEqual(by_item["1"]["parcel_id"], "0227201001")
        self.assertEqual(by_item["1"]["delinquent_tax_amount"], 3641.0)
        self.assertIn("L AND E ESTATES", by_item["1"]["legal_description"])
        self.assertIn("Public bidder tax sale", by_item["798"]["sale_status"])

    def test_concatenated_public_bidder_heading_switches_following_items(self):
        prefix = """OWNER A 0000000001
1) FIRST PARCEL
LOT 1 $100.00PUBLIC BIDDER TAX SALE
OWNER B 0000000798
798) PUBLIC BIDDER PARCEL
OUTLOT A $382.05
"""
        rows = johnson.parse_real_estate_rows(padded(prefix, 2, 702), "2026-08-18")
        by_item = {row["sale_item_number"]: row for row in rows}
        self.assertIn("Regular tax sale", by_item["1"]["sale_status"])
        self.assertIn("Public bidder tax sale", by_item["798"]["sale_status"])

    def test_owner_names_are_never_stored(self):
        synthetic = []
        for item in range(1, 701):
            synthetic.append(f"SECRET OWNER NAME {item:010d}\n{item}) TEST LEGAL $10.00")
        synthetic.append("MOBILE HOMES")
        rows = johnson.parse_real_estate_rows("\n".join(synthetic), "2026-08-18")
        forbidden = {"owner", "owner_name", "taxpayer", "mailing_address"}
        for row in rows:
            self.assertFalse(forbidden.intersection(row))
            self.assertNotIn("SECRET OWNER NAME", str(row))

    def test_publication_amount_is_not_mislabeled_as_opening_bid(self):
        synthetic = []
        for item in range(1, 701):
            synthetic.append(f"OWNER {item:010d}\n{item}) TEST LEGAL $25.00")
        synthetic.append("MOBILE HOMES")
        rows = johnson.parse_real_estate_rows("\n".join(synthetic), "2026-08-18")
        self.assertTrue(all(row["minimum_bid"] is None for row in rows))
        self.assertTrue(all(row["opening_bid"] is None for row in rows))
        self.assertTrue(all(row["delinquent_tax_amount"] == 25.0 for row in rows))


if __name__ == "__main__":
    unittest.main()
