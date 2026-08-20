import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "source-registry.json"


class SourceRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DATA.read_text(encoding="utf-8"))
        cls.rows = cls.doc["jurisdictions"]

    def test_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_source_registry.py")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_no_duplicate_jurisdictions(self):
        keys = [(row["state"], row["county_or_locality"], row["sale_system"]) for row in self.rows]
        self.assertEqual(len(keys), len(set(keys)))

    def test_property_query_true_rows_have_a_real_collector_file(self):
        live_rows = [row for row in self.rows if row["property_query"]]
        self.assertGreater(len(live_rows), 0)
        for row in live_rows:
            module = row.get("collector_module")
            self.assertTrue(module, row)
            self.assertTrue((ROOT / module).is_file(), f"missing collector module: {module}")

    def test_covers_every_state_touched_by_real_data(self):
        states_with_data = {row["state"] for row in self.rows if row["property_query"]}
        self.assertEqual(states_with_data, {"IN", "AZ", "WA", "TX", "FL", "OK"})

    def test_blocked_rows_document_a_reason(self):
        for row in self.rows:
            if row["collector_status"] == "blocked":
                self.assertTrue(row.get("blocker"))


if __name__ == "__main__":
    unittest.main()
