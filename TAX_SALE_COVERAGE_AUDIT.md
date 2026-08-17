# Tax Sale Coverage Audit

Generated 2026-08-16 by direct inspection of the `main` branch (no prior audit
file existed in this repository — this is the first one). It reflects the
state of the codebase **after** the fixes and additions made in this same
change: the Grant County, Indiana collector and the Cochise-County data-loss
fix described below.

Machine-readable version: [`data/source-registry.json`](data/source-registry.json),
validated by `scripts/validate_source_registry.py`. This document is the
human-readable companion; the registry is authoritative for status per
jurisdiction.

## 1. What "Property query = Yes" means here

A jurisdiction only counts as a real property-level query if there is
executable collector code, checked into `scripts/`, that produces individually
identified records (one row per certificate/parcel/sale item/property) into
`data/tax-lien-properties.json` or `data/properties.json`, with a `last_success_at`
timestamp and (ideally) a test module. Everything else — a market-summary row
in `index.html`, a link, a schedule description — is **informational only**
and marked `property_query: false` / `collector_status: identified` in the
registry, no matter how well-written the summary is.

This audit found 28 scripts named `add_*_tax_lien_market.py` / `add_*.py` that
only insert a single descriptive row into `index.html`. None of them touch
`data/tax-lien-properties.json` or `data/properties.json` — confirmed by
grepping every script in `scripts/` for those two filenames. They are real,
useful, sourced-and-linked informational content, but they are not collectors.

## 2. Current verified baseline (as of this audit)

### Tax-lien property details (`data/tax-lien-properties.json`)

| State | County | Records | Status | Collector |
|---|---|---:|---|---|
| IN | Allen | 574 | live | `refresh_tax_lien_properties.py` |
| IN | Tippecanoe | 91 | live (retains prior rows on transient fetch failure) | `refresh_tax_lien_properties.py` |
| IN | Wabash | 57 | live | `refresh_tax_lien_properties.py` |
| IN | Grant | 85 | **new** — snapshot | `refresh_tax_lien_properties.py` |
| AZ | Coconino | 33 | snapshot (source blocks automation, verified snapshot retained) | `refresh_tax_lien_properties.py` |
| AZ | Cochise | 11,678 | live | `refresh_arizona_cochise_tax_liens.py` |
| **Total** | | **12,518** | 2 states, 6 counties | |

### Tax-deed / foreclosure scanner (`data/properties.json`)

| State | County | Records | Status | Collector |
|---|---|---:|---|---|
| WA | King | 145 | live | `refresh_properties.py` |
| TX | Tarrant | 20 | live (assessor enrichment 1/20) | `refresh_properties.py` |
| FL | Putnam | 38 | live | `refresh_florida_tax_deeds.py` |
| FL | Escambia | 1 | snapshot (host blocks automation) | `refresh_florida_tax_deeds.py` |
| FL | Brevard | 0 | zero_active (collector runs, list currently empty) | `refresh_properties.py` |
| **Total** | | **204** (+ 33 Coconino tax-lien records cross-listed and clearly labeled) | 3 states, 4 counties + Coconino | |

**Note on the original task brief's baseline:** the brief quoted 755 tax-lien
records across 4 counties. That was already stale by the time this audit ran
— `main` had gained an 11,678-record Cochise County, AZ collector
(`refresh_arizona_cochise_tax_liens.py`, merged the same day) that the brief's
snapshot predates. The tax-deed baseline (237 records) matched exactly.

## 3. Bug found and fixed: cross-collector data loss

Full incident write-up: [`BUGS.md`](BUGS.md) (BUG-001).

`refresh_tax_lien_properties.py` rebuilt `data/tax-lien-properties.json` from
scratch on every run — `properties = []`, then only ever repopulated it with
Allen/Tippecanoe/Wabash/Coconino (now +Grant) rows. It had no knowledge of
Cochise County, which is written to the **same file** by a separate script,
`refresh_arizona_cochise_tax_liens.py`, on a separate daily workflow
(`refresh-properties.yml`, 13:17 UTC) that runs *before*
`refresh-tax-lien-properties.yml` (14:37 UTC).

Net effect in production: every day at 14:37 UTC, the 11,678 verified Cochise
County records were silently deleted from `data/tax-lien-properties.json`,
until the next day's 13:17 UTC Cochise run put them back. This is exactly the
kind of failure the reliability requirements were written to prevent — except
it wasn't a network failure, it was two independently-scheduled collectors
sharing one output file without either one knowing about the other.

**This is not a hypothetical.** It fired for real on `main` while this fix was
in progress: at 2026-08-17 ~07:09 UTC, the scheduled `refresh-tax-lien-properties.yml`
workflow ran the still-unfixed script and dropped `main`'s live dataset from
12,433 records to 755 (confirmed via `git show origin/main:data/tax-lien-properties.json`
at the time). It stayed broken for about two minutes until this fix's PR
(#4) merged and its own CI run regenerated the file correctly back to 12,518
records. See `BUGS.md` BUG-001 for the full timeline.

**Fix:** `refresh_tax_lien_properties.py` now reads the existing output file
before writing, computes which `profile_id`s it owns (Allen/Tippecanoe/Wabash/
Grant/Coconino), and preserves every other collector's rows and profile
metadata untouched (see `foreign_entries()` in the script). A regression test,
`ForeignCollectorPreservationTests` in `tests/test_tax_lien_properties.py`,
exercises this directly with a fixture file so it can't silently regress
again. Verified locally: re-running the collector now produces 12,518 total
records (840 own + 11,678 preserved Cochise) instead of 840.

This is a systemic risk worth flagging for future work: **any** two scripts
that write to the same JSON file without coordinating ownership can reproduce
this bug. `refresh_properties.py` and `refresh_florida_tax_deeds.py` share
`data/properties.json` in a similar way — they were checked and are mutually
safe today (each merges rather than overwrites), but there's no structural
guard preventing a future regression there. Consider it a backlog item.

## 4. New collector added this session

**Grant County, Indiana** — `refresh_tax_lien_properties.py`, reusing the
existing generic `indiana_ad_rows()` PDF parser with zero new parsing logic
(same regex, same word-reconstruction fallback already proven on Tippecanoe
and Wabash). Source: the county's official 2026 Commissioners' Certificate
Sale advertisement PDF, hosted on `in.gov`. Produces 85 individually
identified certificate/parcel records.

Honesty note: the advertised sale date (2026-04-28) has already passed as of
this audit. This is recorded as `collector_status: snapshot` (not `live`),
and every row's `sale_status` / `important_rules` field says explicitly that
the sale date has passed and per-item current availability has not been
reconfirmed with the County Auditor — the same epistemic pattern already used
for Coconino County's blocked-source snapshot. Records are real and
individually identified; they are not claimed to be currently biddable.

## 5. Jurisdictions checked and found blocked (not bypassed)

| Source | URL | Result |
|---|---|---|
| Johnson County, IN tax sale document center | `johnsoncounty.in.gov/egov/apps/document/center.egov` | HTTP 403 |
| Hillsborough County, FL county-held certificates | `lienhub.com/county/hillsborough/certsale/main` | HTTP 403, no public bulk export without login |
| Orange County, FL county-held certificates | `lienhub.com/county/orange/certsale/main` | HTTP 403, same LienHub platform as Hillsborough |
| Riverside County, CA tax-defaulted inventory | `countytreasurer.org/inventory-all-tax-defaulted-property` | HTTP 403 |
| Kosciusko County, IN (pre-existing) | `kosciusko.in.gov/egov/apps/document/center.egov` | HTTP 403 (previously documented, reconfirmed) |
| Monroe County, IN (pre-existing) | `in.gov/counties/monroe/Departments/treasurer/` | SharePoint-only link, no stable anonymous download |

None of these were bypassed (no auth, no CAPTCHA solving, no cookie-gated
access). Each is recorded in `data/source-registry.json` with
`collector_status: blocked` and a `blocker` explanation, per the task's
requirement to document and move on rather than retry indefinitely.

Grant County, Indiana was the first accessible target found after these
attempts — same `in.gov` domain pattern already proven reachable (Wabash uses
the same domain), and its PDF parsed cleanly with existing code.

## 6. Nationwide source registry (Phase 1)

`data/source-registry.json` — 79 jurisdiction rows, schema exactly as
specified in the task brief (`state`, `county_or_locality`, `sale_system`,
`official_information_url`, `current_list_url`, `assessor_url`,
`collector_status`, `property_query`, `last_attempt_at`, `last_success_at`,
`current_record_count`, `blocker`, `collector_module`, `test_module`).
Validated by `scripts/validate_source_registry.py`, which enforces the same
evidence rule as `scripts/validate_project_management.py` already enforces
for `data/project-management.json`: a row cannot claim `property_query: true`
without a real, on-disk `collector_module` and a nonzero verified record
count (or `zero_active`, which is allowed to be zero).

Breakdown:

| collector_status | Count |
|---|---:|
| live | 7 |
| snapshot | 3 |
| zero_active | 1 |
| identified (informational only, real source, no collector) | 35 |
| blocked | 5 |
| not_started | 28 |

`property_query: true` — 11 jurisdictions, 12,722 total verified records
(the registry's own per-jurisdiction sum; this differs slightly from the raw
dataset-file totals because Coconino County is intentionally cross-listed
in both the tax-lien and tax-deed products but only counted once per
jurisdiction here).

**Honesty note on nationwide scope:** the task asks the registry to
"eventually cover every applicable U.S. state and every county, parish,
municipality, district, or statewide tax-sale authority." Hand-verifying
~3,000+ counties in one pass is not something that can be done without
fabricating data, which the brief explicitly forbids. This registry instead:

- Includes a verified row for every jurisdiction this repository has *any*
  real evidence about (a working collector, a documented informational
  source with a real URL, or a documented blocker) — 51 rows.
- Includes one honest `not_started` row per U.S. state with zero research
  done so far (28 states) — explicitly *not* claiming coverage, just tracking
  that the state exists and hasn't been looked at. `sale_system` is left
  `null` for these rather than guessed, per the no-fabrication rule.

Expanding `not_started` rows into real per-county entries, state by state, is
the top of the Phase 2 backlog (see §7).

## 7. Backlog / next priorities

Ordered roughly by leverage (structured-source availability × existing code
reuse potential), not by state alphabetically:

1. **Florida certificate sales beyond LienHub-blocked counties.** Orange,
   Broward, Miami-Dade, Palm Beach, Pinellas, Hillsborough all have real
   informational sources but no collector. Their *annual* certificate auction
   (as opposed to the blocked county-held resale) may publish a structured
   pre-auction certificate list separately from LienHub — not yet checked.
2. **More Indiana counties via the existing `indiana_ad_rows()` parser.**
   It is already generic and proven on 4 counties now. Any Indiana county
   with a same-format legal-ad PDF on a reachable `in.gov`/county domain
   (not blocked, not SharePoint-only) is close to zero-marginal-cost to add.
   Hamilton County's 2026 list was "available mid-August 2026" per the
   county's own page — worth checking again shortly.
3. **Assessor/GIS enrichment for the existing 755 non-Cochise tax-lien
   records** (`assessed_value` is 0/null across the board today) — flagged
   already in `data/project-management.json` WS-03.
4. **Tests for `refresh_properties.py`, `refresh_florida_tax_deeds.py`, and
   `refresh_arizona_cochise_tax_liens.py`** — none have dedicated test
   modules yet; only the Indiana/Coconino/Grant path
   (`tests/test_tax_lien_properties.py`) and the new registry
   (`tests/test_source_registry.py`) do.
5. **California tax-defaulted property auctions** (Bid4Assets/GovEase-based,
   LA County and San Diego flagged P1 in the existing backlog) — Riverside's
   direct inventory page is blocked; Bid4Assets' own auction catalog pages
   were not yet checked and may be more permissive.
6. **State-by-state `not_started` expansion** — turn each of the 28
   `not_started` registry rows into real per-county rows once an official
   source is actually found and verified for that state.

## 8. Relationship to `data/project-management.json`

This repository already had an equivalent structured backlog/dashboard,
`data/project-management.json` (added by a separate session shortly before
this audit, PR #2 "Add project management coverage dashboard", merged
2026-08-15). It tracks similar ground at the workstream/query level. This
audit and `data/source-registry.json` are complementary, not a replacement:

- `project-management.json` tracks **workstreams and prioritized next
  actions** at a coarser grain (P0–P3 priority, progress %).
- `data/source-registry.json` is the **exact schema requested** for this
  task — `official_information_url` / `current_list_url` / `assessor_url` /
  `last_attempt_at` as distinct fields, which `project-management.json` does
  not carry.

One gap found in `project-management.json` while cross-checking: it has no
entry at all for Cochise County despite Cochise holding 11,678 of the
project's 12,518 live tax-lien records. Flagged here; not fixed in
`project-management.json` itself in this change, to avoid touching a file
another active session owns without coordinating first.
