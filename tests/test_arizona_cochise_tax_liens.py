import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "tax-lien-properties.json"
sys.path.insert(0, str(ROOT / "scripts"))
import refresh_arizona_cochise_tax_liens as refresher  # noqa: E402


FIXTURE_CSV = (
    "﻿Parcel Number,Legal Description,Total Amount\r\n"
    '"111-22-333","LOT 1 BLOCK A COCHISE SUB","1173.86"\r\n'
    '"111-22-333","LOT 1 BLOCK A COCHISE SUB","1173.86"\r\n'  # duplicate parcel, must be deduped
    '"444-55-666","","2500.00"\r\n'  # missing legal description
    '"777-88-999","LOT 3","not-a-number"\r\n'  # unparseable amount -> None, row still kept
    '"","",""\r\n'  # blank parcel -> skipped
)


class FakeResponse:
    def __init__(self, text, status_code=200, content_type="text/csv"):
        self.text = text
        self.status_code = status_code
        self.headers = {"content-type": content_type}

    def raise_for_status(self):
        pass


class DownloadRowsTests(unittest.TestCase):
    def test_parses_dedupes_and_normalizes_fixture_csv(self):
        with patch("refresh_arizona_cochise_tax_liens.requests.get", return_value=FakeResponse(FIXTURE_CSV)):
            rows = refresher.download_rows()
        parcels = [r["parcel_id"] for r in rows]
        self.assertEqual(len(parcels), len(set(parcels)), "duplicate parcel was not deduplicated")
        self.assertEqual(sorted(parcels), ["111-22-333", "444-55-666", "777-88-999"])

    def test_every_row_is_an_individual_certificate_with_no_owner_field(self):
        with patch("refresh_arizona_cochise_tax_liens.requests.get", return_value=FakeResponse(FIXTURE_CSV)):
            rows = refresher.download_rows()
        forbidden = {"owner", "owner_name", "mailing_address", "taxpayer"}
        for row in rows:
            self.assertEqual(row["profile_id"], "AZ-Cochise-OTC")
            self.assertEqual(row["state"], "AZ")
            self.assertEqual(row["county"], "Cochise")
            self.assertTrue(row["record_id"].startswith("AZ-Cochise-OTC-"))
            self.assertFalse(forbidden.intersection(row))

    def test_unparseable_amount_becomes_none_not_a_crash(self):
        with patch("refresh_arizona_cochise_tax_liens.requests.get", return_value=FakeResponse(FIXTURE_CSV)):
            rows = refresher.download_rows()
        row = next(r for r in rows if r["parcel_id"] == "777-88-999")
        self.assertIsNone(row["minimum_bid"])

    def test_missing_legal_description_does_not_crash(self):
        with patch("refresh_arizona_cochise_tax_liens.requests.get", return_value=FakeResponse(FIXTURE_CSV)):
            rows = refresher.download_rows()
        row = next(r for r in rows if r["parcel_id"] == "444-55-666")
        self.assertIsNone(row["legal_description"])

    def test_empty_response_refuses_to_publish(self):
        empty_csv = "Parcel Number,Legal Description,Total Amount\r\n"
        with patch("refresh_arizona_cochise_tax_liens.requests.get", return_value=FakeResponse(empty_csv)):
            with self.assertRaises(RuntimeError):
                refresher.download_rows()


class UpdateDetailsTests(unittest.TestCase):
    """update_details() must only touch its own profile_id (AZ-Cochise-OTC)
    and preserve everything else already in the file -- this is the fix
    that made refresh_tax_lien_properties.py stop erasing Cochise's rows
    (BUG-001); this test locks down that Cochise's own writer still behaves
    correctly on the other side of that relationship."""

    def setUp(self):
        self.original_details = refresher.DETAILS
        self.original_index = refresher.INDEX
        fixture = {
            "schema_version": 1,
            "counts": {},
            "profiles": {"IN-Allen-2026": {"state": "IN", "county": "Allen"}},
            "properties": [
                {"record_id": "IN-Allen-2026-1", "profile_id": "IN-Allen-2026", "parcel_id": "1"},
                {"record_id": "AZ-Cochise-OTC-old", "profile_id": "AZ-Cochise-OTC", "parcel_id": "old"},
            ],
        }
        self.details_path = ROOT / "tests" / "_fixture_cochise_details.json"
        self.details_path.write_text(json.dumps(fixture), encoding="utf-8")
        self.index_path = ROOT / "tests" / "_fixture_cochise_index.html"
        self.index_path.write_text("const rows=[\n];", encoding="utf-8")
        refresher.DETAILS = self.details_path
        refresher.INDEX = self.index_path

    def tearDown(self):
        refresher.DETAILS = self.original_details
        refresher.INDEX = self.original_index
        self.details_path.unlink(missing_ok=True)
        self.index_path.unlink(missing_ok=True)

    def test_other_profiles_survive_a_cochise_update(self):
        new_rows = [{
            "record_id": "AZ-Cochise-OTC-new", "profile_id": "AZ-Cochise-OTC",
            "parcel_id": "new", "minimum_bid": 100.0,
        }]
        refresher.update_details(new_rows)
        doc = json.loads(self.details_path.read_text(encoding="utf-8"))
        profile_ids = {p.get("profile_id") for p in doc["properties"]}
        self.assertIn("IN-Allen-2026", profile_ids)
        self.assertIn("AZ-Cochise-OTC", profile_ids)
        cochise_ids = {p["record_id"] for p in doc["properties"] if p.get("profile_id") == "AZ-Cochise-OTC"}
        self.assertEqual(cochise_ids, {"AZ-Cochise-OTC-new"})

    def test_existing_rows_returns_only_cochise_profile(self):
        prior = refresher.existing_rows()
        self.assertEqual(len(prior), 1)
        self.assertEqual(prior[0]["record_id"], "AZ-Cochise-OTC-old")

    def test_existing_rows_empty_when_details_file_missing(self):
        self.details_path.unlink()
        self.assertEqual(refresher.existing_rows(), [])


class MainFallbackTests(unittest.TestCase):
    """A source failure must preserve prior data rather than deleting it or
    crashing when prior data exists to fall back on (BUG-001)."""

    def setUp(self):
        self.original_details = refresher.DETAILS
        self.original_index = refresher.INDEX
        fixture = {
            "schema_version": 1, "counts": {}, "profiles": {},
            "properties": [
                {"record_id": "AZ-Cochise-OTC-old", "profile_id": "AZ-Cochise-OTC", "parcel_id": "old"},
            ],
        }
        self.details_path = ROOT / "tests" / "_fixture_cochise_main_details.json"
        self.details_path.write_text(json.dumps(fixture), encoding="utf-8")
        self.index_path = ROOT / "tests" / "_fixture_cochise_main_index.html"
        self.index_path.write_text("const rows=[\n];", encoding="utf-8")
        refresher.DETAILS = self.details_path
        refresher.INDEX = self.index_path

    def tearDown(self):
        refresher.DETAILS = self.original_details
        refresher.INDEX = self.original_index
        self.details_path.unlink(missing_ok=True)
        self.index_path.unlink(missing_ok=True)

    def test_source_failure_with_prior_data_leaves_details_file_untouched(self):
        before = self.details_path.read_text(encoding="utf-8")
        with patch("refresh_arizona_cochise_tax_liens.download_rows", side_effect=RuntimeError("source down")):
            refresher.main()
        after = self.details_path.read_text(encoding="utf-8")
        self.assertEqual(before, after, "DETAILS file must be untouched (not erased) when the source fails")

    def test_source_failure_with_no_prior_data_raises(self):
        self.details_path.write_text(json.dumps({"properties": []}), encoding="utf-8")
        with patch("refresh_arizona_cochise_tax_liens.download_rows", side_effect=RuntimeError("source down")):
            with self.assertRaises(RuntimeError):
                refresher.main()


if __name__ == "__main__":
    unittest.main()
