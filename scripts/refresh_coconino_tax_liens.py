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


def get(url: str, timeout: int = 45) -> requests.Response:
    r = requests.get(url, headers={"User-Agent": UA, "Accept": "application/pdf,text/html"}, timeout=timeout)
    r.raise_for_status()
    return r


def money(v: str):
    try:
        return float(v.replace(",", ""))
    except Exception:
        return None


def parse_pdf(raw: bytes):
    rows = []
    seen = set()
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=2, y_tolerance=3) or ""
            for line in text.splitlines():
                line = re.sub(r"\s+", " ", line).strip()
                # Current Coconino OTC list starts each parcel row with account + parcel
                # and ends with a purchase amount, optionally followed by an asterisk.
                m = re.match(r"^(R\d{7})\s+([0-9A-Z]+)\s+(.+?)\s+([\d,]+\.\d{2})\s*\*?$", line)
                if not m:
                    continue
                account, parcel, raw_desc, amount_text = m.groups()
                if account in seen:
                    continue
                seen.add(account)
                amount = money(amount_text)
                rows.append({
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
                    "legal_description": raw_desc,
                    "tax_status": "Tax lien certificate — over the counter",
                    "official_url": SOURCE_PAGE,
                    "source_document": OTC_PDF,
                    "auction_url": AUCTION_URL,
                    "title_review_status": "not_reviewed",
                    "data_completeness": "official Coconino OTC tax-lien list",
                    "research_priority": {
                        "score": 45,
                        "label": "Medium research priority",
                        "reasons": [
                            "official over-the-counter tax-lien certificate list",
                            "purchase amount captured from county list",
                            "property/title due diligence not reviewed",
                        ],
                    },
                })
    return rows


def upsert_registry(now: str):
    doc = json.loads(REGISTRY.read_text(encoding="utf-8")) if REGISTRY.exists() else {"counties": []}
    counties = [x for x in doc.get("counties", []) if not (x.get("state") == "AZ" and x.get("county") == "Coconino")]
    counties.append({
        "state": "AZ",
        "state_name": "Arizona",
        "county": "Coconino",
        "source_url": SOURCE_PAGE,
        "auction_url": AUCTION_URL,
        "coverage": "official_otc_tax_lien_feed",
        "sale_type": "tax_lien",
    })
    doc["counties"] = counties
    doc["updated_at"] = now
    REGISTRY.write_text(json.dumps(doc, indent=2), encoding="utf-8")


def main():
    now = datetime.now(timezone.utc).isoformat()
    raw = get(OTC_PDF).content
    rows = parse_pdf(raw)
    if not rows:
        raise SystemExit("Coconino official OTC PDF downloaded but no tax-lien rows parsed")

    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    keep = [p for p in doc.get("properties", []) if not (p.get("state") == "AZ" and p.get("county") == "Coconino" and p.get("sale_type") == "tax_lien")]
    doc["properties"] = keep + rows
    doc["updated_at"] = now
    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    upsert_registry(now)

    if STATUS.exists():
        st = json.loads(STATUS.read_text(encoding="utf-8"))
        health = [x for x in st.get("source_health", []) if not (x.get("state") == "AZ" and x.get("county") == "Coconino")]
        health.append({
            "state": "AZ",
            "county": "Coconino",
            "source_url": SOURCE_PAGE,
            "auction_url": AUCTION_URL,
            "checked_at": now,
            "ok": True,
            "note": f"Parsed {len(rows)} official over-the-counter tax-lien certificates from the current county PDF.",
        })
        st["source_health"] = health
        st["property_count"] = len(doc["properties"])
        st["states_tracked"] = len({p.get("state") for p in doc["properties"] if p.get("state")})
        st["counties_tracked"] = len({(p.get("state"), p.get("county")) for p in doc["properties"] if p.get("state") and p.get("county")})
        st["updated_at"] = now
        st.setdefault("notes", []).append(f"Coconino County AZ: added {len(rows)} current official OTC tax-lien certificates; sale_type=tax_lien keeps them distinct from tax deed/foreclosure rows.")
        STATUS.write_text(json.dumps(st, indent=2), encoding="utf-8")

    print(f"Coconino: parsed and merged {len(rows)} OTC tax-lien rows")


if __name__ == "__main__":
    main()
