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

    def test_florida_rows_never_carry_a_real_owner_name(self):
        for row in self.florida_rows:
            self.assertIsNone(row.get("owner"))


class OwnerNameNeverCollectedTests(unittest.TestCase):
    """Regression test: Putnam's own official "Lands Available" list and the
    FDOR cadastral feed both put a real owner name directly in band with the
    fields this collector wants -- see BUG-005 in BUGS.md. base_row() and the
    Putnam record-unpacking in main() must never let it through, even though
    it's sitting right there in the source data at a fixed position."""

    def test_base_row_never_emits_an_owner(self):
        row = refresher.base_row("Putnam", "case-1", "parcel-1", "legal", "01/01/2026", None, 100.0, "https://example.com")
        self.assertIsNone(row.get("owner"))

    def test_putnam_record_unpacking_skips_the_owner_slot(self):
        # Same shape as a putnam_live()/putnam_snapshot() record: a real
        # owner name sits at index 1, exactly where it appears in
        # data/florida-putnam-verified-snapshot.json.
        record = ["case-1", "REAL PERSON NAME", "parcel-1", "legal", "01/01/2026", "02/01/2026", 100.0]
        row = refresher.base_row("Putnam", record[0], *record[2:], "https://example.com")
        self.assertIsNone(row.get("owner"))
        self.assertNotIn("REAL PERSON NAME", json.dumps(row))

    def test_cadastral_enrich_does_not_set_owner_name_even_if_the_feed_returns_one(self):
        rows = [{"parcel_id": "parcel-1", "county": "Putnam", "owner": None}]

        def fake_fetch(url, params=None, timeout=35):
            return json.dumps({"features": [{"attributes": {
                "PARCEL_ID": "parcel-1", "OWN_NAME": "REAL PERSON NAME", "JV": 1000, "DOR_UC": "0001",
            }}]})

        original_fetch = refresher.fetch
        refresher.fetch = fake_fetch
        try:
            refresher.cadastral_enrich(rows)
        finally:
            refresher.fetch = original_fetch
        self.assertIsNone(rows[0].get("owner"))


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
