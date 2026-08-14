#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
STATUS = ROOT / "data" / "refresh-status.json"
API = "https://data.kingcounty.gov/resource/dkna-i698.json"
UA = "TaxLienGuideBot/2.0 (public-record repair; no access-control bypass)"


def get_rows(parcel: str):
    # King County real-property account numbers can extend the 10-digit parcel number.
    # Only accept a prefix fallback when it resolves to one unique account number.
    r = requests.get(
        API,
        params={"$limit": 500, "$where": f"account_number like '{parcel}%'"},
        headers={"User-Agent": UA, "Accept": "application/json"},
        timeout=45,
    )
    r.raise_for_status()
    rows = r.json()
    accounts = {str(x.get("account_number") or "").strip() for x in rows if x.get("account_number")}
    return rows if len(accounts) == 1 else []


def amount(v):
    try:
        # The King County receivables feed stores fixed-width monetary values as cents.
        return float(v) / 100.0
    except Exception:
        return 0.0


def year(row):
    try:
        return int(row.get("bill_year") or 0)
    except Exception:
        return 0


def main():
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    wa = [p for p in doc.get("properties", []) if p.get("state") == "WA" and p.get("county") == "King"]
    changed = recovered_value = recovered_tax = 0

    for p in wa:
        if p.get("assessed_value") not in (None, "") and (p.get("tax_status") or p.get("tax_due_estimate") not in (None, "")):
            continue
        parcel = str(p.get("parcel_id") or "").strip()
        if len(parcel) != 10 or not parcel.isdigit():
            continue
        try:
            rows = get_rows(parcel)
        except Exception:
            continue
        if not rows:
            continue

        latest = max(rows, key=year)
        before = json.dumps(p, sort_keys=True, default=str)
        account = str(latest.get("account_number") or "").strip()
        if account:
            p["account_number"] = account

        lv = amount(latest.get("land_value"))
        iv = amount(latest.get("imps_value"))
        if p.get("assessed_value") in (None, "") and (lv or iv):
            p["land_value"] = lv
            p["improvement_value"] = iv
            p["assessed_value"] = lv + iv
            p["market_value"] = lv + iv
            p["value_basis"] = "King County tax receivables unique parcel-prefix account"
            recovered_value += 1

        if not p.get("tax_status"):
            p["tax_status"] = latest.get("tax_status")
        if not p.get("bill_year"):
            p["bill_year"] = latest.get("bill_year")
        if p.get("tax_due_estimate") in (None, ""):
            billed = sum(amount(x.get("billed_amount")) for x in rows)
            paid = sum(amount(x.get("paid_amount")) for x in rows)
            p["tax_due_estimate"] = max(0.0, round(billed - paid, 2))
            p["delinquent_years"] = sorted({x.get("bill_year") for x in rows if x.get("bill_year")})
            recovered_tax += 1

        if json.dumps(p, sort_keys=True, default=str) != before:
            changed += 1

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")

    note = (
        f"King County unique parcel-prefix tax fallback changed {changed}/{len(wa)} rows; "
        f"recovered assessed value {recovered_value}, tax fields {recovered_tax}."
    )
    if STATUS.exists():
        st = json.loads(STATUS.read_text(encoding="utf-8"))
        st.setdefault("notes", []).append(note)
        for h in st.get("source_health", []):
            if h.get("state") == "WA" and h.get("county") == "King":
                h["note"] = (h.get("note") or "") + " " + note
        STATUS.write_text(json.dumps(st, indent=2), encoding="utf-8")
    print(note)


if __name__ == "__main__":
    main()
