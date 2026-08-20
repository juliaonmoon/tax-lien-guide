# Bug Log & Fixes
### Last updated: August 20, 2026 (BUG-007)

---

## BUG-007 — `refresh_florida_tax_deeds.py`'s shared-file merge is scoped by state only, not (state, county); latent, not yet fired

**Severity:** Medium (same failure shape as BUG-001/BUG-002 -- a shared-file collector clobbering another collector's rows -- but currently dormant, not actively happening)
**Found:** August 20, 2026, while adding a new tax-deed collector (Oklahoma County, OK) to `data/properties.json` and reviewing how the file's existing writers avoid clobbering each other
**Affected:** `scripts/refresh_florida_tax_deeds.py`
**Status:** Not fixed. Flagged and documented; the fix belongs to a dedicated change, not bundled into an unrelated new-collector PR.

### What's wrong
`data/properties.json` has three writers: `refresh_properties.py` (fully rebuilds its own 3 hardcoded sources -- Brevard FL, Tarrant TX, King WA -- every run), `refresh_florida_tax_deeds.py` (Putnam FL, Escambia FL), and now `scripts/refresh_oklahoma_county_ok_tax_deeds.py` (Oklahoma County, OK). The workflow runs them in that order every day.

`refresh_florida_tax_deeds.py`'s `merge_state_rows(existing, new_rows, state)` drops every existing row where `row["state"] == state` before adding its own new rows back. It is called with `state="FL"`. But **two different counties share the FL state code in this file**: Brevard (written by `refresh_properties.py`, upstream in the same job) and Putnam/Escambia (written by this script). Because the merge key is state-only, every time `refresh_florida_tax_deeds.py` runs, it silently drops *all* FL rows -- including whatever Brevard rows `refresh_properties.py` just wrote earlier in the same job -- before re-adding only its own Putnam/Escambia rows.

This has not actually caused data loss yet, purely by luck of current conditions: Brevard is currently `zero_active` (STATUS.md: "0, zero_active -- real collector, genuinely nothing active right now"), so there has been nothing for the FL-wide merge to drop. **The moment Brevard's official sale-list page has an active listing again, this will silently delete it from the published file every single day**, the same way BUG-001 silently deleted Cochise County's 11,678 records every day until fixed.

### Why this wasn't fixed here
Found as a side effect of adding a new collector to the same shared file, not the task at hand. Following this repo's "no cross-project/unrelated fixes bundled into an unrelated change" discipline -- flagging it here (and in `TAX_SALE_COVERAGE_AUDIT.md` §8f) rather than silently patching someone else's collector inside an unrelated PR. The new Oklahoma collector added in the same session as this bug was found does **not** have this problem: its own `merge_state_county_rows()` is scoped by `(state, county)` deliberately, specifically because writing it surfaced this issue in the neighboring Florida script.

### Fix (for whoever picks this up)
Change `refresh_florida_tax_deeds.py`'s `merge_state_rows(existing, new_rows, state)` to accept and filter by `(state, county)` pairs instead of state alone -- e.g. drop rows matching `(row["state"], row["county"]) in {("FL","Putnam"), ("FL","Escambia")}`, mirroring the pattern in `refresh_oklahoma_county_ok_tax_deeds.py`'s `merge_state_county_rows()`. Add a regression test asserting a Florida refresh does not remove a Brevard row (the mirror image of `MergeStateRowsTests.test_replaces_only_the_target_state` in `tests/test_florida_tax_deeds.py`, which currently only tests that *other states* survive, not that *other counties in the same state* survive).

### Rule for future collectors
**When multiple collectors share one output file and are distinguished by more than one field (state *and* county), the merge/replace key used to avoid clobbering must include every field that distinguishes one collector's ownership from another's -- not just the first one that happens to be unique among the collectors that exist today.** A merge key that's "unique enough for now" silently stops being safe the moment a new collector is added that shares the coarser key, and the failure is invisible until the clobbered collector's row count is nonzero again.

---

## BUG-006 — A brand-new Iowa collector that had never gone live was crashing the entire shared daily data pipeline, blocking Indiana/Cochise/Linn publishing for 15+ consecutive runs
**Severity:** Critical (same blast-radius class as BUG-001: one collector's problem silently stopped the whole project's daily data refresh from publishing anything, for over a day)
**Found:** August 19, 2026, while checking GitHub Actions run history after merging the Johnson County parser fix (PR #17) — found the scheduled "Refresh property-level tax liens" workflow had been failing since 2026-08-18T08:29 UTC, including its actual 14:37 UTC daily cron run
**Affected:** `.github/workflows/refresh-tax-lien-properties.yml`
**Status:** Fixed, then partially superseded by a deliberate later decision — see "Update" below

### What happened
`scripts/refresh_iowa_johnson_tax_liens.py` was recently added to this workflow's steps (no `continue-on-error`), followed by a "Verify Iowa collectors materially populated generated output" step that hard-requires `IA-Johnson-2026` to have >=700 rows and `IA-Linn-2026` to have >=1500 rows, with no exception.

Both `refresh_iowa_johnson_tax_liens.py` and `refresh_iowa_linn_tax_liens.py` already had a fallback-to-prior-data pattern matching BUG-002's convention (`existing_rows()` / preserve on failure) -- but only when prior data exists. Neither county's collector has ever successfully published a single row yet. So every time the live source was unreachable or unparseable (confirmed live: `RuntimeError: Johnson County parser found only 159 real-estate rows; expected at least 700`), `main()`'s fallback found `existing_rows()` empty and re-raised, crashing the job with exit code 1 -- before the Linn step, the Verify step, `recount_tax_lien_properties.py`, the test suite, or the Publish step ever ran. That blocked *every* collector in this shared job, including the long-established, currently-working Indiana and Cochise County data, from being republished. Confirmed via GitHub Actions run history: repeated `failure` conclusions on `push` events from 2026-08-18T08:29 UTC through at least 2026-08-19T01:45 UTC, including the actual `schedule`-triggered 14:37 UTC production run.

No data was corrupted -- the scripts raise before writing anything, and the Publish step (which does a fresh `git reset --hard origin/main` before committing) never ran. The failure mode was staleness (the site's Indiana/Cochise data stopped getting daily refreshes), not incorrect published data.

### Fix
Two changes to `refresh-tax-lien-properties.yml`, following the same pattern already established for exactly this problem in `refresh-properties.yml` (`core_property_refresh` / `king_public_safety` steps):
1. Added `continue-on-error: true` to the Johnson and Linn refresh steps, so a failure in either no longer aborts the job.
2. Changed the "Verify Iowa collectors" step: a profile with **zero** rows now prints a warning and is skipped (not yet live -- expected and acceptable), while a profile with **some but too few** rows (a genuine partial/corrupt parse, like the live 159-row case) still hard-fails as before. Only `if not county_rows: continue` was added; the `len(county_rows) < minimum` regression check is unchanged for any profile that does produce rows.

The underlying question of *why* the Johnson County PDF currently parses to only 159 of the expected 700+ rows is still open -- this fix does not address that, it only stops that open question from taking down the rest of the project's daily data pipeline while it's unresolved. Investigating the live PDF requires an environment with real internet access (this session's did not, see `HANDOFF.md`).

### Files changed
- `.github/workflows/refresh-tax-lien-properties.yml` -- `continue-on-error: true` on the two Iowa steps; the Verify step tolerates zero rows for a profile that has never gone live.

### Rule for future collectors
**A brand-new collector that has never had a successful run is a *day-zero* case, not the same as an established collector suddenly losing its data (BUG-002's case) -- both need a fallback, but "fall back to nothing" must never be allowed to abort a shared job that other, already-working collectors depend on.** When adding a new collector to an existing shared workflow: (1) wrap its own step in `continue-on-error: true` if it's genuinely independent of the steps around it, and (2) any downstream validation step with a hard minimum-row-count requirement must explicitly tolerate zero rows for a profile that has no baseline yet, while still failing hard on a non-zero-but-implausibly-low count (that's a real parsing regression, not a pending launch).

### Update, August 19, 2026 — the zero-row tolerance was deliberately reverted for `refresh-tax-lien-properties.yml`
Commit `4eed211` ("fix: require Iowa property-level lien coverage before publish", pushed directly to `main`, not through a PR) removed the `if not county_rows: continue` tolerance added above and restored the unconditional hard-fail, with an explicit new rationale in the raised message: *"Refusing to publish a silently incomplete Iowa property-level dataset."* That commit landed alongside several other same-session commits actually fixing the underlying Linn County parser (`fix: recognize Linn County multi-row Excel headers`, `fix: tolerate trailing text in Linn County PDF item lines`, `fix: use resilient Linn County parser in recurring refresh`, adding `scripts/repair_iowa_linn_pdf_parser.py`) -- i.e. this was a deliberate, informed policy choice by whoever was driving that work (real-time root-cause fixing, something this session couldn't do without live internet access), not an accidental regression. `continue-on-error: true` on the Johnson/Linn steps themselves was left in place, but since the Verify step right after them still hard-fails unconditionally, the net effect for this workflow is the same full-pipeline block this bug originally described (confirmed live: a `push`-triggered run at 2026-08-19T05:12 UTC still failed with `IA-Johnson-2026: only 0 generated rows`, and `data/tax-lien-properties.json` on `main` still shows 0 rows for both `IA-Johnson-2026` and `IA-Linn-2026`).

**Do not silently re-revert this without understanding why it was chosen.** If picking this up again: check whether the Linn/Johnson parsers have since been fixed for real (which would make the whole tolerate-vs-block question moot) before touching the Verify logic again. `refresh-properties.yml`'s identical duplicate Verify block (see "Rule" above -- it was never fixed there either, this session's prepared parallel fix was discarded on discovering the revert rather than pushed) is in the same state for the same reason: left alone pending the real parser fix, not because it was overlooked.

Real, verified progress as of the same 2026-08-19T05:13 UTC run: Linn's new `repair_iowa_linn_pdf_parser.py` (Excel-first with a repaired PDF fallback) now finds **524** real-estate rows, up from 214 before this session's earlier check on PR #18 -- genuine improvement, still short of the 1500 minimum. Johnson is unchanged at 159. Because the Verify step's `minimums` dict checks `IA-Johnson-2026` first and raises immediately on it, **Johnson alone is currently the sole blocker for this workflow** -- Linn's now-improved output never even gets evaluated against its own threshold before the job dies. Worth knowing: fixing Johnson alone might be enough to unblock this workflow soon, independent of whether Linn ever reaches 1500.

### Update, August 19, 2026 (afternoon) — johnsoncountyiowa.gov now hard-blocks all automated access; the 159-row shortfall investigation is stalled behind a new, more fundamental blocker
This session had real, unrestricted internet access (unlike the session that wrote the "Update" above) and set out to fetch the live PDF and compare its real structure to the parser's assumptions, per the standing instruction not to guess at a fix. Findings, most important first:

1. **The site is currently unreachable to any automated client, sitewide, not just for the PDF.** `curl` (with and without a browser-realistic `User-Agent`), `WebFetch`, and a real, non-headless-flagged Chrome browser driven via Playwright (`channel="chrome"`) all get HTTP 403 with a Cloudflare **interactive** challenge page (`title: Just a moment...`, `cType: 'interactive'` in the challenge payload — this variant requires genuine human interaction, not just a JS-capable client; it will not auto-clear). Confirmed on the PDF URL, the treasurer page (`/treasurer/tax-sale-publication-lists`), the bare homepage (`/`), and even `/robots.txt` and a nonexistent path — i.e. this is a domain-wide Cloudflare bot-protection rule, not something targeting scrapers of this one file.
2. **This is brand new, and it broke GitHub Actions too, not just this session's sandbox.** Checked actual run logs (`gh run view --log`): the 2026-08-19T05:13 UTC run (`refresh_iowa_johnson_tax_liens.py`, original parser) and the 2026-08-19T06:29 UTC run (`repair_iowa_johnson_parser.py` at commit `2e77207`, the item-anchored version, pre-column-rewrite) **both successfully fetched the real PDF** and both independently landed on exactly **159** rows. Then the very next run, 2026-08-19T07:18 UTC (`repair_iowa_johnson_parser.py` at commit `7dad1a9`, the column-aware coordinate-based rewrite) failed immediately with `requests.exceptions.HTTPError: 403 Client Error: Forbidden` on `fetch_pdf()` — the Cloudflare block appeared on the live site sometime in that ~49-minute window and is still active as of this writing (re-confirmed with a direct `curl` retry).
3. **The column-aware rewrite (`7dad1a9`, current `repair_iowa_johnson_parser.py`) has never actually been tested against real data.** Its first-ever live CI run hit the new 403 wall before extracting a single byte of PDF text. So it's not that the rewrite "made no difference" (159 -> 159) — it never ran. The only two real, apples-to-apples data points we have are the *pre-rewrite* item-anchored parser and the original sequential-scan parser, both of which independently produced 159 from two separate live fetches of the actual current PDF. That's a real, mildly interesting signal (two different regex-based algorithms agree exactly), but it doesn't confirm or rule out the column-interleaving theory the rewrite was built on, since neither of those two ever attempted word-coordinate-based column reconstruction.
4. **No cached copy exists to substitute for a live fetch.** Checked the Wayback Machine (`archive.org/wayback/available` and a CDX search over `johnsoncountyiowa.gov/sites/default/files/*` and `*gazette*`/`*2026-06*`) — no snapshot of this PDF or the publication-lists page has ever been archived.

**Net effect: the original question ("why does the real PDF only parse to 159 of 700+ rows") is currently unanswerable from any environment, including GitHub Actions, until johnsoncountyiowa.gov's Cloudflare rule changes.** Per the standing instruction not to guess at a fix without seeing the real PDF, **no change was made to either Johnson County parser script this session.** `data/project-management.json`'s `TL-IA-JOHNSON` row was set to `status: "blocked"` (previously `in_progress`) with a note pointing back here, so a future session doesn't re-attempt the same fetch expecting a different result without first checking whether the block has lifted.

**If picking this up again:** first re-run the exact `curl` sitewide check above (homepage + robots.txt + the PDF URL) before touching parser code — if any of those now return 200, the block was transient and the real investigation (column-aware extraction vs. the true PDF layout) can resume. If still blocked, this needs either (a) the county's site to reopen access on its own, or (b) an explicit decision from the user about whether a heavier-weight legitimate access path (e.g. a real, human-supervised browser session) is worth pursuing for a public-records PDF — not something to solve unilaterally by defeating an interactive bot challenge.

---

## BUG-005 — Florida tax-deed collector was actually publishing real owner names for 38 live Putnam/Escambia rows, not just latently capable of it like BUG-004
**Severity:** High (unlike BUG-004, this one had already fired — real individual names, not just business names, were live in `data/properties.json` on GitHub Pages)
**Found:** August 18, 2026, immediately after fixing BUG-004, by auditing the rest of `scripts/` for the same `"owner"` pattern
**Affected:** `scripts/refresh_florida_tax_deeds.py` (`putnam_live()`/`base_row()`/`cadastral_enrich()`), `data/properties.json` (Putnam + Escambia rows)
**Status:** Fixed

### What happened
While fixing BUG-004 (Tarrant County), a repo-wide grep for other `"owner"` assignments turned up a second, more severe instance of the exact same convention violation:

1. `putnam_live()`'s regex captures the text immediately following each `T.D. <case-number>` line on Putnam Clerk's own official "Lands Available for Taxes" list. That text is the property owner's name printed on the document itself (confirmed directly in `data/florida-putnam-verified-snapshot.json`, e.g. record `["2018-0008244", "KARY M BEARD JR", ...]`). This value flowed straight through `base_row()`'s `owner` parameter into the published row.
2. `cadastral_enrich()` separately requested `OWN_NAME` from the Florida DOR statewide cadastral feed and used it to backfill `owner` when not already set (covering Escambia, which has no owner in its own source list).

Unlike BUG-004, this wasn't just live-and-unexercised — checking `data/properties.json` directly showed **all 39 Florida rows (38 Putnam, 1 Escambia) had a real owner name populated**, including real individuals' full names (e.g. "CRYSTAL SCHEERER", "KARY M BEARD JR"), not just business names. This had been true since Putnam/Escambia were added (2026-08-15) and was still live at the time of this fix.

### Fix
- `base_row()` no longer takes an `owner` parameter; it always emits `"owner": None`.
- `putnam_live()`'s record tuples still carry the raw owner-name text at index 1 (unchanged, to stay compatible with the existing snapshot fixture format), but the two call sites that build rows from those tuples now explicitly skip that slot before calling `base_row()`.
- `cadastral_enrich()` no longer requests `OWN_NAME` from the FDOR feed at all (removed from the `outFields` list) and no longer has an owner-backfill branch.
- Cleared the `owner` field to `null` on all 39 already-published Florida rows in `data/properties.json` (targeted values-only change; every other field on those rows is untouched).

### Tests added
`tests/test_florida_tax_deeds.py`:
- `test_florida_rows_never_carry_a_real_owner_name` — asserts every live Putnam/Escambia row has `owner is None`.
- `OwnerNameNeverCollectedTests.test_base_row_never_emits_an_owner` — `base_row()` never produces an owner key from its own logic.
- `OwnerNameNeverCollectedTests.test_putnam_record_unpacking_skips_the_owner_slot` — feeds a record shaped exactly like a `putnam_live()`/snapshot tuple, with a real name at index 1, and asserts it never reaches the row (checked both via the `owner` field and via a full-row string search, so a future refactor that puts the name somewhere else in the row is also caught).
- `OwnerNameNeverCollectedTests.test_cadastral_enrich_does_not_set_owner_name_even_if_the_feed_returns_one` — feeds `cadastral_enrich()` a fake FDOR response that does include `OWN_NAME`, and asserts the row's `owner` stays `None`.

### Files changed
- `scripts/refresh_florida_tax_deeds.py` — see Fix above.
- `data/properties.json` — 39 Florida rows' `owner` field set to `null`.
- `tests/test_florida_tax_deeds.py` — new regression tests (above).

### Rule for future collectors
Same rule as BUG-004, restated because it was violated twice independently in the same session: **check every field a source response contains against the no-bulk-owner-names convention before wiring it into a row, not just the fields you intentionally asked for.** A source can hand you a name whether or not you requested it (Putnam's list prints it inline; FDOR's `outFields` had to be explicitly asked to stop including it) — the discipline has to be "never let this specific field through," not "don't go looking for it."

---

## BUG-004 — Tarrant County tax-deed collector silently harvested real owner names, contradicting the repo's no-bulk-owner-names privacy convention
**Severity:** Medium (privacy-policy inconsistency; not a data-integrity or availability bug like BUG-001/002/003 — no incorrect data was ever published, but the code was one working upstream page away from violating a documented convention)
**Found:** August 18, 2026, flagged as an already-known-but-unreconciled gap in `STATUS.md`'s "Hard-won gotchas" section, then confirmed by reading the code
**Affected:** `scripts/refresh_properties.py` (`tad_enrich()`, used by `tarrant_properties()`)
**Status:** Fixed

### What happened
Every other collector in this repo enforces "owner names are intentionally
never collected in bulk tax-lien data" (`STATUS.md`) — King County's `owner`
field is always a fixed placeholder string, and Arizona/Indiana collectors
never touch an owner field at all. `tad_enrich()`, which enriches Tarrant
County TX tax-deed rows from the public Tarrant Appraisal District site,
was the one exception: its results-table parser read the owner-name cell at
`tail[2]` into `out["owner"]`, which `tarrant_properties()` then merged
straight into the published row via `row.update(extra)`.

This hadn't actually surfaced in `data/properties.json` yet — every current
Tarrant row shows `TAD lookup failed: HTTPError` in `enrichment_note`, so
the owner-scraping code path wasn't executing in practice — but it was live
and would have started publishing real names the moment TAD's site started
responding normally again. No test caught it: `test_refresh_properties.py`
only asserted the King placeholder, not that Tarrant/TAD enrichment stays
owner-free.

### Fix
Removed the `out["owner"]=tail[2]` line from `tad_enrich()` entirely — the
owner cell is simply skipped now, same as if the convention had been
followed from day one. Market-value extraction (`tail[3]`) is unaffected
since it doesn't depend on the owner assignment happening first.

### Tests added
`tests/test_refresh_properties.py`:
- `test_tarrant_rows_never_carry_a_real_owner_name` — asserts every live
  Tarrant row in `data/properties.json` has `owner is None`, mirroring the
  existing King placeholder test.
- `TadEnrichOwnerNameTests.test_owner_column_is_skipped_even_though_present_in_source_html`
  — feeds `tad_enrich()` a fixture HTML table row that *does* contain a
  plausible owner name in the TAD column position, and asserts the
  returned dict never has an `"owner"` key, while address/city/market
  value still parse correctly. This is the regression guard: it fails if
  the owner line is ever reintroduced, even before the live site would
  reveal it.

### Files changed
- `scripts/refresh_properties.py` — `tad_enrich()` no longer extracts an
  owner name.
- `tests/test_refresh_properties.py` — new regression tests (above).

### Rule for future collectors
**"Owner names are never collected in bulk" applies to every collector,
with no ad-hoc exceptions, even when the upstream public source makes the
name trivially available in the same response as the fields you do want.**
If a future collector's source happens to expose owner data alongside
useful fields, skip that specific field explicitly (as `tad_enrich()` now
does) rather than accepting a "TODO reconcile with convention" callout in
`STATUS.md`.

---

## BUG-003 — Both data-refresh workflows silently tested `main` on PR pushes, and could publish branch content straight to `main` without review
**Severity:** Critical (a `push`-triggered run on any branch could commit and push directly to `main`, bypassing PR review entirely -- confirmed to have actually happened, see below)
**Found:** August 18, 2026, in two stages -- first as a CI crash, then as an actual unreviewed push to `main`
**Affected:** `.github/workflows/refresh-tax-lien-properties.yml` and `.github/workflows/refresh-properties.yml` (both present since each workflow's original commit -- not introduced in this change)
**Status:** Fixed

### What happened -- part 1 (CI silently tested main, not the PR)
Both data-refresh workflows trigger on `push` (for fast feedback when a
collector script changes) in addition to `schedule` and `workflow_dispatch`.
Both also start with:
```yaml
- uses: actions/checkout@v4
- name: Sync latest main
  run: |
    git fetch origin main
    git reset --hard origin/main
```
This unconditional `reset --hard origin/main` runs regardless of which ref
triggered the workflow. For a `push` to a feature/PR branch, `checkout@v4`
correctly checks out that branch's commit -- and then this step immediately
throws it away and resets to `main` instead. Every step after it (running
the collector, running the test suite) then operates on `main`, not on the
actual pushed diff. This was invisible on prior PRs because the affected
files already existed on `main` in a working, older form -- the check would
silently re-validate `main` and report "pass" regardless of what the PR
changed. It surfaced when a PR added a brand new file
(`scripts/enrich_indiana_assessed_values.py`) that only existed on the PR
branch: the workflow reset the checkout away from it, then crashed trying
to run a script that (from its point of view) didn't exist.

**First fix attempt:** added `if: github.ref == 'refs/heads/main'` to the
"Sync latest main" step in both workflows, reasoning that the "Publish"
step's own `reset --hard origin/main` (further down each workflow, inside
its retry loop) was a separate, correctly-unconditional concern since
publishing always needs to target the latest `main`.

### What happened -- part 2 (that "separate concern" was actually the same bug, and it fired for real)
That reasoning was wrong. Once the "Sync latest main" step stopped wiping
the branch checkout, both workflows' **Publish** steps -- which build their
commit from a wholesale copy of the entire `data/` directory
(`cp -a data /tmp/refresh-output/data` in `refresh-properties.yml`) and then
unconditionally `git push origin HEAD:main` -- started publishing *whatever
was in the branch's checkout*, not just the output of that workflow's own
scripts. On a `push`-triggered run for a PR branch, that includes any data
file the branch had already modified for reasons that had nothing to do
with that workflow's own steps.

This was confirmed to actually happen, not just a theoretical read of the
code: a manually-triggered run of "Refresh property-level tax liens" on a
PR branch (queued to verify the BUG-003 fix above) picked up that branch's
already-enriched `data/tax-lien-properties.json` and committed+pushed it
directly to `main` as `d423057` ("chore: refresh property-level tax
liens"), and a run of "Refresh tax deed property data" on the same branch
did the same via its own wholesale-directory-copy publish step
(`b47696a`). Neither the enrichment script nor the workflow step that runs
it existed on `main` at the time -- only the *output* landed there,
unreviewed, ahead of the code that produces it. The data itself was real
and correct (verified official Indiana assessed values, not fabricated),
so no incorrect data reached `main` -- but the process violation is real:
a `push` to a feature branch was able to write directly to `main` with no
PR, no review, and no branch protection in the way.

### Fix
Extended the same guard to the **Publish** step in both workflows:
`if: github.ref == 'refs/heads/main'`. A workflow run now only ever pushes
to `main` when it is actually running on `main` itself (scheduled runs,
`workflow_dispatch` on `main`, or a `push` landing on `main` post-merge).
A `push`-triggered run on any other branch now validates (runs the
collector, runs the test suite) without ever being able to write to
`main` -- publishing only ever happens through an actual merge to `main`,
same as everywhere else in this repo's workflow.

### Rule for future workflow changes
**Any step that runs `git push origin HEAD:main` (or resets to `main`)
must be scoped to `if: github.ref == 'refs/heads/main'`, full stop --
including "obviously main-only" steps like Publish.** Don't reason about
which steps are "safe" to leave unconditional; if a workflow triggers on
`push` to non-default branches at all, every write-to-main step needs the
guard, or a `push` to any branch matching that workflow's path filters can
write to `main` without review.

---

## BUG-002 — `refresh_properties.py` had no fallback if a source fetch failed; a source's rows would just vanish for that run
**Severity:** High (same bug class as BUG-001, not yet observed firing in production, found while adding test coverage)
**Found:** August 17, 2026, while writing `tests/test_refresh_properties.py`
**Affected:** `data/properties.json` (King, Tarrant, Brevard rows)
**Status:** Fixed

### What happened
`refresh_properties.py`'s `main()` rebuilt its list of properties from
scratch every run: `properties = []`, then for each of its 3 sources
(Brevard, Tarrant, King) it tried to fetch and parse that county's data,
and on success extended `properties` with the parsed rows. If the fetch or
parse for a source raised an exception, the `except` branch only logged
the error into `source_health` — it never fell back to that source's
previously published rows. The whole `properties` list (missing whatever
source had just failed) was then written out unconditionally.

This is the same failure class as BUG-001 (a source's data silently
disappearing from the published file on a transient failure), just in a
different script and not yet confirmed to have fired in production —
found by inspection while writing tests, not by observing a live
incident.

Unlike BUG-001, this wasn't a *cross-collector* conflict — `refresh_properties.py`
is the sole owner of the King/Tarrant/Brevard rows in `data/properties.json`
(Florida rows are owned separately by `refresh_florida_tax_deeds.py`, which
already merges correctly — see `merge_state_rows()` and its tests). The gap
here was simpler: no per-source retry/fallback logic existed at all for its
own sources.

### Fix
Added `prior_by_county()`, which reads the current `data/properties.json`
and groups existing rows by `(state, county)`. In `main()`, if a source's
fetch/parse raises, the except branch now falls back to that source's rows
from `prior_by_county()` instead of contributing nothing, and records
`retained_previous_rows` in that source's `source_health` entry.

### Tests added
`tests/test_refresh_properties.py`:
- `PropertiesDatasetTests` — schema and per-county-parcel uniqueness checks
  on the live dataset, plus a check that King's `owner` field is always the
  documented placeholder string, never a real name.
- `PriorByCountyFallbackTests` — regression test for `prior_by_county()`
  against a fixture file, including the missing-file case.

Also added `tests/test_florida_tax_deeds.py`, which extracts and directly
tests `merge_state_rows()` (a small refactor, no behavior change) —
confirming the Florida side of this same file-sharing relationship stays
correct in isolation, and `tests/test_arizona_cochise_tax_liens.py`, which
covers CSV parsing/dedup/no-owner-names and the `main()` fallback path
already present in `refresh_arizona_cochise_tax_liens.py`.

### Files changed
- `scripts/refresh_properties.py` — added `prior_by_county()`; `main()`
  now falls back to prior rows per-source on failure.
- `scripts/refresh_florida_tax_deeds.py` — extracted `merge_state_rows()`
  from inline logic in `main()` (no behavior change; done for testability).
- `tests/test_refresh_properties.py` — new.
- `tests/test_florida_tax_deeds.py` — new.
- `tests/test_arizona_cochise_tax_liens.py` — new.

### Rule for future collectors
Same rule as BUG-001, extended: **every collector must be able to survive
its own source failing**, not just failures caused by another collector
sharing its output file. If a fetch or parse can raise, there must be a
fallback to the previously published rows for that specific source — never
an unconditional rebuild-from-scratch.

---

## BUG-001 — `refresh_tax_lien_properties.py` silently deleted Cochise County's 11,678 records every day
**Severity:** Critical (largest dataset in the project, ~93% of all tax-lien records, deleted daily)
**Found:** August 16, 2026, while building the nationwide source registry
**Affected:** `data/tax-lien-properties.json` (all consumers: `tax-lien-properties.html`, `calendar.html`, `property-screener.html`, the PWA cache)
**Status:** Fixed

### What happened
Two separate daily scheduled workflows both write into the same output file,
`data/tax-lien-properties.json`, with no coordination between them:

- `refresh-properties.yml` (cron `17 13 * * *`, 13:17 UTC) runs
  `refresh_arizona_cochise_tax_liens.py`, which does a read-modify-write:
  it removes only its own `profile_id` (`AZ-Cochise-OTC`) and re-adds its
  11,678 fresh records, leaving everything else in the file untouched.
- `refresh-tax-lien-properties.yml` (cron `37 14 * * *`, 14:37 UTC — later
  the same day) runs `refresh_tax_lien_properties.py`, which rebuilt the
  entire output file from scratch every run: `properties = []`, then only
  ever repopulated it with Allen/Tippecanoe/Wabash/Coconino County rows.
  It had no knowledge that Cochise County existed at all.

Net effect: every day at 14:37 UTC, the 11,678 verified Cochise County
records were silently overwritten out of existence, dropping the dataset
from 12,433 records down to 755. They only came back the next day at 13:17
UTC when the Cochise collector ran again — so the site was serving a
dataset missing 93% of its real content for roughly 23 of every 24 hours.

**This wasn't just found in testing — it fired for real in production
mid-fix.** While the fix for this bug was being developed and reviewed
(2026-08-17, ~07:09 UTC), the scheduled `refresh-tax-lien-properties.yml`
workflow ran on `main` using the still-unfixed script and reproduced the
exact failure: `main`'s `data/tax-lien-properties.json` dropped from
12,433 records to 755 (`states: 2, counties: 4`, no Cochise) for about two
minutes until the fix's PR (#4) was merged and its own refresh regenerated
the file correctly. Confirmed via `git show origin/main:data/tax-lien-properties.json`
at the time, and via the merged PR's own CI run of
`refresh-tax-lien-properties.yml` immediately restoring 12,518 records.

### Fix
`refresh_tax_lien_properties.py` now reads the existing output file before
writing, computes which `profile_id`s it owns (Allen/Tippecanoe/Wabash/
Grant/Coconino — all derived as `{state}-{county}-2026`), and preserves
every other collector's rows and profile metadata exactly as written,
untouched (`foreign_entries()`). It no longer assumes it is the only writer
of its output file.

### Tests added
`ForeignCollectorPreservationTests` in `tests/test_tax_lien_properties.py`:
- `test_unmanaged_profile_is_preserved` — a fixture file with an
  `AZ-Cochise-OTC` profile survives a call to `foreign_entries()` when that
  profile isn't in the caller's managed set.
- `test_managed_profile_is_excluded` — a profile that *is* in the managed
  set is correctly excluded (so the collector doesn't duplicate its own
  rows on top of a stale prior version of itself).

### Files changed
- `scripts/refresh_tax_lien_properties.py` — added `foreign_entries()`;
  `main()` now merges preserved rows into the final output and counts
  instead of overwriting.
- `tests/test_tax_lien_properties.py` — new regression test class.

### Rule for future collectors
**Any script that writes to a JSON file another script also writes to must
never assume it owns the whole file.** Read the existing file first, only
touch the `profile_id`s / record IDs you actually manage, and preserve
everything else untouched. This applies to `data/properties.json` too —
`refresh_properties.py` and `refresh_florida_tax_deeds.py` share it and
were checked as part of this fix (both already merge rather than
overwrite, so they're currently safe), but there's no structural guard
preventing a future regression there. See `TAX_SALE_COVERAGE_AUDIT.md` §3.
