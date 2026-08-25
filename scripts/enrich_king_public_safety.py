#!/usr/bin/env python3
"""Bound King County public-safety enrichment so incomplete official-source refreshes cannot silently publish."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("enrich_king_public_safety_impl.py")
PROPS = Path(__file__).resolve().parents[1] / "data" / "properties.json"
TIMEOUT_SECONDS = 600


def king_public_safety_coverage() -> tuple[int, int]:
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    rows = [
        p for p in (doc.get("properties") or [])
        if p.get("state") == "WA" and p.get("county") == "King"
    ]
    filled = sum(p.get("public_safety_12mo_offenses") not in (None, "") for p in rows)
    return filled, len(rows)


def main() -> None:
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(
            f"King County public-safety enrichment exceeded {TIMEOUT_SECONDS}s; "
            "failing this optional step so the workflow can restore previously verified metrics."
        )
        raise SystemExit(124)

    if result.returncode:
        raise SystemExit(result.returncode)

    # A source can return HTTP 200 yet omit one or more patrol districts. Treat
    # that as an incomplete refresh rather than success so the existing recovery
    # step can restore only previously verified official-source values.
    filled, total = king_public_safety_coverage()
    if total and filled < total:
        print(
            f"King County public-safety refresh is incomplete ({filled}/{total}); "
            "failing closed so verified historical metrics can be restored."
        )
        raise SystemExit(3)

    print(f"King County public-safety refresh verified complete coverage: {filled}/{total}.")


if __name__ == "__main__":
    main()
