#!/usr/bin/env python3
"""Validate proof-based project-management query status."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "project-management.json"
ALLOWED_TYPES = {"tax_lien", "tax_deed", "both"}
ALLOWED_STATUSES = {
    "working", "partial", "snapshot", "zero_active", "blocked", "planned",
    "information_only", "not_started", "in_progress",
}
ALLOWED_PRIORITIES = {"P0", "P1", "P2", "P3"}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    errors: list[str] = []
    queries = payload.get("queries")
    require(isinstance(queries, list) and bool(queries), "queries must be a non-empty list", errors)
    seen: set[str] = set()

    for index, row in enumerate(queries or []):
        prefix = f"queries[{index}]"
        query_id = row.get("id")
        require(isinstance(query_id, str) and bool(query_id), f"{prefix}: id is required", errors)
        if isinstance(query_id, str):
            require(query_id not in seen, f"{prefix}: duplicate id {query_id}", errors)
            seen.add(query_id)
            prefix = query_id

        require(row.get("type") in ALLOWED_TYPES, f"{prefix}: invalid type", errors)
        require(row.get("status") in ALLOWED_STATUSES, f"{prefix}: invalid status", errors)
        require(row.get("priority") in ALLOWED_PRIORITIES, f"{prefix}: invalid priority", errors)
        require(isinstance(row.get("query"), bool), f"{prefix}: query must be boolean", errors)
        require(isinstance(row.get("records"), int) and row.get("records", -1) >= 0, f"{prefix}: records must be a non-negative integer", errors)
        require(bool(row.get("next_action")), f"{prefix}: next_action is required", errors)

        if row.get("query"):
            collector = row.get("collector_module")
            require(bool(collector), f"{prefix}: developed query requires collector_module", errors)
            if collector:
                require((ROOT / collector).is_file(), f"{prefix}: collector_module does not exist: {collector}", errors)
            success = row.get("last_success_at")
            require(bool(success), f"{prefix}: developed query requires last_success_at", errors)
            if success:
                try:
                    datetime.fromisoformat(success.replace("Z", "+00:00"))
                except ValueError:
                    errors.append(f"{prefix}: last_success_at is not ISO-8601")

        if row.get("verification") == "verified":
            test_module = row.get("test_module")
            require(row.get("query") is True, f"{prefix}: verified requires query=true", errors)
            require(row.get("records", 0) > 0, f"{prefix}: verified requires nonzero property records", errors)
            require(bool(test_module), f"{prefix}: verified requires test_module", errors)
            if test_module:
                require((ROOT / test_module).is_file(), f"{prefix}: test_module does not exist: {test_module}", errors)

    if errors:
        raise SystemExit("Project-management validation failed:\n- " + "\n- ".join(errors))
    print(f"Validated {len(queries)} project query targets; {sum(1 for row in queries if row.get('query'))} developed queries.")


if __name__ == "__main__":
    main()
