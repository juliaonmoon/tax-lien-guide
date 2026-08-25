import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import refresh_iowa_scott_tax_liens as scott  # noqa: E402


HEADER = (
    "Item Number", "Year", "Type", "District", "Parcel", "Receipt",
    "Name Type 1", "Name 1", "Address Attention 1", "Address Lines 1",
    "Address City State 1", "Zip 1", "Name Type 2", "Name 2",
    "Address Attention 2", "Address Lines 2", "Address City State 2", "Zip 2",
    "Name Type 3", "Name 3", "Address Attention 3", "Address Lines 3",
    "Address City State 3", "Zip 3", "Situs Address", "Net Acres",
    "Legal Description", "Record Type", "Class", "First Half", "Second Half",
    "Interest", "Costs", "First Half Billed", "Second Half Billed",
    "Land Value 1", "Building Value 1", "Dwelling Value 1", "Land Value 2",
    "Building Value 2", "Dwelling Value 2", "Gross Tax", "Net Tax",
    "Date Paid 1 yyyyMMdd", "Date Paid 2 yyyyMMdd", None, "Sale Amount",
)


def _row(item, year, rtype, cls, first, second, interest, costs, sale_amount,
         parcel="A0001-01", situs="123 MAIN ST", legal="LOT 1", acres=0,
         owner="REAL OWNER NAME"):
    values = [None] * len(HEADER)
    values[0] = item
    values[1] = year
    values[2] = rtype
    values[3] = "DAD - DAVENPORT DAVENPORT"
    values[4] = parcel
    values[5] = 1000 + item
    values[7] = owner
    values[24] = situs
    values[25] = acres
    values[26] = legal
    values[27] = "Tax"
    values[28] = cls
    values[29] = first
    values[30] = second
    values[31] = interest
    values[32] = costs
    values[46] = sale_amount
    return tuple(values)


class ScottCountyCollectorTests(unittest.TestCase):
    def test_simple_ct_item_with_no_special_assessment_rows(self):
        rows = [HEADER, _row(100, 2024, "CT", "R", 100, 100, 10, 4, 234.0)]
        result = scott.parse_rows(rows, "2026-08-25", min_expected=1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["record_id"], "IA-Scott-2026-100")
        self.assertEqual(result[0]["delinquent_tax_amount"], 234.0)
        self.assertEqual(result[0]["property_type"], "Real estate")

    def test_ct_item_with_special_assessment_siblings_is_included_in_fee_check(self):
        # component total across CT + 2 SA siblings (1085.5) + $20 fee = 1105.5
        rows = [
            HEADER,
            _row(200, 2024, "CT", "R", 305, 305, 73, 4, 1105.5),
            _row(200, 2024, "SA", "R", 194.5, 0, 32, 5, None),
            _row(200, 2024, "SA", "R", 139, 0, 23, 5, None),
        ]
        result = scott.parse_rows(rows, "2026-08-25", min_expected=1)
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0]["delinquent_tax_amount"], 1105.5)

    def test_mobile_home_item_is_classified_and_included(self):
        rows = [HEADER, _row(300, 2024, "MH", None, 0, 84, 6, 4, 114.0, parcel="INFL455A10829HP13")]
        result = scott.parse_rows(rows, "2026-08-25", min_expected=1)
        self.assertEqual(result[0]["property_type"], "Mobile home")
        self.assertEqual(result[0]["delinquent_tax_amount"], 114.0)

    def test_item_missing_sale_amount_is_excluded_not_guessed(self):
        rows = [HEADER, _row(400, 2011, "DT", "R", 624, 624, 2996, 4, None)]
        with self.assertRaises(RuntimeError):
            scott.parse_rows(rows, "2026-08-25")

    def test_item_failing_fee_invariant_is_excluded_not_trusted_blindly(self):
        # Sale Amount doesn't reconcile to component total + $20 -- must be
        # rejected rather than published on the source's say-so alone.
        rows = [HEADER, _row(500, 2024, "CT", "R", 100, 100, 10, 4, 999999.0)]
        with self.assertRaises(RuntimeError):
            scott.parse_rows(rows, "2026-08-25")

    def test_multi_year_item_with_only_historical_rows_and_no_primary_is_excluded(self):
        # Mirrors the real item 1847 pathology: years of DT/SA history with no
        # CT/MH row at all in one of the years -- must not be published.
        rows = [
            HEADER,
            _row(600, 2011, "DT", "R", 100, 100, 10, 4, None),
            _row(600, 2011, "SA", "R", 50, 0, 5, 5, None),
        ]
        with self.assertRaises(RuntimeError):
            scott.parse_rows(rows, "2026-08-25")

    def test_owner_and_taxpayer_fields_never_appear_in_output(self):
        rows = [HEADER, _row(700, 2024, "CT", "R", 100, 100, 10, 4, 234.0, owner="SOMEONE PRIVATE")]
        result = scott.parse_rows(rows, "2026-08-25", min_expected=1)
        for row in result:
            self.assertNotIn("owner", row)
            self.assertNotIn("taxpayer", row)
            for value in row.values():
                self.assertNotEqual(value, "SOMEONE PRIVATE")

    def test_minimum_row_floor_is_enforced(self):
        rows = [HEADER] + [
            _row(i, 2024, "CT", "R", 10, 10, 1, 4, 45.0, parcel=f"A000{i}-01")
            for i in range(1, 5)
        ]
        with self.assertRaises(RuntimeError):
            scott.parse_rows(rows, "2026-08-25")


if __name__ == "__main__":
    unittest.main()
