#!/usr/bin/env python3
"""Fail closed on jurisdiction-level calendar events."""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "data" / "tax-sale-market-events.json"
ALLOWED_HOSTS = {
    "taxsale.baltimorecountymd.gov",
    "dat.maryland.gov",
    "decaturcounty.in.gov",
    "www.decaturcounty.in.gov",
    "hancockin.gov",
    "www.hancockin.gov",
    "hamiltoncounty.in.gov",
    "www.hamiltoncounty.in.gov",
    "allencounty.in.gov",
    "www.allencounty.in.gov",
    "legacy.lakecountyin.org",
}
FORBIDDEN_KEYS = {"owner", "owner_name", "taxpayer", "taxpayer_name", "mailing_name"}


def main() -> None:
    doc = json.loads(EVENTS.read_text(encoding="utf-8"))
    rows = doc.get("properties")
    assert isinstance(rows, list) and rows, "market event feed must contain at least one verified event"
    ids = set()
    for row in rows:
        assert row.get("record_type") == "market_event"
        assert row.get("market_level_only") is True
        assert row.get("sale_type") in {"tax_lien", "tax_deed"}
        assert row.get("record_id") and row["record_id"] not in ids
        ids.add(row["record_id"])
        date.fromisoformat(row["auction_date"])
        assert row.get("sale_date") == row.get("auction_date")
        assert row.get("state") and row.get("county")
        assert not (FORBIDDEN_KEYS & set(row)), "owner/taxpayer fields are forbidden in market-level feed"
        for key in ("official_source_url", "secondary_official_source_url"):
            if row.get(key):
                host = urlparse(row[key]).hostname
                assert host in ALLOWED_HOSTS, f"unapproved source host: {host}"
        assert row.get("official_source_url"), "every market event requires a primary official source"
        assert "not a parcel" in row.get("important_rules", "").lower(), "market-level limitation must be explicit"
    print(f"Validated {len(rows)} market-level official calendar event(s)")


if __name__ == "__main__":
    main()
