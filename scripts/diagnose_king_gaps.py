#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
OUT = ROOT / "data" / "king-gaps.json"

FIELDS = {
    "address": lambda p: bool(str(p.get("address") or "").strip()),
    "city_zip": lambda p: bool(str(p.get("city") or "").strip()) and bool(str(p.get("zip") or "").strip()),
    "coordinates": lambda p: p.get("latitude") is not None and p.get("longitude") is not None,
    "assessed_value": lambda p: p.get("assessed_value") not in (None, "") and float(p.get("assessed_value") or 0) > 0,
    "property_type": lambda p: bool(str(p.get("property_type") or "").strip()),
    "legal_description": lambda p: bool(str(p.get("legal_description") or "").strip()),
    "tax_status": lambda p: bool(str(p.get("tax_status") or "").strip()) or p.get("tax_due_estimate") not in (None, ""),
    "neighborhood": lambda p: p.get("neighborhood_value_score") is not None,
    "opening_bid": lambda p: p.get("opening_bid") not in (None, ""),
}


def main():
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    wa = [p for p in doc.get("properties", []) if p.get("state") == "WA" and p.get("county") == "King"]
    gaps = []
    counter = Counter()
    by_field = defaultdict(list)
    address_status_counts = Counter()
    for p in wa:
        missing = [name for name, test in FIELDS.items() if not test(p)]
        counter.update(missing)
        for field in missing:
            by_field[field].append(str(p.get("parcel_id") or ""))
        if "address" in missing:
            address_status_counts[str(p.get("address_status") or "Unclassified")] += 1
        if missing:
            gaps.append({
                "parcel_id": p.get("parcel_id"),
                "missing": missing,
                "address_status": p.get("address_status"),
                "coordinate_source": p.get("coordinate_source"),
                "city": p.get("city"),
                "zip": p.get("zip"),
                "property_type": p.get("property_type"),
                "assessed_value": p.get("assessed_value"),
                "land_value": p.get("land_value"),
                "improvement_value": p.get("improvement_value"),
                "value_basis": p.get("value_basis"),
                "legal_description": p.get("legal_description"),
                "tax_status": p.get("tax_status"),
                "tax_due_estimate": p.get("tax_due_estimate"),
                "enrichment_note": p.get("enrichment_note"),
            })
    OUT.write_text(json.dumps({
        "source_updated_at": doc.get("updated_at"),
        "king_count": len(wa),
        "missing_counts": dict(sorted(counter.items())),
        "missing_parcel_ids_by_field": {k: v for k, v in sorted(by_field.items())},
        "missing_address_status_counts": dict(sorted(address_status_counts.items())),
        "gaps": gaps,
    }, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}: {len(gaps)} rows with at least one tracked gap")


if __name__ == "__main__":
    main()
