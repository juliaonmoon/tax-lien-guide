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

   Checked again 2026-08-19 (live `curl`, real network access): still not
   published — `secure2.hamiltoncounty.in.gov/taxsale/` (the actual data
   host behind `hamiltoncounty.in.gov/taxsale`'s redirect) returns HTTP 503
   with a static placeholder page titled *"Tax Sale Listing Coming 2026"*
   and body text *"...2026 is not available."* Not a transient error — a
   deliberate placeholder with `Retry-After: 3600`. Check again in another
   1-2 weeks.
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

   Checked again 2026-08-19 (this session's environment does have general
   egress, confirmed via `curl`): still blocked, but with one incremental,
   authoritative confirmation — `publicaccess.hillsclerk.com` runs on
   Hyland OnBase Public Access (`/_obpa/` client assets), and that
   platform's own `GetQueryDefinition` API returns an `Instructions` string
   for QueryID 285 written by the county itself: *"To search for a
   complete list of Tax Deeds Lands Available use a start and end date
   with a 3 year span."* This confirms (from the source's own metadata,
   not just the query's name) that 285 is genuinely the right query — but
   it says nothing about which `Case Status` value marks a specific row as
   *currently* available. Tried several guesses at a keyword-metadata
   endpoint that might expose a status legend/dropdown
   (`GetKeywordValues`, `GetKeywords`, `GetKeywordList`,
   `GetKeywordDefinitions` for QueryID 285) — all either 404'd or fell
   back to the same generic document-type list, not a status enum. The
   OnBase client JS (`obpa_app.js`) is generic/vendor-side, no
   Hillsborough-specific status strings baked in. `hillsborough.realtaxdeed.com`
   (the county's separate RealAuction auction site, also linked from
   hillsclerk.com/taxdeeds) is a JS-rendered SPA that returns nothing
   useful to a plain fetch — would need an actual interactive browser
   session to drive its search UI and read the rendered status labels,
   which this session didn't have (browser extension not connected).
   **Still not resolved. Next attempt needs either a working interactive
   browser session against this exact site, or a direct answer from the
   Clerk's office** — do not guess a status→availability mapping from
   field names alone.

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
   rows from the official PDF (unchanged across two different parser
   versions and two independent live fetches, 05:13 and 06:29 UTC);
   Linn County genuinely improved from 0 (XLSX)/214 (PDF fallback) to
   **524** of 1500+ expected rows after a same-day parser fix (multi-row
   Excel header recognition + PDF trailing-text tolerance) — real
   progress, still short. Because the Verify gate checks Johnson first
   and raises immediately, **Johnson is currently the sole blocker** for
   `refresh-tax-lien-properties.yml`'s daily publish, independent of
   Linn's progress. No data was corrupted at any point — both
   collectors fail before writing anything, so the failure mode is
   staleness/non-publication, not incorrect data.

   **2026-08-19 afternoon update — the Johnson County source itself is
   now blocked, superseding the parsing investigation for now.** A
   session with real, unrestricted internet access set out to fetch the
   live PDF and compare its structure to the parser's assumptions, and
   found `johnsoncountyiowa.gov` now returns an interactive Cloudflare
   challenge (HTTP 403) for every request — the PDF, the treasurer page,
   the bare homepage, even `robots.txt` — confirmed via `curl`, `WebFetch`,
   and a real (non-headless-flagged) Chrome browser driven by Playwright.
   GitHub Actions run logs confirm this is new and sitewide, not specific
   to this session: the 06:29 UTC run still fetched the real PDF fine
   (159 rows, pre-column-rewrite parser); the very next run at 07:18 UTC
   failed with `requests.exceptions.HTTPError: 403 Client Error:
   Forbidden` on `fetch_pdf()` before extracting anything. The
   column-aware coordinate-based rewrite (`repair_iowa_johnson_parser.py`
   at commit `7dad1a9`) has therefore never actually been tested against
   real data — its first live run hit this new wall. No Wayback Machine
   snapshot of the PDF exists to substitute. Per the standing "don't
   fabricate or infer without live evidence" rule, no parser change was
   made; `TL-IA-JOHNSON` in `data/project-management.json` was set to
   `status: "blocked"`. Full detail in `BUGS.md` BUG-006's matching
   2026-08-19 afternoon update. Next session: recheck the site (a plain
   `curl` to the homepage is enough) before re-attempting anything here.

8e. **Scott County, IA — a promising fifth Iowa county, but not built,
   2026-08-19.** Tracked previously only as GitHub issue #16 (official
   2026 XLSX blocked with HTTP 403 as of 2026-08-18). Rechecked this
   session with live network access: the block was bot-UA filtering, not
   a real access-control wall — a standard browser User-Agent gets a
   clean HTTP 200 and a real 71,973-byte, 297-data-row workbook from
   `https://www3.scottcountyiowa.gov/treasurer/pub/tax_sale/2026/20260616_Tax_Sale_List.xlsx`.

   Did not build a collector against it — the row structure is
   meaningfully different from Linn/Johnson/Dubuque/Woodbury's and not
   safe to guess at. Findings: (1) real owner names/mailing addresses are
   in cleanly named columns (`Name 1/2/3`, `Address Lines 1/2/3`, etc.) —
   trivial to exclude, not the blocker; (2) the same `Item Number` recurs
   across multiple `Year`/`Receipt` rows (e.g. item 1847 has rows from
   tax years 2011 *and* 2012, several `Type: SA` special-assessment rows
   per year alongside one `Type: DT` row) — this reads as a running
   receipt ledger per certificate, not a flat one-row-per-parcel list,
   and the correct dedup/aggregation rule to reach a single authoritative
   current-amount-owed per item is not obvious from the data alone: the
   precomputed `Sale Amount` column is populated on some but not all of a
   given item's rows, with no visible pattern yet checked; (3) real
   estate (`Class: R`) and mobile-home (`Type: MH`, `Class` blank) items
   are interleaved by `Item Number`, not cleanly sectioned the way
   Johnson County's PDF separates them. Checked the 2023 Annual Tax Sale
   Rules PDF for a format spec — procedural only, no column
   documentation. Tried to cross-reference one item's current balance
   against Iowa's statewide treasurer parcel-lookup site
   (`iowa.govtechtaxpro.com`) to empirically confirm what `Sale Amount`
   means — connection timed out, not reachable this session. Logged as
   `TL-IA-SCOTT` (`status: "blocked"`, P2) in
   `data/project-management.json`; full detail also posted to issue #16.
   **Next attempt needs either an authoritative explanation of the row
   format from the Treasurer's office, or successfully cross-referencing
   a handful of known items against a live independent source** — same
   standard already applied to Indiana's DLGF byte-position parser
   (verified against 5 known parcels before shipping). Do not guess the
   aggregation rule; a wrong guess here would mean publishing incorrect
   dollar amounts, not just missing rows.

8f. **Oklahoma County, OK -- new tax-deed collector shipped, 2026-08-20.**
   Picked from the 28 `not_started` states as a tractable first entry.
   Source: the Treasurer's own "ACTIVE RESALE ACCOUNTS"/county-owned
   parcel list (`docs.oklahomacounty.org/treasurer/CountyOwnedList.asp`)
   -- properties that received no bidder at the annual June resale
   auction and are now county-owned, available for direct purchase (or,
   rarely, scheduled for a future public resale). A plain fetch without a
   browser-like User-Agent looked blocked; a normal one works fine, same
   "bot-UA filtering, not real access control" pattern already seen
   elsewhere in this project.

   Chose this source over the many other candidates checked because it is
   unusually clean: a live, server-rendered classic-ASP HTML table (no JS
   rendering needed), one row per parcel, and -- unlike most of this
   project's sources -- **the table itself never publishes an owner name
   at all**, so there was nothing to filter out. 196 real parcels parsed
   and committed (`scripts/refresh_oklahoma_county_ok_tax_deeds.py`,
   `tests/test_oklahoma_county_ok_tax_deeds.py`, 11 tests). Verified the
   "Suggested Initial Bid Amount" column is the real asking price (never
   $0 across all 196 rows, range $210-$17,840) versus "Initial Bid
   Amount", which is $0.00 for every row except the one formally
   scheduled for a specific future public sale -- confirmed by checking
   the full table, not guessed from one sample row.

   Deliberately scoped as a base-fields-only first version: no
   legal description, land value, or assessed value yet. Each row does
   carry a link to a per-parcel Oklahoma County Assessor detail page
   (`AssessorWP5/AN-R.asp`) that *would* let a follow-up enrich those
   fields -- but that same page also carries the parcel's current owner
   name and full historical deed Grantor/Grantee names, so enriching from
   it safely needs the parser to explicitly stop before the "Deed
   Transaction History" section, the same discipline already applied to
   Tarrant's TAD lookup and King County's assessor enrichment. Not done
   in this change; documented as the collector's `next_action` in
   `data/project-management.json` (`TD-OK-OKLAHOMA`) rather than rushed.

   Writes to the shared `data/properties.json` (same file as King/Tarrant/
   Brevard/Putnam/Escambia). Deliberately merges scoped by *(state,
   county)*, not state alone -- writing this surfaced a latent, currently-
   dormant version of the same clobbering risk in the neighboring
   `refresh_florida_tax_deeds.py` (its merge is state-only, safe today
   only because Brevard currently has 0 active rows). Logged as BUG-007
   in `BUGS.md` rather than fixed here -- out of scope for this change.

8g. **Michigan statewide surplus properties -- new tax-deed collector
   shipped, 2026-08-20, same session as Oklahoma (8f).** Second pick from
   the (now 26) `not_started` states. Considered Michigan because the
   state's tax-foreclosure system is unusually centralized: the Michigan
   Department of Treasury and dozens of counties all run their auctions
   through one platform, tax-sale.info.

   That platform has two very different kinds of listing. Its per-county
   live auction catalogs (e.g. `/listings/catalog/2830` for Antrim) are
   real, public, no-login, per-parcel data (Parcel ID, State Equalized
   Value, legal description, minimum bid) -- but each one is a single
   scheduled event that opens and closes within hours (the Antrim catalog
   checked while researching this happened to be *the day of* its own
   auction), making it a poor fit for a daily-refreshed dataset. Its
   **Surplus Properties** list (`/surplus` -> `/listings/surplus`) is the
   durable alternative: parcels that already went through an auction,
   received no bidder, and are being reoffered first-come-first-served
   with "no schedule" for when new ones are added or old ones are
   claimed -- the same rolling-inventory shape as Florida's Lands
   Available and Oklahoma's county-owned resale list (8f). Chose this one
   deliberately over the live catalogs for that durability reason, not
   because it was the only option found.

   24 real parcels parsed and committed
   (`scripts/refresh_michigan_surplus_tax_properties.py`,
   `tests/test_michigan_surplus_tax_properties.py`, 14 tests), spanning 5
   of the roughly 8 counties tax-sale.info listed as having surplus
   inventory at collection time (Arenac, Bay, Jackson, Monroe, Otsego);
   the rest had zero, which the source's own page explicitly says is
   normal ("Some counties may have many parcels, and others none").
   Confirmed the parser correctly *excludes* the live-auction catalog
   pages sharing the same site (a fixture test asserts a live-catalog
   page's HTML, which lacks the "Surplus <year>" title marker, returns no
   row) so a future change to this collector can't accidentally start
   pulling in the time-sensitive dataset instead.

   Like Oklahoma, this source never publishes an owner name anywhere on
   the parcel detail page -- confirmed by grepping the full rendered text
   of five real sample pages (not just the fields being extracted) for
   the word "owner"; the only hits were generic policy text such as "Can
   Only Be Sold To Adjacent Owner". Money fields that read "TBA" (minimum
   bid, current tax -- common on properties not yet fully processed) are
   parsed as `null`, never `0`, so a not-yet-priced property never looks
   like a free one.

8h. **Woodbury County, IA tax liens -- 469 missing rows recovered
   (1100 -> 1569/1569), root cause fixed; Dubuque County, IA found
   independently broken while verifying the fix, 2026-08-20.** Picked up
   issue #29 (Woodbury regressed below its 1500-row publish minimum,
   blocking the entire shared `refresh-properties.yml` job). Root cause:
   a pdfplumber text-extraction artifact was splitting dollar amounts
   with a stray internal space (`$348.00` extracted as `$ 3 48.00`),
   which broke the parser's own $20-certificate-fee safety check and
   silently dropped the row -- the safety check was doing its job
   correctly, the bug was in what reached it. Confirmed live against the
   real 2026 PDF and fixed by collapsing the stray whitespace before
   parsing; recovered the complete 1569/1569 real-estate item range,
   verified (not just row-count-verified -- spot-checked that recovered
   values still satisfy the fee invariant). Full detail in BUGS.md
   BUG-008.

   Running the downstream pipeline in order to confirm issue #29 was
   *actually* resolved (not just Woodbury's own step) surfaced that
   Dubuque has never successfully published either -- 9/576 items, not a
   regression from this change. Root cause: the county's PDF resets item
   numbering per district (item "8)" and "9)" each appear 100+ times
   across different districts), but the parser dedupes globally by raw
   item number, discarding every reuse after the first. Filed as issue
   #35 with full evidence; not fixed -- needs the identification key
   reworked to include district, and needs confirming 576 is even the
   right total under a per-district-aware count.

   Workaround shipped so Dubuque's still-broken state doesn't re-block
   the shared pipeline the way Woodbury did: added to `blocked_zero_ok`
   in both workflow files' Verify step, plus `continue-on-error: true`
   on its own refresh step, mirroring the existing Johnson/Linn pattern.

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
