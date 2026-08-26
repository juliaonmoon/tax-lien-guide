#!/usr/bin/env python3
"""Teach calendar.html to include verified jurisdiction-level market events.

Parcel-level rows remain the preferred calendar source.  This extra feed is only
for an officially confirmed sale date when no parcel collector exists, so a
newly researched county is not silently absent from the calendar.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CALENDAR = ROOT / "calendar.html"
MARKER = "data/tax-sale-market-events.json"

OLD_PROMISE = "Promise.all([fetch('data/properties.json',{cache:'no-store'}).then(r=>r.json()),fetch('data/tax-lien-properties.json',{cache:'no-store'}).then(r=>r.json())]).then(([deeds,liens])=>{"
NEW_PROMISE = "Promise.all([fetch('data/properties.json',{cache:'no-store'}).then(r=>r.json()),fetch('data/tax-lien-properties.json',{cache:'no-store'}).then(r=>r.json()),fetch('data/tax-sale-market-events.json',{cache:'no-store'}).then(r=>r.json())]).then(([deeds,liens,marketEvents])=>{"
OLD_MERGE = "merged=[...(deeds.properties||[]),...lienRows]"
NEW_MERGE = "marketRows=(marketEvents.properties||[]),merged=[...(deeds.properties||[]),...lienRows,...marketRows]"


def main() -> None:
    text = CALENDAR.read_text(encoding="utf-8")
    if MARKER in text:
        print("Calendar market-event feed already enabled")
        return
    if OLD_PROMISE not in text:
        raise SystemExit("Calendar data-loading signature changed; refusing unsafe patch")
    if OLD_MERGE not in text:
        raise SystemExit("Calendar merge signature changed; refusing unsafe patch")
    text = text.replace(OLD_PROMISE, NEW_PROMISE, 1)
    text = text.replace(OLD_MERGE, NEW_MERGE, 1)
    CALENDAR.write_text(text, encoding="utf-8")
    print("Enabled market-level official sale events in calendar")


if __name__ == "__main__":
    main()
