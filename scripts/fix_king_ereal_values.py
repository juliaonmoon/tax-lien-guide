#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
STATUS = ROOT / "data" / "refresh-status.json"
UA = "TaxLienGuideBot/2.4 (public King County assessor value research; no owner aggregation)"
BASE = "https://blue.kingcounty.com/Assessor/eRealProperty/Detail.aspx?ParcelNbr={}"
RECEIVABLES = "https://data.kingcounty.gov/resource/dkna-i698.json"


def money(text):
    if text in (None, ""):
        return None
    m = re.search(r"\$?\s*([0-9][0-9,]*(?:\.\d{1,2})?)", str(text))
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except Exception:
        return None


def extract_values(html):
    soup = BeautifulSoup(html, "html.parser")
    pairs = []
    for tr in soup.find_all("tr"):
        cells = [re.sub(r"\s+", " ", c.get_text(" ", strip=True)).strip() for c in tr.find_all(["th", "td"])]
        if len(cells) >= 2:
            pairs.append((cells[0].lower(), cells[-1]))

    land = impr = total = None
    for label, value in pairs:
        v = money(value)
        if v is None:
            continue
        if "appraised" in label and "land" in label and "value" in label:
            land = v
        elif "appraised" in label and ("improvement" in label or "imps" in label) and "value" in label:
            impr = v
        elif "total appraised" in label or ("appraised value" in label and "land" not in label and "improvement" not in label and "imps" not in label):
            total = v

    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    if land is None:
        m = re.search(r"Appraised\s+Land\s+Value\s*[:$]?\s*\$?([0-9,]+(?:\.\d{1,2})?)", text, re.I)
        if m:
            land = money(m.group(1))
    if impr is None:
        m = re.search(r"Appraised\s+(?:Improvements?|Imps)\s+Value\s*[:$]?\s*\$?([0-9,]+(?:\.\d{1,2})?)", text, re.I)
        if m:
            impr = money(m.group(1))
    if total is None:
        m = re.search(r"Total\s+Appraised\s+Value\s*[:$]?\s*\$?([0-9,]+(?:\.\d{1,2})?)", text, re.I)
        if m:
            total = money(m.group(1))

    if total is None and (land is not None or impr is not None):
        total = (land or 0) + (impr or 0)
    if total is not None and total <= 0:
        total = None
    return land, impr, total


def fetch_with_retry(session, url, *, params=None, attempts=4):
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            r = session.get(url, params=params, timeout=(10, 45), allow_redirects=True)
            r.raise_for_status()
            return r
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_error = e
            if attempt < attempts:
                time.sleep(1.5 * attempt)
                continue
            raise
        except requests.exceptions.HTTPError as e:
            last_error = e
            status = getattr(e.response, "status_code", None)
            if status in (429, 500, 502, 503, 504) and attempt < attempts:
                time.sleep(1.5 * attempt)
                continue
            raise
    if last_error:
        raise last_error


def receivable_values(session, account_number):
    """Return latest positive official land/improvement values for one account."""
    if not account_number:
        return None, None, None, None
    safe_account = str(account_number).replace("'", "''")
    params = {
        "$select": "account_number,bill_year,land_value,imps_value",
        "$where": f"account_number='{safe_account}'",
        "$order": "bill_year DESC",
        "$limit": "25",
    }
    r = fetch_with_retry(session, RECEIVABLES, params=params)
    rows = r.json()
    for row in rows:
        land = money(row.get("land_value"))
        impr = money(row.get("imps_value"))
        total = (land or 0) + (impr or 0)
        if total > 0:
            return land, impr, total, row.get("bill_year")
    return None, None, None, None


def main():
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    wa = [p for p in doc.get("properties", []) if p.get("state") == "WA" and p.get("county") == "King"]
    targets = [p for p in wa if p.get("parcel_id") and p.get("assessed_value") in (None, "")]
    recovered = 0
    recovered_receivables = 0
    recovered_ereal = 0
    reachable = 0
    failures = {}
    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept": "application/json,text/html,application/xhtml+xml"})

    for p in targets:
        pin = str(p["parcel_id"])
        url = BASE.format(pin)
        try:
            land, impr, total, bill_year = receivable_values(session, p.get("account_number"))
            if total is not None:
                if land is not None:
                    p["land_value"] = land
                if impr is not None:
                    p["improvement_value"] = impr
                p["assessed_value"] = total
                p["market_value"] = total
                p["value_basis"] = "King County Real Property Tax Receivables land + improvements"
                p["appraisal_url"] = "https://data.kingcounty.gov/Property-Assessments/Real-Property-Tax-Receivables/dkna-i698"
                p["appraisal_source"] = "King County Real Property Tax Receivables"
                if bill_year:
                    p["appraisal_year"] = str(bill_year)
                recovered += 1
                recovered_receivables += 1
                continue
        except Exception as e:
            key = f"receivables_{type(e).__name__}"
            failures[key] = failures.get(key, 0) + 1

        try:
            r = fetch_with_retry(session, url)
            reachable += 1
            land, impr, total = extract_values(r.text)
            if total is not None:
                if land is not None:
                    p["land_value"] = land
                if impr is not None:
                    p["improvement_value"] = impr
                p["assessed_value"] = total
                p["market_value"] = total
                p["value_basis"] = "King County eReal Property appraised value"
                p["appraisal_url"] = url
                p["appraisal_source"] = "King County Assessor eReal Property"
                recovered += 1
                recovered_ereal += 1
        except Exception as e:
            key = f"ereal_{type(e).__name__}"
            failures[key] = failures.get(key, 0) + 1
        time.sleep(0.15)

    PROPS.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    summary = (
        f"King County assessed-value fallback: attempted {len(targets)} missing-value parcels; "
        f"recovered {recovered} ({recovered_receivables} from official tax receivables, "
        f"{recovered_ereal} from eReal); eReal reachable for {reachable}; failures {failures or 'none'}."
    )
    if STATUS.exists():
        st = json.loads(STATUS.read_text(encoding="utf-8"))
        st.setdefault("notes", []).append(summary)
        for h in st.get("source_health", []):
            if h.get("state") == "WA" and h.get("county") == "King":
                h["note"] = (h.get("note", "") + " " + summary).strip()
        STATUS.write_text(json.dumps(st, indent=2), encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
