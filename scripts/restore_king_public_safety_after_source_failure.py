#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "data" / "properties.json"
PREVIOUS = Path("/tmp/properties-before-refresh.json")

FIELDS = [
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
]


def king_rows(doc: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        p for p in (doc.get("properties") or [])
        if p.get("state") == "WA" and p.get("county") == "King" and p.get("parcel_id")
    ]


def coverage(doc: dict[str, Any]) -> int:
    return sum(
        p.get("public_safety_12mo_offenses") not in (None, "")
        for p in king_rows(doc)
    )


def git_json(sha: str) -> dict[str, Any] | None:
    try:
        raw = subprocess.check_output(
            ["git", "show", f"{sha}:data/properties.json"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return json.loads(raw)
    except Exception:
        return None


def find_verified_history(minimum: int) -> dict[str, Any] | None:
    """Return a recent committed snapshot with near-complete legitimate coverage.

    This is only a resilience fallback. It never manufactures a metric and only
    copies fields that were already published from official sources.
    """
    try:
        commits = subprocess.check_output(
            ["git", "rev-list", "--max-count=40", "HEAD", "--", "data/properties.json"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).splitlines()
    except Exception:
        return None
    for sha in commits[1:]:
        doc = git_json(sha)
        if doc is None:
            continue
        rows = king_rows(doc)
        if len(rows) >= 140 and coverage(doc) >= minimum:
            print(f"King County public-safety resilience: using verified history {sha[:12]} with {coverage(doc)}/{len(rows)} coverage.")
            return doc
    return None


def restore_from(cur: dict[str, Any], source: dict[str, Any]) -> int:
    prior = {
        str(p.get("parcel_id")): p
        for p in king_rows(source)
    }
    restored = 0
    for p in king_rows(cur):
        old = prior.get(str(p.get("parcel_id")))
        if not old or old.get("public_safety_12mo_offenses") in (None, ""):
            continue
        changed = False
        for field in FIELDS:
            if p.get(field) in (None, "", []) and old.get(field) not in (None, "", []):
                p[field] = old[field]
                changed = True
        if changed:
            p["public_safety_data_status"] = "Prior verified official-source value preserved after incomplete current refresh"
            restored += 1
    return restored


def main() -> None:
    if not CURRENT.exists():
        return
    cur = json.loads(CURRENT.read_text(encoding="utf-8"))
    total = len(king_rows(cur))
    before = coverage(cur)
    restored = 0

    if PREVIOUS.exists():
        try:
            prev = json.loads(PREVIOUS.read_text(encoding="utf-8"))
            restored += restore_from(cur, prev)
        except Exception as exc:
            print(f"King County public-safety resilience: prior-run snapshot unreadable: {exc}")

    # A successful process can still be incomplete (for example when the current
    # patrol-district feed omits a district). If the immediately prior snapshot
    # does not restore full coverage, use a recent committed snapshot that itself
    # proves near-complete official-source coverage. This fills blanks only.
    if coverage(cur) < total:
        historical = find_verified_history(minimum=max(140, total - 5))
        if historical is not None:
            restored += restore_from(cur, historical)

    after = coverage(cur)
    if restored:
        CURRENT.write_text(json.dumps(cur, indent=2), encoding="utf-8")
    print(
        f"King County public-safety resilience: coverage {before}/{total} -> {after}/{total}; "
        f"restored prior verified metrics for {restored} parcel(s)."
    )


if __name__ == "__main__":
    main()
