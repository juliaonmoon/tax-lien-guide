#!/usr/bin/env python3
"""Privacy-safe Dubuque 2026 PDF structure diagnostics.

Prints only structural token counts, marker shapes, and distance histograms. It
never prints source lines, taxpayer names, legal text, addresses, or other free
text from the county publication.
"""

from __future__ import annotations

import re
from collections import Counter

import refresh_iowa_dubuque_tax_liens as dubuque

MARKER_SHAPE_RE = re.compile(r"(?<!\d)(\d{1,3})\s*([^\d\s])")


def _nearest_previous_parcel_distance(lines: list[str], item_index: int, limit: int = 40) -> tuple[int | None, bool]:
    """Return backward distance and whether another item marker blocked it first."""
    saw_prior_item = False
    for distance in range(1, min(limit, item_index) + 1):
        line = lines[item_index - distance]
        if dubuque._item_match(line):
            saw_prior_item = True
            break
        if dubuque.PARCEL_RE.search(line):
            return distance, False
    return None, saw_prior_item


def _nearest_money_distance(lines: list[str], item_index: int, limit: int = 20) -> tuple[int | None, bool]:
    """Return forward amount distance and whether another item/parcel blocks it."""
    for distance in range(0, min(limit, len(lines) - item_index - 1) + 1):
        line = lines[item_index + distance]
        if distance and (dubuque._item_match(line) or dubuque.PARCEL_RE.search(line)):
            return None, True
        if dubuque.MONEY_RE.search(line):
            return distance, False
    return None, False


def main() -> None:
    raw = dubuque.fetch_pdf()
    strategies = dubuque.extract_line_strategies(raw)
    print(f"pdf_bytes={len(raw)} strategies={len(strategies)}")

    for name, lines in strategies.items():
        shape_counts: Counter[str] = Counter()
        parcel_distances: Counter[str] = Counter()
        money_distances: Counter[str] = Counter()
        production_matches = 0
        parcel_lines = 0
        money_lines = 0
        candidate_successes = 0

        for idx, line in enumerate(lines):
            match = dubuque._item_match(line)
            if match:
                production_matches += 1
                pdist, pblocked = _nearest_previous_parcel_distance(lines, idx)
                mdist, mblocked = _nearest_money_distance(lines, idx)
                parcel_distances[str(pdist) if pdist is not None else ("blocked_by_item" if pblocked else "none")] += 1
                money_distances[str(mdist) if mdist is not None else ("blocked" if mblocked else "none")] += 1
                if dubuque._candidate_row(lines, idx, match, "diagnostic"):
                    candidate_successes += 1

            has_parcel = bool(dubuque.PARCEL_RE.search(line))
            has_money = bool(dubuque.MONEY_RE.search(line))
            parcel_lines += int(has_parcel)
            money_lines += int(has_money)

            for marker in MARKER_SHAPE_RE.finditer(line):
                number = int(marker.group(1))
                if 1 <= number <= dubuque.REAL_ESTATE_ITEM_COUNT:
                    shape_counts[repr(marker.group(2))] += 1

        print(
            f"{name}: lines={len(lines)} production_item_matches={production_matches} "
            f"candidate_successes={candidate_successes} parcel_lines={parcel_lines} money_lines={money_lines}"
        )
        print(f"{name}: marker_shapes={shape_counts.most_common(12)}")
        print(f"{name}: previous_parcel_distance={parcel_distances.most_common()}")
        print(f"{name}: forward_money_distance={money_distances.most_common()}")


if __name__ == "__main__":
    main()
