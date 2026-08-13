#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import pdfplumber
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
PROPS = DATA / "properties.json"
STATUS = DATA / "refresh-status.json"
REGISTRY = DATA / "county-sources.json"

UA = "TaxLienGuideBot/1.1 (daily public-record research prototype; no access-control bypass)"
HEADERS = {"User-Agent": UA}
TODAY = datetime.now(timezone.utc).date()

SOURCES = [
    {
        "state": "FL",
        "state_name": "Florida",
        "county": "Brevard",
        "source_url": "https://www.brevardclerk.us/tax-deed-sales",
        "auction_url": "https://www.brevard.realforeclose.com/",
        "collector": "brevard",
    },
    {
        "state": "TX",
        "state_name": "Texas",
        "county": "Tarrant",
        "source_url": "https://www.tarrantcountytx.gov/en/constables/constable-3/delinquent-tax-sales/monthly-tax-sales-listings.html",
        "auction_url": None,
        "collector": "tarrant",
    },
]


def get(url: str, timeout: int = 30) -> requests.Response:
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return r


def money(v):
    if v in (None, ""):
        return None
    try:
        return float(re.sub(r"[^0-9.\-]", "", str(v)))
    except Exception:
        return None


def score(p: dict) -> dict:
    """Transparent research-priority score. Not a buy recommendation."""
    points = 50
    reasons = []
    av = money(p.get("assessed_value"))
    bid = money(p.get("opening_bid"))
    if av and bid and av > 0:
        ratio = bid / av
        p["bid_to_assessed_ratio"] = round(ratio, 4)
        if ratio <= 0.10:
            points += 20
            reasons.append("opening bid <=10% of assessed value")
        elif ratio <= 0.25:
            points += 10
            reasons.append("opening bid <=25% of assessed value")
        elif ratio >= 0.70:
            points -= 20
            reasons.append("opening bid >=70% of assessed value")
    else:
        reasons.append("assessed-value comparison not yet available")

    if p.get("opening_bid") is not None:
        points += 5
        reasons.append("official opening/minimum bid captured")
    else:
        reasons.append("opening/minimum bid not published in this feed")

    if p.get("sale_status", "").lower() in {"active", "for sale"}:
        points += 5
        reasons.append("currently listed by official source")
    if not p.get("parcel_id"):
        points -= 15
        reasons.append("missing parcel/account identifier")
    if not p.get("official_url"):
        points -= 15
        reasons.append("missing official source link")
    if p.get("title_review_status") in (None, "unknown", "not_reviewed"):
        points -= 10
        reasons.append("title/surviving liens not reviewed")

    points = max(0, min(100, points))
    label = "High research priority" if points >= 70 else "Medium research priority" if points >= 45 else "Low research priority"
    return {"score": points, "label": label, "reasons": reasons}


def parse_date(text: str):
    text = text.strip()
    for fmt in ("%m/%d/%y", "%m/%d/%Y", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    return None


def brevard_properties() -> tuple[list[dict], str]:
    """Find the next Brevard sale and parse its official PDF list."""
    base = SOURCES[0]["source_url"]
    r = get(base)
    soup = BeautifulSoup(r.text, "html.parser")
    candidates = []
    for a in soup.find_all("a", href=True):
        d = parse_date(a.get_text(" ", strip=True))
        if d and d >= TODAY and "tax-deed-sales" in a["href"]:
            candidates.append((d, urljoin(base, a["href"])))
    if not candidates:
        return [], "No upcoming Brevard tax-deed sale page found"
    sale_date, sale_page = sorted(candidates)[0]
    sale = get(sale_page)
    sale_soup = BeautifulSoup(sale.text, "html.parser")
    pdf_url = None
    for a in sale_soup.find_all("a", href=True):
        label = a.get_text(" ", strip=True).lower()
        if ".pdf" in label or "pdf" in a["href"].lower() or "file_id=" in a["href"].lower():
            pdf_url = urljoin(sale_page, a["href"])
            break
    if not pdf_url:
        return [], f"Upcoming Brevard sale {sale_date.isoformat()} found, but no official PDF list found"

    pdf_bytes = get(pdf_url).content
    rows = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables() or []
            for table in tables:
                for raw in table:
                    vals = [re.sub(r"\s+", " ", (x or "")).strip() for x in raw]
                    joined = " | ".join(vals)
                    if not re.search(r"\bACTIVE\b", joined, re.I):
                        continue
                    # Expected columns include Case Status, Case Number, Application Number,
                    # Parcel Number, Sale Date and Opening Bid. Locate by recognizable values.
                    nums = [v for v in vals if re.fullmatch(r"\d{6}", v)]
                    parcel_candidates = [v for v in vals if re.fullmatch(r"\d{7,10}", v)]
                    date_candidates = [v for v in vals if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", v)]
                    money_candidates = [money(v) for v in vals if re.fullmatch(r"\$?[\d,]+(?:\.\d{1,2})?", v)]
                    case_number = nums[0] if nums else None
                    parcel_id = parcel_candidates[0] if parcel_candidates else None
                    opening_bid = None
                    # Opening bid is normally the last money-like table value; exclude small deposit-balance values.
                    plausible = [x for x in money_candidates if x is not None and x >= 100]
                    if plausible:
                        opening_bid = plausible[-1]
                    if not parcel_id:
                        continue
                    rows.append({
                        "state": "FL",
                        "state_name": "Florida",
                        "county": "Brevard",
                        "case_number": case_number,
                        "parcel_id": parcel_id,
                        "sale_date": (date_candidates[-1] if date_candidates else sale_date.strftime("%m/%d/%Y")),
                        "sale_status": "Active",
                        "opening_bid": opening_bid,
                        "assessed_value": None,
                        "address": None,
                        "property_type": None,
                        "official_url": sale_page,
                        "source_document": pdf_url,
                        "auction_url": "https://www.brevard.realforeclose.com/",
                        "title_review_status": "not_reviewed",
                        "data_completeness": "auction list only",
                    })

    # pdfplumber table extraction can vary. Fallback to text parsing for parcel IDs if necessary.
    if not rows:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            text = "\n".join((p.extract_text() or "") for p in pdf.pages)
        pattern = re.compile(r"ACTIVE\s+(\d{6})\s+\d{1,2}/\d{1,2}/\d{4}\s+\d{6}\s+(\d{7,10})\s+(\d{1,2}/\d{1,2}/\d{4})", re.I)
        matches = pattern.findall(text)
        bids = [money(x) for x in re.findall(r"(?m)^\s*(\d{3,}(?:\.\d{1,2})?)\s*$", text)]
        for i, (case_number, parcel_id, sdate) in enumerate(matches):
            rows.append({
                "state": "FL", "state_name": "Florida", "county": "Brevard",
                "case_number": case_number, "parcel_id": parcel_id, "sale_date": sdate,
                "sale_status": "Active", "opening_bid": bids[i] if i < len(bids) else None,
                "assessed_value": None, "address": None, "property_type": None,
                "official_url": sale_page, "source_document": pdf_url,
                "auction_url": "https://www.brevard.realforeclose.com/",
                "title_review_status": "not_reviewed", "data_completeness": "auction list only",
            })
    return rows, f"Parsed {len(rows)} properties from Brevard official sale list for {sale_date.isoformat()}"


def tarrant_properties() -> tuple[list[dict], str]:
    """Parse the next official Tarrant County monthly tax-sale listing."""
    base = SOURCES[1]["source_url"]
    r = get(base)
    soup = BeautifulSoup(r.text, "html.parser")
    candidates = []
    for a in soup.find_all("a", href=True):
        label = a.get_text(" ", strip=True)
        d = parse_date(label.title())
        if d and d >= TODAY:
            candidates.append((d, urljoin(base, a["href"])))
    if not candidates:
        # The page can render labels without links; use known official September 2026 page while current.
        candidates = [(datetime(2026, 9, 1).date(), "https://www.tarrantcountytx.gov/en/constables/constable-3/delinquent-tax-sales/monthly-tax-sales-listings/september-1--2026.html")]
    sale_date, sale_url = sorted(candidates)[0]
    page = get(sale_url)
    psoup = BeautifulSoup(page.text, "html.parser")
    rows = []
    for tr in psoup.find_all("tr"):
        cells = [re.sub(r"\s+", " ", x.get_text(" ", strip=True)) for x in tr.find_all(["td", "th"])]
        if len(cells) < 3:
            continue
        cause, account, status = cells[0], cells[1], cells[2]
        if not re.match(r"^[A-Z]?\d", cause) or not re.fullmatch(r"\d+", account):
            continue
        if "for sale" not in status.lower():
            continue
        rows.append({
            "state": "TX",
            "state_name": "Texas",
            "county": "Tarrant",
            "case_number": cause,
            "parcel_id": account,
            "sale_date": sale_date.strftime("%m/%d/%Y"),
            "sale_status": status,
            "opening_bid": None,
            "assessed_value": None,
            "address": None,
            "property_type": None,
            "official_url": sale_url,
            "source_document": sale_url,
            "auction_url": None,
            "title_review_status": "not_reviewed",
            "data_completeness": "official case/account listing; enrichment pending",
        })
    return rows, f"Parsed {len(rows)} for-sale accounts from Tarrant official listing for {sale_date.isoformat()}"


def main():
    now = datetime.now(timezone.utc).isoformat()
    registry = []
    health = []
    properties = []

    collectors = {"brevard": brevard_properties, "tarrant": tarrant_properties}
    for src in SOURCES:
        registry.append({
            "state": src["state"], "state_name": src["state_name"], "county": src["county"],
            "source_url": src["source_url"], "auction_url": src.get("auction_url"),
            "coverage": "property_feed_prototype",
        })
        h = {"state": src["state"], "county": src["county"], "source_url": src["source_url"],
             "auction_url": src.get("auction_url"), "checked_at": now, "ok": False, "note": ""}
        try:
            get(src["source_url"])
            h["ok"] = True
            rows, note = collectors[src["collector"]]()
            properties.extend(rows)
            h["note"] = note
        except Exception as e:
            h["note"] = f"{type(e).__name__}: {str(e)[:220]}"
        health.append(h)

    for p in properties:
        p["research_priority"] = score(p)

    properties.sort(key=lambda x: (x.get("sale_date") or "", x.get("state") or "", x.get("county") or "", x.get("parcel_id") or ""))
    REGISTRY.write_text(json.dumps({"updated_at": now, "prototype": True, "counties": registry}, indent=2), encoding="utf-8")
    PROPS.write_text(json.dumps({"updated_at": now, "prototype": True, "properties": properties}, indent=2), encoding="utf-8")
    STATUS.write_text(json.dumps({
        "updated_at": now,
        "refresh_frequency": "daily",
        "prototype": True,
        "states_tracked": 2,
        "counties_tracked": 2,
        "official_sources_registered": len(registry),
        "property_count": len(properties),
        "source_health": health,
        "notes": [
            "Prototype scope: Brevard County, Florida and Tarrant County, Texas.",
            "Property rows come from official county sale listings only; no CAPTCHA or access-control bypassing.",
            "Assessed values, addresses, property type, title and surviving-lien review are enrichment fields and may be blank initially.",
            "Research priority is a transparent triage score, not a recommendation to bid or purchase."
        ]
    }, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
