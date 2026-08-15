#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "data" / "properties.json"
PREVIOUS = Path("/tmp/properties-before-refresh.json")
STATUS = ROOT / "data" / "refresh-status.json"


def is_king(p: dict) -> bool:
    return p.get("state") == "WA" and p.get("county") == "King"


def main() -> None:
    if not CURRENT.exists() or not PREVIOUS.exists():
        return

    cur_doc = json.loads(CURRENT.read_text(encoding="utf-8"))
    prev_doc = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    cur_props = list(cur_doc.get("properties") or [])
    prev_king = [p for p in (prev_doc.get("properties") or []) if is_king(p)]
    cur_king = [p for p in cur_props if is_king(p)]

    # King County's official Socrata foreclosure feed occasionally returns a
    # transient service error. A daily refresh must never erase a previously
    # verified 100+ parcel dataset because that source was temporarily down.
    # Treat a collapse below 80% of the prior parcel count as source failure and
    # preserve the entire previous verified King County slice for this run.
    if not prev_king:
        print("King County feed resilience: no previous verified King rows available.")
        return

    threshold = max(1, int(len(prev_king) * 0.80))
    if len(cur_king) >= threshold:
        print(
            f"King County feed resilience: current feed has {len(cur_king)} rows "
            f"vs {len(prev_king)} previous; no whole-slice restore needed."
        )
        return

    non_king = [p for p in cur_props if not is_king(p)]
    cur_doc["properties"] = non_king + prev_king
    CURRENT.write_text(json.dumps(cur_doc, indent=2), encoding="utf-8")

    msg = (
        f"King County feed resilience: official refresh returned only {len(cur_king)} "
        f"rows versus {len(prev_king)} previously verified rows; preserved the prior "
        "verified King County slice instead of publishing a destructive source-outage drop."
    )
    print(msg)

    if STATUS.exists():
        st = json.loads(STATUS.read_text(encoding="utf-8"))
        st.setdefault("notes", []).append(msg)
        for h in st.get("source_health", []):
            if h.get("state") == "WA" and h.get("county") == "King":
                h["status"] = "degraded-preserved"
                h["note"] = (str(h.get("note") or "") + " " + msg).strip()
        STATUS.write_text(json.dumps(st, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
