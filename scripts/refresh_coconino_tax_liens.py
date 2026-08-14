#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pdfplumber
import requests

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
REGISTRY = ROOT / "data" / "county-sources.json"
STATUS = ROOT / "data" / "refresh-status.json"

SOURCE_PAGE = "https://www.coconino.az.gov/376/Tax-Liens"
OTC_PDF = "https://www.coconino.az.gov/DocumentCenter/View/43"
AUCTION_URL = "https://coconino.arizonataxsale.com/"
UA = "TaxLienGuideBot/2.1 (public tax-lien research; no access-control bypass)"

# Verified against Coconino County's official August 2026 OTC PDF on 2026-08-14.
# The county's document host returns HTTP 403 to GitHub-hosted automation, so this
# snapshot is used only when the normal public download is blocked. Owner names are
# intentionally omitted; parcel/account and purchase amount are enough for screening.
FALLBACK_SNAPSHOT = [
    ("R0006315", "50143062", 2670.91),
    ("R0006649", "40048023", 500.30),
    ("R0006784", "40133028", 1754.04),
    ("R0008866", "20636011", 4467.11),
    ("R0008876", "20636018", 2098.43),
    ("R0012584", "20605036", 5008.10),
    ("R0015203", "50163049", 931.39),
    ("R0015978", "50109093", 3039.31),
    ("R0028724", "40040023", 74.17),
    ("R0031461", "20612037", 5417.44),
    ("R0032428", "40107001F", 409.96),
    ("R0033458", "40039037", 190.19),
    ("R0034210", "30120005H", 87.37),
    ("R0034859", "30221005C", 99.04),
    ("R0036111", "40047029", 74.17),
    ("R0037045", "20611046", 2346.14),
    ("R0042329", "20206038", 3455.18),
    ("R0043006", "50129074", 100.17),
    ("R0047011", "50173043", 2862.31),
    ("R0051506", "50177079", 2793.74),
    ("R0054965", "50318056", 3362.57),
    ("R0055273", "20508035", 1566.13),
    ("R0056041", "50109081", 3039.31),
    ("R0056042", "50109082", 3039.31),
    ("R0056043", "50109083", 3077.09),
    ("R0059711", "40050023", 204.59),
    ("R0062291", "40114140", 67.20),
    ("R0063347", "40114134", 311.02),
    ("R0066944", "40040033", 266.84),
    ("R0147592", "30118049E", 101.16),
    ("R0352909", "20267001E", 320.65),
    ("R1454684", "40133029Z", 610.23),
    ("R1455509", "10804147A", 1678.33),
]


def get(url: str, timeout: int = 45) -> requests.Response:
    r = requests.get(url, headers={"User-Agent": UA, "Accept": "application/pdf,text/html"}, timeout=timeout)
    r.raise_for_status()
    return r


def money(v: str):
    try:
        return float(v.replace(",", ""))
    except Exception:
        return None


def make_row(account: str, parcel: str, amount: float, legal=None, source_mode="live_pdf"):
    return {
        "state": "AZ",
        "state_name": "Arizona",
        "county": "Coconino",
        "sale_type": "tax_lien",
        "sale_type_label": "Tax lien certificate",
        "case_number": account,
        "account_number": account,
        "parcel_id": parcel,
        "sale_date": None,
        "sale_status": "Over-the-counter tax lien available",
        "opening_bid": None,
        "opening_bid_note": "This is a tax-lien certificate list, not a tax-deed opening bid. See lien purchase amount.",
        "lien_purchase_amount": amount,
        "assessed_value": None,
        "market_value": None,
        "address": None,
        "owner": None,
        "property_type": None,
        "legal_description": legal,
        "tax_status": "Tax lien certificate — over the counter",
        "official_url": SOURCE_PAGE,
        "source_document": OTC_PDF,
        "auction_url": AUCTION_URL,
        "title_review_status": "not_reviewed",
        "data_completeness": "official Coconino OTC tax-lien list",
        "source_mode": source_mode,
        "research_priority": {
            "score": 45,
            "label": "Medium research priority",
            "reasons": [
                "official over-the-counter tax-lien certificate list",
                "purchase amount captured from county list",
                "property/title due diligence not reviewed",
            ],
        },
    }


def parse_pdf(raw: bytes):
    rows = []
    seen = set()
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=2, y_tolerance=3) or ""
            for line in text.splitlines():
                line = re.sub(r"\s+", " ", line).strip()
                m = re.match(r"^(R\d{7})\s+([0-9A-Z]+)\s+(.+?)\s+([\d,]+\.\d{2})\s*\*?$", line)
                if not m:
                    continue
                account, parcel, raw_desc, amount_text = m.groups()
                if account in seen:
                    continue
                seen.add(account)
                rows.append(make_row(account, parcel, money(amount_text), raw_desc, "live_pdf"))
    return rows


def fallback_rows():
    return [make_row(a, p, amt, None, "verified_snapshot_2026-08-14") for a, p, amt in FALLBACK_SNAPSHOT]


def upsert_registry(now: str, coverage: str):
    doc = json.loads(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.exists() else {"counties": []}
    counties = [x for x in doc.get("counties", []) if not (x.get("state") == "AZ" and x.get("county") == "Coconino")]
    counties.append({
        "state": "AZ",
        "state_name": "Arizona",
        "county": "Coconino",
        "source_url": SOURCE_PAGE,
        "auction_url": AUCTION_URL,
        "coverage": coverage,
        "sale_type": "tax_lien",
    })
    doc["counties"] = counties
    doc["updated_at"] = now
    REGISTRY.write_text(json.dumps(doc, indent=2), encoding="utf-8")


def main():
    now = datetime.now(timezone.utc).isoformat()
    mode = "live_pdf"
    try:
        rows = parse_pdf(get(OTC_PDF).content)
        if not rows:
            raise RuntimeError("official PDF downloaded but no rows parsed")
    except requests.HTTPError as e:
        if e.response is None or e.response.status_code != 403:
            raise
        # Do not try to evade the county's bot restriction. Use the last verified
        # official snapshot and keep the source link visible for manual verification.
        rows = fallback_rows()
        mode = "verified_snapshot_2026-08-14"
    if not rows:
        raise SystemExit("No Coconino tax-lien rows available")

    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    keep = [p for p in doc.get("properties", []) if not (p.get("state") == "AZ" and p.get("county") == "Coconino" and p.get("sale_type") == "tax_lien")]
    doc["properties"] = keep + rows
    doc["updated_at"] = now
    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    upsert_registry(now, "official_otc_tax_lien_feed" if mode == "live_pdf" else "verified_official_snapshot")

    if STATUS.exists():
        st = json.loads(STATUS.read_text(encoding="utf-8"))
        health = [x for x in st.get("source_health", []) if not (x.get("state") == "AZ" and x.get("county") == "Coconino")]
        note = f"Loaded {len(rows)} Coconino OTC tax-lien certificates from the official county list."
        if mode != "live_pdf":
            note += " County document host blocks GitHub automation (HTTP 403); using the verified 2026-08-14 official snapshot without bypassing that restriction."
        health.append({
            "state": "AZ",
            "county": "Coconino",
            "source_url": SOURCE_PAGE,
            "auction_url": AUCTION_URL,
            "checked_at": now,
            "ok": True,
            "note": note,
        })
        st["source_health"] = health
        st["property_count"] = len(doc["properties"])
        st["states_tracked"] = len({p.get("state") for p in doc["properties"] if p.get("state")})
        st["counties_tracked"] = len({(p.get("state"), p.get("county")) for p in doc["properties"] if p.get("state") and p.get("county")})
        st["updated_at"] = now
        st.setdefault("notes", []).append(note + " sale_type=tax_lien keeps these rows distinct from tax deed/foreclosure rows.")
        STATUS.write_text(json.dumps(st, indent=2), encoding="utf-8")

    print(f"Coconino: merged {len(rows)} OTC tax-lien rows ({mode})")


if __name__ == "__main__":
    main()
