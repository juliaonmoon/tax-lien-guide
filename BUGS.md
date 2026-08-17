# Bug Log & Fixes
### Last updated: August 17, 2026 (BUG-001)

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
