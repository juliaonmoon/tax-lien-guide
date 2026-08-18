# Bug Log & Fixes
### Last updated: August 18, 2026 (BUG-003)

---

## BUG-003 — Both data-refresh workflows silently tested `main`, not the pushed branch, on every PR
**Severity:** High (CI validation gap -- a push-triggered check could pass or fail without any relation to what was actually pushed)
**Found:** August 18, 2026, when this PR's own CI run crashed with "No such file or directory" for a file that had just been committed and pushed
**Affected:** `.github/workflows/refresh-tax-lien-properties.yml` and `.github/workflows/refresh-properties.yml` (present since each workflow's original commit -- not introduced in this change)
**Status:** Fixed

### What happened
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
actual pushed diff.

This was invisible on prior PRs because the affected files already existed
on `main` in a working, if older, form -- the check would just silently
re-validate whatever was already on `main` and report "pass," regardless of
what the PR actually changed. It surfaced now because this PR adds a brand
new file (`scripts/enrich_indiana_assessed_values.py`) that only exists on
the PR branch: the workflow reset away the checkout that had it, then tried
to run `python scripts/enrich_indiana_assessed_values.py` against a
checkout of `main` that had never heard of it, and crashed with
`No such file or directory`.

The step's intent is legitimate for its `schedule`/`workflow_dispatch`
runs -- always operate on the freshest `main` regardless of any raciness
in how the runner's default checkout landed -- it just should never apply
to a `push` event on a non-`main` ref.

### Fix
Added `if: github.ref == 'refs/heads/main'` to the "Sync latest main" step
in both workflows. This preserves the original behavior for scheduled runs,
`workflow_dispatch` runs, and `push` events that land on `main` itself
(e.g. after a merge), while a `push` to any other branch now keeps
`checkout@v4`'s actual pushed content all the way through the job -- so the
generated `refresh`/`validate` checks on a PR now genuinely test that PR's
diff. The separate `reset --hard origin/main` inside the "Publish" step's
retry loop (further down each workflow) was left untouched -- that one is
correctly unconditional, since publishing always needs to target the
latest `main` regardless of what triggered the run.

### Rule for future workflow changes
**Never reset a workflow's checkout to `main` unconditionally when the
workflow also triggers on `push` to other branches.** If a step's purpose
is "always operate on the freshest default branch," it must be scoped with
`if: github.ref == 'refs/heads/<default-branch>'` (or equivalent), or it
silently defeats PR-level CI validation for every other branch.

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
