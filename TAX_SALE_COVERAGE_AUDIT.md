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
safe today (each merges rather than overwrites).

**Follow-up (2026-08-17, BUG-002):** while adding test coverage, found and
fixed a related-but-different gap in `refresh_properties.py` itself: it had
no fallback if fetching/parsing one of its own sources (Brevard/Tarrant/King)
failed — that source's rows would simply be missing from that run's output,
with no retained-previous-rows fallback like the Indiana/Cochise scripts
have. This wasn't the cross-collector conflict BUG-001 was (Florida already
merges correctly via the new `merge_state_rows()`), just a missing fallback
for the script's own sources. Fixed via `prior_by_county()`; see `BUGS.md`
BUG-002 for the full write-up.

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
   informational sources but no collector. Checked 2026-08-18: Hillsborough's
   *annual* certificate sale for 2026 has already passed (next one May 2027),
   so a pre-auction certificate list isn't currently obtainable there. Not
   yet checked for Orange/Broward/Miami-Dade/Palm Beach/Pinellas specifically.
2. **More Indiana counties via the existing `indiana_ad_rows()` parser.**
   It is already generic and proven on 4 counties now. Any Indiana county
   with a same-format legal-ad PDF on a reachable `in.gov`/county domain
   (not blocked, not SharePoint-only) is close to zero-marginal-cost to add.
   Checked 2026-08-18: Hamilton County's 2026 list still isn't published
   ("mid-August" came and went) — check again in a week or two. Montgomery
   County's page returns HTTP 403.
3. ~~Assessor/GIS enrichment for the existing 755 non-Cochise tax-lien
   records~~ — **done 2026-08-17.** `scripts/enrich_indiana_assessed_values.py`
   pulls the official DLGF "Real Property" fixed-width file for each of the
   4 Indiana counties from the Indiana Gateway for Government Units
   (`gateway.ifionline.org`, no login/CAPTCHA/access-control workaround —
   a public form on an official state-partnered portal), matches by
   digit-normalized parcel number, and fills `assessed_value`,
   `market_value`, `property_address`/`address`, `city`, `zip`, and
   `legal_description` when missing (never overwrites an existing value).
   Field byte positions come from the authoritative regulation defining
   this fixed-width format, 50 IAC 26-20-4, not guesswork — verified
   against 5 known real Allen County parcels before writing the parser
   (5/5 matched with correct addresses/values). Result: 807/807 (100%)
   Indiana tax-lien records matched; `with_assessed_value` went from 0 to
   805 (2 parcels have a genuine $0 assessment, left as `null`, not
   fabricated). Wired into `refresh-tax-lien-properties.yml` to run after
   the base collector on every daily refresh.
4. ~~Tests for `refresh_properties.py`, `refresh_florida_tax_deeds.py`, and
   `refresh_arizona_cochise_tax_liens.py`~~ — **done 2026-08-17.** Every
   live/snapshot collector now has a dedicated test module:
   `tests/test_refresh_properties.py`, `tests/test_florida_tax_deeds.py`,
   `tests/test_arizona_cochise_tax_liens.py` (plus the pre-existing
   `tests/test_tax_lien_properties.py` and `tests/test_source_registry.py`).
   Writing these tests also surfaced and fixed BUG-002. Remaining gap: a
   Brevard-specific zero-active parser fixture (Brevard currently has 0
   active records, so there's nothing live to assert a parse against yet).
5. **California tax-defaulted property auctions** (Bid4Assets/GovEase-based,
   LA County and San Diego flagged P1 in the existing backlog) — Riverside's
   direct inventory page is blocked. Checked 2026-08-18: Bid4Assets itself is
   reachable via a real browser (not via plain HTTP fetch — that gets a 403,
   likely bot detection) but has no active California auction between now
   and the next one (Santa Clara County, Oct 23-26 2026) — nothing to
   collect yet, and no public API was found on the site. LA County's own
   Bid4Assets page confirms no sale currently scheduled. Worth rechecking
   closer to an actual auction date.
6. **State-by-state `not_started` expansion** — turn each of the 28
   `not_started` registry rows into real per-county rows once an official
   source is actually found and verified for that state.
7. **Hillsborough County, FL tax-deed "Lands Available" — real API found and
   mapped in detail (2026-08-18), but blocked on one specific unresolved
   question before it can safely become a collector.**

   The Clerk of Court's public-access system
   (`publicaccess.hillsclerk.com/TD/`) is a genuine, unblocked JSON API:
   `POST /TD/api/CustomQuery/KeywordSearch` with body
   `{"QueryID":285,"Keywords":[{"ID":412,"Value":"","KeywordOperator":"="},
   {"ID":413,"Value":"","KeywordOperator":"="},{"ID":1013,"Value":"",
   "KeywordOperator":"="},{"ID":1014,"Value":"","KeywordOperator":"="}],
   "FromDate":"<ISO date>","ToDate":"<ISO date>","QueryLimit":<n>}`
   (query type `285` = "PAV - TD - List of Lands Available"). No login,
   CAPTCHA, or access-control workaround — confirmed reachable via a real
   browser; a plain HTTP fetch got a 403 (likely basic bot-UA filtering,
   not a real access control), so a collector should set a real
   User-Agent, same as every other collector in this repo already does.

   Each result row's `DisplayColumnValues` is a fixed 8-item array whose
   meaning is given directly by the UI's own column headers — no
   guessing required: `[0]=File#, [1]=Folio#, [2]=Auction Date,
   [3]=Certificate#, [4]=Case Status, [5]=Opening Bid, [6]=Winning Bid,
   [7]=Document Type`. Confirmed real values exist for every column (e.g.
   `File# "2026-541", Folio# "0384720000", Auction Date "8/13/2026",
   Certificate# "2023/3694", Case Status "SOLD", Opening Bid "$1,502.05",
   Winning Bid "$2,100.00"`), so — unlike first thought — the opening bid
   and property-identifying fields do NOT require opening a separate PDF
   per property; they're already in this response for cases far enough
   along in the process. Each case also appears multiple times (once per
   associated document — "TD - Tax Deed", "TD - O & E Report", "TD - Tax
   Collector Cert (DR513)", "TD - Tax Collector App (DR512)", "TD -
   Certificate of Mailing"), so a collector needs to dedupe by File# and
   merge/prefer the row with the most populated fields.

   **The actual blocker:** across a 500-row sample, observed `Case Status`
   values were `SALE` (377), `REDEEMED` (28), `SOLD` (25), `BANKRUPTCY`
   (3), `PENDING` (2) — **none of them says "available."** Florida
   Statute 197.502 is specific about when a property legally becomes
   "lands available for taxes": only after the auction produced *no
   bidder* (or the certificate holder failed to pay within 30 days) —
   that's a distinct state from "SALE" (which reads more like "in the
   sale process," i.e. scheduled/upcoming, not resolved). Guessing which
   of these statuses maps to genuinely-still-available would risk telling
   someone a sold or redeemed property is available — not acceptable.
   **Do not build a collector against this API until this is resolved
   with actual evidence** (e.g. cross-reference a case with a known
   real-world "lands available" listing and see what status/fields it
   carries, or find official documentation of the status codes this
   system uses — the same standard already applied to Indiana's 50 IAC
   26-20-4 rather than reverse-engineering byte positions from samples).

   Checked again 2026-08-18: still blocked, no new evidence gathered this
   session — the session's environment had no general internet egress
   (confirmed via direct `curl` test, GitHub-only network policy), so
   live research against `publicaccess.hillsclerk.com` wasn't possible.
   Same constraint applied to rechecking whether Hamilton County IN's 2026
   list has been published. Both remain open for a session with broader
   network access.

8b. ~~Tarrant County tax-deed collector was scraping real owner names from
   the Tarrant Appraisal District into the published `owner` field~~ —
   **fixed 2026-08-18, see BUG-004 in `BUGS.md`.** This was a privacy-
   convention violation waiting to happen (not yet visible in published
   data because TAD lookups were failing at the time it was found), not a
   coverage gap — `tad_enrich()` now skips the owner column entirely, with
   a regression test guarding it.

8c. ~~Florida (Putnam/Escambia) tax-deed collector was actually publishing
   real individual owner names for all 39 live rows~~ — **fixed
   2026-08-18, see BUG-005 in `BUGS.md`.** Found immediately after 8b by
   auditing the rest of `scripts/` for the same pattern. Unlike 8b, this
   one had already fired in production: Putnam's own official "Lands
   Available for Taxes" list prints an owner name inline (captured by
   `putnam_live()`'s regex), and the FDOR cadastral feed's `OWN_NAME`
   backfilled it for Escambia. Both paths removed; `owner` is now always
   `null` for these 39 rows, with regression tests covering both source
   paths.

8d. **Iowa (Johnson/Linn County) property-level tax-lien collectors —
   real code exists, currently 0 records live, actively being
   worked on by multiple sessions (2026-08-18/19).** Not yet reflected
   correctly in `data/project-management.json` until this entry (was a
   single stale `TL-IA-ALL` "no property collector" row; now split into
   `TL-IA-JOHNSON` / `TL-IA-LINN`, both `in_progress`).

   Both counties have real collectors (`scripts/repair_iowa_johnson_parser.py`,
   `scripts/repair_iowa_linn_pdf_parser.py`) wired into both daily
   workflows, with dedicated test modules
   (`tests/test_iowa_johnson_tax_liens.py`, `tests/test_iowa_linn_tax_liens.py`).
   Neither has ever published a single row: both workflows share a hard
   "Verify Iowa ... output" gate requiring >=700 Johnson rows and >=1500
   Linn rows before anything (including the long-established Indiana and
   Cochise data in the same job) is allowed to publish. That gate briefly
   became a same-blast-radius incident of its own — see BUG-001-class
   BUG-006 in `BUGS.md` — fixed to tolerate a not-yet-live collector,
   then **deliberately reverted** by a later commit in favor of "refuse
   to publish incomplete Iowa data," which is the current, intentional
   policy. Don't re-litigate that without reading BUG-006's "Update"
   section first.

   Current verified numbers (checked directly against GitHub Actions
   logs and `data/tax-lien-properties.json` on `main`, 2026-08-19):
   Johnson County's parser finds 159 of the ~700+ expected real-estate
   rows from the official PDF (unchanged across multiple runs — root
   cause still unknown, needs a session with real internet access to
   inspect the actual PDF, not guesswork); Linn County genuinely
   improved from 0 (XLSX)/214 (PDF fallback) to **524** of 1500+
   expected rows after a same-day parser fix (multi-row Excel header
   recognition + PDF trailing-text tolerance) — real progress, still
   short. Because the Verify gate checks Johnson first and raises
   immediately, **Johnson is currently the sole blocker** for
   `refresh-tax-lien-properties.yml`'s daily publish, independent of
   Linn's progress. No data was corrupted at any point — both
   collectors fail before writing anything, so the failure mode is
   staleness/non-publication, not incorrect data.

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
