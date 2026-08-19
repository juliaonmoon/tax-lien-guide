#!/usr/bin/env python3
"""Resilient Johnson County, Iowa 2026 tax-sale publication parser.

The county PDF is a newspaper proof and text extraction can separate a taxpayer
name/parcel line from its numbered sale item.  This parser anchors on the
official numbered real-estate items (1-799), searches only the preceding item
boundary for the 10-digit parcel ID, and never stores taxpayer/owner names.
It stops before the separate MOBILE HOMES section.
"""

from __future__ import annotations

import re
from datetime import date

import requests

from refresh_iowa_johnson_tax_liens import (
    ITEM_START,
    MONEY,
    PROFILE_ID,
    existing_rows,
    extract_text,
    fetch_pdf,
    update_details,
)

PARCEL_ANYWHERE = re.compile(r"\b(\d{10})\b")


def parse_real_estate_rows_by_item(text: str, verified: str) -> list[dict]:
    text = text.split("\nMOBILE HOMES", 1)[0]
    lines = [line.rstrip() for line in text.splitlines()]
    rows: list[dict] = []
    seen_items: set[int] = set()
    last_exact_public_bidder_marker = -1

    for item_index, line in enumerate(lines):
        if "PUBLIC BIDDER TAX SALE" in line:
            last_exact_public_bidder_marker = item_index

        match = ITEM_START.match(line)
        if not match:
            continue
        item_number = int(match.group(1))
        if not (1 <= item_number <= 799) or item_number in seen_items:
            continue

        # Find the nearest parcel identifier between this item and the prior
        # numbered item.  Long taxpayer names can cause the parcel ID to be
        # extracted onto a separate line, so fixed look-behind distances are
        # unreliable.  We never retain the surrounding taxpayer text.
        parcel = None
        j = item_index - 1
        while j >= 0:
            if ITEM_START.match(lines[j]):
                break
            candidates = PARCEL_ANYWHERE.findall(lines[j])
            if candidates:
                parcel = candidates[-1]
                break
            j -= 1
        if parcel is None:
            continue

        description_parts = [match.group(2).strip()] if match.group(2).strip() else []
        published_total = None
        marker_inside_block = False

        # Read this item's description only until the next numbered item or
        # the next parcel/taxpayer line.  This prevents owner names from ever
        # entering the emitted legal description.
        for k in range(item_index, min(item_index + 80, len(lines))):
            candidate = lines[k]
            if k > item_index:
                if ITEM_START.match(candidate) or PARCEL_ANYWHERE.search(candidate):
                    break
                description_parts.append(candidate.strip())
            if "PUBLIC BIDDER TAX SALE" in candidate:
                marker_inside_block = True
            amounts = MONEY.findall(candidate)
            if amounts:
                published_total = round(float(amounts[-1].replace(",", "")), 2)
                if description_parts:
                    description_parts[-1] = (
                        MONEY.sub("", description_parts[-1])
                        .replace("PUBLIC BIDDER TAX SALE", "")
                        .strip()
                    )
                break

        if published_total is None:
            continue

        row_public_bidder = last_exact_public_bidder_marker >= 0 and last_exact_public_bidder_marker < item_index
        if marker_inside_block and last_exact_public_bidder_marker < item_index:
            row_public_bidder = True

        legal = re.sub(r"\s+", " ", " ".join(part for part in description_parts if part)).strip() or None
        sale_class = "Public bidder tax sale" if row_public_bidder else "Regular tax sale"
        redemption = (
            "90-day notice of right of redemption may be issued after 9 months from sale"
            if row_public_bidder
            else "90-day notice of right of redemption may be issued after 1 year 9 months from sale"
        )
        rows.append(
            {
                "record_id": f"IA-Johnson-2026-{item_number}",
                "profile_id": PROFILE_ID,
                "state": "IA",
                "state_name": "Iowa",
                "county": "Johnson",
                "parcel_id": parcel,
                "sale_item_number": str(item_number),
                "legal_description": legal,
                "auction_date": "2026-06-15",
                "sale_date": "2026-06-15",
                "auction_time": "08:00 CT",
                "auction_format": "In person; percentage-interest bid down with random selection among tied active bidders",
                "auction_location": "Johnson County Administration Building, Room 110, 913 S Dubuque St, Iowa City, IA 52240",
                "auction_url": "https://johnsoncountyiowa.gov/treasurer/tax-sale-publication-lists",
                "official_source_url": "https://johnsoncountyiowa.gov/sites/default/files/2026-06/Gazette%20Proof%202026%20Johnson%20Co%20Delinquent%20Taxes.pdf",
                "direct_listing_url": "https://johnsoncountyiowa.gov/treasurer/tax-sale-publication-lists",
                "minimum_bid": None,
                "opening_bid": None,
                "delinquent_tax_amount": published_total,
                "sale_status": f"Official 2026 publication snapshot — {sale_class}; sale date has passed and current parcel status must be reconfirmed",
                "lien_type": "Iowa tax sale certificate / property-tax lien",
                "sale_type": "tax_lien",
                "maximum_statutory_return": "2% per month redemption interest; fractions of a month count as a whole month",
                "winning_rate_mechanism": "Items are offered at 100%; active bidders bid the percentage interest in the parcel down in whole percentages from 99% to 1%, with random selection among remaining bidders",
                "redemption_period": redemption,
                "important_rules": "The county publication warns that some listed taxes may have been paid after publication. A tax-sale certificate is not immediate ownership; consult current county records before relying on any listed item.",
                "data_source": "Johnson County Treasurer official 2026 delinquent-tax publication PDF",
                "last_verified": verified,
                "source_mode": "official_2026_publication_snapshot",
                "data_completeness": {"published_fields": 8, "tracked_fields": 19, "percent": 42},
                "research_priority": {
                    "score": 42,
                    "label": "Low research priority",
                    "reasons": [
                        "Official parcel ID is published",
                        "Official legal description is published",
                        "County publishes the delinquent-tax amount",
                        "The 2026 sale date is confirmed but has passed",
                    ],
                    "disclaimer": "Research-priority ranking only; not a buy recommendation.",
                },
            }
        )
        seen_items.add(item_number)

    rows.sort(key=lambda row: int(row["sale_item_number"]))
    if len(rows) < 700:
        raise RuntimeError(f"Johnson County item-anchored parser found only {len(rows)} real-estate rows; expected at least 700")
    if any(int(row["sale_item_number"]) > 799 for row in rows):
        raise RuntimeError("Johnson County parser crossed into the mobile-home section")
    if any(any("owner" in str(key).lower() for key in row) for row in rows):
        raise RuntimeError("Johnson County parser emitted a restricted owner-name field")
    return rows


def main() -> None:
    try:
        rows = parse_real_estate_rows_by_item(extract_text(fetch_pdf()), date.today().isoformat())
    except (requests.RequestException, RuntimeError) as exc:
        prior = existing_rows()
        if not prior:
            raise
        print(
            f"Johnson County IA: live official publication unavailable/unparseable; "
            f"preserved {len(prior)} previously verified rows. Reason: {exc}"
        )
        return
    update_details(rows)
    print(
        f"Johnson County IA: loaded {len(rows)} official real-estate tax-lien rows "
        "with item-anchored parser; owner names intentionally omitted"
    )


if __name__ == "__main__":
    main()
