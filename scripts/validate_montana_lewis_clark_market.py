#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
MARKER = "Montana — Lewis and Clark County"


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    start = text.find("{state:'" + MARKER + "'")
    if start < 0:
        raise SystemExit(f"Missing generated market row: {MARKER}")
    end = text.find("}\n", start)
    if end < 0:
        end = text.find("},", start)
    row = text[start : end + 1] if end >= 0 else text[start : start + 5000]

    required = [
        "MARKET-LEVEL ONLY",
        "10%/yr statutory delinquent-tax interest",
        "tax-lien assignment certificate is not immediate property ownership",
    ]
    missing = [item for item in required if item not in row]
    if missing:
        raise SystemExit("Lewis and Clark market safety validation failed: " + ", ".join(missing))

    forbidden = ["owner_name:", "taxpayer_name:", "opening_bid:"]
    present = [item for item in forbidden if item in row]
    if present:
        raise SystemExit("Lewis and Clark market row contains forbidden property-level fields: " + ", ".join(present))

    print("Lewis and Clark County market-level safety boundary verified")


if __name__ == "__main__":
    main()
