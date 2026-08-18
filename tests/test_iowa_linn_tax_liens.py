import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import refresh_iowa_linn_tax_liens as linn  # noqa: E402


SAMPLE = """Real Estate
00100 - BERTRAM TWP/CEDAR RAPIDS SCH/FD2
1. NEMEC JOANN 142442701500000
A.P. #336 LOT 1 W200' .......................................................................$2,873.00
2. LAND DOUGLAS C 151930200300000
P.O.S. #2155 PARCEL A .............................................................................$8.00
Public Bidder Real Estate
03200 - FAIRFAX CITY/COLLEGE SCH
1547. *BISAILLON DANIEL W & LONNA E 201610301500000
VANDERBILT E4.83' W1/2 LOT 8 BLK 4..................................................$37.00
1568. *SAMPLE OWNER 142999999999999
SAMPLE REAL ESTATE LEGAL DESCRIPTION ........................................$101.00
I, Brent C. Oleson, Treasurer of Linn County, Iowa, hereby give notice that on Monday
the 15th of June 2026, at the Nine O'Clock in the forenoon at Jean Oxley Public Service Center, I will as provided by law, offer for sale all mobile homes hereinafter listed on which
Taxes of any description shall remain due and unpaid to the time of sale.
1569. MOBILE HOME OWNER 112000HDC412621A
FOREST BROOK 1996 Title #57AG69321
Park: MHP79 - Vernon Village................................................................$105.00
"""


class LinnParserTests(unittest.TestCase):
    def test_parser_keeps_real_estate_and_excludes_mobile_homes(self):
        original_threshold = None
        # The production parser intentionally enforces >=1500 rows. Exercise its
        # parsing logic on a synthetic sample by padding real-estate items.
        text = SAMPLE
        extras = []
        for n in range(3, 1501):
            extras.append(f"{n}. OWNER OMITTED {n:015d}\nLEGAL LOT {n} ........................................$10.00")
        text = text.replace("Public Bidder Real Estate", "\n".join(extras) + "\nPublic Bidder Real Estate")
        rows = linn.parse_real_estate_rows(text, "2026-08-18")
        self.assertGreaterEqual(len(rows), 1500)
        by_item = {row["sale_item_number"]: row for row in rows}
        self.assertEqual(by_item["1"]["parcel_id"], "142442701500000")
        self.assertEqual(by_item["1"]["delinquent_tax_amount"], 2873.0)
        self.assertEqual(by_item["1547"]["sale_status"].split("—")[-1].strip().split(";")[0], "Public bidder tax sale")
        self.assertEqual(by_item["1547"]["redemption_period"], "90-day notice of right of redemption may be issued after 9 months from sale")
        self.assertNotIn("1569", by_item)
        self.assertTrue(all("owner" not in key.lower() for row in rows for key in row.keys()))

    def test_parcel_ids_must_be_real_estate_shape(self):
        match = linn.ITEM.match("10. SOME NAME 152137800100000")
        self.assertIsNotNone(match)
        self.assertIsNone(linn.ITEM.match("1569. MOBILE NAME 112000HDC412621A"))


if __name__ == "__main__":
    unittest.main()
