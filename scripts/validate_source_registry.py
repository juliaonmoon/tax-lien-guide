#!/usr/bin/env python3
"""Validate the nationwide source registry, and enforce evidence for property_query=true rows."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "source-registry.json"
ALLOWED_STATUSES = {
    "live", "snapshot", "zero_active", "identified", "blocked", "not_started", "not_applicable",
}
REQUIRED_KEYS = {
    "state", "county_or_locality", "sale_system", "official_information_url",
    "current_list_url", "assessor_url", "collector_status", "property_query",
    "last_attempt_at", "last_success_at", "current_record_count", "blocker",
    "collector_module", "test_module",
}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    errors: list[str] = []
    jurisdictions = payload.get("jurisdictions")
    require(isinstance(jurisdictions, list) and bool(jurisdictions), "jurisdictions must be a non-empty list", errors)

    seen: set[tuple] = set()
    total_records = 0
    for index, row in enumerate(jurisdictions or []):
        prefix = f"jurisdictions[{index}] ({row.get('state')}/{row.get('county_or_locality')})"
        missing = REQUIRED_KEYS - row.keys()
        require(not missing, f"{prefix}: missing keys {sorted(missing)}", errors)

        require(bool(row.get("state")), f"{prefix}: state is required", errors)
        require(bool(row.get("county_or_locality")), f"{prefix}: county_or_locality is required", errors)
        require(row.get("collector_status") in ALLOWED_STATUSES, f"{prefix}: invalid collector_status", errors)
        require(isinstance(row.get("property_query"), bool), f"{prefix}: property_query must be boolean", errors)
        require(
            isinstance(row.get("current_record_count"), int) and row.get("current_record_count", -1) >= 0,
            f"{prefix}: current_record_count must be a non-negative integer", errors,
        )

        key = (row.get("state"), row.get("county_or_locality"), row.get("sale_system"))
        require(key not in seen, f"{prefix}: duplicate (state, county_or_locality, sale_system)", errors)
        seen.add(key)

        # Evidence enforcement: property_query=true is a claim that executable
        # collector code produces real records. It must be backed by a real
        # collector module on disk and a nonzero verified record count.
        if row.get("property_query"):
            require(row.get("collector_status") in {"live", "snapshot", "zero_active"},
                    f"{prefix}: property_query=true requires collector_status of live/snapshot/zero_active", errors)
            collector = row.get("collector_module")
            require(bool(collector), f"{prefix}: property_query=true requires collector_module", errors)
            if collector:
                require((ROOT / collector).is_file(), f"{prefix}: collector_module does not exist: {collector}", errors)
            if row.get("collector_status") != "zero_active":
                require(row.get("current_record_count", 0) > 0,
                        f"{prefix}: property_query=true (non zero_active) requires current_record_count > 0", errors)
            success = row.get("last_success_at")
            require(bool(success), f"{prefix}: property_query=true requires last_success_at", errors)
            if success:
                try:
                    datetime.fromisoformat(str(success).replace("Z", "+00:00"))
                except ValueError:
                    errors.append(f"{prefix}: last_success_at is not ISO-8601")
        else:
            require(row.get("current_record_count", 0) == 0,
                    f"{prefix}: property_query=false rows must not claim a nonzero current_record_count", errors)

        if row.get("collector_status") == "blocked":
            require(bool(row.get("blocker")), f"{prefix}: blocked rows require a blocker explanation", errors)

        total_records += row.get("current_record_count") or 0

    summary = payload.get("summary", {})
    if isinstance(summary, dict) and "total_verified_property_records" in summary:
        require(
            summary["total_verified_property_records"] == total_records,
            f"summary.total_verified_property_records ({summary.get('total_verified_property_records')}) "
            f"does not match the sum of current_record_count across jurisdictions ({total_records})",
            errors,
        )

    if errors:
        raise SystemExit("Source registry validation failed:\n- " + "\n- ".join(errors))
    live_count = sum(1 for row in jurisdictions if row.get("property_query"))
    print(f"Validated {len(jurisdictions)} registry jurisdictions; {live_count} with property_query=true; {total_records} total verified records.")


if __name__ == "__main__":
    main()
