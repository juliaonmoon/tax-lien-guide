import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "tax-lien-properties.json"
sys.path.insert(0, str(ROOT / "scripts"))
import refresh_tax_lien_properties as refresher  # noqa: E402


class TaxLienDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DATA.read_text(encoding="utf-8"))
        profiles = cls.doc.get("profiles", {})
        cls.rows = [{**profiles.get(row.get("profile_id"), {}), **row} for row in cls.doc["properties"]]

    def test_property_level_volume_and_unique_ids(self):
        self.assertGreaterEqual(len(self.rows), 600)
        ids = [row["record_id"] for row in self.rows]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_row_is_an_individual_lien(self):
        for row in self.rows:
            self.assertEqual(row["sale_type"], "tax_lien")
            self.assertTrue(row.get("parcel_id") or row.get("certificate_number"))
            self.assertTrue(row.get("official_source_url"))
            self.assertTrue(row.get("data_source"))
            self.assertTrue(row.get("last_verified"))

    def test_owner_names_are_not_collected(self):
        forbidden = {"owner", "owner_name", "mailing_address", "taxpayer"}
        for row in self.rows:
            self.assertFalse(forbidden.intersection(row))

    def test_counts_match_rows(self):
        counts = self.doc["counts"]
        self.assertEqual(counts["total_records"], len(self.rows))
        self.assertEqual(counts["with_parcel_id"], sum(bool(x.get("parcel_id")) for x in self.rows))
        self.assertEqual(counts["with_address"], sum(bool(x.get("property_address")) for x in self.rows))
        self.assertEqual(counts["with_auction_date"], sum(bool(x.get("auction_date")) for x in self.rows))
        self.assertEqual(counts["with_minimum_bid"], sum(x.get("minimum_bid") is not None for x in self.rows))
        self.assertEqual(counts["with_assessed_value"], sum(x.get("assessed_value") is not None for x in self.rows))

    def test_page_loads_dedicated_json_and_keeps_names_distinct(self):
        page = (ROOT / "tax-lien-properties.html").read_text(encoding="utf-8")
        screener = (ROOT / "property-screener.html").read_text(encoding="utf-8")
        calendar = (ROOT / "calendar.html").read_text(encoding="utf-8")
        self.assertIn("data/tax-lien-properties.json", page)
        self.assertIn("One row is one individual tax lien", page)
        self.assertIn("Sort by: Upcoming date", page)
        self.assertIn("Tax Deed Property Screener", screener)
        self.assertIn("data/tax-lien-properties.json", calendar)
        self.assertIn("typeFilter", calendar)

    def test_pwa_caches_lien_dataset(self):
        worker = (ROOT / "sw.js").read_text(encoding="utf-8")
        self.assertIn("./data/tax-lien-properties.json", worker)

    def test_grant_county_present_with_expected_profile(self):
        grant = [row for row in self.rows if row.get("county") == "Grant" and row.get("state") == "IN"]
        self.assertGreaterEqual(len(grant), 50)
        for row in grant:
            self.assertEqual(row["profile_id"], "IN-Grant-2026")
            self.assertTrue(row.get("parcel_id"))
            self.assertIn("2026-04-28", row.get("sale_status") or "")

    def test_hamilton_county_present_with_expected_profile(self):
        hamilton = [row for row in self.rows if row.get("county") == "Hamilton" and row.get("state") == "IN"]
        self.assertGreaterEqual(len(hamilton), 100)
        for row in hamilton:
            self.assertEqual(row["profile_id"], "IN-Hamilton-2026")
            self.assertTrue(row.get("parcel_id"))
            self.assertEqual(row.get("auction_date"), "2026-10-08")


class ForeignCollectorPreservationTests(unittest.TestCase):
    """Regression test: this script must never delete records another
    collector (e.g. refresh_arizona_cochise_tax_liens.py) wrote to the same
    output file for a profile_id it does not manage."""

    def setUp(self):
        self.original_output = refresher.OUTPUT
        fixture = {
            "schema_version": 1,
            "properties": [
                {"record_id": "AZ-Cochise-OTC-12345", "profile_id": "AZ-Cochise-OTC", "parcel_id": "12345"},
                {"record_id": "AZ-Cochise-OTC-67890", "profile_id": "AZ-Cochise-OTC", "parcel_id": "67890"},
            ],
            "profiles": {
                "AZ-Cochise-OTC": {"state": "AZ", "county": "Cochise", "sale_type": "tax_lien"},
            },
        }
        fixture_path = ROOT / "tests" / "_fixture_tax_lien_properties.json"
        fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
        refresher.OUTPUT = fixture_path
        self.fixture_path = fixture_path

    def tearDown(self):
        refresher.OUTPUT = self.original_output
        self.fixture_path.unlink(missing_ok=True)

    def test_unmanaged_profile_is_preserved(self):
        managed = {"IN-Allen-2026", "IN-Tippecanoe-2026", "IN-Wabash-2026", "IN-Grant-2026", "AZ-Coconino-2026"}
        compact, profiles, full = refresher.foreign_entries(managed)
        self.assertEqual(len(compact), 2)
        self.assertEqual(len(full), 2)
        self.assertIn("AZ-Cochise-OTC", profiles)
        self.assertTrue(all(row["profile_id"] == "AZ-Cochise-OTC" for row in compact))

    def test_managed_profile_is_excluded(self):
        managed = {"AZ-Cochise-OTC"}
        compact, profiles, full = refresher.foreign_entries(managed)
        self.assertEqual(compact, [])
        self.assertEqual(profiles, {})
        self.assertEqual(full, [])


if __name__ == "__main__":
    unittest.main()
