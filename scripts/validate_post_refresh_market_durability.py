#!/usr/bin/env python3
"""Fail publication if a required post-refresh tax-lien market silently disappears.

This validator intentionally checks only public market labels and published return-rule
text in index.html. It does not read, collect, or aggregate owner names or other
restricted personal information.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

REQUIRED_PUBLISHERS = [
    "scripts/add_colorado_arapahoe_tax_lien_market.py",
    "scripts/add_colorado_el_paso_tax_lien_market.py",
    "scripts/add_colorado_larimer_tax_lien_market.py",
    "scripts/add_colorado_adams_tax_lien_market.py",
    "scripts/add_colorado_boulder_tax_lien_market.py",
    "scripts/add_colorado_mesa_tax_lien_market.py",
    "scripts/add_colorado_pueblo_tax_lien_market.py",
    "scripts/add_colorado_douglas_tax_lien_market.py",
    "scripts/add_colorado_logan_tax_lien_market.py",
    "scripts/add_colorado_alamosa_tax_lien_market.py",
    "scripts/add_colorado_morgan_tax_lien_market.py",
    "scripts/add_colorado_fremont_tax_lien_market.py",
    "scripts/add_colorado_delta_tax_lien_market.py",
    "scripts/add_colorado_garfield_tax_lien_market.py",
    "scripts/add_colorado_routt_tax_lien_market.py",
    "scripts/add_colorado_chaffee_tax_lien_market.py",
    "scripts/add_colorado_pitkin_tax_lien_market.py",
    "scripts/add_colorado_san_miguel_tax_lien_market.py",
    "scripts/add_colorado_broomfield_tax_lien_market.py",
    "scripts/add_colorado_teller_tax_lien_market.py",
    "scripts/add_colorado_montrose_tax_lien_market.py",
    "scripts/add_colorado_elbert_tax_lien_market.py",
    "scripts/add_colorado_grand_tax_lien_market.py",
    "scripts/add_colorado_archuleta_tax_lien_market.py",
    "scripts/add_colorado_eagle_tax_lien_market.py",
    "scripts/add_colorado_rio_blanco_tax_lien_market.py",
    "scripts/add_colorado_moffat_tax_lien_market.py",
    "scripts/add_florida_hernando_tax_lien_market.py",
    "scripts/add_florida_putnam_tax_lien_market.py",
    "scripts/add_florida_bay_tax_lien_market.py",
    "scripts/add_florida_broward_tax_lien_market.py",
    "scripts/add_iowa_polk_tax_lien_market.py",
    "scripts/add_iowa_dallas_tax_lien_market.py",
    "scripts/add_iowa_pottawattamie_tax_lien_market.py",
    "scripts/add_iowa_black_hawk_tax_lien_market.py",
    "scripts/add_iowa_story_tax_lien_market.py",
    "scripts/add_iowa_warren_tax_lien_market.py",
    "scripts/add_montana_gallatin_tax_lien_market.py",
    "scripts/add_montana_missoula_tax_lien_market.py",
    "scripts/add_montana_cascade_tax_lien_market.py",
    "scripts/add_montana_yellowstone_tax_lien_market.py",
    "scripts/add_montana_lewis_clark_tax_lien_market.py",
    "scripts/add_montana_lake_tax_lien_market.py",
    "scripts/add_montana_flathead_tax_lien_market.py",
    "scripts/add_montana_ravalli_tax_lien_market.py",
    "scripts/add_montana_glacier_tax_lien_market.py",
    "scripts/add_montana_beaverhead_tax_lien_market.py",
    "scripts/add_montana_rosebud_tax_lien_market.py",
    "scripts/add_montana_butte_silver_bow_tax_lien_market.py",
    "scripts/add_montana_richland_tax_lien_market.py",
]
OPTIONAL_PUBLISHERS = ["scripts/add_colorado_weld_tax_lien_market.py"]

REQUIRED_MARKET_RATE_TEXT = {
    "Colorado — Logan County": "14%/yr for 2026 certificate",
}

REQUIRED_MARKET_SAFETY_TEXT = {
    "Iowa — Black Hawk County": "MARKET-LEVEL ONLY",
    "Iowa — Story County": "MARKET-LEVEL ONLY",
    "Iowa — Warren County": "MARKET-LEVEL ONLY",
    "Montana — Gallatin County": "MARKET-LEVEL ONLY",
    "Montana — Missoula County": "MARKET-LEVEL ONLY",
    "Montana — Cascade County": "MARKET-LEVEL ONLY",
    "Montana — Yellowstone County": "MARKET-LEVEL ONLY",
    "Montana — Flathead County": "MARKET-LEVEL ONLY",
    "Montana — Ravalli County": "MARKET-LEVEL ONLY",
    "Montana — Glacier County": "MARKET-LEVEL ONLY",
    "Montana — Beaverhead County": "MARKET-LEVEL ONLY",
    "Montana — Rosebud County": "MARKET-LEVEL ONLY",
    "Montana — Butte-Silver Bow": "MARKET-LEVEL ONLY",
    "Montana — Richland County": "MARKET-LEVEL ONLY",
    "Colorado — Alamosa County": "does not publish amounts due",
    "Colorado — Morgan County": "MARKET-LEVEL ONLY",
    "Colorado — Fremont County": "MARKET-LEVEL ONLY",
    "Colorado — Delta County": "MARKET-LEVEL ONLY",
    "Colorado — Garfield County": "MARKET-LEVEL ONLY",
    "Colorado — Routt County": "MARKET-LEVEL ONLY",
    "Colorado — Chaffee County": "MARKET-LEVEL ONLY",
    "Colorado — Pitkin County": "MARKET-LEVEL ONLY",
    "Colorado — San Miguel County": "MARKET-LEVEL ONLY",
    "Colorado — Broomfield County": "MARKET-LEVEL ONLY",
    "Colorado — Teller County": "MARKET-LEVEL ONLY",
    "Colorado — Montrose County": "MARKET-LEVEL ONLY",
    "Colorado — Elbert County": "MARKET-LEVEL ONLY",
    "Colorado — Grand County": "MARKET-LEVEL ONLY",
    "Colorado — Archuleta County": "MARKET-LEVEL ONLY",
    "Colorado — Eagle County": "MARKET-LEVEL ONLY",
    "Colorado — Rio Blanco County": "MARKET-LEVEL ONLY",
    "Colorado — Moffat County": "MARKET-LEVEL ONLY",
    "Florida — Bay County": "MARKET-LEVEL ONLY",
    "Florida — Broward County": "MARKET-LEVEL ONLY",
}

MARKER_RE = re.compile(r"^MARKER\s*=\s*(.+)$", re.MULTILINE)


def marker_for(script_path: Path) -> str:
    text = script_path.read_text(encoding="utf-8")
    match = MARKER_RE.search(text)
    if not match:
        raise SystemExit(f"{script_path}: missing literal MARKER constant")
    try:
        marker = ast.literal_eval(match.group(1).strip())
    except Exception as exc:
        raise SystemExit(f"{script_path}: MARKER is not a safe string literal: {exc}") from exc
    if not isinstance(marker, str) or not marker.strip():
        raise SystemExit(f"{script_path}: MARKER must be a non-empty string")
    return marker


def market_row(index_text: str, marker: str) -> str | None:
    start = index_text.find("{state:'" + marker + "'")
    if start == -1:
        return None
    end_match = re.search(r"\}\s*(?:,|\n\];)", index_text[start:])
    if not end_match:
        return None
    return index_text[start : start + end_match.end()]


def main() -> None:
    index_text = INDEX.read_text(encoding="utf-8")
    missing: list[str] = []
    checked: list[str] = []

    publisher_paths = [ROOT / path for path in REQUIRED_PUBLISHERS]
    publisher_paths += [ROOT / path for path in OPTIONAL_PUBLISHERS if (ROOT / path).exists()]

    for path in publisher_paths:
        if not path.exists():
            missing.append(f"missing publisher script: {path.relative_to(ROOT)}")
            continue
        marker = marker_for(path)
        checked.append(marker)
        if marker not in index_text:
            missing.append(f"missing generated market row: {marker}")

    for marker, expected_rate in REQUIRED_MARKET_RATE_TEXT.items():
        row = market_row(index_text, marker)
        if row is None:
            missing.append(f"cannot validate rate because market row is missing: {marker}")
            continue
        expected_field = f"maxReturn:'{expected_rate}'"
        if expected_field not in row:
            missing.append(
                f"{marker}: expected verified max-return text {expected_rate!r} was overwritten or missing"
            )

    for marker, expected_text in REQUIRED_MARKET_SAFETY_TEXT.items():
        row = market_row(index_text, marker)
        if row is None:
            missing.append(f"cannot validate safety boundary because market row is missing: {marker}")
            continue
        if expected_text not in row:
            missing.append(
                f"{marker}: required source-redistribution safety text {expected_text!r} is missing"
            )

    if missing:
        raise SystemExit(
            "Post-refresh market durability validation failed:\n- " + "\n- ".join(missing)
        )

    print(f"Verified {len(checked)} required post-refresh tax-lien market rows in index.html")
    for marker in checked:
        print(f"  OK: {marker}")
    for marker, expected_rate in REQUIRED_MARKET_RATE_TEXT.items():
        print(f"  RATE OK: {marker} -> {expected_rate}")
    for marker, expected_text in REQUIRED_MARKET_SAFETY_TEXT.items():
        print(f"  SAFETY OK: {marker} preserves {expected_text!r}")


if __name__ == "__main__":
    main()
