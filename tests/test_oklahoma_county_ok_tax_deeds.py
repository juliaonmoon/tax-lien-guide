import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import refresh_oklahoma_county_ok_tax_deeds as ok  # noqa: E402


HEADER_ROW = """
<tr>
<td bgcolor="#003366"><b><font color="#FFFFFF">Record#</font></b></td>
<td bgcolor="#003366"><b><font color="#FFFFFF">Parcel_No</font></b></td>
<td bgcolor="#003366"><b><font color="#FFFFFF">Parcel Map Per Assessor</font></b></td>
<td bgcolor="#003366"><b><font color="#FFFFFF">Scheduled Sale Date/Time</font></b></td>
<td bgcolor="#003366"><b><font color="#FFFFFF">Initial Bid Amount</font></b></td>
<td bgcolor="#003366"><b><font color="#FFFFFF">Suggested Initial Bid Amount</font></b></td>
<td bgcolor="#003366"><b><font color="#FFFFFF">Physical Address Per Assessor/Legal Description</font></b></td>
</tr>
"""

UNSCHEDULED_ROW = """
<tr>
<td nowrap><font size="2">1</font></td>
<td valign="top" nowrap><font size="2">1024-12-702-1015</font></td>
<td nowrap><font size="2"><a href="https://experience.arcgis.com/map1">Map Parcel</a></font></td>
<td valign="top" nowrap><font size="2">N/A</font></td>
<td valign="top" nowrap align="right"><font size="2">$0.00</font></td>
<td valign="top" nowrap align="right"><font size="2">$470.00</font></td>
<td nowrap><font size="2"><a href="https://docs.oklahomacounty.org/AssessorWP5/AN-R.asp?PropertyID=745">0 UNKNOWN CHOCTAW</a></font></td>
</tr>
"""

SCHEDULED_ROW = """
<tr bgcolor='#dfebf8'>
<td nowrap><font size="2">97</font></td>
<td valign="top" nowrap><font size="2">2680-05-147-3000</font></td>
<td nowrap><font size="2"><a href="https://experience.arcgis.com/map2">Map Parcel</a></font></td>
<td valign="top" nowrap><font size="2">09/03/2026 04:00 pm</font></td>
<td valign="top" nowrap align="right"><font size="2">$265.00</font></td>
<td valign="top" nowrap align="right"><font size="2">$265.00</font></td>
<td nowrap><font size="2"><a href="https://docs.oklahomacounty.org/AssessorWP5/AN-R.asp?PropertyID=901">0 UNKNOWN OKC</a></font></td>
</tr>
"""

REAL_ADDRESS_ROW = """
<tr>
<td nowrap><font size="2">60</font></td>
<td valign="top" nowrap><font size="2">1802-07-169-9245</font></td>
<td nowrap><font size="2"><a href="https://experience.arcgis.com/map3">Map Parcel</a></font></td>
<td valign="top" nowrap><font size="2">N/A</font></td>
<td valign="top" nowrap align="right"><font size="2">$0.00</font></td>
<td valign="top" nowrap align="right"><font size="2">$17,840.00</font></td>
<td nowrap><font size="2"><a href="https://docs.oklahomacounty.org/AssessorWP5/AN-R.asp?PropertyID=222">1545 NE 42ND ST OKC</a></font></td>
</tr>
"""

DUPLICATE_ROW = UNSCHEDULED_ROW  # same parcel number repeated

NOISE_ROW = """
<tr><td colspan="7">The Oklahoma County Resale Is Complete See You Next Year!</td></tr>
"""


def padded_table(*extra_rows: str, count: int = 150) -> str:
    filler = []
    for i in range(count):
        filler.append(f"""
<tr>
<td nowrap><font size="2">{i + 1000}</font></td>
<td valign="top" nowrap><font size="2">{1000 + i:04d}-01-000-{i:04d}</font></td>
<td nowrap><font size="2"><a href="https://example.com/map">Map Parcel</a></font></td>
<td valign="top" nowrap><font size="2">N/A</font></td>
<td valign="top" nowrap align="right"><font size="2">$0.00</font></td>
<td valign="top" nowrap align="right"><font size="2">$500.00</font></td>
<td nowrap><font size="2"><a href="https://example.com/detail">0 UNKNOWN OKC</a></font></td>
</tr>
""")
    return "<table>" + HEADER_ROW + NOISE_ROW + "".join(filler) + "".join(extra_rows) + "</table>"


class ParseCountyOwnedListTests(unittest.TestCase):
    def test_parses_one_row_per_unique_parcel(self):
        rows = ok.parse_county_owned_list(padded_table(UNSCHEDULED_ROW, SCHEDULED_ROW), "2026-08-19")
        by_parcel = {r["parcel_id"]: r for r in rows}
        self.assertIn("1024-12-702-1015", by_parcel)
        self.assertIn("2680-05-147-3000", by_parcel)
        self.assertEqual(len(rows), len(by_parcel))

    def test_header_and_notice_rows_are_skipped(self):
        rows = ok.parse_county_owned_list(padded_table(UNSCHEDULED_ROW), "2026-08-19")
        for row in rows:
            self.assertNotIn("Record#", row["parcel_id"])
            self.assertNotIn("Complete", row.get("city") or "")

    def test_duplicate_parcel_only_counted_once(self):
        rows = ok.parse_county_owned_list(padded_table(UNSCHEDULED_ROW, DUPLICATE_ROW), "2026-08-19")
        matches = [r for r in rows if r["parcel_id"] == "1024-12-702-1015"]
        self.assertEqual(len(matches), 1)

    def test_unscheduled_row_has_no_sale_date_and_uses_suggested_bid(self):
        rows = ok.parse_county_owned_list(padded_table(UNSCHEDULED_ROW), "2026-08-19")
        row = next(r for r in rows if r["parcel_id"] == "1024-12-702-1015")
        self.assertIsNone(row["sale_date"])
        self.assertEqual(row["opening_bid"], 470.0)
        self.assertEqual(row["county_initial_bid_amount"], 0.0)
        self.assertEqual(row["sale_status"], "County-owned; available for direct purchase from the Treasurer (not yet scheduled for a public resale)")

    def test_scheduled_row_captures_sale_date(self):
        rows = ok.parse_county_owned_list(padded_table(SCHEDULED_ROW), "2026-08-19")
        row = next(r for r in rows if r["parcel_id"] == "2680-05-147-3000")
        self.assertEqual(row["sale_date"], "09/03/2026")
        self.assertEqual(row["sale_status"], "County-owned; scheduled for a public resale")
        self.assertEqual(row["opening_bid"], 265.0)

    def test_placeholder_address_becomes_city_only(self):
        rows = ok.parse_county_owned_list(padded_table(UNSCHEDULED_ROW), "2026-08-19")
        row = next(r for r in rows if r["parcel_id"] == "1024-12-702-1015")
        self.assertEqual(row["city"], "Choctaw")
        self.assertIsNone(row["address"])

    def test_real_address_is_captured_when_not_the_placeholder_pattern(self):
        rows = ok.parse_county_owned_list(padded_table(REAL_ADDRESS_ROW), "2026-08-19")
        row = next(r for r in rows if r["parcel_id"] == "1802-07-169-9245")
        self.assertEqual(row["address"], "1545 NE 42ND ST OKC")
        self.assertIsNone(row["city"])

    def test_below_minimum_row_count_raises(self):
        with self.assertRaises(RuntimeError):
            ok.parse_county_owned_list(padded_table(count=5), "2026-08-19")


class OwnerNameNeverCollectedTests(unittest.TestCase):
    """This source's table never publishes an owner name at all, but keep an
    explicit regression test anyway -- see BUG-004/BUG-005 in BUGS.md for why
    this convention gets a dedicated test on every collector, not just the
    ones known to have violated it."""

    def test_no_row_ever_carries_an_owner_value(self):
        rows = ok.parse_county_owned_list(padded_table(UNSCHEDULED_ROW, SCHEDULED_ROW, REAL_ADDRESS_ROW), "2026-08-19")
        for row in rows:
            self.assertIsNone(row.get("owner"))


class MergeStateCountyRowsTests(unittest.TestCase):
    def test_replaces_only_the_target_state_and_county(self):
        existing = [
            {"state": "WA", "county": "King", "parcel_id": "1"},
            {"state": "OK", "county": "Oklahoma", "parcel_id": "old"},
            {"state": "OK", "county": "Someday-Other-County", "parcel_id": "keep-me"},
        ]
        new_rows = [{"state": "OK", "county": "Oklahoma", "parcel_id": "new"}]
        merged = ok.merge_state_county_rows(existing, new_rows, "OK", "Oklahoma")
        self.assertEqual(
            {(r["state"], r["county"], r["parcel_id"]) for r in merged},
            {("WA", "King", "1"), ("OK", "Someday-Other-County", "keep-me"), ("OK", "Oklahoma", "new")},
        )

    def test_empty_new_rows_still_clears_stale_rows(self):
        existing = [{"state": "OK", "county": "Oklahoma", "parcel_id": "stale"}]
        merged = ok.merge_state_county_rows(existing, [], "OK", "Oklahoma")
        self.assertEqual(merged, [])


if __name__ == "__main__":
    unittest.main()
