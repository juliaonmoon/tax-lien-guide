#!/usr/bin/env python3
"""Bound King County public-safety enrichment so incomplete official-source refreshes cannot silently publish."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).with_name("enrich_king_public_safety_impl.py")
PROPS = Path(__file__).resolve().parents[1] / "data" / "properties.json"
TIMEOUT_SECONDS = 600
PUBLIC_SAFETY_FIELDS = [
    "public_safety_12mo_offenses",
    "public_safety_scope",
    "public_safety_period_start",
    "public_safety_period_end",
    "public_safety_source",
    "public_safety_area",
    "public_safety_boundary_source",
    "public_safety_precinct",
    "public_safety_sector",
    "public_safety_rate_published",
    "public_safety_data_status",
]


def king_rows(doc: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        p for p in (doc.get("properties") or [])
        if p.get("state") == "WA" and p.get("county") == "King"
    ]


def king_public_safety_coverage(doc: dict[str, Any] | None = None) -> tuple[int, int]:
    if doc is None:
        doc = json.loads(PROPS.read_text(encoding="utf-8"))
    rows = king_rows(doc)
    filled = sum(p.get("public_safety_12mo_offenses") not in (None, "") for p in rows)
    return filled, len(rows)


def preserve_preexisting_verified_metrics(before: dict[str, Any], after: dict[str, Any]) -> int:
    """Restore only metrics the scoped collector cleared during this invocation.

    This does not invent data or block fresher successful updates. It merely keeps a
    previously verified official-source metric when the scoped KCSO/SPD mapping has
    no current match; downstream official fallback collectors may still overwrite it
    with a newer legitimate value later in the full refresh.
    """
    prior = {
        str(p.get("parcel_id")): p
        for p in king_rows(before)
        if p.get("parcel_id") and p.get("public_safety_12mo_offenses") not in (None, "")
    }
    restored = 0
    for p in king_rows(after):
        if p.get("public_safety_12mo_offenses") not in (None, ""):
            continue
        old = prior.get(str(p.get("parcel_id")))
        if not old:
            continue
        changed = False
        for field in PUBLIC_SAFETY_FIELDS:
            if p.get(field) in (None, "", []) and old.get(field) not in (None, "", []):
                p[field] = old[field]
                changed = True
        if changed:
            p["public_safety_data_status"] = "Prior verified official-source value preserved when scoped refresh had no current geographic match"
            restored += 1
    return restored


def main() -> None:
    before = json.loads(PROPS.read_text(encoding="utf-8"))
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

    after = json.loads(PROPS.read_text(encoding="utf-8"))
    preserved = preserve_preexisting_verified_metrics(before, after)
    if preserved:
        PROPS.write_text(json.dumps(after, indent=2), encoding="utf-8")
        print(f"King County public-safety scoped refresh preserved {preserved} prior verified metric(s) that had no current geographic match.")

    # A source can return HTTP 200 yet omit one or more patrol districts. Treat
    # truly unresolved coverage as incomplete so the workflow can restore only
    # previously verified official-source values from a recent safe snapshot.
    filled, total = king_public_safety_coverage(after)
    if total and filled < total:
        print(
            f"King County public-safety refresh is incomplete ({filled}/{total}); "
            "failing closed so verified historical metrics can be restored."
        )
        raise SystemExit(3)

    print(f"King County public-safety refresh verified complete coverage: {filled}/{total}.")


if __name__ == "__main__":
    main()
