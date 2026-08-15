#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import json
from datetime import date, datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DETAILS = ROOT / "data" / "tax-lien-properties.json"
INDEX = ROOT / "index.html"

SOURCE_PAGE = "https://www.cochise.az.gov/439/Treasurer"
LIST_PAGE = "https://parcelinquiry.azurewebsites.us/Main/TaxLienSale"
CSV_URL = "https://parcelinquiry.azurewebsites.us/Main/TaxLienList"
PARCEL_INQUIRY = "https://parcelinquirytreasurer.cochise.az.gov/"
PROFILE_ID = "AZ-Cochise-OTC"
MARKER = "Arizona — Cochise County"
UA = "TaxLienGuideBot/2.2 (public tax-lien research; no access-control bypass)"

SUMMARY_ROW = r'''{state:'Arizona — Cochise County',product:'Tax lien / Certificate of Purchase',schedule:'Annual tax-lien sale is held each February. The Treasurer also publishes a nightly-updated list of tax liens currently available for purchase.',availability:'Open now — nightly available-lien list',maxReturn:'16%/yr statutory max',interest:'Arizona tax liens are subject to the statutory 16% annual maximum; auction bidders may accept a lower rate. Current over-the-counter purchase terms must be verified with the Treasurer.',bid:'https://www.cochise.az.gov/439/Treasurer',canadian:'County instructions require a bidder application and tax-identification information. Non-U.S. bidders should confirm accepted documentation with the Treasurer before funding.',itin:'Verify current taxpayer-identification and withholding-document requirements directly with Cochise County.',online:'Annual sale has used GovEase; current available tax liens cannot be purchased online and funds must be sent to the Treasurer.',otc:'YES — the county publishes a nightly-updated available tax-lien list.',deed:'A certificate holder must use judicial foreclosure for a Treasurer deed; the lien is not immediate ownership.',special:'The official available-lien list is separate from Cochise County tax-deed land sales. The guide intentionally omits owner names from the bulk feed.',source:'https://www.cochise.az.gov/439/Treasurer'}'''


def download_rows() -> list[dict]:
    r = requests.get(CSV_URL, headers={"User-Agent": UA, "Accept": "text/csv,text/plain,*/*"}, timeout=60)
    r.raise_for_status()
    reader = csv.DictReader(io.StringIO(r.text.lstrip("\ufeff")))
    out = []
    seen = set()
    for raw in reader:
        parcel = (raw.get("Parcel Number") or "").strip()
        if not parcel or parcel in seen:
            continue
        seen.add(parcel)
        legal = (raw.get("Legal Description") or "").strip() or None
        amount_text = (raw.get("Total Amount") or "").replace(",", "").strip()
        try:
            amount = float(amount_text)
        except ValueError:
            amount = None
        out.append({
            "record_id": f"AZ-Cochise-OTC-{parcel}",
            "profile_id": PROFILE_ID,
            "state": "AZ",
            "county": "Cochise",
            "parcel_id": parcel,
            "legal_description": legal,
            "minimum_bid": amount,
            "opening_bid": None,
            "delinquent_tax_amount": None,
            "fees_costs": "County-published Total Amount is shown as the current listed lien purchase amount; certificate/processing and other applicable fees may be additional. Verify exact amount with the Treasurer before purchase.",
            "sale_status": "Available tax lien — nightly county list",
            "lien_type": "Arizona tax lien / Certificate of Purchase",
            "auction_format": "Over the counter / county assignment",
            "auction_location": "Cochise County Treasurer",
            "auction_url": LIST_PAGE,
            "official_source_url": CSV_URL,
            "direct_listing_url": PARCEL_INQUIRY,
            "maximum_statutory_return": "16%/yr statutory maximum; actual certificate rate may be lower",
            "winning_rate_mechanism": "Current available-lien assignment; annual auction uses Arizona interest-rate bidding rules",
            "redemption_period": "Generally 3 years before judicial foreclosure may begin; verify certificate-specific timing",
            "important_rules": "This is a tax lien, not a tax deed or immediate ownership. Cochise County states tax liens cannot be purchased online and judicial foreclosure is required for a Treasurer deed.",
            "data_source": "Cochise County Treasurer nightly available tax-lien CSV",
            "last_verified": date.today().isoformat(),
            "data_completeness": {
                "published_fields": 8 if legal and amount is not None else 7,
                "tracked_fields": 19,
                "percent": 42 if legal and amount is not None else 37,
            },
            "research_priority": {
                "score": 34,
                "label": "Low research priority",
                "reasons": [
                    "Official parcel ID is published",
                    "Official legal description is published" if legal else "Legal description not published for this row",
                    "County publishes a current available-lien total amount" if amount is not None else "Current purchase amount is not available",
                    "Address, assessed value and property type still require parcel-level public-record research",
                ],
                "disclaimer": "Research-priority ranking only; not a buy recommendation.",
            },
        })
    if not out:
        raise RuntimeError("Cochise official TaxLienList returned no parseable rows")
    return out


def update_details(rows: list[dict]) -> None:
    doc = json.loads(DETAILS.read_text(encoding="utf-8"))
    profiles = doc.setdefault("profiles", {})
    profiles[PROFILE_ID] = {
        "state": "AZ",
        "state_name": "Arizona",
        "county": "Cochise",
        "auction_format": "Over the counter / county assignment",
        "auction_location": "Cochise County Treasurer",
        "auction_url": LIST_PAGE,
        "direct_listing_url": PARCEL_INQUIRY,
        "official_source_url": SOURCE_PAGE,
        "sale_status": "Nightly available tax-lien list",
        "lien_type": "Arizona tax lien / Certificate of Purchase",
        "sale_type": "tax_lien",
        "maximum_statutory_return": "16%/yr statutory maximum; actual certificate rate may be lower",
        "winning_rate_mechanism": "Annual auction follows Arizona interest-rate bidding; current list is available-lien assignment inventory",
        "redemption_period": "Generally 3 years before judicial foreclosure may begin; verify certificate-specific timing",
        "important_rules": "Cochise County states tax liens cannot be purchased online. Certificate holders must use judicial foreclosure for a Treasurer deed. Tax lien inventory is distinct from the county's separate tax-deed land sales.",
        "data_source": "Cochise County Treasurer nightly available tax-lien CSV",
        "last_verified": date.today().isoformat(),
        "source_mode": "live_official_csv",
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
    rows = download_rows()
    update_details(rows)
    update_summary()
    print(f"Cochise County: loaded {len(rows)} live official tax-lien records; owner names intentionally omitted")


if __name__ == "__main__":
    main()
