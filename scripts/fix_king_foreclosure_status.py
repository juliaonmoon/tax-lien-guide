#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
STATUS = ROOT / "data" / "refresh-status.json"
FORECLOSURE_URL = "https://kingcounty.gov/en/dept/executive-services/buildings-property/treasury-operations/tax-foreclosures/auctions/properties"
RECORDER_URL = "https://kingcounty.gov/en/dept/executive-services/certificates-permits-licenses/records-licensing/recorders-office/records-search"


def main():
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    wa = [p for p in doc.get("properties", []) if p.get("state") == "WA" and p.get("county") == "King"]
    tax_fixed = 0
    legal_marked = 0

    for p in wa:
        # Every WA row in this dataset is sourced from King County's current
        # "Properties in foreclosure status" list. When the receivables feed has
        # no account match, use that official status rather than leaving tax_status blank.
        if not p.get("tax_status"):
            p["tax_status"] = "In tax foreclosure"
            p["tax_status_basis"] = "King County official Properties in foreclosure status list"
            p["tax_status_source_url"] = FORECLOSURE_URL
            tax_fixed += 1

        # Do not fabricate legal descriptions. For the rare GIS-orphan rows,
        # document the legitimate source limitation and point to the Recorder's
        # individual parcel-search service instead of automating/scraping it.
        if not p.get("legal_description"):
            p["legal_description_status"] = (
                "Not present in King County bulk parcel/GIS or WA State Parcels feeds; "
                "individual King County Recorder parcel search required"
            )
            p["legal_description_source_url"] = RECORDER_URL
            legal_marked += 1

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    note = (
        f"King County official foreclosure-status fallback filled tax status for {tax_fixed}/{len(wa)} rows; "
        f"documented individual-Recorder requirement for {legal_marked} missing legal descriptions."
    )
    if STATUS.exists():
        st = json.loads(STATUS.read_text(encoding="utf-8"))
        st.setdefault("notes", []).append(note)
        for h in st.get("source_health", []):
            if h.get("state") == "WA" and h.get("county") == "King":
                h["note"] = ((h.get("note") or "") + " " + note).strip()
        STATUS.write_text(json.dumps(st, indent=2), encoding="utf-8")
    print(note)


if __name__ == "__main__":
    main()
