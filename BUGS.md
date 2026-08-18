# Bug Log & Fixes
### Last updated: August 18, 2026 (BUG-004)

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
