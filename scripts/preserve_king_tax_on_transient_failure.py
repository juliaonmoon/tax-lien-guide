#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "data" / "properties.json"
PREVIOUS = Path("/tmp/properties-before-refresh.json")
STATUS = ROOT / "data" / "refresh-status.json"

FIELDS = [
    "tax_status",
    "bill_year",
    "tax_due_estimate",
    "delinquent_years",
    "tax_due_basis",
    "tax_due_currency",
    "tax_due_normalized",
]


def main():
    if not CURRENT.exists() or not PREVIOUS.exists():
        return

    cur_doc = json.loads(CURRENT.read_text(encoding="utf-8"))
    prev_doc = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    prev = {
        str(p.get("parcel_id")): p
        for p in prev_doc.get("properties", [])
        if p.get("state") == "WA" and p.get("county") == "King" and p.get("parcel_id")
    }

    restored = 0
    for p in cur_doc.get("properties", []):
        if p.get("state") != "WA" or p.get("county") != "King":
            continue
        note = str(p.get("enrichment_note") or "")
        if "tax lookup" not in note or not any(x in note for x in ("Timeout", "Connection", "HTTPError", "RequestException")):
            continue
        old = prev.get(str(p.get("parcel_id")))
        if not old:
            continue
        changed = False
        for field in FIELDS:
            if p.get(field) in (None, "", []) and old.get(field) not in (None, "", []):
                p[field] = old[field]
                changed = True
        if changed:
            p["tax_data_status"] = "Last verified value preserved after transient King County lookup failure"
            restored += 1

    if restored:
        CURRENT.write_text(json.dumps(cur_doc, indent=2), encoding="utf-8")
        if STATUS.exists():
            st = json.loads(STATUS.read_text(encoding="utf-8"))
            msg = f"King County tax resilience: preserved prior verified tax fields for {restored} parcel(s) after transient lookup failures."
            st.setdefault("notes", []).append(msg)
            for h in st.get("source_health", []):
                if h.get("state") == "WA" and h.get("county") == "King":
                    h["note"] = (h.get("note", "") + " " + msg).strip()
            STATUS.write_text(json.dumps(st, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
