#!/usr/bin/env python3
"""Run the core property refresh with a hard process-group timeout.

GitHub Actions step timeouts can leave descendant processes alive long enough to
write stale generated files after the workflow has restored a verified snapshot.
Run refresh_properties.py in its own process group and terminate the entire group
on timeout so a timed-out core refresh cannot overwrite later WA enrichment.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("refresh_properties.py")
TIMEOUT_SECONDS = 14 * 60
GRACE_SECONDS = 10


def main() -> None:
    proc = subprocess.Popen(
        [sys.executable, str(SCRIPT)],
        start_new_session=True,
    )
    try:
        code = proc.wait(timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        print(
            f"Core property refresh exceeded {TIMEOUT_SECONDS}s; terminating its entire process group "
            "before verified data is restored."
        )
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
        raise SystemExit(124)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
