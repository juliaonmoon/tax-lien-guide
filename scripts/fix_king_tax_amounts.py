#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
STATUS = ROOT / "data" / "refresh-status.json"
API = "https://data.kingcounty.gov/resource/dkna-i698.json"
UA = "TaxLienGuideBot/2.6 (public King County tax-receivable normalization)"


def raw_amount(v):
    """King County receivable amount fields are fixed-width values with 2 implied decimals."""
    try:
        return float(v or 0)
    except Exception:
        return 0.0


def main():
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    wa = [p for p in doc.get("properties", []) if p.get("state") == "WA" and p.get("county") == "King"]
    corrected = failed = 0

    for p in wa:
        acct = str(p.get("account_number") or "").strip()
        if not acct:
            continue
        try:
            r = requests.get(
                API,
                params={"$limit": 500, "$where": f"account_number='{acct}'"},
                headers={"User-Agent": UA, "Accept": "application/json"},
                timeout=35,
            )
            r.raise_for_status()
            rows = r.json()
        except Exception:
            failed += 1
            continue
        if not rows:
            continue

        billed_cents = sum(raw_amount(x.get("billed_amount")) for x in rows)
        paid_cents = sum(raw_amount(x.get("paid_amount")) for x in rows)
        p["tax_due_estimate"] = round(max(0.0, billed_cents - paid_cents) / 100.0, 2)
        p["tax_due_basis"] = "King County Real Property Tax Receivables; billed minus paid; source fields use 2 implied decimal places"
        p["tax_due_currency"] = "USD"
        p["tax_due_normalized"] = True
        corrected += 1
        time.sleep(0.02)

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    note = f"King County tax normalization: corrected {corrected}/{len(wa)} rows to dollars from 2-decimal fixed-width receivable amounts; {failed} API lookups failed and were left unchanged."
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
