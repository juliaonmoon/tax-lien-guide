#!/usr/bin/env python3
"""Fail publication if a required post-refresh tax-lien market silently disappears.

This validator intentionally checks only public market labels in index.html. It does not
read, collect, or aggregate owner names or other restricted personal information.
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
    "scripts/add_florida_hernando_tax_lien_market.py",
    "scripts/add_florida_putnam_tax_lien_market.py",
]
OPTIONAL_PUBLISHERS = ["scripts/add_colorado_weld_tax_lien_market.py"]

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

    if missing:
        raise SystemExit(
            "Post-refresh market durability validation failed:\n- " + "\n- ".join(missing)
        )

    print(f"Verified {len(checked)} required post-refresh tax-lien market rows in index.html")
    for marker in checked:
        print(f"  OK: {marker}")


if __name__ == "__main__":
    main()
