#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"

# City of Bellevue / Bellevue Police Department year-end 2025 report,
# published February 25, 2026. This is a citywide annual fallback, not a
# neighborhood or parcel-level crime rate. Keep that scope explicit so it is
# not compared as if it were the KCSO/SPD neighborhood/district metrics.
SOURCE = "https://bellevuewa.gov/city-news/crime-drops-again"
PERIOD_START = "2025-01-01"
PERIOD_END = "2025-12-31"
OFFENSES = 5698


def main() -> None:
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    filled = 0

    for p in doc.get("properties", []):
        if p.get("state") != "WA" or p.get("county") != "King":
            continue
        if str(p.get("city") or "").strip().upper() != "BELLEVUE":
            continue

        # Do not overwrite a more granular official metric if one becomes
        # available later. This only fills currently blank Bellevue rows.
        if p.get("public_safety_12mo_offenses") not in (None, ""):
            continue

        p["public_safety_12mo_offenses"] = OFFENSES
        p["public_safety_area"] = "BELLEVUE"
        p["public_safety_scope"] = (
            "Bellevue Police Department citywide year-end reported-crime total for 2025; "
            "annual raw count, not a parcel/neighborhood metric and not population-adjusted"
        )
        p["public_safety_period_start"] = PERIOD_START
        p["public_safety_period_end"] = PERIOD_END
        p["public_safety_source"] = SOURCE
        p.pop("public_safety_boundary_source", None)
        filled += 1

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"Bellevue official annual public-safety fallback filled {filled} King County parcels")


if __name__ == "__main__":
    main()
