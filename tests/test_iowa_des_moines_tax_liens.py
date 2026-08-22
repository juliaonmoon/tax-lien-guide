import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "refresh_iowa_des_moines_tax_liens.py"
spec = importlib.util.spec_from_file_location("des_moines", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class DesMoinesCollectorTests(unittest.TestCase):
    def test_money_parser_accepts_county_published_amount(self):
        self.assertEqual(mod._money_value("3,696.00"), 3696.00)
        self.assertEqual(mod._money_value("$1,467.00"), 1467.00)
        self.assertIsNone(mod._money_value("OWNER"))

    def test_text_row_parser_shape_matches_real_property_row(self):
        line = "*713 BURL/BURL 16-05-256-010 3,696.00"
        match = mod.TEXT_ROW_RE.match(line)
        self.assertIsNotNone(match)
        item_token, parcel_id, amount_token = match.groups()
        self.assertEqual(item_token, "*713")
        self.assertEqual(parcel_id, "16-05-256-010")
        self.assertEqual(mod._money_value(amount_token), 3696.00)

    def test_mobile_home_identifier_does_not_match_real_property(self):
        self.assertIsNone(mod.PARCEL_RE.match("150G17665"))
        self.assertIsNone(mod.PARCEL_RE.match("INFLT55A70124AU13"))
        self.assertIsNotNone(mod.PARCEL_RE.match("11-11-327-015"))

    def test_real_property_boundary_and_corroborated_floor(self):
        self.assertEqual(mod.REAL_ESTATE_LAST_ITEM, 723)
        self.assertEqual(mod.MIN_EXPECTED_REAL_ESTATE_ROWS, 597)


if __name__ == "__main__":
    unittest.main()
