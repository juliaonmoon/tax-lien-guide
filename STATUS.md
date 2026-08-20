# tax-lien-guide — Project Status

## What this is

A nationwide property-level tax lien / tax deed database. GitHub Pages
static site + Python collector scripts + GitHub Actions cron jobs. The
non-negotiable rule: **one row = one individual certificate/parcel/sale
item/property** — never a market summary, a link, or a state-level
description. **Both Claude and ChatGPT actively build on this repo** —
expect `main` to have moved since you last looked; always `git pull`
before touching anything.

## Stack & services

No server, no ports. It's a static site (`index.html`,
`tax-lien-properties.html`, `tax-deed.html`, `property-screener.html`,
`calendar.html`, `project-management.html`, `source-registry.html`) reading
JSON files under `data/`, deployed via GitHub Pages. Data is produced by
Python scripts under `scripts/`, run on a daily cron by GitHub Actions
(`.github/workflows/`). To preview locally: `python -m http.server` from
the repo root (add a `.claude/launch.json` entry pointed at that port if
using the Browser pane).

Python deps used across collectors: `requests`, `beautifulsoup4`,
`pdfplumber`, `pypdf`, `openpyxl`. Tests: `python -m pytest tests/` or
`python -m unittest discover -s tests -v` (CI uses the latter).

## File map

- `TAX_SALE_COVERAGE_AUDIT.md` — **the primary written record.** Narrative
  audit + backlog, updated after every real change. Both Claude and
  ChatGPT read this; tell ChatGPT to read it to update the PM report.
- `BUGS.md` — bug log, `BUG-NNN` format (same convention as the user's
  other repo, `C:\Users\jules\bot projects\BUGS.md`). Currently BUG-001
  through BUG-003.
- `data/source-registry.json` + `source-registry.html` — Claude-built
  nationwide jurisdiction registry (schema: state, county_or_locality,
  sale_system, collector_status, property_query, collector_module,
  test_module, etc.). Validated by `scripts/validate_source_registry.py`.
- `data/project-management.json` + `project-management.html` — the
  **ChatGPT-built "PM tab."** Update this whenever collector work is done
  — standing rule, see Conventions below. **Preserve its compact
  single-line-per-object JSON formatting** when editing (targeted
  string/Edit-tool replacement only — never `json.dump(..., indent=2)` the
  whole file, it produces a huge noisy diff). Validated by
  `scripts/validate_project_management.py`.
- `data/tax-lien-properties.json` — tax lien dataset (Indiana + Arizona).
  Written by `scripts/refresh_tax_lien_properties.py` (Allen, Tippecanoe,
  Wabash, Grant, Coconino) and `scripts/refresh_arizona_cochise_tax_liens.py`
  (Cochise — 93% of all tax-lien records). **Both scripts write to the
  same file; each must only touch its own `profile_id`s and preserve
  everything else** (see BUG-001).
- `scripts/enrich_indiana_assessed_values.py` — fills `assessed_value`,
  `market_value`, `property_address`, `city`, `zip`, `legal_description`
  for the 4 Indiana counties from the official Indiana Gateway
  (`gateway.ifionline.org`). Only fills missing fields, never overwrites.
- `data/properties.json` — tax deed dataset (WA/TX/FL/OK/MI). Written by
  `scripts/refresh_properties.py` (King, Tarrant, Brevard),
  `scripts/refresh_florida_tax_deeds.py` (Putnam, Escambia),
  `scripts/refresh_oklahoma_county_ok_tax_deeds.py` (Oklahoma County), and
  `scripts/refresh_michigan_surplus_tax_properties.py` (statewide surplus
  properties, multi-county) — all three new 2026-08-20. Same shared-file
  caution as above (see BUG-002); Oklahoma's and Michigan's writers merge
  scoped by (state, county) / state respectively, chosen so neither can
  clobber another collector's rows the way BUG-007 describes.
- `.github/workflows/refresh-tax-lien-properties.yml` (cron 14:37 UTC) and
  `refresh-properties.yml` (cron 13:17 UTC) — daily data refresh +
  publish. Share concurrency group `tax-lien-guide-data-writes`. These
  two workflows duplicate the same Johnson/Linn Iowa steps and a
  "Verify Iowa ... output" gate almost verbatim — see BUG-006: a
  brand-new collector's day-zero failure blocked the entire pipeline
  (Indiana/Cochise included) for 15+ runs; fixed with
  `continue-on-error: true` + zero-row tolerance, then **deliberately
  reverted** for `refresh-tax-lien-properties.yml` on 2026-08-19 in
  favor of hard-blocking publish until Iowa coverage is real (see
  BUG-006's "Update" section before touching this again — it's an
  intentional tradeoff tied to active work fixing the Linn/Johnson
  parsers themselves, not an oversight). As of this note, both
  workflows still hard-block on Iowa's current 0-row state.
- `tests/` — one test module per collector, fixture-based (no live network
  calls in tests). 87 tests as of 2026-08-20.

## What works (verified)

- **Indiana tax liens**: Allen (574), Tippecanoe (91), Wabash (57), Grant
  (85, snapshot — sale date passed) — all real, all now enriched with
  official assessed values (807/807 matched, verified against 5 known
  parcels before trusting the parser).
- **Arizona tax liens**: Coconino (33, snapshot), Cochise (11,678, live —
  the largest dataset in the project).
- **Tax deeds**: King WA (145, live), Tarrant TX (live, count fluctuates
  daily), Putnam FL (38, live), Escambia FL (1, snapshot), Brevard FL (0,
  zero_active — real collector, genuinely nothing active right now),
  **Oklahoma County OK (196, live — new 2026-08-20)**: county-owned
  resale parcels (received no bidder at the annual June auction), from
  the Treasurer's own server-rendered HTML list. No owner names published
  by the source at all. **Michigan statewide surplus properties (24, live
  — new 2026-08-20)**: unsold post-auction parcels across 5 counties
  (Arenac/Bay/Jackson/Monroe/Otsego currently) from tax-sale.info's
  rolling Surplus Properties list — deliberately chosen over that same
  platform's per-county live auction catalogs, which are single scheduled
  events that go stale within hours.
- Iowa property-level tax liens (Johnson/Linn/Woodbury/Dubuque) exist as
  real collector code but have not cleared their publish-safety gates yet
  — see "Pending / blocked" below; not counted here.
- Total: 12,518 tax-lien records + 454 tax-deed records as of 2026-08-20
  (Coconino is intentionally cross-listed in both, clearly labeled).
- Full test suite green (87/87) as of 2026-08-20.

## Hard-won gotchas

- **BUG-001**: Two scripts (`refresh_tax_lien_properties.py` and
  `refresh_arizona_cochise_tax_liens.py`) write to the same
  `tax-lien-properties.json` on independent daily schedules. One of them
  used to fully rebuild the file from scratch, silently deleting the
  other's 11,678 records every day. Fix pattern: a shared-file writer must
  read the existing file first, touch only its own `profile_id`s, and
  preserve everything else (`foreign_entries()` in the fixed script).
  **Any new collector sharing a data file with another must follow this
  pattern from day one.**
- **BUG-002**: Same failure class, different script —
  `refresh_properties.py` had no fallback if one of its own sources
  (Brevard/Tarrant/King) failed to fetch; that source's rows would just
  vanish for the run. Fix: `prior_by_county()` retains the previous rows
  for a failed source instead of publishing nothing.
- **BUG-003 — the big one for CI safety**: both refresh workflows had a
  step that did `git reset --hard origin/main` and a later step that did
  `git push origin HEAD:main`, both **unconditional regardless of which
  branch triggered the run**. A `push` to any feature branch could
  silently commit and push straight to `main`, bypassing PR review
  entirely — confirmed to actually happen (twice, via manually-triggered
  `workflow_dispatch` runs on a PR branch). **Any workflow step that
  resets to or pushes to `main` must be gated with
  `if: github.ref == 'refs/heads/main'` — no exceptions, don't reason
  about which steps are "obviously safe" to leave unconditional.**
- Multiple bots (`tax-lien-data-bot`, `tax-deed-data-bot`) and other AI
  sessions commit to `main` frequently and independently — `git fetch
  origin main` and check `git log origin/main -1` immediately before
  branching or merging, every time, no exceptions.
- Official government fixed-width/structured data formats: don't guess
  field positions from samples. Find the authoritative spec first (e.g.
  Indiana's 50 IAC 26-20-4 defines exact byte positions for the DLGF
  Real Property file — used for `enrich_indiana_assessed_values.py`,
  verified against 5 known real parcels before trusting it).
- Owner names are intentionally never collected in bulk tax-lien data
  (established privacy convention, enforced by
  `test_owner_names_are_not_collected`-style tests). Two collectors were
  found violating it and fixed 2026-08-18: Tarrant County TX (BUG-004,
  latent — TAD lookups were failing, so no real name had actually
  published yet) and Florida Putnam/Escambia (BUG-005, **live** — 39
  published rows had real individual owner names, e.g. from Putnam's own
  official "Lands Available" list and the FDOR cadastral feed's
  `OWN_NAME`). Both collectors now hard-code `owner: null` with a
  regression test guarding it; check any *new* collector's source fields
  against this convention explicitly, since a source can hand you a name
  whether or not you asked for it.
- `gh pr checks` and even `gh pr create`/`gh api` can 503 transiently —
  retry once after a short wait rather than assuming it's broken.

## Pending / blocked

- **Johnson County, IA tax liens never actually gone live, and the source
  itself is now blocked** — `scripts/repair_iowa_johnson_parser.py`
  currently parses only ~159 of the expected 700+ real-estate rows from
  the live PDF (confirmed via GitHub Actions logs, 2026-08-19), so it
  keeps preserving zero rows (see BUG-006 for the pipeline-blocking fix;
  this note is about the parsing shortfall itself). A session with real
  internet access confirmed 2026-08-19 that `johnsoncountyiowa.gov` now
  returns an interactive Cloudflare challenge (HTTP 403) sitewide —
  curl, WebFetch, a real Chrome browser, and GitHub Actions itself all
  get the same block, which appeared between two runs today after two
  different parser versions each successfully fetched the real PDF and
  both landed on exactly 159 rows. The 159-vs-700+ question is
  unanswerable until the block lifts; do not guess at a parser fix
  without a live fetch. See BUGS.md BUG-006's 2026-08-19 afternoon
  update. `data/project-management.json`'s `TL-IA-JOHNSON` row is now
  marked `blocked`. Linn County IA is improving but still short: a real
  (non-sandboxed) CI run on PR #18 (2026-08-19, early) found the XLSX
  parser returning 0 rows and its then-PDF-fallback finding 214 of the
  1500+ expected; a separate session then shipped
  `scripts/repair_iowa_linn_pdf_parser.py` (multi-row Excel header
  recognition + trailing-text tolerance), and a later same-day run
  (05:13 UTC) shows genuine progress to **524** rows — still short of
  1500, but real movement, unlike Johnson which is unchanged at 159.
  See BUG-006's "Update" section: because the Verify step checks
  Johnson first, Johnson alone is currently the sole blocker for
  `refresh-tax-lien-properties.yml`'s daily publish, independent of
  Linn's progress.
- **Hillsborough County, FL tax-deed collector** — real, unblocked JSON
  API fully mapped (`POST publicaccess.hillsclerk.com/TD/api/CustomQuery/KeywordSearch`,
  query type `285`). Blocked on one specific question: none of the
  observed `Case Status` values (`SALE`, `SOLD`, `REDEEMED`, `BANKRUPTCY`,
  `PENDING`) is labeled "available," and Florida Statute 197.502 defines
  "lands available for taxes" as a specific legal state (no bidder at
  auction, or buyer failed to pay). Needs real evidence for the
  status-to-availability mapping before writing a parser — full detail in
  `TAX_SALE_COVERAGE_AUDIT.md` §7, item 7.
- **Hamilton County, IN** — 2026 tax sale list not yet published as of
  2026-08-19 (was promised "mid-August"; live-confirmed via `curl` against
  `secure2.hamiltoncounty.in.gov/taxsale/`, which 503s with a "Tax Sale
  Listing Coming 2026" placeholder). Check again in a week or two; same
  generic `indiana_ad_rows()` parser should work once it's out.
- **Montgomery County, IN** — page returns HTTP 403. Not pursued further.
- **Scott County, IA** — official 2026 XLSX list's HTTP 403 cleared
  2026-08-19 (was bot-UA filtering, not real access control), but the row
  structure is genuinely more complex than Linn/Johnson/Dubuque/Woodbury
  (multi-year receipt rows per Item Number, no obvious single
  current-amount-owed field) — not safe to build a parser without an
  authoritative explanation or cross-referencing known items against a
  live source first. See `TAX_SALE_COVERAGE_AUDIT.md` §8e and issue #16.
- **Arizona statewide assessor enrichment** — no equivalent to Indiana's
  DLGF Gateway exists; Cochise/Coconino's own GIS/open-data sites are
  dead ends (empty portals, no parcel dataset found). Not pursued further
  unless a new lead surfaces.
- **California tax-defaulted auctions (Bid4Assets)** — reachable via a
  real browser (plain HTTP fetch gets a 403, likely bot-UA filtering), no
  public API found, and no active CA auction currently listed (next one:
  Santa Clara County, Oct 23–26, 2026). Recheck closer to that date.
- 26 states in `data/source-registry.json` are honestly marked
  `not_started` — no fabricated coverage, just not yet researched. (Was
  28; Oklahoma and Michigan both moved to `live` 2026-08-20.)

## Conventions

- Never commit directly to `main`. Every change: branch → commit → push →
  PR → merge (verify CI first, or verify manually if CI doesn't cover the
  change — e.g. via `gh workflow run <name> --ref <branch>` for a clean
  signal when concurrency cancels the push-triggered check).
- **Update `data/project-management.json` (the PM tab) as part of any
  collector work** — not a separate catch-up step. Bump the relevant
  workstream progress and add/update query rows. See "Preserve its
  compact JSON formatting" above.
- Update `TAX_SALE_COVERAGE_AUDIT.md` after every completed collector,
  bug fix, or significant investigation (even negative findings — "X is
  blocked because Y" is worth recording so nobody re-checks it next week).
- A jurisdiction only earns `property_query: true` / `collector_status:
  live|snapshot|zero_active` when real, executable, tested collector code
  produces individually verified records. A market-summary row or link is
  never coverage.
- Run the full test suite before every PR (`python -m pytest tests/`).
- Never fabricate or infer a field value without official evidence —
  find the authoritative source/spec first.
