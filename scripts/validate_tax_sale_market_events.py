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
    # Arizona county-government sources verified by dedicated market publishers.
    "www.apachecountyaz.gov",
    "to.pima.gov",
    "www.to.pima.gov",
    "www.coconino.az.gov",
    "www.yavapaiaz.gov",
    # Nebraska county-government sources verified by dedicated market publishers.
    "frontiercounty.ne.gov",
    "www.frontiercounty.ne.gov",
    "buffalocounty.ne.gov",
    "www.buffalocounty.ne.gov",
    "scottsbluffcountyne.gov",
    "www.scottsbluffcountyne.gov",
    "thurstoncountyne.gov",
    "www.thurstoncountyne.gov",
    "adamscountyne.gov",
    "www.adamscountyne.gov",
    "colfaxcountyne.gov",
    "www.colfaxcountyne.gov",
    "lancaster.ne.gov",
    "www.lancaster.ne.gov",
    "dodgecounty.nebraska.gov",
    "www.dodgecounty.nebraska.gov",
    "treasurer.douglascounty-ne.gov",
}
FORBIDDEN_KEYS = {"owner", "owner_name", "taxpayer", "taxpayer_name", "mailing_name"}


def has_explicit_market_level_boundary(row: dict) -> bool:
    """Require text that clearly says the event is not parcel-level inventory.

    Older verified events use the phrase "not a parcel listing". Newer guarded
    publishers use equivalent wording such as "no parcel inventory ... is
    republished/inferred". Accept either without weakening the market-level-only
    schema or owner/taxpayer protections.
    """
    rules = row.get("important_rules", "").lower()
    return (
        "not a parcel" in rules
        or "no parcel inventory" in rules
        or "parcel inventory" in rules and ("not republished" in rules or "republished or inferred" in rules)
    )


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
        assert has_explicit_market_level_boundary(row), "market-level limitation must be explicit"
    print(f"Validated {len(rows)} market-level official calendar event(s)")


if __name__ == "__main__":
    main()
