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
    "IN-DecaturCounty-2026-market-event": {
        "record_id": "IN-DecaturCounty-2026-market-event",
        "record_type": "market_event",
        "state": "IN",
        "state_name": "Indiana",
        "county": "Decatur County",
        "sale_type": "tax_lien",
        "product_type": "Real property tax sale / tax sale certificate",
        "auction_date": "2026-09-25",
        "sale_date": "2026-09-25",
        "auction_time": "10:00 local time",
        "auction_format": "Public auction at the Decatur County Courthouse meeting room; official notice allows local officials to switch to an electronic ZeusAuction sale on the same date/time with updates posted before the sale",
        "sale_status": "Scheduled by Decatur County for September 25, 2026 beginning at 10:00 AM local time. Parcels can be paid, withheld, or otherwise become ineligible before or during the sale; verify current status with the County before relying on this event.",
        "official_source_url": "https://decaturcounty.in.gov/wp-content/uploads/2026/08/2nd-Advertisement-08-18-26.pdf",
        "secondary_official_source_url": "https://decaturcounty.in.gov/auditor/",
        "important_rules": "Market-level calendar event only. The official notice says the delinquent-tax auction is subject to the right of redemption and minimum bids are prescribed by law but can change before the auction. This is not a parcel listing, not a Sheriff mortgage/judicial foreclosure sale, and not a representation of immediate deed ownership. No owner names or parcel inventory are republished here; no parcel-level minimum bid is inferred or frozen from the changing official list.",
        "data_source": "Decatur County Auditor 2026 Notice of Real Property Tax Sale (second advertisement) and Auditor page",
        "last_verified": "2026-08-26",
        "market_level_only": True,
    },
    "IN-HancockCounty-2026-market-event": {
        "record_id": "IN-HancockCounty-2026-market-event",
        "record_type": "market_event",
        "state": "IN",
        "state_name": "Indiana",
        "county": "Hancock County",
        "sale_type": "tax_lien",
        "product_type": "Tax sale / certificate of lien",
        "auction_date": "2026-09-18",
        "sale_date": "2026-09-18",
        "auction_time": "10:00 ET",
        "auction_format": "Online auction through ZeusAuction conducted by SRI; parcels close in batches and unsold properties may be offered again in a final batch",
        "sale_status": "Scheduled by Hancock County for September 18, 2026 starting at 10:00 AM Eastern. Eligible parcels can change before the sale; verify current status with the County before relying on this event.",
        "official_source_url": "https://www.hancockin.gov/606/Tax-Sale",
        "secondary_official_source_url": "https://www.hancockin.gov/421/Sheriffs-Sale",
        "important_rules": "Market-level calendar event only. Hancock County states the winning bidder buys a certificate of lien, not immediate ownership, and the purchaser has no right to enter or alter the property during the redemption period. This is not a parcel listing and is separate from Sheriff/foreclosure sales. No owner names or parcel inventory are republished here; no parcel-level minimum bid is inferred or frozen from a changing list.",
        "data_source": "Hancock County Treasurer/Auditor Tax Sale page and Hancock County Sheriff sale distinction page",
        "last_verified": "2026-08-26",
        "market_level_only": True,
    },
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
