#!/usr/bin/env python3
"""Privacy-safe Dubuque 2026 PDF structure diagnostics.

Prints only structural token counts/marker shapes plus whether a line contains a
parcel ID or dollar amount. It never prints source lines, taxpayer names, legal
text, addresses, or other free text from the county publication.
"""

from __future__ import annotations

import re

import refresh_iowa_dubuque_tax_liens as dubuque

# Broader than the production parser on purpose: identify punctuation that the
# PDF text layer places after 1-3 digit tokens without exposing surrounding text.
MARKER_SHAPE_RE = re.compile(r"(?<!\d)(\d{1,3})\s*([^\d\s])")


def main() -> None:
    raw = dubuque.fetch_pdf()
    strategies = dubuque.extract_line_strategies(raw)
    print(f"pdf_bytes={len(raw)} strategies={len(strategies)}")

    for name, lines in strategies.items():
        shape_counts: dict[str, int] = {}
        production_matches = 0
        parcel_lines = 0
        money_lines = 0
        samples: list[tuple[int, str, bool, bool]] = []

        for idx, line in enumerate(lines):
            if dubuque._item_match(line):
                production_matches += 1
            has_parcel = bool(dubuque.PARCEL_RE.search(line))
            has_money = bool(dubuque.MONEY_RE.search(line))
            parcel_lines += int(has_parcel)
            money_lines += int(has_money)

            for match in MARKER_SHAPE_RE.finditer(line):
                number = int(match.group(1))
                if not 1 <= number <= dubuque.REAL_ESTATE_ITEM_COUNT:
                    continue
                punct = match.group(2)
                key = repr(punct)
                shape_counts[key] = shape_counts.get(key, 0) + 1
                if len(samples) < 30:
                    samples.append((number, key, has_parcel, has_money))

        ranked = sorted(shape_counts.items(), key=lambda item: (-item[1], item[0]))[:12]
        print(
            f"{name}: lines={len(lines)} production_item_matches={production_matches} "
            f"parcel_lines={parcel_lines} money_lines={money_lines} marker_shapes={ranked}"
        )
        print(f"{name}: structural_samples={samples}")


if __name__ == "__main__":
    main()
