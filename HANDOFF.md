# Handoff

## ⚡ In-flight work

**Clean stop.** No collector or fix is mid-implementation. This session
started by re-reading `STATUS.md`/`HANDOFF.md`, then discovered its
environment had no general internet egress (only GitHub reachable —
confirmed via a direct `curl` 403 on the CONNECT tunnel, `WebFetch`/`WebSearch`-driven
page fetches to non-GitHub domains failed the same way), which ruled out
the two obvious next steps from the prior handoff (resolving the
Hillsborough status-mapping blocker, rechecking Hamilton County IN's tax
sale list) — both need live fetches against county/state government sites.

Pivoted to something verifiable without network access: fixed BUG-004
(`BUGS.md`) — `scripts/refresh_properties.py`'s `tad_enrich()` was scraping
a real owner name from the Tarrant Appraisal District into the published
`owner` field, contradicting the repo's documented "owner names never
collected in bulk" convention. This was flagged as a known-but-unreconciled
gap in the previous `STATUS.md`. Fixed by dropping the owner-column
extraction; added two regression tests (`tests/test_refresh_properties.py`)
including one that feeds `tad_enrich()` a fixture HTML row with a real name
in the owner-column position and asserts it never comes out.

Committed, pushed, and opened **PR #13**
(`claude/tax-lien-guide-handoff-990v3q` → `main`), then subscribed to its
CI/review activity. While CI was running, audited the rest of `scripts/`
for the same `"owner"` pattern and found a second, worse instance: BUG-005
— `scripts/refresh_florida_tax_deeds.py` was **actually publishing** real
individual owner names for all 39 live Putnam/Escambia rows (not just
latently capable of it like BUG-004), sourced from Putnam's own official
"Lands Available" list text and the FDOR cadastral feed's `OWN_NAME`. Fixed
the same way — `owner` now always `null`, four new regression tests in
`tests/test_florida_tax_deeds.py` — and additionally cleared the `owner`
field on the 39 already-published rows in `data/properties.json` (targeted
values-only edit). Pushed as a second commit onto the same branch/PR #13.

Full suite is 55/55 (was 49/49 at session start). Also updated
`STATUS.md`, `TAX_SALE_COVERAGE_AUDIT.md` (§7 items 8b/8c), and
`data/project-management.json`'s `TD-TX-TARRANT`/`TD-FL-PUTNAM`/
`TD-FL-ESCAMBIA` notes per the standing conventions.

**Check PR #13's current state before doing anything else** —
`https://github.com/juliaonmoon/tax-lien-guide/pull/13`. This session
subscribed to its activity and scheduled a ~1hr self-check-in
(`send_later`), so it may already be merged, may have review comments to
address, or may still be waiting; don't assume based on this file alone.

Next concrete step after that: same as the prior handoff's still-open
items — resolve the Hillsborough status-mapping question with real
evidence, or check whether Hamilton County IN's list has been published —
but only from a session/environment with actual internet access beyond
GitHub. Worth checking your own environment's egress with a quick `curl`
before assuming those are reachable. Also worth another pass over the
remaining `scripts/` files (King County enrichment/fix scripts especially)
for the same class of privacy-convention gap, in case BUG-004/BUG-005
weren't the only two.

## ❓ Open decisions

None pending. The user said "keep going" / "you decide" for backlog
prioritization generally — no specific open question is blocking work.

## 🆕 New gotchas this session

- **Not every session/environment running this project has general
  internet access.** This one only reached GitHub (its network policy);
  `curl` to `example.com` and `www.google.com` both got a 403 on the
  CONNECT tunnel, same as the actual government sites this project's
  collectors need. If live research against an external site is the next
  task, verify egress first (`curl -sS -o /dev/null -w "%{http_code}\n"
  https://example.com`) rather than assuming it'll work — this project's
  own collector scripts only ever actually run inside GitHub Actions
  (which does have full internet), not necessarily inside whatever session
  is editing them.
- BUG-004/BUG-005 (see `BUGS.md`) are a reminder that "not yet reconciled
  with convention" callouts in `STATUS.md` are real open bugs, not just
  notes — worth treating them as backlog items even when there's no live
  network to do "real" collector work. They're also a reminder that a
  known violation in one collector is worth grepping the rest of `scripts/`
  for immediately — BUG-005 (Florida, live, 39 real names actually
  published) was strictly worse than BUG-004 (Tarrant, latent) and was
  only found by checking whether the same mistake had been made elsewhere.

## 📁 Project path

This session's working directory is `/home/user/tax-lien-guide` (a Claude
Code web/cloud session, not the Windows local clone `C:\Users\jules\tax-lien-guide`
referenced in earlier handoffs — both are valid clones of the same GitHub
repo, just from different sessions/machines).

## 📜 Transcript path

Not applicable to this session (cloud/remote execution, no local
`~/.claude/projects/` transcript file).
