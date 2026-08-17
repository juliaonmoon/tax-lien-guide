#!/usr/bin/env python3
"""Bound King County public-safety enrichment so transient source/geometry stalls cannot block the full refresh."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("enrich_king_public_safety_impl.py")
TIMEOUT_SECONDS = 600


def main() -> None:
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(
            f"King County public-safety enrichment exceeded {TIMEOUT_SECONDS}s; "
            "failing this optional step so the workflow can restore previously verified metrics."
        )
        raise SystemExit(124)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
