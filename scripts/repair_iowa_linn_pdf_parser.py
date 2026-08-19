#!/usr/bin/env python3
"""Run Linn County's existing Excel-first collector with a safer PDF item matcher.

The official 2026 Linn County PDF can place extraction artifacts after the
15-digit parcel number on an item's first line.  The original PDF parser
required the parcel number to be the final token on that line, which caused
valid real-estate items to be skipped.  This wrapper relaxes only that
syntactic assumption; taxpayer/owner text is still discarded by the existing
parser and mobile-home item 1569+ remains excluded.
"""
from __future__ import annotations

import re

import refresh_iowa_linn_tax_liens as pdf_linn
import refresh_iowa_linn_tax_liens_xlsx as xlsx_linn

# Keep the same capture groups expected by parse_real_estate_rows(), but allow
# harmless trailing extraction text after the official 15-digit parcel ID.
RELAXED_ITEM = re.compile(r"^\s*(\d{1,4})\.\s+.*?\b(\d{15})\b(?:\s+.*)?$")


def install_parser_fix() -> None:
    pdf_linn.ITEM = RELAXED_ITEM


def main() -> None:
    install_parser_fix()
    xlsx_linn.main()


if __name__ == "__main__":
    main()
