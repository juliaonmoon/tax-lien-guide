#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPS = ROOT / "data" / "properties.json"
OUT = ROOT / "data" / "king-gaps.json"

FIELDS = {
    "address": lambda p: bool(str(p.get("address") or "").strip()),
    "city_zip": lambda p: bool(str(p.get("city") or "").strip()) and bool(str(p.get("zip") or "").strip()),
    "coordinates": lambda p: p.get("latitude") is not None and p.get("longitude") is not None,
    "assessed_value": lambda p: p.get("assessed_value") not in (None, "") and float(p.get("assessed_value") or 0) > 0,
    "property_type": lambda p: bool(str(p.get("property_type") or "").strip()),
    "legal_description": lambda p: bool(str(p.get("legal_description") or "").strip()),
    "tax_status": lambda p: bool(str(p.get("tax_status") or "").strip()) or p.get("tax_due_estimate") not in (None, ""),
    "neighborhood": lambda p: p.get("neighborhood_value_score") is not None,
    "opening_bid": lambda p: p.get("opening_bid") not in (None, ""),
}

OPTIONAL_METRICS = {
    "rental_days_on_market": lambda p: p.get("rental_days_on_market") not in (None, ""),
    "public_safety": lambda p: p.get("public_safety_12mo_offenses") not in (None, "") or p.get("public_safety_score") not in (None, "") or p.get("crime_rate") not in (None, ""),
}

SOURCE_LIMITATIONS = {
    "opening_bid": {
        "status": "awaiting_official_publication",
        "source": "https://kingcounty.gov/en/dept/executive-services/buildings-property/treasury-operations/tax-foreclosures/auctions",
        "note": "King County's current official foreclosure pages confirm the September 9, 16, and 23, 2026 online auction schedule but do not currently publish the tax-foreclosure opening-bid amounts. Do not infer, estimate, or substitute Sheriff judicial-foreclosure bids.",
    },
    "legal_description": {
        "status": "individual_record_search_required_for_remaining_orphans",
        "source": "https://recordsearch.kingcounty.gov/LandmarkWeb",
        "note": "Two GIS-orphan parcels remain without legal descriptions in the machine-readable county sources. Recorder research must be done individually; the pipeline does not bulk-query or scrape restricted record-search pages.",
    },
    "address": {
        "status": "no_assigned_situs_for_some_parcels",
        "source": "https://www5.kingcounty.gov/SDC?Layer=address_point",
        "note": "Some foreclosure parcels have no assigned situs address in King County GIS. The pipeline keeps those addresses blank rather than assigning a nearby or inferred street address.",
    },
    "public_safety": {
        "status": "populated_from_official_sources_with_mixed_geographic_scopes",
        "sources": [
            "https://data.kingcounty.gov/Law-Enforcement-Safety/KCSO-Offense-Reports-2020-to-Present/4kmt-kfqf",
            "https://data.seattle.gov/Public-Safety/SPD-Crime-Data-2008-Present/tazs-3rd5",
            "https://data.seattle.gov/Public-Safety/Seattle-Police-Department-Micro-Community-Policing/ru88-fbhk",
            "https://data.wa.gov/Public-Safety/Washington-State-Uniform-Crime-Reporting-National-/vvfu-ry7f",
            "https://bellevuewa.gov/city-news/crime-drops-again",
        ],
        "note": "All current King County foreclosure parcels have a legitimate public-safety metric. KCSO patrol-district and SPD neighborhood metrics are preferred where available; remaining independent-city gaps are filled from Washington OFM/SAC's official 2024 NIBRS agency totals, and Bellevue may use its official citywide published total. These values have different geographic scopes and periods, so they are descriptive context only and must not be ranked as directly comparable parcel-level crime rates.",
    },
    "rental_days_on_market": {
        "status": "no_reliable_public_source_integrated",
        "note": "The pipeline has complete Census/ACS ZIP-level rental proxies, but no reliable public parcel/ZIP-level days-on-market source is currently integrated. Days-on-market remains blank rather than using a fabricated proxy.",
    },
}

# Missing fields in this set are not actionable by the automated enrichment pipeline
# until the cited official source changes or an individual, non-bulk public-record lookup
# is performed. Keeping this classification explicit prevents scheduled runs from
# repeatedly treating proven source limitations as code defects.
BOUNDED_FIELDS = {"address", "legal_description", "opening_bid"}
BOUNDED_OPTIONAL_METRICS = {"rental_days_on_market"}


def normalized_city(p):
    city = str(p.get("city") or "").strip().upper()
    return city or "UNCLASSIFIED"


def main():
    doc = json.loads(PROPS.read_text(encoding="utf-8"))
    wa = [p for p in doc.get("properties", []) if p.get("state") == "WA" and p.get("county") == "King"]
    gaps = []
    counter = Counter()
    by_field = defaultdict(list)
    address_status_counts = Counter()
    for p in wa:
        missing = [name for name, test in FIELDS.items() if not test(p)]
        counter.update(missing)
        for field in missing:
            by_field[field].append(str(p.get("parcel_id") or ""))
        if "address" in missing:
            address_status_counts[str(p.get("address_status") or "Unclassified")] += 1
        if missing:
            gaps.append({
                "parcel_id": p.get("parcel_id"),
                "missing": missing,
                "address_status": p.get("address_status"),
                "coordinate_source": p.get("coordinate_source"),
                "city": p.get("city"),
                "zip": p.get("zip"),
                "property_type": p.get("property_type"),
                "assessed_value": p.get("assessed_value"),
                "land_value": p.get("land_value"),
                "improvement_value": p.get("improvement_value"),
                "value_basis": p.get("value_basis"),
                "legal_description": p.get("legal_description"),
                "tax_status": p.get("tax_status"),
                "tax_due_estimate": p.get("tax_due_estimate"),
                "enrichment_note": p.get("enrichment_note"),
            })

    optional_coverage = {}
    optional_missing_by_city = {}
    for name, test in OPTIONAL_METRICS.items():
        filled = sum(1 for p in wa if test(p))
        missing_rows = [p for p in wa if not test(p)]
        optional_coverage[name] = {"filled": filled, "total": len(wa), "missing": len(missing_rows)}
        optional_missing_by_city[name] = dict(sorted(Counter(normalized_city(p) for p in missing_rows).items(), key=lambda kv: (-kv[1], kv[0])))

    fixable_missing = {k: v for k, v in sorted(counter.items()) if k not in BOUNDED_FIELDS and v}
    bounded_missing = {k: v for k, v in sorted(counter.items()) if k in BOUNDED_FIELDS and v}
    optional_fixable_missing = {
        name: info["missing"]
        for name, info in optional_coverage.items()
        if name not in BOUNDED_OPTIONAL_METRICS and info["missing"]
    }
    optional_bounded_missing = {
        name: info["missing"]
        for name, info in optional_coverage.items()
        if name in BOUNDED_OPTIONAL_METRICS and info["missing"]
    }
    no_fixable_gaps = not fixable_missing and not optional_fixable_missing

    completion = {
        "status": "bounded_complete" if no_fixable_gaps else "fixable_gaps_remain",
        "no_fixable_gaps_remain": no_fixable_gaps,
        "fixable_missing_counts": fixable_missing,
        "bounded_missing_counts": bounded_missing,
        "optional_fixable_missing_counts": optional_fixable_missing,
        "optional_bounded_missing_counts": optional_bounded_missing,
        "note": (
            "All remaining blanks are documented source limitations; future runs should only reopen WA enrichment when an official source changes or a new legitimate public source is added."
            if no_fixable_gaps
            else "At least one tracked field lacks coverage without a documented source limitation and should be investigated as a pipeline defect."
        ),
    }

    OUT.write_text(json.dumps({
        "source_updated_at": doc.get("updated_at"),
        "king_count": len(wa),
        "completion": completion,
        "missing_counts": dict(sorted(counter.items())),
        "missing_parcel_ids_by_field": {k: v for k, v in sorted(by_field.items())},
        "missing_address_status_counts": dict(sorted(address_status_counts.items())),
        "optional_metric_coverage": optional_coverage,
        "optional_metric_missing_by_city": optional_missing_by_city,
        "source_limitations": SOURCE_LIMITATIONS,
        "gaps": gaps,
    }, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}: {len(gaps)} rows with at least one tracked gap")
    print("Completion:", completion)
    print("Optional metric coverage:", optional_coverage)
    print("Optional metric missing by city:", optional_missing_by_city)


if __name__ == "__main__":
    main()
