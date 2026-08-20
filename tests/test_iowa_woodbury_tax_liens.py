import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import refresh_iowa_woodbury_tax_liens as woodbury  # noqa: E402


HEADER = "1 0001 - GRANT/MAPLE VALLEY ANTHON OTO SCH 874428300002 BODNAR FARMS LLC"


class SplitMoneyRegressionTests(unittest.TestCase):
    """Regression test for a live 2026-08-20 bug: pdfplumber extracts roughly
    30% of this county's real-estate rows with a stray space inside the
    dollar amount ("$ 3 48.00" for what the PDF renders as $348.00), which
    broke the same-$20-fee invariant check in _published_amounts() and
    silently dropped the row. Confirmed live against the real 2026 PDF:
    fixing this recovered exactly the missing rows, 1100 -> 1569 (the full
    expected real-estate set), with no fabricated values -- every recovered
    amount still satisfies the same fee invariant. See BUGS.md / issue #29."""

    def test_three_digit_amount_split_after_first_digit(self):
        line = f"{HEADER} $ 3 48.00 $ 368.00"
        self.assertEqual(woodbury._published_amounts(line), (348.0, 368.0))

    def test_two_digit_amount_split_after_first_digit(self):
        line = f"{HEADER} $ 5 2.00 $ 7 2.00"
        self.assertEqual(woodbury._published_amounts(line), (52.0, 72.0))

    def test_single_digit_amount_split_before_decimal(self):
        line = f"{HEADER} $ 8 .00 $ 2 8.00"
        self.assertEqual(woodbury._published_amounts(line), (8.0, 28.0))

    def test_comma_grouped_five_digit_amount_split(self):
        line = f"{HEADER} $ 11,626.00 $ 1 1,646.00"
        self.assertEqual(woodbury._published_amounts(line), (11626.0, 11646.0))

    def test_unsplit_amounts_still_parse_normally(self):
        line = f"{HEADER} $348.00 $368.00"
        self.assertEqual(woodbury._published_amounts(line), (348.0, 368.0))

    def test_does_not_merge_across_the_two_separate_dollar_amounts(self):
        # Each amount starts with its own "$" -- the collapse must stop at
        # the next "$", never bridge into the second figure.
        line = f"{HEADER} $ 3 48.00 $ 3 68.00"
        self.assertEqual(woodbury._published_amounts(line), (348.0, 368.0))

    def test_amounts_that_fail_the_fee_invariant_are_still_rejected(self):
        # The split-money fix must not weaken the existing $20-fee safety
        # check -- a genuinely wrong/unrelated pair of numbers still returns
        # None rather than being accepted.
        line = f"{HEADER} $100.00 $500.00"
        self.assertIsNone(woodbury._published_amounts(line))


if __name__ == "__main__":
    unittest.main()
