import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "tax-lien-properties.json"
sys.path.insert(0, str(ROOT / "scripts"))
import refresh_montana_yellowstone_tax_liens as refresher  # noqa: E402


PRIOR_HTML = """
<table>
<tr><td colspan="5">Tax Year - 2023</td></tr>
<th>Tax Code</th><th>Name</th><th>1st</th><th>2nd</th><th>Total</th>
<tr><td  align="center">A00607</td><td>SOMEBODY</td><td>0.00</td><td>5668.33</td><td>5668.33</td></tr>
<tr><td  align="center">A00607</td><td>SOMEBODY ELSE</td><td>0</td><td>223.85</td><td>223.85</td></tr>
<tr><td colspan="5">Tax Year - 2024</td></tr>
<tr><td  align="center">B00100</td><td>ANOTHER PERSON</td><td>50.00</td><td>50.00</td><td>100.00</td></tr>
</table>
"""

CURRENT_HTML = """
<table>
<tr><td colspan="5">Tax Year - 2024</td></tr>
<th>Tax Code</th><th>Name</th><th>1st</th><th>2nd</th><th>Total</th>
<tr><td  align="center">B00100</td><td>ANOTHER PERSON</td><td>50.00</td><td>50.00</td><td>100.00</td></tr>
<tr><td colspan="5">Tax Year - 2025</td></tr>
<tr><td  align="center">C00200</td><td>THIRD PERSON</td><td>10.00</td><td>10.00</td><td>20.00</td></tr>
<tr><td  align="center">Z99999</td><td>BAD ROW</td><td>x</td><td>y</td><td>not-a-number</td></tr>
</table>
"""

ADDITIONAL_HTML = """
<table>
<tr><td colspan="5">Additional Properties Available for 2025*</td></tr>
<th>Tax Code</th><th>Name</th><th>1st</th><th>2nd</th><th>Total</th>
<tr><td  align="center">D00300 (2024) </td><td>FOURTH PERSON</td><td>5.00</td><td>0.00</td><td>5.00</td></tr>
</table>
"""


class FakeResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        pass


def fake_get_factory(mapping):
    def fake_get(url, headers=None, timeout=None):
        for needle, html in mapping.items():
            if needle in url:
                return FakeResponse(html)
        raise AssertionError(f"unexpected URL requested: {url}")
    return fake_get


DEFAULT_MAPPING = {
    "year=2024": PRIOR_HTML,
    "year=2025": CURRENT_HTML,
    "TaxDelSpecial_Export": ADDITIONAL_HTML,
}


class DownloadRowsTests(unittest.TestCase):
    def test_parses_and_normalizes_fixture_html(self):
        with patch("refresh_montana_yellowstone_tax_liens.requests.get", side_effect=fake_get_factory(DEFAULT_MAPPING)):
            rows = refresher.download_rows()
        parcels = {r["parcel_id"] for r in rows}
        self.assertEqual(parcels, {"A00607", "B00100", "C00200", "D00300"})

    def test_cross_file_duplicate_is_deduped(self):
        with patch("refresh_montana_yellowstone_tax_liens.requests.get", side_effect=fake_get_factory(DEFAULT_MAPPING)):
            rows = refresher.download_rows()
        b_rows = [r for r in rows if r["parcel_id"] == "B00100"]
        self.assertEqual(len(b_rows), 1, "same tax_code/tax_year/total appearing in both exports must be deduped")

    def test_same_code_and_year_distinct_totals_both_kept_with_suffix(self):
        with patch("refresh_montana_yellowstone_tax_liens.requests.get", side_effect=fake_get_factory(DEFAULT_MAPPING)):
            rows = refresher.download_rows()
        a_rows = sorted((r for r in rows if r["parcel_id"] == "A00607"), key=lambda r: r["minimum_bid"])
        self.assertEqual(len(a_rows), 2, "distinct certificates on the same tax_code/tax_year must both be kept")
        self.assertTrue(a_rows[0]["record_id"].endswith("-1"))
        self.assertTrue(a_rows[1]["record_id"].endswith("-2"))
        self.assertNotEqual(a_rows[0]["record_id"], a_rows[1]["record_id"])

    def test_parenthetical_year_override_applies(self):
        with patch("refresh_montana_yellowstone_tax_liens.requests.get", side_effect=fake_get_factory(DEFAULT_MAPPING)):
            rows = refresher.download_rows()
        d_row = next(r for r in rows if r["parcel_id"] == "D00300")
        self.assertIn("-2024", d_row["record_id"])

    def test_unparseable_total_is_skipped_not_a_crash(self):
        with patch("refresh_montana_yellowstone_tax_liens.requests.get", side_effect=fake_get_factory(DEFAULT_MAPPING)):
            rows = refresher.download_rows()
        parcels = {r["parcel_id"] for r in rows}
        self.assertNotIn("Z99999", parcels)

    def test_every_row_has_no_owner_field(self):
        with patch("refresh_montana_yellowstone_tax_liens.requests.get", side_effect=fake_get_factory(DEFAULT_MAPPING)):
            rows = refresher.download_rows()
        forbidden = {"owner", "owner_name", "mailing_address", "taxpayer", "name"}
        for row in rows:
            self.assertEqual(row["profile_id"], "MT-Yellowstone-Assignments")
            self.assertEqual(row["state"], "MT")
            self.assertEqual(row["county"], "Yellowstone")
            self.assertTrue(row["record_id"].startswith("MT-Yellowstone-Assignments-"))
            self.assertFalse(forbidden.intersection(row))

    def test_all_htmls_unparseable_refuses_to_publish(self):
        empty_mapping = {"year=2024": "<table></table>", "year=2025": "<table></table>", "TaxDelSpecial_Export": "<table></table>"}
        with patch("refresh_montana_yellowstone_tax_liens.requests.get", side_effect=fake_get_factory(empty_mapping)):
            with self.assertRaises(RuntimeError):
                refresher.download_rows()


class UpdateDetailsTests(unittest.TestCase):
    """update_details() must only touch its own profile_id and preserve
    everything else already in the file (same BUG-001 shared-file pattern
    as refresh_arizona_cochise_tax_liens.py)."""

    def setUp(self):
        self.original_details = refresher.DETAILS
        self.original_index = refresher.INDEX
        fixture = {
            "schema_version": 1,
            "counts": {},
            "profiles": {"IN-Allen-2026": {"state": "IN", "county": "Allen"}},
            "properties": [
                {"record_id": "IN-Allen-2026-1", "profile_id": "IN-Allen-2026", "parcel_id": "1"},
                {"record_id": "MT-Yellowstone-Assignments-old", "profile_id": "MT-Yellowstone-Assignments", "parcel_id": "old"},
            ],
        }
        self.details_path = ROOT / "tests" / "_fixture_yellowstone_details.json"
        self.details_path.write_text(json.dumps(fixture), encoding="utf-8")
        self.index_path = ROOT / "tests" / "_fixture_yellowstone_index.html"
        self.index_path.write_text("const rows=[\n];", encoding="utf-8")
        refresher.DETAILS = self.details_path
        refresher.INDEX = self.index_path

    def tearDown(self):
        refresher.DETAILS = self.original_details
        refresher.INDEX = self.original_index
        self.details_path.unlink(missing_ok=True)
        self.index_path.unlink(missing_ok=True)

    def test_other_profiles_survive_a_yellowstone_update(self):
        new_rows = [{
            "record_id": "MT-Yellowstone-Assignments-new", "profile_id": "MT-Yellowstone-Assignments",
            "parcel_id": "new", "minimum_bid": 100.0,
        }]
        refresher.update_details(new_rows)
        doc = json.loads(self.details_path.read_text(encoding="utf-8"))
        profile_ids = {p.get("profile_id") for p in doc["properties"]}
        self.assertIn("IN-Allen-2026", profile_ids)
        self.assertIn("MT-Yellowstone-Assignments", profile_ids)
        mt_ids = {p["record_id"] for p in doc["properties"] if p.get("profile_id") == "MT-Yellowstone-Assignments"}
        self.assertEqual(mt_ids, {"MT-Yellowstone-Assignments-new"})

    def test_existing_rows_returns_only_yellowstone_profile(self):
        prior = refresher.existing_rows()
        self.assertEqual(len(prior), 1)
        self.assertEqual(prior[0]["record_id"], "MT-Yellowstone-Assignments-old")

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
                {"record_id": "MT-Yellowstone-Assignments-old", "profile_id": "MT-Yellowstone-Assignments", "parcel_id": "old"},
            ],
        }
        self.details_path = ROOT / "tests" / "_fixture_yellowstone_main_details.json"
        self.details_path.write_text(json.dumps(fixture), encoding="utf-8")
        self.index_path = ROOT / "tests" / "_fixture_yellowstone_main_index.html"
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
        with patch("refresh_montana_yellowstone_tax_liens.download_rows", side_effect=RuntimeError("source down")):
            refresher.main()
        after = self.details_path.read_text(encoding="utf-8")
        self.assertEqual(before, after, "DETAILS file must be untouched (not erased) when the source fails")

    def test_source_failure_with_no_prior_data_raises(self):
        self.details_path.write_text(json.dumps({"properties": []}), encoding="utf-8")
        with patch("refresh_montana_yellowstone_tax_liens.download_rows", side_effect=RuntimeError("source down")):
            with self.assertRaises(RuntimeError):
                refresher.main()


if __name__ == "__main__":
    unittest.main()
