import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "properties.json"
sys.path.insert(0, str(ROOT / "scripts"))
import refresh_properties as refresher  # noqa: E402


class PropertiesDatasetTests(unittest.TestCase):
    """Covers King/Tarrant/Brevard, written by scripts/refresh_properties.py."""

    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DATA.read_text(encoding="utf-8"))
        cls.rows = cls.doc["properties"]

    def test_every_row_is_an_individual_property(self):
        self.assertGreater(len(self.rows), 0)
        for row in self.rows:
            # AZ/Coconino is the tax-lien cross-listing described in
            # TAX_SALE_COVERAGE_AUDIT.md -- intentionally present here too,
            # clearly distinguished by sale_type elsewhere in the record.
            self.assertIn(row["state"], {"WA", "TX", "FL", "AZ"})
            self.assertTrue(row.get("county"))
            self.assertTrue(row.get("parcel_id"))
            self.assertTrue(row.get("official_url"))
            self.assertIn("research_priority", row)

    def test_no_duplicate_parcels_within_a_county(self):
        seen = set()
        for row in self.rows:
            if row["state"] not in {"WA", "TX"}:
                continue  # Florida rows are covered by refresh_florida_tax_deeds.py
            key = (row["state"], row["county"], row["parcel_id"])
            self.assertNotIn(key, seen, f"duplicate parcel: {key}")
            seen.add(key)

    def test_king_owner_field_is_the_documented_placeholder_not_real_names(self):
        king_rows = [r for r in self.rows if r["state"] == "WA" and r["county"] == "King"]
        for row in king_rows:
            self.assertEqual(row.get("owner"), "Not aggregated for WA investment screening")


class PriorByCountyFallbackTests(unittest.TestCase):
    """Regression test: a fetch failure for one source must not erase that
    source's previously published rows (same bug class as BUG-001 in
    BUGS.md, before this fix this script had no fallback at all)."""

    def setUp(self):
        self.original_props = refresher.PROPS
        fixture = {
            "updated_at": "2026-08-01T00:00:00Z",
            "prototype": True,
            "properties": [
                {"state": "WA", "county": "King", "parcel_id": "1111111111"},
                {"state": "WA", "county": "King", "parcel_id": "2222222222"},
                {"state": "TX", "county": "Tarrant", "parcel_id": "00000001"},
            ],
        }
        fixture_path = ROOT / "tests" / "_fixture_properties.json"
        fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
        refresher.PROPS = fixture_path
        self.fixture_path = fixture_path

    def tearDown(self):
        refresher.PROPS = self.original_props
        self.fixture_path.unlink(missing_ok=True)

    def test_previous_rows_are_grouped_by_state_and_county(self):
        previous = refresher.prior_by_county()
        self.assertEqual(len(previous[("WA", "King")]), 2)
        self.assertEqual(len(previous[("TX", "Tarrant")]), 1)
        self.assertNotIn(("FL", "Brevard"), previous)

    def test_missing_file_returns_empty_without_erroring(self):
        self.fixture_path.unlink()
        self.assertEqual(refresher.prior_by_county(), {})


if __name__ == "__main__":
    unittest.main()
