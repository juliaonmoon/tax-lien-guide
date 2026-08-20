#!/usr/bin/env python3
"""Privacy-safe Dubuque 2026 PDF structure diagnostics.

Prints only structural counts, coordinate buckets, and distance histograms. It
never prints source lines, taxpayer names, parcel IDs, dollar values, legal text,
addresses, or other free text from the county publication.
"""

from __future__ import annotations

import io
import re
from collections import Counter
from statistics import median

import pdfplumber

import refresh_iowa_dubuque_tax_liens as dubuque

ITEM_WORD_RE = re.compile(r"^(\d{1,3})\)$")
PARCEL_WORD_RE = re.compile(r"^\d{10}$")
MONEY_WORD_RE = re.compile(r"^\$?[\d,]+\.\d{2}$")


def _bucket(value: float, size: int = 25) -> int:
    return int(value // size) * size


def _column(x: float) -> str:
    return "left" if x < 250 else "right"


def main() -> None:
    raw = dubuque.fetch_pdf()
    print(f"pdf_bytes={len(raw)}")

    item_x = Counter()
    parcel_x = Counter()
    money_x = Counter()
    item_numbers: list[int] = []
    row_money_distances: list[float] = []
    preceding_parcel_distances: list[float] = []
    fallback_signed_gaps = Counter()
    fallback_x_diffs = Counter()
    missing_by_page = Counter()
    missing_by_column = Counter()
    page_counts: list[tuple[int, int, int]] = []

    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
            items = []
            parcels = []
            monies = []
            for word in words:
                text = word["text"].strip()
                item_match = ITEM_WORD_RE.match(text)
                if item_match:
                    number = int(item_match.group(1))
                    if 1 <= number <= dubuque.REAL_ESTATE_ITEM_COUNT:
                        items.append(word)
                        item_numbers.append(number)
                        item_x[_bucket(float(word["x0"]))] += 1
                if PARCEL_WORD_RE.match(text):
                    parcels.append(word)
                    parcel_x[_bucket(float(word["x0"]))] += 1
                if MONEY_WORD_RE.match(text):
                    monies.append(word)
                    money_x[_bucket(float(word["x0"]))] += 1
            page_counts.append((len(items), len(parcels), len(monies)))

            for item in items:
                iy = (float(item["top"]) + float(item["bottom"])) / 2
                ix = float(item["x0"])
                same_row_money = [
                    money for money in monies
                    if abs(((float(money["top"]) + float(money["bottom"])) / 2) - iy) <= 3
                    and float(money["x0"]) > ix
                    and _column(float(money["x0"]) - 200) == _column(ix)
                ]
                if same_row_money:
                    nearest = min(same_row_money, key=lambda money: float(money["x0"]) - ix)
                    row_money_distances.append(float(nearest["x0"]) - ix)

                prior = [
                    parcel for parcel in parcels
                    if _column(float(parcel["x0"])) == _column(ix)
                    and float(parcel["bottom"]) <= float(item["top"]) + 1
                    and 0 <= float(item["top"]) - float(parcel["bottom"]) <= 45
                ]
                if prior:
                    nearest_parcel = min(prior, key=lambda parcel: float(item["top"]) - float(parcel["bottom"]))
                    preceding_parcel_distances.append(float(item["top"]) - float(nearest_parcel["bottom"]))
                    continue

                missing_by_page[page_no] += 1
                missing_by_column[_column(ix)] += 1
                same_col = [parcel for parcel in parcels if _column(float(parcel["x0"])) == _column(ix)]
                if same_col:
                    nearest_any = min(
                        same_col,
                        key=lambda parcel: abs(
                            ((float(parcel["top"]) + float(parcel["bottom"])) / 2) - iy
                        ),
                    )
                    py = (float(nearest_any["top"]) + float(nearest_any["bottom"])) / 2
                    fallback_signed_gaps[_bucket(py - iy, 5)] += 1
                    fallback_x_diffs[_bucket(float(nearest_any["x0"]) - ix, 25)] += 1
                else:
                    fallback_signed_gaps[999] += 1

    number_counts = Counter(item_numbers)
    print(f"pages={len(page_counts)} page_structural_counts={page_counts}")
    print(
        f"item_tokens={len(item_numbers)} distinct_item_numbers={len(number_counts)} "
        f"singletons={sum(1 for c in number_counts.values() if c == 1)} duplicates={sum(1 for c in number_counts.values() if c > 1)}"
    )
    print(f"item_x_buckets={item_x.most_common(20)}")
    print(f"parcel_x_buckets={parcel_x.most_common(20)}")
    print(f"money_x_buckets={money_x.most_common(20)}")
    print(
        f"items_with_same_row_money={len(row_money_distances)} "
        f"median_item_to_money_dx={median(row_money_distances) if row_money_distances else None}"
    )
    print(
        f"items_with_near_preceding_parcel={len(preceding_parcel_distances)} "
        f"median_item_to_parcel_vertical_gap={median(preceding_parcel_distances) if preceding_parcel_distances else None}"
    )
    print(f"missing_join_by_page={dict(missing_by_page)} missing_join_by_column={dict(missing_by_column)}")
    print(f"missing_join_nearest_parcel_signed_gap_buckets={dict(fallback_signed_gaps)}")
    print(f"missing_join_nearest_parcel_xdiff_buckets={dict(fallback_x_diffs)}")


if __name__ == "__main__":
    main()
