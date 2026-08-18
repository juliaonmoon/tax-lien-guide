import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "properties.json"
sys.path.insert(0, str(ROOT / "scripts"))
import refresh_florida_tax_deeds as refresher  # noqa: E402


class FloridaTaxDeedDatasetTests(unittest.TestCase):
    """Covers Putnam/Escambia, written by scripts/refresh_florida_tax_deeds.py."""

    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DATA.read_text(encoding="utf-8"))
        cls.florida_rows = [
            r for r in cls.doc["properties"]
            if r["state"] == "FL" and r["county"] in {"Putnam", "Escambia"}
        ]

    def test_every_row_is_an_individual_lands_available_parcel(self):
        self.assertGreater(len(self.florida_rows), 0)
        for row in self.florida_rows:
            self.assertTrue(row.get("parcel_id"))
            self.assertTrue(row.get("case_number"))
            self.assertEqual(row.get("sale_status"), "Lands available")
            self.assertTrue(row.get("official_url"))
            self.assertIn("research_priority", row)

    def test_no_duplicate_parcels(self):
        seen = set()
        for row in self.florida_rows:
            key = (row["county"], row["parcel_id"])
            self.assertNotIn(key, seen, f"duplicate parcel: {key}")
            seen.add(key)


class MergeStateRowsTests(unittest.TestCase):
    """Regression test for merge_state_rows(): a Florida refresh must never
    touch rows belonging to other states (see BUG-001 in BUGS.md for what
    happens when a shared-file collector doesn't respect this)."""

    def test_replaces_only_the_target_state(self):
        existing = [
            {"state": "WA", "county": "King", "parcel_id": "1"},
            {"state": "TX", "county": "Tarrant", "parcel_id": "2"},
            {"state": "FL", "county": "Putnam", "parcel_id": "old"},
        ]
        new_florida_rows = [{"state": "FL", "county": "Putnam", "parcel_id": "new"}]
        merged = refresher.merge_state_rows(existing, new_florida_rows, "FL")
        self.assertEqual(
            {(r["state"], r["parcel_id"]) for r in merged},
            {("WA", "1"), ("TX", "2"), ("FL", "new")},
        )

    def test_empty_new_rows_still_clears_stale_state_rows(self):
        existing = [{"state": "FL", "county": "Putnam", "parcel_id": "stale"}]
        merged = refresher.merge_state_rows(existing, [], "FL")
        self.assertEqual(merged, [])

    def test_other_states_survive_when_target_state_absent(self):
        existing = [{"state": "WA", "county": "King", "parcel_id": "1"}]
        merged = refresher.merge_state_rows(existing, [{"state": "FL", "parcel_id": "new"}], "FL")
        self.assertEqual(len(merged), 2)


class PutnamSnapshotFallbackTests(unittest.TestCase):
    def test_snapshot_file_is_present_and_has_records(self):
        records, verified_at = refresher.putnam_snapshot()
        self.assertGreater(len(records), 0)
        self.assertTrue(verified_at)


if __name__ == "__main__":
    unittest.main()
