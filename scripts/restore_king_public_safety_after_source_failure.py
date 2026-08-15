#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

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
]


def main() -> None:
    if not CURRENT.exists() or not PREVIOUS.exists():
        return
    cur = json.loads(CURRENT.read_text(encoding="utf-8"))
    prev = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    prior = {
        str(p.get("parcel_id")): p
        for p in (prev.get("properties") or [])
        if p.get("state") == "WA" and p.get("county") == "King" and p.get("parcel_id")
    }
    restored = 0
    for p in cur.get("properties") or []:
        if p.get("state") != "WA" or p.get("county") != "King":
            continue
        old = prior.get(str(p.get("parcel_id")))
        if not old or old.get("public_safety_12mo_offenses") in (None, ""):
            continue
        changed = False
        for field in FIELDS:
            if p.get(field) in (None, "", []) and old.get(field) not in (None, "", []):
                p[field] = old[field]
                changed = True
        if changed:
            p["public_safety_data_status"] = "Prior verified value preserved after temporary official-source failure"
            restored += 1
    if restored:
        CURRENT.write_text(json.dumps(cur, indent=2), encoding="utf-8")
    print(f"King County public-safety resilience: restored prior verified metrics for {restored} parcel(s).")


if __name__ == "__main__":
    main()
