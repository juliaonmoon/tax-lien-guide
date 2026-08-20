import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import refresh_michigan_surplus_tax_properties as mi  # noqa: E402


def lot_page(*, title: str, county: str, min_bid: str, current_tax: str,
             parcel_id: str, sev: str, address: str, legal: str,
             description: str) -> str:
    """Build a minimal fixture matching tax-sale.info's real lot-detail HTML
    structure closely enough for the regex-based field extractor to exercise
    the same code paths as the live page (labelled <li> blocks, a repeated
    "Parcel Information:" section, button-wrapped labels for some fields)."""
    return f"""
    <html><body>
    <h2>Lot {title}: {county} Surplus 2026 Preview</h2>
    <ul class="portfolio-meta">
        <li><span><i class="icon-ok"></i>Minimum Bid:</span>{min_bid}</li>
        <li>
            <span>
                <button type="button" onclick="showInfoBubble('x');">
                    <i class="icon-ok"></i>Current Tax:<i class="icon-info-sign"></i>
                </button>
            </span>
            {current_tax}
        </li>
        <li><span><i class="icon-calendar3"></i>Auction Info:</span></li>
        <li>
            <span>
                <button type="button">
                    <i class="icon-ok"></i>Parcel ID:<i class="icon-info-sign"></i>
                </button>
            </span>
            {parcel_id}
        </li>
        <li>
            <span>
                <button type="button">
                    <i class="icon-ok"></i>SEV:<i class="icon-info-sign"></i>
                </button>
            </span>
            {sev}
        </li>
        <li><span>Address:</span>{address}</li>
        <li><span>Legal Description:</span>{legal}</li>
    </ul>
    <div>Parcel Information:
        <h3>{description}</h3>
        Parcel ID: {parcel_id}
        Address: {address}
    </div>
    <div>PROPERTY DETAILS: Please Login or Create a Free Account to See Full Listing Details</div>
    </body></html>
    """


VACANT_LOT = lot_page(
    title="580201", county="Monroe", min_bid="TBA", current_tax="TBA",
    parcel_id="02-335-021-00", sev="$1,600.00", address="INDIAN RD TEMPERANCE",
    legal="INDIAN ACRES N 10 FT OF LOT 20",
    description="Vacant Parcel - Can Only Be Sold To Adjacent Owner",
)

PRICED_LOT = lot_page(
    title="90101", county="Bay", min_bid="$100.00", current_tax="$12.50",
    parcel_id="010-019-400-175-00", sev="$50.00", address="W JENNY ST BAY CITY",
    legal="THAT PT OF W 5 A. OF NE 1/4 OF SE 1/4",
    description="~0.22 Acre Commercial Vacant Lot On W Jenny St. Bay City",
)

LIVE_AUCTION_LOT = """
<html><body>
<h2>Lot 496: Antrim Preview</h2>
<ul class="portfolio-meta">
    <li><span>Minimum Bid:</span>$755.37</li>
    <li><span>Parcel ID:</span>05-13-325-267-00</li>
</ul>
</body></html>
"""


class ParseLotDetailTests(unittest.TestCase):
    def test_tba_fields_become_none_not_zero(self):
        row = mi.parse_lot_detail(VACANT_LOT, "98066", "2026-08-20")
        self.assertIsNone(row["opening_bid"])
        self.assertIsNone(row["current_tax_due"])
        self.assertEqual(row["opening_bid_note"], "TBA -- not yet published by the county")

    def test_priced_lot_parses_money_fields(self):
        row = mi.parse_lot_detail(PRICED_LOT, "111143", "2026-08-20")
        self.assertEqual(row["opening_bid"], 100.0)
        self.assertEqual(row["current_tax_due"], 12.5)
        self.assertEqual(row["assessed_value"], 50.0)
        self.assertIsNone(row["opening_bid_note"])

    def test_county_extracted_from_title(self):
        row = mi.parse_lot_detail(VACANT_LOT, "98066", "2026-08-20")
        self.assertEqual(row["county"], "Monroe")
        row2 = mi.parse_lot_detail(PRICED_LOT, "111143", "2026-08-20")
        self.assertEqual(row2["county"], "Bay")

    def test_parcel_id_legal_description_and_address_captured(self):
        row = mi.parse_lot_detail(VACANT_LOT, "98066", "2026-08-20")
        self.assertEqual(row["parcel_id"], "02-335-021-00")
        self.assertEqual(row["legal_description"], "INDIAN ACRES N 10 FT OF LOT 20")
        self.assertEqual(row["address"], "INDIAN RD TEMPERANCE")

    def test_state_and_sale_status_fixed_fields(self):
        row = mi.parse_lot_detail(VACANT_LOT, "98066", "2026-08-20")
        self.assertEqual(row["state"], "MI")
        self.assertIn("Surplus", row["sale_status"])

    def test_non_surplus_live_auction_page_is_rejected(self):
        # A live per-county auction catalog page (title has no "Surplus
        # <year>") must never be picked up by this collector -- it's a
        # different, time-sensitive dataset this collector doesn't cover.
        row = mi.parse_lot_detail(LIVE_AUCTION_LOT, "159825", "2026-08-20")
        self.assertIsNone(row)

    def test_missing_parcel_id_is_rejected(self):
        broken = VACANT_LOT.replace("02-335-021-00", "")
        row = mi.parse_lot_detail(broken, "98066", "2026-08-20")
        self.assertIsNone(row)


class OwnerNameNeverCollectedTests(unittest.TestCase):
    """This source's parcel detail page never publishes an owner name --
    the only place the word appears is generic policy text like "Can Only
    Be Sold To Adjacent Owner". Explicit regression test anyway, matching
    every other collector in this repo -- see BUG-004/BUG-005 in BUGS.md."""

    def test_no_row_ever_carries_an_owner_value(self):
        for page in (VACANT_LOT, PRICED_LOT):
            row = mi.parse_lot_detail(page, "1", "2026-08-20")
            self.assertIsNone(row.get("owner"))


class ExtractLotIdsTests(unittest.TestCase):
    def test_extracts_unique_ids_in_numeric_order(self):
        html = '<a href="/lot/show/id/300">x</a><a href="/lot/show/id/100">y</a><a href="/lot/show/id/100">dup</a>'
        self.assertEqual(mi.extract_lot_ids(html), ["100", "300"])


class MergeStateRowsTests(unittest.TestCase):
    def test_replaces_only_the_target_state(self):
        existing = [
            {"state": "WA", "county": "King", "parcel_id": "1"},
            {"state": "MI", "county": "Bay", "parcel_id": "old"},
        ]
        new_rows = [{"state": "MI", "county": "Monroe", "parcel_id": "new"}]
        merged = mi.merge_state_rows(existing, new_rows, "MI")
        self.assertEqual(
            {(r["state"], r["parcel_id"]) for r in merged},
            {("WA", "1"), ("MI", "new")},
        )

    def test_empty_new_rows_still_clears_stale_rows(self):
        existing = [{"state": "MI", "county": "Bay", "parcel_id": "stale"}]
        merged = mi.merge_state_rows(existing, [], "MI")
        self.assertEqual(merged, [])


class MoneyParsingTests(unittest.TestCase):
    def test_tba_is_none(self):
        self.assertIsNone(mi._money("TBA"))

    def test_none_is_none(self):
        self.assertIsNone(mi._money(None))

    def test_dollar_with_commas(self):
        self.assertEqual(mi._money("$1,600.00"), 1600.0)


if __name__ == "__main__":
    unittest.main()
