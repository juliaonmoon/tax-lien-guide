#!/usr/bin/env python3
"""Privacy-safe Dubuque 2026 PDF structure diagnostics.

Prints only structural token counts, distance histograms, and candidate-ambiguity
counts. It never prints source lines, taxpayer names, parcel IDs, dollar values,
legal text, addresses, or other free text from the county publication.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict

import refresh_iowa_dubuque_tax_liens as dubuque

MARKER_SHAPE_RE = re.compile(r"(?<!\d)(\d{1,3})\s*([^\d\s])")


def _nearest_previous_parcel_distance(lines: list[str], item_index: int, limit: int = 40) -> tuple[int | None, bool]:
    saw_prior_item = False
    for distance in range(1, min(limit, item_index) + 1):
        line = lines[item_index - distance]
        if dubuque._sale_item_match(line):
            saw_prior_item = True
            break
        if dubuque.PARCEL_RE.search(line):
            return distance, False
    return None, saw_prior_item


def _nearest_money_distance(lines: list[str], item_index: int, limit: int = 20) -> tuple[int | None, bool]:
    for distance in range(0, min(limit, len(lines) - item_index - 1) + 1):
        line = lines[item_index + distance]
        if distance and (dubuque._sale_item_match(line) or dubuque.PARCEL_RE.search(line)):
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
        raw_item_matches = 0
        sale_item_matches = 0
        parcel_lines = 0
        money_lines = 0
        candidate_successes = 0
        by_item: dict[int, list[tuple[str, float]]] = defaultdict(list)

        for idx, line in enumerate(lines):
            broad = dubuque._item_match(line)
            if broad:
                raw_item_matches += 1
            match = dubuque._sale_item_match(line)
            if match:
                sale_item_matches += 1
                pdist, pblocked = _nearest_previous_parcel_distance(lines, idx)
                mdist, mblocked = _nearest_money_distance(lines, idx)
                parcel_distances[str(pdist) if pdist is not None else ("blocked_by_item" if pblocked else "none")] += 1
                money_distances[str(mdist) if mdist is not None else ("blocked" if mblocked else "none")] += 1
                candidate = dubuque._candidate_row(lines, idx, match, "diagnostic")
                if candidate:
                    candidate_successes += 1
                    by_item[int(candidate["sale_item_number"])].append(
                        (candidate["parcel_id"], candidate["delinquent_tax_amount"])
                    )

            has_parcel = bool(dubuque.PARCEL_RE.search(line))
            has_money = bool(dubuque.MONEY_RE.search(line))
            parcel_lines += int(has_parcel)
            money_lines += int(has_money)

            for marker in MARKER_SHAPE_RE.finditer(line):
                number = int(marker.group(1))
                if 1 <= number <= dubuque.REAL_ESTATE_ITEM_COUNT:
                    shape_counts[repr(marker.group(2))] += 1

        ambiguity = Counter()
        duplicate_shapes = Counter()
        for candidates in by_item.values():
            keys = Counter(candidates)
            unique_count = len(keys)
            if unique_count == 1:
                ambiguity["one_unique"] += 1
            elif unique_count == 2:
                ambiguity["two_unique"] += 1
            elif unique_count >= 3:
                ambiguity["three_plus_unique"] += 1
            top = keys.most_common()
            if top:
                winner_votes = top[0][1]
                runner_votes = top[1][1] if len(top) > 1 else 0
                if winner_votes > runner_votes:
                    duplicate_shapes[f"strict_majority_{winner_votes}_to_{runner_votes}"] += 1
                else:
                    duplicate_shapes["tie"] += 1
        ambiguity["items_with_any_candidate"] = len(by_item)
        ambiguity["items_without_candidate"] = dubuque.REAL_ESTATE_ITEM_COUNT - len(by_item)

        print(
            f"{name}: lines={len(lines)} raw_item_matches={raw_item_matches} sale_item_matches={sale_item_matches} "
            f"candidate_successes={candidate_successes} parcel_lines={parcel_lines} money_lines={money_lines}"
        )
        print(f"{name}: marker_shapes={shape_counts.most_common(12)}")
        print(f"{name}: previous_parcel_distance={parcel_distances.most_common()}")
        print(f"{name}: forward_money_distance={money_distances.most_common()}")
        print(f"{name}: candidate_ambiguity={dict(ambiguity)} majority_shapes={dict(duplicate_shapes)}")


if __name__ == "__main__":
    main()
