import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "refresh_iowa_des_moines_tax_liens.py"
spec = importlib.util.spec_from_file_location("des_moines", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class DesMoinesCollectorTests(unittest.TestCase):
    def word(self, text, x0, top, bottom=None):
        return {"text": text, "x0": float(x0), "top": float(top), "bottom": float(bottom if bottom is not None else top + 8)}

    def test_item_and_amount_from_same_visual_row(self):
        line = [
            self.word("*713", 20, 100),
            self.word("001", 58, 100),
            self.word("-", 82, 100),
            self.word("BURL/BURL", 92, 100),
            self.word("16-05-256-010", 165, 100),
            self.word("3,696.00", 275, 100),
            self.word("OWNER", 350, 100),
        ]
        self.assertEqual(mod._item_token(line), (713, True))
        self.assertEqual(mod._amount_after_parcel(line, line[4]), 3696.00)

    def test_wrapped_district_can_recover_nearest_item(self):
        lines = [
            [self.word("649", 20, 80), self.word("151", 55, 80), self.word("-", 78, 80)],
            [self.word("FRANKLIN/MED/NORTHERN", 90, 90)],
            [self.word("DES", 90, 100), self.word("MOINES", 115, 100), self.word("COUNTY", 155, 100)],
            [self.word("06-18-100-006", 165, 110), self.word("1,467.00", 275, 110)],
        ]
        self.assertEqual(mod._find_preceding_item(lines, 3), (649, False))

    def test_mobile_home_identifier_does_not_match_real_property(self):
        self.assertIsNone(mod.PARCEL_RE.match("150G17665"))
        self.assertIsNone(mod.PARCEL_RE.match("INFLT55A70124AU13"))
        self.assertIsNotNone(mod.PARCEL_RE.match("11-11-327-015"))

    def test_real_property_boundary_ends_before_mobile_home_section(self):
        self.assertEqual(mod.REAL_ESTATE_LAST_ITEM, 723)
        self.assertGreaterEqual(mod.MIN_EXPECTED_REAL_ESTATE_ROWS, 600)


if __name__ == "__main__":
    unittest.main()
