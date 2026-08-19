import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import refresh_iowa_warren_tax_liens as warren


class WarrenCountyTaxLienTests(unittest.TestCase):
    def test_parser_keeps_real_estate_and_discards_names(self):
        original_count = warren.REAL_ESTATE_ITEM_COUNT
        try:
            warren.REAL_ESTATE_ITEM_COUNT = 3
            lines = [
                "01151 - ALLEN TWP/CARLISLE SCH/CARLISLE FIRE/001",
                "GABRIELE, JOHN J III/NICHOEL A 01000060222",
                "1) 6-77-23",
                "W 400' N 250.80'",
                "NE NE........................................................$6,287.00",
                "KILLEN, PERRY III/TINA 01000070842",
                "2) 7-77-23",
                "E 264' N 930' & SE 6.78A NW SE.......................$1,978.00",
                "48300 - INDIANOLA CITY/INDIANOLA SCH/023",
                "*FFE OF INDIANOLA LLC 48670000015",
                "3) 25-76-24",
                "OL SOUTH IND W 4' S 1/2 OL 1 EX S 95'................$20.00",
                "MOBILE HOME OWNER 06L11563",
                "4) 91AC52373 1978 LIBERTY",
                "WH.............................................................$144.00",
            ]
            rows = warren.parse_real_estate_rows(lines, "2026-08-19")
        finally:
            warren.REAL_ESTATE_ITEM_COUNT = original_count

        self.assertEqual([row["sale_item_number"] for row in rows], ["1", "2", "3"])
        self.assertEqual(rows[0]["parcel_id"], "01000060222")
        self.assertEqual(rows[0]["delinquent_tax_amount"], 6287.00)
        self.assertIsNone(rows[0]["opening_bid"])
        self.assertIsNone(rows[0]["minimum_bid"])
        self.assertIn("Public bidder", rows[2]["sale_status"])
        for row in rows:
            self.assertFalse(any("owner" in key.lower() or "taxpayer" in key.lower() for key in row))
            self.assertEqual(row["sale_type"], "tax_lien")
            self.assertIn("2% per month", row["maximum_statutory_return"])

    def test_incomplete_real_estate_section_fails_closed(self):
        original_count = warren.REAL_ESTATE_ITEM_COUNT
        try:
            warren.REAL_ESTATE_ITEM_COUNT = 2
            lines = [
                "NAME 01000060222",
                "1) 6-77-23",
                "NE NE........................................................$10.00",
            ]
            with self.assertRaises(RuntimeError):
                warren.parse_real_estate_rows(lines, "2026-08-19")
        finally:
            warren.REAL_ESTATE_ITEM_COUNT = original_count


if __name__ == "__main__":
    unittest.main()
