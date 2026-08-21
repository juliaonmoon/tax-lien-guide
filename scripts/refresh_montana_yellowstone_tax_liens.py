#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DETAILS = ROOT / "data" / "tax-lien-properties.json"
INDEX = ROOT / "index.html"

SOURCE_PAGE = "https://www.yellowstonecountymt.gov/treasurer/TaxSales.asp"
CURRENT_URL = "https://www.yellowstonecountymt.gov/treasurer/TaxDel_Export.asp?year=2025&wv=False"
PRIOR_URL = "https://www.yellowstonecountymt.gov/treasurer/TaxDel_Export.asp?year=2024&wv=False"
ADDITIONAL_URL = "https://www.yellowstonecountymt.gov/treasurer/TaxDelSpecial_Export.asp?wv=False"
PROFILE_ID = "MT-Yellowstone-Assignments"
MARKER = "Montana — Yellowstone County"
UA = "TaxLienGuideBot/2.2 (public tax-lien research; no access-control bypass)"

SUMMARY_ROW = r'''{state:'Montana — Yellowstone County',product:'Tax lien / assignment certificate',schedule:'Tax liens attach August 1 each year. An assignment lottery is held in mid-to-late August for tax-code order preference; unassigned liens become available first-come, first-served afterward.',availability:'Open seasonally — remaining assignments available first-come, first-served after the August lottery',maxReturn:'10%/yr statutory interest (MCA 15-16-102) plus a one-time 2% penalty; not bid down',interest:'Montana delinquent taxes draw interest at 5/6 of 1% per month (10%/yr) under MCA 15-16-102, plus a 2% one-time penalty. The county-published Total Due figure explicitly excludes accrued penalty and interest.',bid:'https://www.yellowstonecountymt.gov/treasurer/TaxSales.asp',canadian:'County lottery/assignment paperwork requires a bidder application. Non-U.S. bidders should confirm accepted documentation with the Treasurer before funding.',itin:'Verify current taxpayer-identification and withholding-document requirements directly with Yellowstone County.',online:'Lottery entries and assignment requests are handled directly with the Treasurer; confirm current payment/submission methods with the office.',otc:'Partial — remaining unassigned liens are available first-come, first-served after the annual August lottery.',deed:'A tax deed requires the statutory 3-year redemption period (MCA 15-18-111) to expire and a further tax-deed process; the lien is not immediate ownership.',special:'The county publishes rolling two-year delinquent-list exports plus a separate "Additional Properties" list; the guide merges and deduplicates all three and intentionally omits owner names from the bulk feed.',source:'https://www.yellowstonecountymt.gov/treasurer/TaxSales.asp'}'''

ROW_RE = re.compile(
    r'Tax Year\s*-\s*(?P<year>\d{4})'
    r'|<td\s+align="center">(?P<code>[A-Za-z0-9]+)\s*(?:\((?P<yr_override>\d{4})\))?\s*</td>\s*'
    r'<td>(?P<name>[^<]*)</td>\s*'
    r'<td[^>]*>(?P<h1>[-\d.]*)</td>\s*'
    r'<td[^>]*>(?P<h2>[-\d.]*)</td>\s*'
    r'<td[^>]*>(?P<total>[-\d.]*)</td>'
)


def parse_export(html: str) -> list[dict]:
    rows: list[dict] = []
    current_year: int | None = None
    for m in ROW_RE.finditer(html):
        if m.group("year"):
            current_year = int(m.group("year"))
            continue
        code = m.group("code")
        if not code:
            continue
        year = int(m.group("yr_override")) if m.group("yr_override") else current_year
        if year is None:
            continue
        total_text = (m.group("total") or "").strip()
        try:
            total = float(total_text)
        except ValueError:
            continue
        rows.append({"tax_code": code, "tax_year": year, "total_due": total})
    return rows


def fetch(url: str) -> str:
    r = requests.get(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"}, timeout=60)
    r.raise_for_status()
    return r.text


def download_rows() -> list[dict]:
    htmls = [fetch(PRIOR_URL), fetch(CURRENT_URL), fetch(ADDITIONAL_URL)]
    combined: list[dict] = []
    for html in htmls:
        combined.extend(parse_export(html))

    seen: set[tuple[str, int, float]] = set()
    unique: list[dict] = []
    for row in combined:
        key = (row["tax_code"], row["tax_year"], row["total_due"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)

    unique.sort(key=lambda r: (r["tax_code"], r["tax_year"], r["total_due"]))
    groups: dict[tuple[str, int], list[dict]] = {}
    for row in unique:
        groups.setdefault((row["tax_code"], row["tax_year"]), []).append(row)

    out = []
    for (tax_code, tax_year), members in groups.items():
        multi = len(members) > 1
        for idx, row in enumerate(members, start=1):
            suffix = f"-{idx}" if multi else ""
            record_id = f"{PROFILE_ID}-{tax_code}-{tax_year}{suffix}"
            out.append({
                "record_id": record_id,
                "profile_id": PROFILE_ID,
                "state": "MT",
                "county": "Yellowstone",
                "parcel_id": tax_code,
                "legal_description": None,
                "minimum_bid": row["total_due"],
                "opening_bid": None,
                "delinquent_tax_amount": row["total_due"],
                "fees_costs": "County-published Total Due explicitly excludes accrued penalty and interest (Montana statute: 5/6 of 1%/month plus a one-time 2% penalty under MCA 15-16-102); verify the exact current payoff with the Treasurer before assignment.",
                "sale_status": f"Delinquent tax lien for tax year {tax_year} — rolling county delinquent list",
                "lien_type": "Montana tax lien / assignment certificate",
                "auction_format": "Annual lien assignment lottery each August; remaining liens assigned first-come, first-served afterward",
                "auction_location": "Yellowstone County Treasurer",
                "auction_url": SOURCE_PAGE,
                "official_source_url": CURRENT_URL,
                "direct_listing_url": SOURCE_PAGE,
                "maximum_statutory_return": "10%/yr statutory interest (MCA 15-16-102) plus a one-time 2% penalty; not bid down",
                "winning_rate_mechanism": "Interest rate is fixed by statute, not bid; August lottery determines tax-code assignment order, remaining liens go first-come, first-served",
                "redemption_period": "3 years from the date the lien attaches (MCA 15-18-111)",
                "important_rules": "This is a tax lien, not a tax deed or immediate ownership. A tax-deed process requires the 3-year statutory redemption period to expire first. The published Total Due excludes accrued penalty and interest.",
                "data_source": "Yellowstone County Treasurer delinquent real estate tax lien exports",
                "last_verified": date.today().isoformat(),
                "data_completeness": {
                    "published_fields": 6,
                    "tracked_fields": 19,
                    "percent": 32,
                },
                "research_priority": {
                    "score": 40,
                    "label": "Low research priority",
                    "reasons": [
                        "Official tax code (parcel identifier) is published",
                        "County publishes a current delinquent total-due amount",
                        "No legal description or address published for this row",
                        "Address, assessed value, penalty/interest and property type still require parcel-level public-record research",
                    ],
                    "disclaimer": "Research-priority ranking only; not a buy recommendation.",
                },
            })

    if not out:
        raise RuntimeError(
            "Yellowstone County official delinquent-tax exports returned no parseable rows "
            "(3 fetches: prior-year, current, additional)"
        )
    return out


def existing_rows() -> list[dict]:
    if not DETAILS.exists():
        return []
    doc = json.loads(DETAILS.read_text(encoding="utf-8"))
    return [p for p in doc.get("properties", []) if p.get("profile_id") == PROFILE_ID]


def update_details(rows: list[dict]) -> None:
    doc = json.loads(DETAILS.read_text(encoding="utf-8"))
    profiles = doc.setdefault("profiles", {})
    profiles[PROFILE_ID] = {
        "state": "MT",
        "state_name": "Montana",
        "county": "Yellowstone",
        "auction_format": "Annual lien assignment lottery each August; remaining liens assigned first-come, first-served afterward",
        "auction_location": "Yellowstone County Treasurer",
        "auction_url": SOURCE_PAGE,
        "direct_listing_url": SOURCE_PAGE,
        "official_source_url": SOURCE_PAGE,
        "sale_status": "Rolling delinquent tax-lien list (two-year window plus additional properties)",
        "lien_type": "Montana tax lien / assignment certificate",
        "sale_type": "tax_lien",
        "maximum_statutory_return": "10%/yr statutory interest (MCA 15-16-102) plus a one-time 2% penalty; not bid down",
        "winning_rate_mechanism": "Interest rate is fixed by statute; August lottery determines tax-code assignment order, remaining liens go first-come, first-served",
        "redemption_period": "3 years from the date the lien attaches (MCA 15-18-111)",
        "important_rules": "Tax liens are not tax deeds. A tax-deed process requires the 3-year statutory redemption period to expire. Published Total Due figures exclude accrued penalty and interest.",
        "data_source": "Yellowstone County Treasurer delinquent real estate tax lien exports",
        "last_verified": date.today().isoformat(),
        "source_mode": "live_official_html_export",
    }
    keep = [p for p in doc.get("properties", []) if p.get("profile_id") != PROFILE_ID]
    doc["properties"] = keep + rows
    props = doc["properties"]
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    doc["counts"] = {
        "total_records": len(props),
        "states": len({p.get("state") for p in props if p.get("state")}),
        "counties": len({(p.get("state"), p.get("county")) for p in props if p.get("state") and p.get("county")}),
        "with_parcel_id": sum(bool(p.get("parcel_id")) for p in props),
        "with_address": sum(bool(p.get("property_address")) for p in props),
        "with_auction_date": sum(bool(p.get("auction_date")) for p in props),
        "with_minimum_bid": sum(p.get("minimum_bid") is not None for p in props),
        "with_assessed_value": sum((p.get("assessed_value") is not None or p.get("market_value") is not None) for p in props),
        "with_research_priority": sum(bool(p.get("research_priority")) for p in props),
    }
    DETAILS.write_text(json.dumps(doc, separators=(",", ":")), encoding="utf-8")


def update_summary() -> None:
    text = INDEX.read_text(encoding="utf-8")
    if MARKER in text:
        return
    start = text.find("const rows=[")
    end = text.find("\n];", start)
    if start < 0 or end < 0:
        raise RuntimeError("Could not locate tax-lien summary rows array")
    before, after = text[:end], text[end:]
    insertion = "\n" + SUMMARY_ROW if before.rstrip().endswith(",") else ",\n" + SUMMARY_ROW
    INDEX.write_text(before + insertion + after, encoding="utf-8")


def main() -> None:
    try:
        rows = download_rows()
    except (requests.RequestException, RuntimeError) as exc:
        prior = existing_rows()
        if not prior:
            raise
        update_summary()
        print(
            f"Yellowstone County: live official feed unavailable/unparseable; preserved "
            f"{len(prior)} previously verified records instead of deleting or fabricating data. "
            f"Reason: {exc}"
        )
        return

    update_details(rows)
    update_summary()
    print(f"Yellowstone County: loaded {len(rows)} live official tax-lien records; owner names intentionally omitted")


if __name__ == "__main__":
    main()
