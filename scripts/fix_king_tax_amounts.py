#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
STATUS = ROOT / "data" / "refresh-status.json"


def main():
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    wa = [p for p in doc.get("properties", []) if p.get("state") == "WA" and p.get("county") == "King"]
    corrected = already = 0

    for p in wa:
        due = p.get("tax_due_estimate")
        if due in (None, ""):
            continue
        if p.get("tax_due_normalized") is True:
            already += 1
            continue
        try:
            p["tax_due_estimate"] = round(max(0.0, float(due)) / 100.0, 2)
        except Exception:
            continue
        p["tax_due_basis"] = "King County Real Property Tax Receivables; billed minus paid; source amount fields use 2 implied decimal places"
        p["tax_due_currency"] = "USD"
        p["tax_due_normalized"] = True
        corrected += 1

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    note = f"King County tax normalization: corrected {corrected}/{len(wa)} rows from fixed-width cents to dollars; {already} rows were already normalized."
    if STATUS.exists():
        st = json.loads(STATUS.read_text(encoding="utf-8"))
        st.setdefault("notes", []).append(note)
        for h in st.get("source_health", []):
            if h.get("state") == "WA" and h.get("county") == "King":
                h["note"] = ((h.get("note") or "") + " " + note).strip()
        STATUS.write_text(json.dumps(st, indent=2), encoding="utf-8")
    print(note)


if __name__ == "__main__":
    main()
