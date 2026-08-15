import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "tax-lien-properties.json"


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


if __name__ == "__main__":
    unittest.main()
