#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
OUT = ROOT / "data" / "king-tax-audit.json"
API = "https://data.kingcounty.gov/resource/dkna-i698.json"
UA = "TaxLienGuideBot/2.5 (public tax-receivable validation)"
SAMPLE_PARCELS = ["0121059036", "0222029066", "0200000045"]


def n(v):
    try:
        return float(v)
    except Exception:
        return 0.0


def main():
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    by_pin = {str(p.get("parcel_id")): p for p in doc.get("properties", []) if p.get("state") == "WA" and p.get("county") == "King"}
    report = []
    for pin in SAMPLE_PARCELS:
        p = by_pin.get(pin, {})
        acct = str(p.get("account_number") or pin)
        r = requests.get(API, params={"$limit": 500, "$where": f"account_number='{acct}'"}, headers={"User-Agent": UA, "Accept": "application/json"}, timeout=45)
        r.raise_for_status()
        rows = r.json()
        billed = sum(n(x.get("billed_amount")) for x in rows)
        paid = sum(n(x.get("paid_amount")) for x in rows)
        by_year = {}
        for x in rows:
            y = str(x.get("bill_year") or "")
            by_year.setdefault(y, {"billed": 0.0, "paid": 0.0, "records": 0})
            by_year[y]["billed"] += n(x.get("billed_amount"))
            by_year[y]["paid"] += n(x.get("paid_amount"))
            by_year[y]["records"] += 1
        report.append({
            "parcel_id": pin,
            "account_number": acct,
            "current_site_tax_due_estimate": p.get("tax_due_estimate"),
            "record_count": len(rows),
            "raw_billed_sum": billed,
            "raw_paid_sum": paid,
            "raw_difference": billed - paid,
            "raw_difference_div_100": (billed - paid) / 100.0,
            "by_year": by_year,
            "sample_records": [{k: x.get(k) for k in ("bill_year", "receivable_type", "billed_amount", "paid_amount", "tax_status", "account_status")} for x in rows[:12]],
        })
    OUT.write_text(json.dumps({"samples": report}, indent=2), encoding="utf-8")
    print(json.dumps({"samples": report}, indent=2))


if __name__ == "__main__":
    main()
