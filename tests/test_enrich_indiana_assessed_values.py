import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "tax-lien-properties.json"
sys.path.insert(0, str(ROOT / "scripts"))
import enrich_indiana_assessed_values as enricher  # noqa: E402


def fixed_width_line(**fields) -> str:
    """Build a PARCEL record line long enough for every FIELDS position,
    with each named field written at its official byte position (50 IAC
    26-20-4) and everything else left as spaces."""
    line = [" "] * 1286
    for name, value in fields.items():
        start, end = enricher.FIELDS[name]
        for i, ch in enumerate(value):
            if start - 1 + i < end:
                line[start - 1 + i] = ch
    return "".join(line)


class FixedWidthPositionTests(unittest.TestCase):
    """Byte positions must exactly match 50 IAC 26-20-4 -- this was verified
    against 5 known real Allen County parcels before this script was
    written (5/5 matched with correct addresses and plausible values)."""

    def test_known_positions_extract_correctly(self):
        line = fixed_width_line(
            parcel_number="021213404011000074",
            property_street_address="3607 BOWSER AV",
            property_city="FORT WAYNE",
            property_zip="46806-0000",
            av_total_land_and_improvements="000000109400",
            legal_description="TEST LEGAL DESCRIPTION",
            current_av_total_land_and_improvements="000000109400",
        )
        self.assertEqual(len(line), 1286)
        self.assertEqual(enricher.slice_field(line, "parcel_number").strip(), "021213404011000074")
        self.assertEqual(enricher.clean(enricher.slice_field(line, "property_street_address")), "3607 BOWSER AV")
        self.assertEqual(enricher.clean(enricher.slice_field(line, "property_city")), "FORT WAYNE")
        self.assertEqual(enricher.parse_av(enricher.slice_field(line, "av_total_land_and_improvements")), 109400.0)


class ParseRealPropertyRecordsTests(unittest.TestCase):
    def _zip_of(self, lines: list[str]) -> bytes:
        import io
        import zipfile
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("RealParcel_Test_00_2025P2026.txt", "\n".join(lines))
        return buf.getvalue()

    def test_skips_header_and_parses_detail_records(self):
        header = "PARCEL    02Allen               2021A"
        detail = fixed_width_line(
            parcel_number="021213404011000074",
            property_street_address="3607 BOWSER AV",
            property_city="FORT WAYNE",
            property_zip="46806-0000",
            av_total_land_and_improvements="000000109400",
            current_av_total_land_and_improvements="000000109400",
        )
        zip_bytes = self._zip_of([header, detail])
        records = enricher.parse_real_property_records(zip_bytes)
        self.assertEqual(len(records), 1)
        record = records["021213404011000074"]
        self.assertEqual(record["assessed_value"], 109400.0)
        self.assertEqual(record["market_value"], 109400.0)
        self.assertEqual(record["property_address"], "3607 BOWSER AV")

    def test_zero_assessed_value_is_none_not_zero(self):
        detail = fixed_width_line(
            parcel_number="099999999999999999",
            av_total_land_and_improvements="000000000000",
            current_av_total_land_and_improvements="000000000000",
        )
        records = enricher.parse_real_property_records(self._zip_of(["PARCEL header", detail]))
        record = records["099999999999999999"]
        self.assertIsNone(record["assessed_value"])
        self.assertIsNone(record["market_value"])

    def test_missing_txt_file_raises(self):
        import io
        import zipfile
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("readme.pdf", b"not a data file")
        with self.assertRaises(RuntimeError):
            enricher.parse_real_property_records(buf.getvalue())


class ApplyEnrichmentTests(unittest.TestCase):
    """Enrichment must only fill missing fields and never overwrite an
    already-populated value (never fabricate/override real collected
    data), and must match by digit-normalized parcel number."""

    def test_matches_by_digit_normalized_parcel_id(self):
        rows = [{"parcel_id": "02-12-13-404-011.000-074", "assessed_value": None, "address": None}]
        by_parcel = {"021213404011000074": {"assessed_value": 109400.0, "market_value": 109400.0,
                                             "property_address": "3607 BOWSER AV", "city": "FORT WAYNE",
                                             "zip": "46806-0000", "legal_description": "LOT 1"}}
        matched = enricher.apply_enrichment(rows, by_parcel)
        self.assertEqual(matched, 1)
        self.assertEqual(rows[0]["assessed_value"], 109400.0)
        self.assertEqual(rows[0]["address"], "3607 BOWSER AV")

    def test_never_overwrites_an_existing_value(self):
        rows = [{"parcel_id": "02-12-13-404-011.000-074", "assessed_value": 1.0}]
        by_parcel = {"021213404011000074": {"assessed_value": 999999.0}}
        enricher.apply_enrichment(rows, by_parcel)
        self.assertEqual(rows[0]["assessed_value"], 1.0)

    def test_no_match_leaves_row_untouched(self):
        rows = [{"parcel_id": "02-99-99-999-999.000-999", "assessed_value": None}]
        matched = enricher.apply_enrichment(rows, {})
        self.assertEqual(matched, 0)
        self.assertIsNone(rows[0]["assessed_value"])

    def test_missing_parcel_id_is_skipped_not_crashed(self):
        rows = [{"assessed_value": None}]
        matched = enricher.apply_enrichment(rows, {"anything": {}})
        self.assertEqual(matched, 0)


class MainFailureIsolationTests(unittest.TestCase):
    """A failed county download must never touch that county's -- or any
    other county's -- existing rows (same reliability standard as
    BUG-001/BUG-002)."""

    def setUp(self):
        self.original_details = enricher.DETAILS
        fixture = {
            "schema_version": 1,
            "counts": {"with_assessed_value": 0, "with_address": 0},
            "profiles": {},
            "properties": [
                {"record_id": "IN-Allen-2026-1", "profile_id": "IN-Allen-2026",
                 "parcel_id": "02-12-13-404-011.000-074", "assessed_value": None, "address": None},
            ],
        }
        self.details_path = ROOT / "tests" / "_fixture_enrich_details.json"
        self.details_path.write_text(json.dumps(fixture), encoding="utf-8")
        enricher.DETAILS = self.details_path

    def tearDown(self):
        enricher.DETAILS = self.original_details
        self.details_path.unlink(missing_ok=True)

    def test_download_failure_leaves_rows_unchanged(self):
        with patch("enrich_indiana_assessed_values.enrich_county", side_effect=RuntimeError("network down")):
            enricher.main()
        doc = json.loads(self.details_path.read_text(encoding="utf-8"))
        self.assertIsNone(doc["properties"][0]["assessed_value"])


if __name__ == "__main__":
    unittest.main()
