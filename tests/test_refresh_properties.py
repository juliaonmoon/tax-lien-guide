import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


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

    def test_tarrant_rows_never_carry_a_real_owner_name(self):
        tarrant_rows = [r for r in self.rows if r["state"] == "TX" and r["county"] == "Tarrant"]
        for row in tarrant_rows:
            self.assertIsNone(row.get("owner"))


class TadEnrichOwnerNameTests(unittest.TestCase):
    """Regression test: the Tarrant Appraisal District results table includes
    a real owner name in its results, but STATUS.md's privacy convention says
    owner names are never collected in bulk. tad_enrich() must not surface it,
    even though it's present in the raw HTML it scrapes."""

    def test_owner_column_is_skipped_even_though_present_in_source_html(self):
        html = """
        <table>
          <tr>
            <td>01234567</td>
            <td>123 MAIN ST</td>
            <td>FORT WORTH</td>
            <td>SMITH JOHN D</td>
            <td>150,000</td>
          </tr>
        </table>
        """

        class FakeResponse:
            text = html

        with patch.object(refresher, "get", return_value=FakeResponse()):
            out, note = refresher.tad_enrich("01234567")

        self.assertNotIn("owner", out)
        self.assertEqual(out.get("address"), "123 MAIN ST, FORT WORTH, TX")
        self.assertEqual(out.get("market_value"), 150000.0)
        self.assertEqual(note, "Enriched from Tarrant Appraisal District")


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
