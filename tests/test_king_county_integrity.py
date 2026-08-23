import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAPS = ROOT / "data" / "king-gaps.json"
STATUS = ROOT / "data" / "refresh-status.json"
REFRESH_SCRIPT = ROOT / "scripts" / "refresh_properties.py"


class KingCountyIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(GAPS.read_text(encoding="utf-8"))
        cls.status = json.loads(STATUS.read_text(encoding="utf-8"))
        cls.refresh_script = REFRESH_SCRIPT.read_text(encoding="utf-8")

    def test_foreclosure_slice_did_not_collapse(self):
        # The current official King County foreclosure slice is 145 parcels.
        # Keep this threshold deliberately below the exact count so a legitimate
        # source update can change the list without hiding a catastrophic wipeout.
        self.assertGreaterEqual(self.doc.get("king_count", 0), 100)

    def test_no_regression_in_completed_core_enrichment(self):
        # These are the only currently proven/core source limitations. If fields
        # such as coordinates, city/ZIP, assessed value, property type, tax status,
        # or Neighborhood Value reappear here, fail publication rather than ship a
        # collapsed WA dataset.
        allowed_missing = {"address", "legal_description", "opening_bid"}
        actual_missing = set(self.doc.get("missing_counts", {}))
        unexpected = actual_missing - allowed_missing
        self.assertEqual(unexpected, set(), f"unexpected King County gaps: {sorted(unexpected)}")

    def test_public_safety_coverage_remains_complete(self):
        coverage = self.doc.get("optional_metric_coverage", {}).get("public_safety", {})
        self.assertEqual(coverage.get("missing"), 0)
        self.assertEqual(coverage.get("filled"), self.doc.get("king_count"))

    def test_unassigned_situs_addresses_are_explicitly_classified(self):
        missing_address = self.doc.get("missing_counts", {}).get("address", 0)
        classified = sum(self.doc.get("missing_address_status_counts", {}).values())
        self.assertEqual(classified, missing_address)

    def test_opening_bids_are_not_inferred_before_official_publication(self):
        limitation = self.doc.get("source_limitations", {}).get("opening_bid", {})
        if self.doc.get("missing_counts", {}).get("opening_bid", 0):
            self.assertEqual(limitation.get("status"), "awaiting_official_publication")
            self.assertIn("kingcounty", limitation.get("source", "").lower())

    def test_opening_bid_provenance_does_not_reintroduce_stale_august_promise(self):
        stale = "mid-to-late August"
        self.assertNotIn(stale, self.refresh_script)
        status_notes = " ".join(self.status.get("notes", []))
        self.assertNotIn(stale, status_notes)

        # The canonical collector language must remain fail-closed: no estimates
        # and no substitution of the separate Sheriff judicial-foreclosure bids.
        self.assertIn("not currently published", self.refresh_script)
        self.assertIn("do not estimate", self.refresh_script)
        self.assertIn("Sheriff judicial-foreclosure opening bids", self.refresh_script)


if __name__ == "__main__":
    unittest.main()
