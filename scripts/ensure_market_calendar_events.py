#!/usr/bin/env python3
"""Idempotently restore verified jurisdiction-level calendar events.

This is deliberately limited to market-level metadata from official sources. It
must not add parcel inventory, owner/taxpayer names, or inferred bid amounts.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS_PATH = ROOT / "data" / "tax-sale-market-events.json"

VERIFIED_EVENTS = {
    "IN-HamiltonCounty-2026-market-event": {
        "record_id": "IN-HamiltonCounty-2026-market-event",
        "record_type": "market_event",
        "state": "IN",
        "state_name": "Indiana",
        "county": "Hamilton County",
        "sale_type": "tax_lien",
        "product_type": "Real property tax sale / tax sale certificate",
        "auction_date": "2026-10-08",
        "sale_date": "2026-10-08",
        "auction_time": "10:00 ET",
        "auction_format": "Public auction at the Hamilton County Historic Courthouse; official notice allows local officials to switch to an electronic sale with location updates published before the sale",
        "sale_status": "Scheduled by Hamilton County for October 8, 2026 at 10:00 AM. The official property listing is updated periodically and parcels may be withdrawn; verify current status with the County before relying on this event.",
        "official_source_url": "https://hamiltoncounty.in.gov/452/Real-Property-Tax-Sale",
        "secondary_official_source_url": "https://www.hamiltoncounty.in.gov/1380/Tax-Sale-Notice-2026",
        "important_rules": "Market-level calendar event only. Hamilton County's delinquent real-property tax sale is subject to the right of redemption and is not a parcel listing, Sheriff foreclosure sale, or representation of immediate deed ownership. No owner names or parcel inventory are republished here; minimum bids are not copied because the County states they can change before auction.",
        "data_source": "Hamilton County Auditor/Treasurer Real Property Tax Sale and 2026 official tax-sale notice",
        "last_verified": "2026-08-26",
        "market_level_only": True,
    }
}


def main() -> None:
    doc = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
    rows = doc.get("properties")
    if not isinstance(rows, list):
        raise SystemExit("market event feed properties must be a list")

    by_id = {row.get("record_id"): i for i, row in enumerate(rows) if row.get("record_id")}
    changed = False
    for record_id, verified in VERIFIED_EVENTS.items():
        if record_id in by_id:
            idx = by_id[record_id]
            if rows[idx] != verified:
                rows[idx] = verified
                changed = True
        else:
            rows.append(verified)
            changed = True

    # Stable ordering keeps generated diffs deterministic.
    rows.sort(key=lambda row: (row.get("auction_date", ""), row.get("state", ""), row.get("county", ""), row.get("record_id", "")))

    if changed:
        doc["updated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        EVENTS_PATH.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("Restored/refreshed verified market calendar events")
    else:
        print("Verified market calendar events already present")


if __name__ == "__main__":
    main()
